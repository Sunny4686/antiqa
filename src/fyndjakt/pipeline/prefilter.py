"""Step 1: code-only prefilter. Never discards a listing on text alone; only price can skip it."""

import re
import unicodedata
from dataclasses import dataclass, field

PLUS_TERMS = (
    "stämplad",
    "stämpel",
    "märkt",
    "etikett",
    "signerad",
    "dödsbo",
    "40-tal",
    "50-tal",
    "60-tal",
    "70-tal",
    "teak",
    "palisander",
    "jakaranda",
    "rosewood",
    "formgiven",
    "formgivare",
    "design",
    "vintage",
    "retro",
)
# Phrases that set the replica flag. Matched on word boundaries after normalisation.
REPLICA_TERMS = ("replika", "kopia", "i stil med", "a la", "inspirerad av", "replica", "copy")
REPLICA_SUFFIX = re.compile(r"\w-stil\b")


# Words the title parser sometimes takes for a maker or model: countries, materials, counts, furniture types.
GENERIC_TERMS = frozenset(
    [
        "danmark",
        "dänemark",
        "denmark",
        "sverige",
        "sweden",
        "schweden",
        "norge",
        "norway",
        "finland",
        "italien",
        "italy",
        "tyskland",
        "germany",
        "teak",
        "ek",
        "eke",
        "oak",
        "mahogny",
        "mahogany",
        "palisander",
        "jakaranda",
        "rosewood",
        "bok",
        "björk",
        "birch",
        "valnöt",
        "walnut",
        "furu",
        "pine",
        "alm",
        "ask",
        "massiv",
        "massivt",
        "lackerat",
        "trä",
        "wood",
        "metall",
        "stål",
        "läder",
        "par",
        "stolar",
        "fåtöljer",
        "fåtölj",
        "stol",
        "bord",
        "matbord",
        "soffbord",
        "byrå",
        "skåp",
        "hylla",
        "soffa",
        "matsalsmöbel",
        "matsalsmöbler",
        "möbel",
        "möbler",
        "sittgrupp",
    ]
)
_COUNT_LEAD = re.compile(r"^(ett|två|tre|fyra|fem|sex|sju|åtta|nio|tio|\d+)\b")


def is_generic(term: str) -> bool:
    n = normalize(term)
    return n in GENERIC_TERMS or _COUNT_LEAD.match(n) is not None or len(n) < 3


def normalize(text: str) -> str:
    """Lowercase, strip accents except Swedish å/ä/ö, collapse whitespace."""
    out = []
    for ch in text.lower():
        if ch in "åäö":
            out.append(ch)
            continue
        decomposed = unicodedata.normalize("NFKD", ch)
        out.append("".join(c for c in decomposed if not unicodedata.combining(c)))
    return re.sub(r"\s+", " ", "".join(out)).strip()


def contains_term(haystack: str, term: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", haystack) is not None


@dataclass(frozen=True)
class WatchTerms:
    model_id: int
    terms: tuple[str, ...]  # normalised designer/manufacturer/model/alias strings


@dataclass
class PrefilterResult:
    passed: bool
    reason: str | None = None
    plus_signals: list[str] = field(default_factory=list)
    replica_signals: list[str] = field(default_factory=list)
    matched_model_ids: list[int] = field(default_factory=list)

    @property
    def replica_flag(self) -> bool:
        return bool(self.replica_signals)


def watch_terms(
    model_id: int, designer: str | None, manufacturer: str | None, model_name: str | None, aliases: list[str] | None
) -> WatchTerms:
    raw = [designer, manufacturer, model_name, *(aliases or [])]
    terms = tuple(sorted({normalize(t) for t in raw if t and not is_generic(t)}))
    return WatchTerms(model_id, terms)


def strict_title_match(title: str, designer: str | None, model_name: str | None, aliases: list[str] | None) -> bool:
    """Auction lots: the designer's surname and the model name (or an alias) must both be in the title.
    Auction houses write both, so this keeps precision high and the AI cost per scan low."""
    text = normalize(title)
    surname = normalize(designer).split()[-1] if designer and designer.split() else ""
    if len(surname) < 3 or not contains_term(text, surname):
        return False
    names = [n for n in [model_name, *(aliases or [])] if n and not is_generic(n)]
    return any(contains_term(text, normalize(n).strip("\"'” ")) for n in names)


def prefilter(
    title: str, description: str | None, price_sek: int | None, max_price_sek: int, watchlist: list[WatchTerms]
) -> PrefilterResult:
    if price_sek is not None and price_sek > max_price_sek:
        return PrefilterResult(passed=False, reason=f"pris {price_sek} > {max_price_sek}")

    text = normalize(f"{title} {description or ''}")
    plus = [t for t in PLUS_TERMS if contains_term(text, t)]
    replica = [t for t in REPLICA_TERMS if contains_term(text, t)]
    replica += [m.group(0) for m in REPLICA_SUFFIX.finditer(text)]
    matched = [w.model_id for w in watchlist if any(contains_term(text, t) for t in w.terms)]
    return PrefilterResult(passed=True, plus_signals=plus, replica_signals=replica, matched_model_ids=matched)
