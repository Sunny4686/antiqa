"""Screen capture ingest: the owner browses Blocket / Marketplace himself; a browser extension sends a screenshot
of what is on screen plus the positions of the visible links. Nothing is ever requested from those sites.

The AI reads each listing card off the screenshot (title, price, place, where the photo is); the photo is cropped
from the screenshot and the card goes through the normal assessment. The screenshot itself is deleted after
reading, because it can show other people's names."""

import hashlib
import io
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

import anthropic
from PIL import Image
from pydantic import BaseModel, Field

from fyndjakt.ai.steps import Usage, _usage

CAPTURE_SYSTEM = """Du läser en skärmbild av en sida med begagnade annonser (Blocket eller Facebook Marketplace).
Lista varje annonskort vars bild syns till minst hälften. Visar skärmbilden en enskild öppnad annons: lista
just den annonsen som ett kort, med den största möbelbilden som bildram.
För varje kort: rubriken ordagrant, priset i kronor som heltal (null om det saknas eller är oläsligt), ort om
den syns, och annonsbildens ram som andelar av skärmbildens bredd och höjd (0-1).
Annonser för annat än möbler och inredning (bilar, kläder, elektronik, bostäder): markera is_furniture=false.
Skriv aldrig ut namn på personer, även om de syns. Svara på svenska."""


class CapturedCard(BaseModel):
    title: str
    price_sek: int | None
    place: str | None
    is_furniture: bool
    image_box: list[float] = Field(description="[x0, y0, x1, y1] som andelar 0-1 av skärmbilden")


class CapturedPage(BaseModel):
    cards: list[CapturedCard]


def read_screenshot(client: anthropic.Anthropic, model: str, image_block: dict) -> tuple[CapturedPage, Usage]:
    resp = client.messages.parse(
        model=model,
        max_tokens=3000,
        system=[{"type": "text", "text": CAPTURE_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": [image_block, {"type": "text", "text": "Lista annonskorten."}]}],
        output_format=CapturedPage,
    )
    return resp.parsed_output, _usage(model, resp)


# --- pure helpers ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class LinkBox:
    href: str
    x0: float
    y0: float
    x1: float
    y1: float  # fractions of the viewport, like the AI's boxes


SITES = {"blocket.se": "blocket_ext", "facebook.com": "fb_ext"}
_ITEM_PATHS = (re.compile(r"/item/(\d+)"), re.compile(r"/marketplace/item/(\d+)"), re.compile(r"/(\d{6,})"))


def source_for(page_url: str) -> str | None:
    host = (urlsplit(page_url).hostname or "").lower()
    return next((src for dom, src in SITES.items() if host == dom or host.endswith("." + dom)), None)


def item_id(href: str) -> str | None:
    path = urlsplit(href).path
    for pat in _ITEM_PATHS:
        m = pat.search(path)
        if m:
            return m.group(1)
    return None


def link_for(box: list[float], links: list[LinkBox]) -> str | None:
    """The listing link whose box contains the centre of the card's photo (smallest such box wins)."""
    if len(box) != 4:
        return None
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    hits = [lk for lk in links if lk.x0 <= cx <= lk.x1 and lk.y0 <= cy <= lk.y1 and item_id(lk.href)]
    if not hits:
        return None
    return min(hits, key=lambda lk: (lk.x1 - lk.x0) * (lk.y1 - lk.y0)).href


def crop(png_or_jpeg: bytes, box: list[float], min_px: int = 60) -> bytes | None:
    """Cut the card photo out of the screenshot; None when the box is unusable or tiny."""
    if len(box) != 4:
        return None
    x0, y0, x1, y1 = (min(max(v, 0.0), 1.0) for v in box)
    if x1 <= x0 or y1 <= y0:
        return None
    with Image.open(io.BytesIO(png_or_jpeg)) as im:
        w, h = im.size
        area = (round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))
        if area[2] - area[0] < min_px or area[3] - area[1] < min_px:
            return None
        out = io.BytesIO()
        im.crop(area).convert("RGB").save(out, "JPEG", quality=90)
        return out.getvalue()


def fallback_id(title: str, price: int | None, place: str | None) -> str:
    """Stable id for a card without a readable link, so the same card in two screenshots is one listing."""
    key = f"{title.strip().lower()}|{price}|{(place or '').strip().lower()}"
    return "h" + hashlib.sha256(key.encode()).hexdigest()[:20]
