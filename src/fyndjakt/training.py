"""Training rounds on the comp archive: merge synonym model names, then write a photo-grounded visual profile per
watchlist model. Every call is logged as an AICall, and a round stops at its USD cap."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

import anthropic
from sqlalchemy import select

from fyndjakt.ai import budget, enrich
from fyndjakt.ai.catalog import model_photos, siblings
from fyndjakt.config import Config
from fyndjakt.db import session_scope
from fyndjakt.images import ImageLoader
from fyndjakt.models import AICall, WatchModel
from fyndjakt.watchlist import merge_models

log = logging.getLogger(__name__)


@dataclass
class Report:
    merged: list[str] = field(default_factory=list)
    profiles: int = 0
    spent_usd: float = 0.0
    stopped_at_cap: bool = False


def _log(session, cfg: Config, purpose: str, model: str, usage: object) -> float:  # noqa: ANN001
    u_in = getattr(usage, "input_tokens", 0) or 0
    u_out = getattr(usage, "output_tokens", 0) or 0
    c_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    c_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cost = budget.cost_usd(cfg.model_prices, model, u_in, u_out, c_read, c_write)
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
    return cost


def run(cfg: Config, client: anthropic.Anthropic, loader: ImageLoader, max_usd: float, now: datetime) -> Report:
    rep = Report()
    model = cfg.model_strong

    # 1. Synonyms per designer ("Herrgården" = "Herrgård", "Sjuan" = "7'er" = "Syveren")
    with session_scope() as session:
        by_designer: dict[str, list[WatchModel]] = defaultdict(list)
        for m in session.scalars(select(WatchModel).where(WatchModel.active.is_(True))):
            if m.designer and m.model_name:
                by_designer[m.designer].append(m)
        work = [(d, [(m.id, m.model_name) for m in ms]) for d, ms in by_designer.items() if len(ms) >= 2]
    for designer, pairs in work:
        if rep.spent_usd >= max_usd:
            rep.stopped_at_cap = True
            return rep
        groups, usage = enrich.group_synonyms(client, model, designer, [n for _, n in pairs])
        with session_scope() as session:
            rep.spent_usd += _log(session, cfg, "train_synonyms", model, usage)
            for g in groups:
                ids = [i for i, n in pairs if n in g]
                keeper = merge_models(session, ids)
                if keeper:
                    rep.merged.append(f"{designer}: {' = '.join(g)} -> {keeper.model_name}")

    # 2. Visual profile per model, most valuable first
    with session_scope() as session:
        todo = list(
            session.scalars(
                select(WatchModel.id)
                .where(WatchModel.active.is_(True), WatchModel.notes_generated_at.is_(None))
                .order_by(WatchModel.median_sek.desc())
            )
        )
    for mid in todo:
        if rep.spent_usd >= max_usd:
            rep.stopped_at_cap = True
            break
        with session_scope() as session:
            m = session.get(WatchModel, mid)
            photos = model_photos(session, loader, m.id, n=5)
            others = list(session.scalars(select(WatchModel).where(WatchModel.active.is_(True))))
            notes, usage = enrich.write_model_notes(client, model, m, photos=photos, siblings=siblings(others, m))
            rep.spent_usd += _log(session, cfg, "train_profile", model, usage)
            enrich.apply_notes(m, notes, now)
            rep.profiles += 1
            log.info(
                "profile %s – %s (%d photos), %.3f USD so far", m.designer, m.model_name, len(photos), rep.spent_usd
            )
    return rep
