"""Numbers for /statistik. Pure functions over plain rows; the DB query lives in the web layer."""

import statistics
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

POSITIVE_FEEDBACK = {"köpt", "bra_men_såld"}
NEGATIVE_FEEDBACK = {"ej_intressant", "fel_modell", "replika"}


@dataclass(frozen=True)
class AlertRow:
    listing_id: int
    decision: str
    created_at: datetime
    published_at: datetime | None
    first_seen_at: datetime


@dataclass(frozen=True)
class DealRow:
    sold_at: datetime | None
    sale_sek: int | None
    purchase_sek: int
    costs_sek: int
    fees_sek: int


def week_key(dt: datetime) -> str:
    y, w, _ = dt.isocalendar()
    return f"{y}-v{w:02d}"


def alerts_per_week(alerts: list[AlertRow]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = defaultdict(lambda: {"FYND": 0, "KOLLA_SJALV": 0})
    for a in alerts:
        if a.decision in ("FYND", "KOLLA_SJALV"):
            out[week_key(a.created_at)][a.decision] += 1
    return dict(sorted(out.items()))


def precision(alerts: list[AlertRow], feedback: dict[int, str], decision: str = "FYND") -> tuple[float | None, int]:
    """Share of rated alerts that were good. Returns (precision, number rated)."""
    rated = [feedback[a.listing_id] for a in alerts if a.decision == decision and a.listing_id in feedback]
    rated = [r for r in rated if r in POSITIVE_FEEDBACK | NEGATIVE_FEEDBACK]
    if not rated:
        return None, 0
    return sum(r in POSITIVE_FEEDBACK for r in rated) / len(rated), len(rated)


def latency_minutes(alerts: list[AlertRow]) -> float | None:
    """Median minutes from publication (or first seen) to the final assessment, for alerts."""
    vals = []
    for a in alerts:
        if a.decision not in ("FYND", "KOLLA_SJALV"):
            continue
        start = a.published_at or a.first_seen_at
        vals.append((a.created_at - start) / timedelta(minutes=1))
    return round(statistics.median(vals), 1) if vals else None


def profit_per_month(deals: list[DealRow]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for d in deals:
        if d.sold_at and d.sale_sek is not None:
            out[d.sold_at.strftime("%Y-%m")] += d.sale_sek - d.purchase_sek - d.costs_sek - d.fees_sek
    return dict(sorted(out.items()))


def deal_net(sale_sek: int | None, purchase_sek: int, costs_sek: int, fees_sek: int) -> int | None:
    return None if sale_sek is None else sale_sek - purchase_sek - costs_sek - fees_sek
