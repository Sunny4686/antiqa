"""SQLite job queue and a single worker thread (runs inside the web process)."""

import logging
import re
import threading
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from fyndjakt import capture
from fyndjakt.ai import budget, enrich
from fyndjakt.assess import Deps, assess_listing, notify_owner, send_alert_for
from fyndjakt.backup import backup_sqlite
from fyndjakt.db import session_scope
from fyndjakt.images import image_block, purge_old, resize_jpeg
from fyndjakt.models import AICall, Job, SourceHealth, WatchModel
from fyndjakt.pipeline.prefilter import prefilter, strict_title_match, watch_terms
from fyndjakt.services import (
    IngestListing,
    enqueue,
    get_settings,
    health_problems,
    health_row,
    is_stopped,
    known_comp_ids,
    record_failure,
    record_success,
    upsert_comp,
    upsert_listing,
)
from fyndjakt.sources.auctionet import (
    FURNITURE_CATEGORY,
    FURNITURE_SUBCATEGORIES,
    AuctionetClient,
    SourceBlocked,
    live_price,
    parse_item,
    parse_title,
    strip_html,
)
from fyndjakt.watchlist import link_comps, refresh_watchlist

log = logging.getLogger(__name__)

PERIODIC = (
    "auctionet_live",
    "auctionet_crawl",
    "health_check",
    "title_batch",
    "watchlist_refresh",
    "image_cleanup",
    "backup",
)
NOTES_PER_RUN = 10
MAX_ATTEMPTS = 3
COMMIT_EVERY = 100  # one Auctionet page
BACKFILL_PAGES_PER_RUN = 10  # ~1 min per run, so assessments aren't stuck behind an 8-minute step
CRAWL_MARK = "auctionet:crawl"  # last_success_at = start of the last complete crawl
CRAWL_OVERLAP = timedelta(hours=2)
# "0 new items for 2 h in daytime" applies to continuous sources only; Auctionet runs nightly.
SILENCE_LIMITS: dict[str, timedelta] = {}


def next_local_time(now: datetime, tz: str, hour: int) -> datetime:
    local = now.astimezone(ZoneInfo(tz))
    target = local.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= local:
        target += timedelta(days=1)
    return target.astimezone(UTC)


def next_local_weekday(now: datetime, tz: str, weekday: int, hour: int) -> datetime:
    """Next occurrence of weekday (Monday=0) at hour, local time."""
    t = next_local_time(now, tz, hour)
    while t.astimezone(ZoneInfo(tz)).weekday() != weekday:
        t = next_local_time(t, tz, hour)
    return t


def ensure_periodic(session: Session, now: datetime, tz: str) -> None:
    first_run = {
        "auctionet_live": now,
        "auctionet_crawl": next_local_time(now, tz, 3),
        "health_check": now,
        "title_batch": next_local_time(now, tz, 4),
        "watchlist_refresh": next_local_weekday(now, tz, 6, 5),
        "image_cleanup": next_local_time(now, tz, 6),
        "backup": next_local_time(now, tz, 2),
    }
    for kind in PERIODIC:
        exists = session.scalar(select(Job.id).where(Job.kind == kind, Job.status.in_(("pending", "running"))))
        if not exists:
            enqueue(session, kind, run_at=first_run[kind])


def claim_next(session: Session, now: datetime) -> Job | None:
    job = session.scalar(
        select(Job).where(Job.status == "pending", Job.run_at <= now).order_by(Job.run_at, Job.id).limit(1)
    )
    if job is None:
        return None
    claimed = session.execute(
        update(Job).where(Job.id == job.id, Job.status == "pending").values(status="running", attempts=Job.attempts + 1)
    ).rowcount
    if not claimed:
        return None
    session.refresh(job)
    return job


# --- handlers ---------------------------------------------------------------------------------------


def handle_assess(session: Session, job: Job, deps: Deps, _ctx: dict) -> None:
    assess_listing(session, int(job.payload["listing_id"]), deps)


def handle_send_alert(session: Session, job: Job, deps: Deps, _ctx: dict) -> None:
    """Retry of a Telegram alert that failed during assessment. Raises on failure, so run_one backs off."""
    send_alert_for(session, deps, int(job.payload["assessment_id"]))


