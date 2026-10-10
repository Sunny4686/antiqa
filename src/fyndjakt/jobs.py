"""SQLite job queue and a single worker thread (runs inside the web process)."""

import logging
import threading
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from fyndjakt.ai import budget, enrich
from fyndjakt.assess import Deps, assess_listing, notify_owner
from fyndjakt.backup import backup_sqlite
from fyndjakt.db import session_scope
from fyndjakt.images import purge_old
from fyndjakt.models import AICall, Job, SourceHealth
from fyndjakt.services import (
    enqueue,
    get_settings,
    health_problems,
    is_stopped,
    known_comp_ids,
    record_failure,
    record_success,
    upsert_comp,
)
from fyndjakt.sources.auctionet import (
    FURNITURE_CATEGORY,
    FURNITURE_SUBCATEGORIES,
    AuctionetClient,
    SourceBlocked,
    parse_item,
)
from fyndjakt.watchlist import link_comps, refresh_watchlist

log = logging.getLogger(__name__)

PERIODIC = ("auctionet_crawl", "health_check", "title_batch", "watchlist_refresh", "image_cleanup", "backup")
NOTES_PER_RUN = 10
MAX_ATTEMPTS = 3
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


def handle_auctionet_crawl(session: Session, job: Job, deps: Deps, ctx: dict) -> None:
    now = deps.now()
    try:
        if is_stopped(session, "auctionet", now):
            return
        client: AuctionetClient = ctx["auctionet"]
        known = known_comp_ids(session, "auctionet")
        added = 0
        for item in client.iter_new(known, category_id=FURNITURE_CATEGORY):
            added += upsert_comp(session, "auctionet", parse_item(item))
            if added % 100 == 0:
                session.flush()
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
            limit = int(_budget_left(session, deps) / enrich.EST_USD_PER_TITLE)
            if limit >= 50:
                row = enrich.submit_title_batch(session, deps.ai, deps.config.model_fast, limit=min(limit, 5000))
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
    """One subcategory or designer query per run (<= 10 000 items), then re-enqueues itself with the rest."""
    now = deps.now()
    todo: list[dict] = list(job.payload.get("todo") or [])
    if not todo:
        return
    if is_stopped(session, "auctionet", now):
        enqueue(session, "auctionet_backfill", {"todo": todo}, run_at=now + timedelta(hours=1))
        return
    params, rest = todo[0], todo[1:]
    client: AuctionetClient = ctx["auctionet"]
    added = 0
    try:
        for item in client.iter_all(**params):
            added += upsert_comp(session, "auctionet", parse_item(item))
            if added and added % 200 == 0:
                session.flush()
        record_success(session, "auctionet", now, got_items=added > 0)
        log.info("auctionet backfill %s: %d new comps, %d steps left", params, added, len(rest))
    except SourceBlocked as e:
        record_failure(session, "auctionet", now, f"blocked: {e.reason}", e.reason)
        notify_owner(
            session,
            deps,
            "auctionet",
            f"Källan trasig: auctionet (blockerad: {e.reason}). Stoppad med backoff, inget kringgående.",
        )
        rest = todo  # retry the same step after the backoff
    if rest:
        enqueue(session, "auctionet_backfill", {"todo": rest}, run_at=now + timedelta(seconds=10))


def backfill_plan(designers: list[str] | None = None) -> list[dict]:
    plan = [{"category_id": cid} for cid in FURNITURE_SUBCATEGORIES]
    plan += [{"category_id": FURNITURE_CATEGORY, "q": d} for d in designers or []]
    return plan


HANDLERS: dict[str, Callable[[Session, Job, Deps, dict], None]] = {
    "assess": handle_assess,
    "auctionet_crawl": handle_auctionet_crawl,
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
