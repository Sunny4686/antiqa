"""Download, downscale and cache listing images for the AI steps. Local copies are deleted after 7 days."""

import base64
import hashlib
import io
import time
from pathlib import Path

import httpx
from PIL import Image

MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024
RETENTION_S = 7 * 24 * 3600


def resize_jpeg(data: bytes, max_px: int, quality: int = 85) -> bytes:
    """Fit inside max_px x max_px, re-encode as JPEG (also strips EXIF metadata)."""
    with Image.open(io.BytesIO(data)) as im:
        im = im.convert("RGB")
        im.thumbnail((max_px, max_px))
        out = io.BytesIO()
        im.save(out, "JPEG", quality=quality)
        return out.getvalue()


def image_block(jpeg: bytes) -> dict:
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.standard_b64encode(jpeg).decode()},
    }


class ImageLoader:
    """Fetches each URL at most once per retention period; the AI only ever sees downscaled copies."""

    def __init__(self, cache_dir: str | Path, user_agent: str, http: httpx.Client | None = None):
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._http = http or httpx.Client(headers={"User-Agent": user_agent}, timeout=20.0, follow_redirects=True)

    def _original(self, url: str) -> bytes:
        path = self.dir / (hashlib.sha256(url.encode()).hexdigest() + ".img")
        if path.exists():
            return path.read_bytes()
        r = self._http.get(url)
        r.raise_for_status()
        if len(r.content) > MAX_DOWNLOAD_BYTES:
            raise ValueError(f"image too large: {len(r.content)} bytes")
        path.write_bytes(r.content)
        return r.content

    def blocks(self, urls: list[str], max_px: int, limit: int) -> list[dict]:
        out = []
        for url in urls[:limit]:
            try:
                out.append(image_block(resize_jpeg(self._original(url), max_px)))
            except Exception:  # a broken image must not stop the assessment
                continue
        return out


def purge_old(cache_dir: str | Path, now: float | None = None, retention_s: int = RETENTION_S) -> int:
    now = now if now is not None else time.time()
    removed = 0
    d = Path(cache_dir)
    if not d.exists():
        return 0
    for p in d.glob("*.img"):
        if now - p.stat().st_mtime > retention_s:
            p.unlink(missing_ok=True)
            removed += 1
    return removed