def _utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def handle_auctionet_crawl(session: Session, job: Job, deps: Deps, ctx: dict) -> None:
    now = deps.now()
    try:
        if is_stopped(session, "auctionet", now):
            return
        client: AuctionetClient = ctx["auctionet"]
        known = known_comp_ids(session, "auctionet")
        mark = health_row(session, CRAWL_MARK)
        stop_before = _utc(mark.last_success_at) - CRAWL_OVERLAP if mark.last_success_at else None
        added = 0
        items = client.iter_new(known, stop_before=stop_before, category_id=FURNITURE_CATEGORY)
        for i, item in enumerate(items, 1):
            added += upsert_comp(session, "auctionet", parse_item(item))
            if i % COMMIT_EVERY == 0:
                session.commit()  # short write transactions so ingest and Telegram aren't locked out
        mark.last_success_at = now  # only a complete crawl moves the mark
        record_success(session, "auctionet", now, got_items=added > 0)
        log.info("auctionet: %d new comps", added)
    except SourceBlocked as e:
        record_failure(session, "auctionet", now, f"blocked: {e.reason}", e.reason)
        notify_owner(
            session,
            deps,
            "auctionet",
            f"Källan trasig: auctionet (blockerad: {e.reason}). Stoppad med backoff, inget kringgående.",
        )
    except Exception as e:  # network errors etc.
        row = record_failure(session, "auctionet", now, repr(e), None)
        log.warning("auctionet crawl failed (%d in a row): %r", row.consecutive_failures, e)
    finally:
        enqueue(session, "auctionet_crawl", run_at=next_local_time(now, deps.config.timezone, 3))


TITLE_BATCH_BUDGET_SHARE = 0.5
LIVE_EVERY = timedelta(minutes=30)
LIVE_SOURCE = "auctionet_live"


# Periods and styles outside Scandinavian modern design: not worth an image check.
_OUT_OF_ERA = re.compile(
    r"1[5-8]\d\d-tal|(?:1[5-8]|17|18)00-tal|gustaviansk|rokoko|barock|empire|karl johan|allmoge|louis|biedermeier"
    r"|nyrenässans|jugend|art nouveau|antik",
    re.I,
)


def is_unattributed(title: str) -> bool:
    """No designer in the title and not obviously from another era: the house may not know what it has."""
    return parse_title(title).designer is None and not _OUT_OF_ERA.search(title)


def handle_auctionet_live(session: Session, job: Job, deps: Deps, ctx: dict) -> None:
    """Ongoing Auctionet lots ending soon: keep those that name a watchlist model and assess them.
    Bids change the price, which re-runs only the arithmetic (the AI verdict is reused)."""
    now = deps.now()
    cfg = deps.config
    try:
        if not cfg.auctionet_live_enabled or is_stopped(session, "auctionet", now):
            return
        s = get_settings(session)
        models = list(session.scalars(select(WatchModel).where(WatchModel.active.is_(True))))
        if not models:
            return
        terms = [watch_terms(m.id, m.designer, m.manufacturer, m.model_name, m.aliases) for m in models]
        by_id = {m.id: m for m in models}
        client: AuctionetClient = ctx["auctionet"]
        horizon = now + timedelta(hours=cfg.auctionet_live_horizon_h)
        seen = kept = 0
        for item in client.iter_live(horizon, category_id=FURNITURE_CATEGORY):
            seen += 1
            price, bid = live_price(item, cfg.auctionet_buyer_premium)
            description = strip_html(item.get("description"))
            pf = prefilter(item["title"], description, price, s.max_listing_price_sek, terms)
            hits = [
                mid
                for mid in pf.matched_model_ids
                if strict_title_match(item["title"], by_id[mid].designer, by_id[mid].model_name, by_id[mid].aliases)
            ]
            anonymous = cfg.auctionet_live_anonymous and is_unattributed(item["title"])
            if not (pf.passed and (hits or anonymous)):
                continue
            images = [img.get("w640") or img.get("hd") for img in item.get("images") or []]
            payload = IngestListing(
                source=LIVE_SOURCE,
                external_id=str(item["id"]),
                title=item["title"][:512],
                url=item.get("url"),
                price_sek=price,
                description=description,
                municipality=item.get("location"),
                published_at=datetime.fromtimestamp(item["published_at"], UTC) if item.get("published_at") else None,
                image_urls=[u for u in images if u][:20],
            )
            listing, _new, _changed = upsert_listing(session, payload)
            listing.ends_at = datetime.fromtimestamp(item["ends_at"], UTC) if item.get("ends_at") else None
            listing.current_bid_sek = bid
            kept += 1
            if seen % COMMIT_EVERY == 0:
                session.commit()
        record_success(session, "auctionet", now, got_items=seen > 0)
        log.info(
            "auctionet live: %d lots ending within %.0f h, %d match the watchlist",
            seen,
            cfg.auctionet_live_horizon_h,
            kept,
        )
    except SourceBlocked as e:
        record_failure(session, "auctionet", now, f"blocked: {e.reason}", e.reason)
        notify_owner(
            session,
            deps,
            "auctionet",
            f"Källan trasig: auctionet (blockerad: {e.reason}). Stoppad med backoff, inget kringgående.",
        )
    except Exception as e:  # network errors etc.
        row = record_failure(session, "auctionet", now, repr(e), None)
        log.warning("auctionet live failed (%d in a row): %r", row.consecutive_failures, e)
    finally:
        enqueue(session, "auctionet_live", run_at=now + LIVE_EVERY)


