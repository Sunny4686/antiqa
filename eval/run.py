"""Evaluate screening + verification against a labelled set built from the database.

    uv run python -m eval.run --limit 40          # 20 positives + 20 negatives
    uv run python -m eval.run --dry-run           # show the set and the estimated cost, no API calls

Positives: sold Auctionet comps linked to an active watchlist model. Titles are masked to the furniture type so the
model has to recognise the piece from the photo, as with a private seller who doesn't know what they have.
Negatives: cheap comps without a designer (ordinary furniture) plus listings the owner marked
ej_intressant / fel_modell / replika. Random Blocket listings join the negatives once those are collected.
"""

import argparse
import json
import random
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import anthropic
from sqlalchemy import func, select

from fyndjakt.ai import budget
from fyndjakt.ai.steps import CandidateSpec, screen, verify
from fyndjakt.assess import model_label
from fyndjakt.config import get_config
from fyndjakt.db import session_scope
from fyndjakt.images import ImageLoader
from fyndjakt.migrate import upgrade
from fyndjakt.models import Comp, Feedback, Listing, WatchModel
from fyndjakt.pipeline.candidates import ModelRef, select_candidates
from fyndjakt.pipeline.prefilter import prefilter, watch_terms

CATEGORY_TITLES = {
    "stolar_fatoljer": "Fåtölj",
    "byråer": "Byrå",
    "soffbord": "Soffbord",
    "skåp_hyllor": "Skåp",
    "skrivbord": "Skrivbord",
    "matsalsmöbler": "Matsalsmöbel",
    "matbord": "Matbord",
    "övrigt": "Möbel",
    "soffor": "Soffa",
    "bord": "Bord",
}
EST_USD_PER_ITEM = 0.008  # screen + verify with images on MODEL_FAST
RESULTS = Path(__file__).parent / "results"


@dataclass
class Case:
    kind: str  # positive | negative
    source: str  # comp | feedback:<label>
    ref_id: int
    title: str
    description: str | None
    price_sek: int | None
    image_urls: list[str]
    true_model_id: int | None


@dataclass
class Outcome:
    case: Case
    predicted_model_id: int | None
    match: str | None
    screened_collectible: bool
    cost_usd: float
    latency_s: float
    error: str | None = None


def build_cases(session, n_pos: int, n_neg: int, seed: int) -> list[Case]:
    rng = random.Random(seed)
    active = set(session.scalars(select(WatchModel.id).where(WatchModel.active.is_(True))))
    pos = [
        c
        for c in session.scalars(select(Comp).where(Comp.model_id.is_not(None), Comp.state == "sold"))
        if c.model_id in active and c.image_urls
    ]
    neg = list(
        session.scalars(
            select(Comp)
            .where(Comp.designer.is_(None), Comp.state == "sold", Comp.hammer_sek < 1000)
            .order_by(func.random())
            .limit(n_neg * 3)
        )
    )
    neg = [c for c in neg if c.image_urls]
    fb = session.execute(
        select(Listing, Feedback.label)
        .join(Feedback, Feedback.listing_id == Listing.id)
        .where(Feedback.label.in_(("ej_intressant", "fel_modell", "replika")))
    ).all()
    cases = [
        Case(
            "positive",
            "comp",
            c.id,
            CATEGORY_TITLES.get(c.category or "", "Möbel"),
            None,
            None,
            c.image_urls,
            c.model_id,
        )
        for c in rng.sample(pos, min(n_pos, len(pos)))
    ]
    neg_cases = [
        Case("negative", f"feedback:{label}", lst.id, lst.title, lst.description, lst.price_sek, lst.image_urls, None)
        for lst, label in fb
    ]
    neg_cases += [
        Case("negative", "comp", c.id, CATEGORY_TITLES.get(c.category or "", "Möbel"), None, None, c.image_urls, None)
        for c in neg
    ]
    cases += neg_cases[:n_neg]
    rng.shuffle(cases)
    return cases


