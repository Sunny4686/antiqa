"""Steps 2 and 4: image screening and verification with strict JSON (structured outputs).

The fixed instructions sit in a cached system block; per-listing content goes in the user turn.
"""

from dataclasses import dataclass
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

Confidence = Literal["låg", "medel", "hög"]
ConditionGuess = Literal["utmärkt", "gott", "slitet", "renoveringsobjekt", "okänt"]

SCREEN_SYSTEM = """Du granskar begagnade möbelannonser från Sverige åt en återförsäljare av skandinavisk design.
Avgör om möbeln kan vara en skandinavisk designmöbel med samlarvärde (formgiven modell från en känd formgivare
eller tillverkare, främst 1930-1980), och i så fall vilken formgivare, tillverkare och modell den troligen är.
Var återhållsam: vanliga massproducerade möbler och nytillverkade kopior är inte samlarobjekt. Gissa inte namn
du inte har stöd för i bild eller text; lämna dem tomma. Säljare vet ofta inte vad de har, så rubriken kan vara
helt generisk ("fåtölj", "byrå"): utgå från formen i bilden. När en katalog över bevakade modeller finns, ange
upp till tre katalog-id vars form möbeln liknar (mest trolig först), även om du är osäker; tom lista om ingen
liknar. Svara kort och på svenska."""

VERIFY_SYSTEM = """Du verifierar om en möbel i en annons är en specifik formgiven modell från en kandidatlista.
Arbeta i denna ordning:
1. Lista konkreta bevis som talar FÖR en kandidat (form, detaljer, material, märkning).
2. Lista motbevis och tecken på replika eller licensutgåva (jämför mot kandidatens replica_traps).
3. Läs av etiketter, stämplar och brännmärken ordagrant om de syns.
4. Först därefter: välj kandidatens id, eller null om ingen kandidat stämmer.
match = "yes" bara när bevisen är tydliga; "uncertain" när modellen är trolig men inte bekräftad.
Ange needs_underside_photo = true när ett foto av undersidan eller märkningen skulle avgöra frågan.
Svara på svenska."""


class Screening(BaseModel):
    reason: str = Field(description="Kort motivering, 1-2 meningar")
    is_collectible_design: bool
    designer: str | None
    manufacturer: str | None
    model_name: str | None
    catalog_ids: list[int] = Field(description="Upp till 3 katalog-id som formen liknar, mest trolig först")
    confidence: Confidence


class Verification(BaseModel):
    evidence: list[str]
    contradictions: list[str]
    replica_signals: list[str]
    label_ocr: str | None
    candidate_id: int | None
    match: Literal["yes", "uncertain", "no"]
    condition_guess: ConditionGuess
    needs_underside_photo: bool
    confidence: Confidence


@dataclass
class Usage:
    model: str
    tokens_in: int
    tokens_out: int
    cache_read: int
    cache_write: int


@dataclass
class CandidateSpec:
    id: int
    label: str
    identifying_features: str | None
    replica_traps: str | None
    marks: str | None


# Image blocks come pre-built (downscaled base64, see fyndjakt.images); an empty list means text only.


def _usage(model: str, resp: object) -> Usage:
    u = resp.usage  # type: ignore[attr-defined]
    return Usage(
        model, u.input_tokens, u.output_tokens, u.cache_read_input_tokens or 0, u.cache_creation_input_tokens or 0
    )


def screen(
    client: anthropic.Anthropic,
    model: str,
    title: str,
    price_sek: int | None,
    image_blocks: list[dict],
    catalog: str | None = None,
) -> tuple[Screening, Usage]:
    content = [
        *image_blocks[:1],
        {"type": "text", "text": f"Rubrik: {title}\nPris: {price_sek if price_sek is not None else 'okänt'} kr"},
    ]
    system = [{"type": "text", "text": SCREEN_SYSTEM}]
    if catalog:
        system.append({"type": "text", "text": catalog})
    system[-1]["cache_control"] = {"type": "ephemeral"}  # the catalog is the same for every listing
    resp = client.messages.parse(
        model=model,
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": content}],
        output_format=Screening,
    )
    return resp.parsed_output, _usage(model, resp)


def _reference_content(candidates: list[CandidateSpec], references: dict[int, list[dict]] | None) -> list[dict]:
    """After the listing's own photos: labelled reference photos per candidate, to compare form directly."""
    out: list[dict] = []
    for c in candidates:
        blocks = (references or {}).get(c.id) or []
        if isinstance(blocks, dict):
            blocks = [blocks]
        if blocks:
            out.append(
                {"type": "text", "text": f"Referensbilder (sålda, bekräftade) för kandidat id={c.id}: {c.label}"}
            )
            out += blocks
    if out:
        out.insert(0, {"type": "text", "text": "Ovan: annonsens bilder. Nedan: referensbilder att jämföra formen med."})
    return out


def verify(
    client: anthropic.Anthropic,
    model: str,
    title: str,
    description: str | None,
    price_sek: int | None,
    image_blocks: list[dict],
    candidates: list[CandidateSpec],
    references: dict[int, list[dict]] | None = None,
) -> tuple[Verification, Usage]:
    cand_text = "\n\n".join(
        f"id={c.id}: {c.label}\nKännetecken: {c.identifying_features or '-'}\n"
        f"Replikafällor: {c.replica_traps or '-'}\nMärkning: {c.marks or '-'}"
        for c in candidates
    )
    text = (
        f"Rubrik: {title}\nPris: {price_sek if price_sek is not None else 'okänt'} kr\n"
        f"Annonstext: {description or '-'}\n\nKandidater:\n{cand_text or '(inga)'}"
    )
    resp = client.messages.parse(
        model=model,
        max_tokens=2000,
        system=[{"type": "text", "text": VERIFY_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[
            {
                "role": "user",
                "content": [
                    *image_blocks[:4],
                    *_reference_content(candidates, references),
                    {"type": "text", "text": text},
                ],
            }
        ],
        output_format=Verification,
    )
    return resp.parsed_output, _usage(model, resp)
