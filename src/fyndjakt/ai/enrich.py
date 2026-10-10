"""AI enrichment for M2: comp title parsing in batches (MODEL_FAST, half price) and watchlist notes (MODEL_STRONG)."""

import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Literal

import anthropic
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from fyndjakt.models import AIBatch, Comp, WatchModel

TITLE_SYSTEM = """Du tolkar titlar från svenska auktionshus för möbler. Ange formgivare, tillverkare och modellnamn
bara om de står i titeln eller tydligt följer av den (t.ex. ett känt modellnamn). Hitta inte på. Modellnamn utan
citattecken. Formgivare med normal versalisering ("Bruno Mathsson"). Lämna fält tomma när de saknas."""

TITLE_SCHEMA = {
    "type": "object",
    "properties": {
        "designer": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "manufacturer": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "model_name": {"anyOf": [{"type": "string"}, {"type": "null"}]},
    },
    "required": ["designer", "manufacturer", "model_name"],
    "additionalProperties": False,
}

NOTES_SYSTEM = """Du är expert på skandinavisk möbeldesign och andrahandsmarknaden. För en given modell, skriv
underlag som en bildgranskare kan använda för att känna igen originalet och skilja det från kopior:
identifierande detaljer (form, konstruktion, material, mått), märkning (etiketter, stämplar, brännmärken och var de
sitter) och replikafällor (kända kopior, licensutgåvor, nytillverkning och hur de skiljer sig). Var konkret och kort.
Skriv "osäkert" hellre än att gissa. Svara på svenska."""


# Rough Batches cost per title (~300 tokens in, ~60 out, half price) used to keep a batch inside the budget.
EST_USD_PER_TITLE = 0.0004


class ModelNotes(BaseModel):
    identifying_features: str
    marks: str
    replica_traps: str
    aliases: list[str]
    confidence: Literal["låg", "medel", "hög"]


def comps_needing_parse(session: Session, limit: int) -> list[Comp]:
    return list(session.scalars(select(Comp).where(Comp.parse_status.is_(None)).order_by(Comp.id).limit(limit)))


def submit_title_batch(session: Session, client: anthropic.Anthropic, model: str, limit: int = 5000) -> AIBatch | None:
    comps = comps_needing_parse(session, limit)
    if not comps:
        return None
    requests = [
        {
            "custom_id": f"comp-{c.id}",
            "params": {
                "model": model,
                "max_tokens": 200,
                "system": [{"type": "text", "text": TITLE_SYSTEM, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": c.title}],
                "output_config": {"format": {"type": "json_schema", "schema": TITLE_SCHEMA}},
            },
        }
        for c in comps
    ]
    batch = client.messages.batches.create(requests=requests)
    row = AIBatch(batch_id=batch.id, purpose="comp_titles", model=model, n_requests=len(requests))
    session.add(row)
    for c in comps:
        c.parse_status = "llm_pending"
    session.flush()
    return row


def apply_title_result(comp: Comp, text: str | None) -> None:
    """Pure-ish: write a parsed JSON result onto a comp (only fields the rules left empty)."""
    if text is None:
        comp.parse_status = "llm_failed"
        return
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        comp.parse_status = "llm_failed"
        return
    for k in ("designer", "manufacturer", "model_name"):
        v = (data.get(k) or "").strip() or None
        if v and not getattr(comp, k):
            setattr(comp, k, v)
    comp.parse_status = "llm" if comp.designer else "none"


def collect_batches(
    session: Session,
    client: anthropic.Anthropic,
    now: datetime | None = None,
    on_usage: Callable[[str, object], None] | None = None,
) -> int:
    """Collect ended batches. Returns the number of batches still open."""
    still_open = 0
    for row in session.scalars(select(AIBatch).where(AIBatch.status == "submitted")):
        batch = client.messages.batches.retrieve(row.batch_id)
        if batch.processing_status != "ended":
            still_open += 1
            continue
        for result in client.messages.batches.results(row.batch_id):
            comp = session.get(Comp, int(result.custom_id.removeprefix("comp-")))
            if comp is None:
                continue
            text = None
            if result.result.type == "succeeded":
                msg = result.result.message
                text = next((b.text for b in msg.content if b.type == "text"), None)
                if on_usage:
                    on_usage(row.model, msg.usage)
            elif result.result.type in ("expired", "canceled"):
                comp.parse_status = None  # retry in a later batch
                continue
            apply_title_result(comp, text)
        row.status = "collected"
        row.collected_at = now or datetime.now(UTC)
    return still_open


def write_model_notes(client: anthropic.Anthropic, model: str, m: WatchModel) -> tuple[ModelNotes, object]:
    prompt = (
        f"Formgivare: {m.designer or '-'}\nModell: {m.model_name or '-'}\nTillverkare: {m.manufacturer or '-'}\n"
        f"Kategori: {m.category or '-'}\nAntal sålda på auktion: {m.n_sales}, median {m.median_sek} kr"
    )
    resp = client.messages.parse(
        model=model,
        max_tokens=4000,
        system=[{"type": "text", "text": NOTES_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
        output_format=ModelNotes,
    )
    return resp.parsed_output, resp.usage


def models_needing_notes(session: Session, limit: int) -> list[WatchModel]:
    return list(
        session.scalars(
            select(WatchModel)
            .where(
                WatchModel.active.is_(True),
                WatchModel.auto_generated.is_(True),
                WatchModel.notes_generated_at.is_(None),
            )
            .order_by(WatchModel.median_sek.desc())
            .limit(limit)
        )
    )


def apply_notes(m: WatchModel, notes: ModelNotes, now: datetime) -> None:
    """Fill only empty fields so owner edits are never overwritten."""
    m.identifying_features = m.identifying_features or notes.identifying_features
    m.marks = m.marks or notes.marks
    m.replica_traps = m.replica_traps or notes.replica_traps
    m.aliases = sorted({*(m.aliases or []), *(a.strip() for a in notes.aliases if a.strip())})
    m.notes_generated_at = now
