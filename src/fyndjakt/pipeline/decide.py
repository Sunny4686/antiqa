"""Steps 8-9: escalation, confidence and the alert decision."""

from dataclasses import dataclass

CONFIDENCE_ORDER = {"låg": 0, "medel": 1, "hög": 2}
FYND, KOLLA_SJALV, INGET = "FYND", "KOLLA_SJALV", "INGET"


def should_escalate(match: str | None, net_sek: int | None, min_net_margin_sek: int) -> bool:
    return match in ("yes", "uncertain") and net_sek is not None and net_sek >= 2 * min_net_margin_sek


def combine_confidence(
    model_confidence: str, match: str | None, value_level: str, replica_flag: bool, strong_disagrees: bool = False
) -> str:
    """Cap the model's own confidence with what the code knows."""
    level = CONFIDENCE_ORDER.get(model_confidence, 0)
    if match == "uncertain":
        level = min(level, 1)
    if value_level == "designer_category":
        level = min(level, 1)
    if match not in ("yes", "uncertain") or value_level == "none" or replica_flag or strong_disagrees:
        level = 0
    return next(k for k, v in CONFIDENCE_ORDER.items() if v == level)


def in_quiet_hours(hour: int, start: int, end: int) -> bool:
    if start == end:
        return False
    return start <= hour or hour < end if start > end else start <= hour < end


@dataclass(frozen=True)
class DecisionInput:
    net_sek: int | None
    roi: float | None
    distance_km: float | None
    region: str | None
    confidence: str
    value_level: str
    watched_candidate: bool
    upside_net_sek: int | None  # net computed from P75, or None when there is no value


@dataclass(frozen=True)
class Thresholds:
    min_net_margin_sek: int
    min_roi: float
    max_distance_km: float
    allowed_regions: tuple[str, ...] = ()


def decide(d: DecisionInput, t: Thresholds) -> str:
    near = (d.distance_km is not None and d.distance_km <= t.max_distance_km) or (
        d.region is not None and d.region in t.allowed_regions
    )
    if (
        d.net_sek is not None
        and d.net_sek >= t.min_net_margin_sek
        and d.roi is not None
        and d.roi >= t.min_roi
        and near
        and CONFIDENCE_ORDER[d.confidence] >= CONFIDENCE_ORDER["medel"]
    ):
        return FYND
    big_upside = d.upside_net_sek is None or d.upside_net_sek >= 2 * t.min_net_margin_sek
    if d.watched_candidate and (d.confidence == "låg" or d.value_level == "none") and big_upside:
        return KOLLA_SJALV
    return INGET
