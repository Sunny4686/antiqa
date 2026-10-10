"""Step 3: pick at most N candidate models from the watchlist using prefilter matches and the screening guess."""

from dataclasses import dataclass

from fyndjakt.pipeline.prefilter import contains_term, normalize


@dataclass(frozen=True)
class ModelRef:
    id: int
    designer: str | None
    manufacturer: str | None
    model_name: str | None
    aliases: tuple[str, ...] = ()


def _hit(guess: str | None, *values: str | None) -> bool:
    if not guess:
        return False
    g = normalize(guess)
    for v in values:
        if v and len(v) >= 3:
            n = normalize(v)
            if contains_term(g, n) or contains_term(n, g):
                return True
    return False


def select_candidates(
    models: list[ModelRef],
    text_matched_ids: list[int],
    guess_designer: str | None,
    guess_manufacturer: str | None,
    guess_model: str | None,
    limit: int = 8,
    visual_ids: list[int] | None = None,
) -> list[ModelRef]:
    """visual_ids: catalog ids the screening picked from the picture, most likely first."""
    visual = {mid: rank for rank, mid in enumerate(visual_ids or [])}
    scored: list[tuple[int, int, ModelRef]] = []
    for m in models:
        score = 6 - visual[m.id] if m.id in visual else 0
        if m.id in text_matched_ids:
            score += 3
        if _hit(guess_model, m.model_name, *m.aliases):
            score += 4
        if _hit(guess_designer, m.designer):
            score += 2
        if _hit(guess_manufacturer, m.manufacturer):
            score += 1
        if score:
            scored.append((score, -m.id, m))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [m for _, _, m in scored[:limit]]