def handle_screen_capture(session: Session, job: Job, deps: Deps, _ctx: dict) -> None:
    """Read one screenshot from the browser extension into listings; the screenshot is deleted afterwards."""
    path = Path(job.payload["path"])
    if path.exists() and deps.ai is not None and _budget_left(session, deps) <= 0:
        # Keep the screenshot and read it when the new day's budget opens.
        enqueue(
            session, "screen_capture", job.payload, run_at=budget.next_local_midnight(deps.now(), deps.config.timezone)
        )
        return
    try:
        _read_capture(session, deps, path, job.payload)
    except Exception:
        if job.attempts >= MAX_ATTEMPTS:
            path.unlink(missing_ok=True)
        raise
    path.unlink(missing_ok=True)  # may show people's names: never kept after reading


def _read_capture(session: Session, deps: Deps, path: Path, payload: dict) -> None:
    source = capture.source_for(payload.get("page_url", ""))
    if not path.exists() or deps.ai is None or deps.images is None or source is None:
        return
    raw = path.read_bytes()
    read = deps.capture_fn or capture.read_screenshot
    page, u = read(deps.ai, deps.config.model_fast, image_block(resize_jpeg(raw, 1568)))
    session.add(
        AICall(
            purpose="capture",
            model=u.model,
            tokens_in=u.tokens_in,
            tokens_out=u.tokens_out,
            cache_read_tokens=u.cache_read,
            cache_write_tokens=u.cache_write,
            cost_usd=budget.cost_usd(
                deps.config.model_prices, u.model, u.tokens_in, u.tokens_out, u.cache_read, u.cache_write
            ),
        )
    )
    links = [capture.LinkBox(**lk) for lk in payload.get("links") or []]
    for card in page.cards:
        if not card.is_furniture or not card.title.strip():
            continue
        photo = capture.crop(raw, card.image_box)
        if photo is None:
            continue
        href = capture.link_for(card.image_box, links)
        ext = (capture.item_id(href) if href else None) or capture.fallback_id(card.title, card.price_sek, card.place)
        upsert_listing(
            session,
            IngestListing(
                source=source,
                external_id=ext,
                title=card.title[:512],
                price_sek=card.price_sek if card.price_sek is None or card.price_sek >= 0 else None,
                municipality=card.place,
                url=href,
                image_urls=[deps.images.save_upload(photo)],
            ),
        )


def handle_health_check(session: Session, job: Job, deps: Deps, _ctx: dict) -> None:
    now = deps.now()
    hour = now.astimezone(ZoneInfo(deps.config.timezone)).hour
    rows = [r for r in session.scalars(select(SourceHealth)) if ":" not in r.source]
    for row, reason in health_problems(rows, now, hour, SILENCE_LIMITS):
        notify_owner(session, deps, row.source, f"Källan trasig: {row.source} ({reason})")
    enqueue(session, "health_check", run_at=now + timedelta(minutes=15))


