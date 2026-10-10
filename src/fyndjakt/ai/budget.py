"""Step 10: cost accounting and the daily AI budget guard."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fyndjakt.models import AIBatch, AICall

CACHE_READ_FACTOR = 0.1
CACHE_WRITE_FACTOR = 1.25
# Estimated cost per request of an open (not yet collected) batch, already at the batch discount.
# Open batches count against today's budget until their real cost is logged at collection.
BATCH_EST_USD_PER_REQUEST = 0.0004


def cost_usd(
    prices: dict[str, tuple[float, float]],
    model: str,
    tokens_in: int,
    tokens_out: int,
    cache_read: int = 0,
    cache_write: int = 0,
) -> float:
    p_in, p_out = prices[model]
    return (
        tokens_in * p_in
        + cache_read * p_in * CACHE_READ_FACTOR
        + cache_write * p_in * CACHE_WRITE_FACTOR
        + tokens_out * p_out
    ) / 1_000_000


def local_day_start_utc(now: datetime, tz: str) -> datetime:
    local = now.astimezone(ZoneInfo(tz))
    return local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(UTC)


def spent_today(session: Session, now: datetime, tz: str) -> float:
    """Logged cost since local midnight plus the reservation for batches that are still open."""
    start = local_day_start_utc(now, tz)
    total = session.scalar(select(func.coalesce(func.sum(AICall.cost_usd), 0.0)).where(AICall.created_at >= start))
    reserved = session.scalar(
        select(func.coalesce(func.sum(AIBatch.n_requests), 0)).where(AIBatch.status == "submitted")
    )
    return float(total or 0.0) + float(reserved or 0) * BATCH_EST_USD_PER_REQUEST


def budget_left(session: Session, now: datetime, tz: str, daily_budget_usd: float) -> float:
    return daily_budget_usd - spent_today(session, now, tz)


def next_local_midnight(now: datetime, tz: str) -> datetime:
    """Calendar arithmetic in local time: a local day is 23 or 25 hours at DST changes."""
    zone = ZoneInfo(tz)
    tomorrow = now.astimezone(zone).date() + timedelta(days=1)
    return datetime(tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=zone).astimezone(UTC)