def run_case(case: Case, session, client, loader: ImageLoader, cfg) -> Outcome:
    t0 = time.monotonic()
    cost = 0.0
    models = list(session.scalars(select(WatchModel).where(WatchModel.active.is_(True))))
    by_id = {m.id: m for m in models}
    try:
        pf = prefilter(
            case.title,
            case.description,
            case.price_sek,
            10**9,
            [watch_terms(m.id, m.designer, m.manufacturer, m.model_name, m.aliases) for m in models],
        )
        # Listing images (e.g. Blocket) follow the same flag as production; comp images come from Auctionet.
        urls = case.image_urls if case.source == "comp" or cfg.ai_send_listing_images else []
        scr, u = screen(client, cfg.model_fast, case.title, case.price_sek, loader.blocks(urls, 512, 1))
        cost += budget.cost_usd(cfg.model_prices, u.model, u.tokens_in, u.tokens_out, u.cache_read, u.cache_write)
        refs = [ModelRef(m.id, m.designer, m.manufacturer, m.model_name, tuple(m.aliases or [])) for m in models]
        picked = select_candidates(refs, pf.matched_model_ids, scr.designer, scr.manufacturer, scr.model_name)
        if not picked:
            return Outcome(case, None, None, scr.is_collectible_design, cost, time.monotonic() - t0)
        specs = [
            CandidateSpec(
                r.id,
                model_label(by_id[r.id]),
                by_id[r.id].identifying_features,
                by_id[r.id].replica_traps,
                by_id[r.id].marks,
            )
            for r in picked
        ]
        ver, u = verify(
            client,
            cfg.model_fast,
            case.title,
            case.description,
            case.price_sek,
            loader.blocks(urls, 784, 4),
            specs,
        )
        cost += budget.cost_usd(cfg.model_prices, u.model, u.tokens_in, u.tokens_out, u.cache_read, u.cache_write)
        predicted = ver.candidate_id if ver.match in ("yes", "uncertain") and ver.candidate_id in by_id else None
        return Outcome(case, predicted, ver.match, scr.is_collectible_design, cost, time.monotonic() - t0)
    except Exception as e:  # keep going; errors are reported
        return Outcome(case, None, None, False, cost, time.monotonic() - t0, error=repr(e)[:300])


def summarize(outcomes: list[Outcome]) -> dict:
    """Pure: precision/recall on 'alerted with the right model', false positives by negative source."""
    tp = sum(1 for o in outcomes if o.case.kind == "positive" and o.predicted_model_id == o.case.true_model_id)
    wrong_model = sum(
        1 for o in outcomes if o.case.kind == "positive" and o.predicted_model_id not in (None, o.case.true_model_id)
    )
    fp_by: dict[str, int] = {}
    for o in outcomes:
        if o.case.kind == "negative" and o.predicted_model_id is not None:
            fp_by[o.case.source] = fp_by.get(o.case.source, 0) + 1
    fp = sum(fp_by.values()) + wrong_model
    n_pos = sum(1 for o in outcomes if o.case.kind == "positive")
    lat = sorted(o.latency_s for o in outcomes)
    return {
        "n": len(outcomes),
        "n_positive": n_pos,
        "true_positive": tp,
        "wrong_model": wrong_model,
        "precision": round(tp / (tp + fp), 3) if tp + fp else None,
        "recall": round(tp / n_pos, 3) if n_pos else None,
        "false_positives_by_source": fp_by,
        "errors": sum(1 for o in outcomes if o.error),
        "cost_usd": round(sum(o.cost_usd for o in outcomes), 4),
        "cost_usd_per_item": round(sum(o.cost_usd for o in outcomes) / len(outcomes), 5) if outcomes else None,
        "latency_p50_s": round(lat[len(lat) // 2], 2) if lat else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = get_config()
    upgrade()
    with session_scope() as session:
        cases = build_cases(session, args.limit // 2, args.limit - args.limit // 2, args.seed)
        n_pos = sum(c.kind == "positive" for c in cases)
        print(
            f"{len(cases)} fall ({n_pos} positiva, {len(cases) - n_pos} negativa). "
            f"Uppskattad kostnad ≈ {len(cases) * EST_USD_PER_ITEM:.2f} USD."
        )
        if args.dry_run or not cases:
            return
        if not cfg.anthropic_api_key:
            raise SystemExit("ANTHROPIC_API_KEY saknas i .env")
        client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
        loader = ImageLoader(cfg.image_cache_dir, cfg.user_agent)
        outcomes = []
        for i, case in enumerate(cases, 1):
            outcomes.append(run_case(case, session, client, loader, cfg))
            print(f"  {i}/{len(cases)} {case.kind:8} → {outcomes[-1].match or '-'}", flush=True)
    summary = summarize(outcomes)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"{datetime.now(UTC):%Y%m%d-%H%M%S}.json"
    out.write_text(
        json.dumps(
            {"summary": summary, "models": {"fast": cfg.model_fast}, "outcomes": [asdict(o) for o in outcomes]},
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )
    print(f"Sparat: {out}")


if __name__ == "__main__":
    main()
