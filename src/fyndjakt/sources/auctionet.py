"""Auctionet ended items via the open JSON API (/api/v2/items.json). See docs/recon/RESULTAT.md.

Guardrails: at most one request per `auctionet_min_interval_s`, one at a time; 403/429/captcha stops the source.
"""

import html
import re
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime

import httpx

API = "https://auctionet.com/api/v2/items.json"
FURNITURE_CATEGORY = 16
FURNITURE_SUBCATEGORIES = {
    18: "stolar_fatoljer",
    24: "byråer",
    280: "soffbord",
    23: "skåp_hyllor",
    279: "skrivbord",
    22: "matsalsmöbler",
    281: "matbord",
    17: "övrigt",
    20: "soffor",
    19: "bord",
}
MAX_PAGES = 100  # API caps listings at 100 pages x 100 items per query


class SourceBlocked(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass
class ParsedTitle:
    designer: str | None = None
    manufacturer: str | None = None
    model_name: str | None = None


@dataclass
class CompData:
    external_id: str
    title: str
    state: str
    hammer_sek: int | None
    estimate_sek: int | None
    sold_at: datetime | None
    auction_house: str | None
    category: str | None
    condition_text: str | None
    condition: str | None
    url: str | None
    image_urls: list[str] = field(default_factory=list)
    designer: str | None = None
    manufacturer: str | None = None
    model_name: str | None = None
    parse_status: str | None = None


_TAG = re.compile(r"<[^>]+>")
_QUOTED = re.compile(r"[\"“”«»]([^\"“”«»]{2,60})[\"“”«»]")
_UPPER_LEAD = re.compile(r"^([A-ZÅÄÖÆØÉÜ][A-ZÅÄÖÆØÉÜ&'. -]{2,60}?)\.\s")
_UPPER_LEAD_COMMA = re.compile(r"^([A-ZÅÄÖÆØÉÜ][A-ZÅÄÖÆØÉÜ&'. -]{2,60}?),\s+(?=[A-ZÅÄÖ][a-zåäöé])")
# Leading uppercase words that describe the object, not a person.
TYPE_WORDS = (
    "STOL",
    "FÅTÖLJ",
    "KARMSTOL",
    "VILSTOL",
    "GUNGSTOL",
    "PALL",
    "BÄNK",
    "SOFFA",
    "DIVAN",
    "SCHÄSLONG",
    "BORD",
    "MATBORD",
    "SOFFBORD",
    "SKRIVBORD",
    "SKÅP",
    "VITRIN",
    "BYRÅ",
    "SEKRETÄR",
    "HYLLA",
    "BOKHYLLA",
    "SIDEBOARD",
    "SKÄNK",
    "KOMMOD",
    "SÄNG",
    "SPEGEL",
    "MATSAL",
    "MÖBEL",
    "MÖBLER",
    "SKINN",
    "TABLE",
    "CHAIR",
    "SOFA",
    "CABINET",
    "DESK",
    "SETT",
    "GRUPP",
    "ETT PAR",
    "PAR ",
)
_MAKER_FOR = re.compile(r",\s*([^,]{3,80}?)\s+(?:för|for|by|för firma)\s+([^,.]{2,60})", re.I)


def strip_html(text: str | None) -> str | None:
    if not text:
        return None
    return re.sub(r"\s+", " ", html.unescape(_TAG.sub(" ", text))).strip() or None


def parse_title(title: str) -> ParsedTitle:
    """Rule-based parse of typical titles: 'DESIGNER. Typ "Modell", Tillverkare, ort år.'

    Leaves fields as None when unsure; the rest is resolved by MODEL_FAST later (M2).
    """
    out = ParsedTitle()
    m = _UPPER_LEAD.match(title) or _UPPER_LEAD_COMMA.match(title)
    lead = m.group(1).strip() if m else ""
    if m and " " in lead and not any(w in lead for w in TYPE_WORDS):
        out.designer = lead.title()
    else:
        m = None
    q = _QUOTED.search(title)
    if q:
        out.model_name = q.group(1).strip()
    f = _MAKER_FOR.search(title)
    if f:
        out.designer = out.designer or f.group(1).strip()
        out.manufacturer = f.group(2).strip().rstrip(". ")
    elif out.designer:
        # 'DESIGNER. Typ, Tillverkare, ...' -> the segment after the type is often the maker.
        parts = [p.strip() for p in title[m.end() :].split(",")]  # type: ignore[union-attr]
        if len(parts) >= 2 and parts[1] and not re.search(r"\d", parts[1]) and parts[1][0].isupper():
            out.manufacturer = parts[1].rstrip(". ")
    return out


def classify_condition(text: str | None) -> str | None:
    if not text:
        return None
    t = text.lower()
    if "renover" in t or "restaurer" in t or "trasig" in t:
        return "renoveringsobjekt"
    if any(k in t for k in ("mycket gott", "utmärkt", "nyskick", "excellent", "very good")):
        return "utmärkt"
    if any(k in t for k in ("större skad", "betydande", "kraftig", "omfattande", "lagad", "lagning")):
        return "slitet"
    if any(k in t for k in ("gott", "normalt slitage", "bruksslitage", "ålders", "slitage", "good", "wear")):
        return "gott"
    return None


def hammer(item: dict) -> int | None:
    """Hammer price = highest bid on a sold item. The 'hammered' flag is false for online lots; ignore it."""
    if item.get("state") != "sold":
        return None
    amounts = [b["amount"] for b in item.get("bids") or [] if b.get("amount")]
    return max(amounts) if amounts else None


def parse_item(item: dict) -> CompData:
    condition_text = strip_html(item.get("condition"))
    pt = parse_title(item["title"])
    images = [img.get("w640") or img.get("hd") for img in item.get("images") or []]
    return CompData(
        external_id=str(item["id"]),
        title=item["title"],
        state=item.get("state") or "unknown",
        hammer_sek=hammer(item),
        estimate_sek=item.get("estimate"),
        sold_at=datetime.fromtimestamp(item["ends_at"], UTC) if item.get("ends_at") else None,
        auction_house=item.get("house"),
        category=FURNITURE_SUBCATEGORIES.get(item.get("category_id")),
        condition_text=condition_text,
        condition=classify_condition(condition_text),
        url=item.get("url"),
        image_urls=[u for u in images if u],
        designer=pt.designer,
        manufacturer=pt.manufacturer,
        model_name=pt.model_name,
        # Titles the rules only half understood go to the LLM batch parser, which fills just the empty fields.
        parse_status="rules" if pt.designer and pt.model_name else None,
    )


class AuctionetClient:
    """Serialised, rate-limited client. One shared instance per process."""

    def __init__(self, user_agent: str, min_interval_s: float = 5.0, http: httpx.Client | None = None):
        self._http = http or httpx.Client(
            headers={"User-Agent": user_agent, "Accept": "application/json"}, timeout=30.0, follow_redirects=False
        )
        self._min_interval = max(min_interval_s, 5.0)  # never faster than the guardrail
        self._lock = threading.Lock()
        self._last = 0.0

    def get_page(self, page: int, per_page: int = 100, **params: object) -> dict:
        with self._lock:
            wait = self._last + self._min_interval - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            try:
                r = self._http.get(API, params={"is": "ended", "page": page, "per_page": per_page, **params})
            finally:
                self._last = time.monotonic()
        if r.status_code in (403, 429):
            raise SourceBlocked(str(r.status_code))
        if r.status_code == 302:  # past the page cap
            return {"items": [], "pagination": {"current_page": page, "total_pages": page - 1}}
        r.raise_for_status()
        if "json" not in r.headers.get("content-type", ""):
            raise SourceBlocked("captcha" if "captcha" in r.text.lower() else "non-json")
        return r.json()

    def iter_new(
        self,
        known_ids: set[str],
        max_pages: int = MAX_PAGES,
        stop_before: datetime | None = None,
        **params: object,
    ) -> Iterator[dict]:
        """Newest-ended first; stop after the first page that contains an already known id.

        With stop_before (the start of the last complete crawl), keep going past known ids until the page also
        reaches items that ended before it. A crawl that died half-way then can't leave a permanent gap behind
        the items it did save."""
        for page in range(1, max_pages + 1):
            data = self.get_page(page, **params)
            items = data.get("items") or []
            hit_known = False
            for item in items:
                if str(item["id"]) in known_ids:
                    hit_known = True
                    continue
                yield item
            total = (data.get("pagination") or {}).get("total_pages") or 0
            if stop_before is not None and hit_known:
                ends = [i["ends_at"] for i in items if i.get("ends_at")]
                hit_known = bool(ends) and min(ends) < stop_before.timestamp()
            if hit_known or not items or page >= total:
                return

    def pages(self, start_page: int = 1, count: int = MAX_PAGES, **params: object) -> Iterator[tuple[int, list, bool]]:
        """(page, items, is_last) for up to count pages from start_page, within the page cap."""
        for page in range(start_page, min(start_page + count, MAX_PAGES + 1)):
            data = self.get_page(page, **params)
            items = data.get("items") or []
            total = (data.get("pagination") or {}).get("total_pages") or 0
            last = not items or page >= total or page >= MAX_PAGES
            yield page, items, last
            if last:
                return

    def iter_all(self, max_pages: int = MAX_PAGES, **params: object) -> Iterator[dict]:
        """Every item up to the page cap (backfill). Upserts make re-runs harmless."""
        for _page, items, _last in self.pages(1, max_pages, **params):
            yield from items