def _log_usage(session: Session, deps: Deps, purpose: str, model: str, usage: object, factor: float = 1.0) -> None:
    u_in = getattr(usage, "input_tokens", 0) or 0
    u_out = getattr(usage, "output_tokens", 0) or 0
    c_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    c_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cost = budget.cost_usd(deps.config.model_prices, model, u_in, u_out, c_read, c_write) * factor
    session.add(
        AICall(
            purpose=purpose,
            model=model,
            tokens_in=u_in,
            tokens_out=u_out,
            cache_read_tokens=c_read,
            cache_write_tokens=c_write,
            cost_usd=cost,
        )
    )


def _budget_left(session: Session, deps: Deps) -> float:
    s = get_settings(session)
    return budget.budget_left(session, deps.now(), deps.config.timezone, s.daily_ai_budget_usd)


def handle_title_batch(session: Session, job: Job, deps: Deps, _ctx: dict) -> None:
    """Collect finished comp-title batches, then submit a new one within the remaining daily budget."""
    now = deps.now()
    still_open = 0
    try:
        if deps.ai is None:
            return
        still_open = enrich.collect_batches(
            session, deps.ai, now, on_usage=lambda model, u: _log_usage(session, deps, "comp_titles", model, u, 0.5)
        )
        if still_open == 0:
            # At most half of what's left: the day's listing assessments need the rest.
            limit = int(_budget_left(session, deps) * TITLE_BATCH_BUDGET_SHARE / enrich.EST_USD_PER_TITLE)
            if limit >= 50:
                row = enrich.submit_title_batch(session, deps.ai, deps.config.model_text, limit=min(limit, 5000))
                still_open = 1 if row else 0
    finally:
        # Poll every 30 min while a batch is open, otherwise once a night.
        run_at = now + timedelta(minutes=30) if still_open else next_local_time(now, deps.config.timezone, 4)
        enqueue(session, "title_batch", run_at=run_at)


def handle_watchlist_refresh(session: Session, job: Job, deps: Deps, _ctx: dict) -> None:
    now = deps.now()
    try:
        created, updated = refresh_watchlist(session)
        linked = link_comps(session)
        log.info("watchlist: %d new, %d updated, %d comps linked", created, updated, linked)
        if deps.ai is None:
            return
        for m in enrich.models_needing_notes(session, NOTES_PER_RUN):
            if _budget_left(session, deps) <= 0:
                break
            notes, usage = enrich.write_model_notes(deps.ai, deps.config.model_strong, m)
            _log_usage(session, deps, "model_notes", deps.config.model_strong, usage)
            enrich.apply_notes(m, notes, now)
            session.flush()
    finally:
        enqueue(session, "watchlist_refresh", run_at=next_local_weekday(now, deps.config.timezone, 6, 5))


def handle_image_cleanup(session: Session, job: Job, deps: Deps, _ctx: dict) -> None:
    now = deps.now()
    try:
        removed = purge_old(deps.config.image_cache_dir, now.timestamp())
        # Unread screenshots never linger beyond a day (they can show people's names).
        removed += purge_old(deps.config.capture_dir, now.timestamp(), retention_s=24 * 3600)
        log.info("image cleanup: %d files removed", removed)
    finally:
        enqueue(session, "image_cleanup", run_at=next_local_time(now, deps.config.timezone, 6))


def handle_backup(session: Session, job: Job, deps: Deps, _ctx: dict) -> None:
    now = deps.now()
    try:
        url = deps.config.database_url
        if url.startswith("sqlite:///") and ":memory:" not in url:
            target = backup_sqlite(url.removeprefix("sqlite:///"), deps.config.backup_dir, now)
            log.info("backup written: %s", target)
    finally:
        enqueue(session, "backup", run_at=next_local_time(now, deps.config.timezone, 2))


