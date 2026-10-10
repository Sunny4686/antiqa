"""Step 5: value a listing from comparable sales.

Comp prices are normalised to "utmärkt" condition, summarised, then scaled to the listing's guessed condition.
n >= 5: model-level quantiles. n = 1-4: log-price shrinkage towards the designer x category prior when one
exists. n = 0: no value.
"""

import math
from dataclasses import dataclass

CONDITION_MULTIPLIERS = {"utmärkt": 1.0, "gott": 0.85, "slitet": 0.7, "renoveringsobjekt": 0.55}
DEFAULT_COMP_CONDITION = "gott"


@dataclass(frozen=True)
class CompPrice:
    hammer_sek: int
    condition: str | None = None


@dataclass(frozen=True)
class Valuation:
    p25: int | None
    median: int | None
    p75: int | None
    n: int
    level: str  # model | designer_category | none


def quantile(values: list[float], q: float) -> float:
    """Linear-interpolated quantile of a non-empty list."""
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    pos = (len(s) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def _normalised(comps: list[CompPrice], multipliers: dict[str, float]) -> list[float]:
    out = []
    for c in comps:
        if c.hammer_sek and c.hammer_sek > 0:
            mult = multipliers.get(c.condition or DEFAULT_COMP_CONDITION, multipliers[DEFAULT_COMP_CONDITION])
            out.append(c.hammer_sek / mult)
    return out


def value(
    model_comps: list[CompPrice],
    prior_comps: list[CompPrice],
    listing_condition: str | None,
    multipliers: dict[str, float] = CONDITION_MULTIPLIERS,
    min_n: int = 5,
    shrink_k: float = 3.0,
) -> Valuation:
    model_vals = _normalised(model_comps, multipliers)
    n = len(model_vals)
    if n == 0:
        return Valuation(None, None, None, 0, "none")

    qs = (0.25, 0.5, 0.75)
    est = [quantile(model_vals, q) for q in qs]
    level = "model"
    prior_vals = _normalised(prior_comps, multipliers)
    if n < min_n and prior_vals:
        level = "designer_category"
        prior = [quantile(prior_vals, q) for q in qs]
        est = [
            math.exp((n * math.log(m) + shrink_k * math.log(p)) / (n + shrink_k))
            for m, p in zip(est, prior, strict=True)
        ]

    scale = multipliers.get(listing_condition or DEFAULT_COMP_CONDITION, multipliers[DEFAULT_COMP_CONDITION])
    p25, med, p75 = (round(v * scale) for v in est)
    return Valuation(p25, med, p75, n, level)
