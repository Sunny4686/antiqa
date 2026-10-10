"""SQLite job queue and a single worker thread (runs inside the web process)."""

import logging
import threading
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from fyndjakt.assess import Deps, assess_listing, notify_owner
from fyndjakt.db import session_scope
from fyndjakt.models import Job, SourceHealth
from fyndjakt.services import (
    enqueue,
    health_problems,
    is_stopped,
    known_comp_ids,
    record_failure,
    record_success,
    upsert_comp,
)
from fyndjakt.sources.auctionet import FURNITURE_CATEGORY, AuctionetClient, SourceBlocked, parse_item

log = logging.getLogger(__name__)

PERIODIC = ("auctionet_crawl", "health_check")
MAX_ATTEMPTS = 3
# "0 new items for 2 h in daytime" applies to continuous sources only; Auctionet runs nightly.
SILENCE_LIMITS: dict[str, timedelta] = {}


def next_local_time(now: datetime, tz: str, hour: int) -> datetime:
    local = now.astimezone(ZoneInfo(tz))
    target = local.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= local:
        target += timedelta(days=1)
    return target.astimezone(UTC)


def ensure_periodic(session: Session, now: datetime, tz: str) -> None:
    first_run = {"auctionet_crawl": next_local_time(now, tz, 3), "health_check": now}
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


HANDLERS: dict[str, Callable[[Session, Job, Deps, dict], None]] = {
    "assess": handle_assess,
    "auctionet_crawl": handle_auctionet_crawl,
    "health_check": handle_health_check,
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
