"""Step 10: cost accounting and the daily AI budget guard."""

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from fyndjakt.models import AICall

CACHE_READ_FACTOR = 0.1
CACHE_WRITE_FACTOR = 1.25


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
    start = local_day_start_utc(now, tz)
    total = session.scalar(select(func.coalesce(func.sum(AICall.cost_usd), 0.0)).where(AICall.created_at >= start))
    return float(total or 0.0)


def budget_left(session: Session, now: datetime, tz: str, daily_budget_usd: float) -> float:
    return daily_budget_usd - spent_today(session, now, tz)


def next_local_midnight(now: datetime, tz: str) -> datetime:
    return local_day_start_utc(now, tz) + timedelta(days=1)
