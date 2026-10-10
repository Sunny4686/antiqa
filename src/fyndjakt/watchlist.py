"""Automatic watchlist: group comps by (designer, model), propose models and link comps to them."""

import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from fyndjakt.models import Comp, WatchModel
from fyndjakt.pipeline.prefilter import contains_term, normalize


@dataclass(frozen=True)
class CompRow:
    id: int
    designer: str | None
    manufacturer: str | None
    model_name: str | None
    category: str | None
    hammer_sek: int | None


@dataclass(frozen=True)
class Proposal:
    designer: str
    model_name: str
    manufacturer: str | None
    category: str | None
    n_sales: int
    median_sek: int
    comp_ids: tuple[int, ...]


def group_key(designer: str | None, model_name: str | None) -> tuple[str, str] | None:
    if not designer or not model_name:
        return None
    return normalize(designer), normalize(model_name).strip("\"' ")


def propose_models(rows: list[CompRow], min_sales: int = 3, min_median_sek: int = 3000) -> list[Proposal]:
    """Groups with >= min_sales sales and median hammer >= min_median_sek become watchlist proposals."""
    groups: dict[tuple[str, str], list[CompRow]] = defaultdict(list)
    for r in rows:
        key = group_key(r.designer, r.model_name)
        if key and r.hammer_sek:
            groups[key].append(r)
    out = []
    for members in groups.values():
        if len(members) < min_sales:
            continue
        median = round(statistics.median(m.hammer_sek for m in members))
        if median < min_median_sek:
            continue

        def most_common(values: list[str | None]) -> str | None:
            vals = [v for v in values if v]
            return Counter(vals).most_common(1)[0][0] if vals else None

        out.append(
            Proposal(
                designer=most_common([m.designer for m in members]) or "",
                model_name=most_common([m.model_name for m in members]) or "",
                manufacturer=most_common([m.manufacturer for m in members]),
                category=most_common([m.category for m in members]),
                n_sales=len(members),
                median_sek=median,
                comp_ids=tuple(sorted(m.id for m in members)),
            )
        )
    out.sort(key=lambda p: (-p.median_sek * p.n_sales, p.designer, p.model_name))
    return out


def refresh_watchlist(session: Session, min_sales: int = 3, min_median_sek: int = 3000) -> tuple[int, int]:
    """Insert new auto models and refresh stats on existing ones. Owner-edited rows keep their text fields.

    Returns (created, updated).
    """
    rows = [
        CompRow(c.id, c.designer, c.manufacturer, c.model_name, c.category, c.hammer_sek)
        for c in session.scalars(
            select(Comp).where(
                Comp.state == "sold",
                Comp.hammer_sek.is_not(None),
                Comp.designer.is_not(None),
                Comp.model_name.is_not(None),
            )
        )
    ]
    existing = {group_key(m.designer, m.model_name): m for m in session.scalars(select(WatchModel))}
    created = updated = 0
    for p in propose_models(rows, min_sales, min_median_sek):
        key = group_key(p.designer, p.model_name)
        m = existing.get(key)
        if m is None:
            m = WatchModel(
                designer=p.designer,
                model_name=p.model_name,
                manufacturer=p.manufacturer,
                category=p.category,
                aliases=[],
                active=True,
                auto_generated=True,
            )
            session.add(m)
            session.flush()
            existing[key] = m
            created += 1
        else:
            updated += 1
        m.n_sales, m.median_sek = p.n_sales, p.median_sek
        for cid in p.comp_ids:
            session.get(Comp, cid).model_id = m.id
    return created, updated


def link_comps(session: Session) -> int:
    """Attach unlinked comps to watchlist models by designer + model name/alias in the title."""
    models = [m for m in session.scalars(select(WatchModel).where(WatchModel.active.is_(True))) if m.designer]
    linked = 0
    for c in session.scalars(select(Comp).where(Comp.model_id.is_(None), Comp.designer.is_not(None))):
        d, title = normalize(c.designer), normalize(c.title)
        for m in models:
            names = [normalize(n) for n in (m.model_name, *(m.aliases or [])) if n and len(n) >= 3]
            if normalize(m.designer) in d and any(contains_term(title, n) for n in names):
                c.model_id = m.id
                linked += 1
                break
    return linked