def handle_auctionet_backfill(session: Session, job: Job, deps: Deps, ctx: dict) -> None:
    """Up to BACKFILL_PAGES_PER_RUN pages of one plan step per run, then re-enqueues itself with the rest."""
    now = deps.now()
    todo: list[dict] = list(job.payload.get("todo") or [])
    if not todo:
        return
    if is_stopped(session, "auctionet", now):
        enqueue(session, "auctionet_backfill", {"todo": todo}, run_at=now + timedelta(hours=1))
        return
    step, rest = todo[0], todo[1:]
    params = {k: v for k, v in step.items() if k != "page"}
    start = int(step.get("page", 1))
    client: AuctionetClient = ctx["auctionet"]
    added = 0
    try:
        done, reached = False, start
        for page_no, items, last in client.pages(start, BACKFILL_PAGES_PER_RUN, **params):
            for item in items:
                added += upsert_comp(session, "auctionet", parse_item(item))
            session.commit()  # one page per write transaction
            done, reached = last, page_no
        if done:
            record_success(session, "auctionet", now, got_items=added > 0)
            log.info("auctionet backfill %s done; %d steps left", params, len(rest))
        else:
            rest = [{**params, "page": reached + 1}, *rest]
            log.info("auctionet backfill %s: up to page %d, %d new comps", params, reached, added)
    except SourceBlocked as e:
        record_failure(session, "auctionet", now, f"blocked: {e.reason}", e.reason)
        notify_owner(
            session,
            deps,
            "auctionet",
            f"Källan trasig: auctionet (blockerad: {e.reason}). Stoppad med backoff, inget kringgående.",
        )
        rest = todo  # retry the same step after the backoff (pages already saved are simply upserted again)
    if rest:
        enqueue(session, "auctionet_backfill", {"todo": rest}, run_at=now + timedelta(seconds=10))


def backfill_plan(designers: list[str] | None = None) -> list[dict]:
    plan = [{"category_id": cid} for cid in FURNITURE_SUBCATEGORIES]
    plan += [{"category_id": FURNITURE_CATEGORY, "q": d} for d in designers or []]
    return plan


HANDLERS: dict[str, Callable[[Session, Job, Deps, dict], None]] = {
    "assess": handle_assess,
    "send_alert": handle_send_alert,
    "auctionet_crawl": handle_auctionet_crawl,
    "auctionet_live": handle_auctionet_live,
    "screen_capture": handle_screen_capture,
    "auctionet_backfill": handle_auctionet_backfill,
    "health_check": handle_health_check,
    "title_batch": handle_title_batch,
    "watchlist_refresh": handle_watchlist_refresh,
    "image_cleanup": handle_image_cleanup,
    "backup": handle_backup,
}


def run_one(deps: Deps, ctx: dict) -> bool:
    """Claim and run one due job. Returns False when nothing was due."""
    now = deps.now()
    with session_scope() as session:
        job = claim_next(session, now)
        if job is None:
            return False
        job_id, kind, attempts = job.id, job.kind, job.attempts
    try:
        with session_scope() as session:
            job = session.get(Job, job_id)
            HANDLERS[kind](session, job, deps, ctx)
            job.status = "done"
    except Exception as e:
        log.exception("job %s (%s) failed", job_id, kind)
        with session_scope() as session:
            job = session.get(Job, job_id)
            job.last_error = repr(e)[:2000]
            if attempts >= MAX_ATTEMPTS:
                job.status = "failed"
            else:
                job.status = "pending"
                job.run_at = now + timedelta(minutes=2**attempts)
    return True


class Worker:
    def __init__(self, deps: Deps, ctx: dict, poll_s: float = 2.0):
        self.deps, self.ctx, self.poll_s = deps, ctx, poll_s
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="fyndjakt-worker", daemon=True)

    def start(self) -> None:
        with session_scope() as session:
            # Jobs left 'running' by a crash are retried.
            session.execute(update(Job).where(Job.status == "running").values(status="pending"))
            ensure_periodic(session, self.deps.now(), self.deps.config.timezone)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=10)

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                if not run_one(self.deps, self.ctx):
                    self._stop.wait(self.poll_s)
            except Exception:
                log.exception("worker loop error")
                self._stop.wait(self.poll_s)
