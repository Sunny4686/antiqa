"""Download, downscale and cache listing images for the AI steps. Local copies are deleted after 7 days."""

import base64
import hashlib
import io
import time
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from PIL import Image

MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024
RETENTION_S = 7 * 24 * 3600
BLOCK_PAUSE_S = 6 * 3600


class ImageSourceBlocked(Exception):
    """403/429/captcha from an image host. Fetching from that host stops; nothing is circumvented."""

    def __init__(self, host: str, reason: str):
        super().__init__(f"{host}: {reason}")
        self.host, self.reason = host, reason


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

    def __init__(
        self,
        cache_dir: str | Path,
        user_agent: str,
        http: httpx.Client | None = None,
        clock=time.time,  # noqa: ANN001
    ):
        self.dir = Path(cache_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._http = http or httpx.Client(headers={"User-Agent": user_agent}, timeout=20.0, follow_redirects=True)
        self._clock = clock
        self.blocked_until: dict[str, float] = {}
        self.blocked_events: list[ImageSourceBlocked] = []  # drained by the caller to alert the owner

    def _original(self, url: str) -> bytes:
        path = self.dir / (hashlib.sha256(url.encode()).hexdigest() + ".img")
        if path.exists():
            if self._clock() - path.stat().st_mtime <= RETENTION_S:
                return path.read_bytes()
            path.unlink(missing_ok=True)  # past retention: never reuse, fetch again
        host = urlsplit(url).hostname or ""
        if self.blocked_until.get(host, 0) > self._clock():
            raise ImageSourceBlocked(host, "paused")
        with self._http.stream("GET", url) as r:
            if r.status_code in (403, 429):
                self._block(host, str(r.status_code))
            r.raise_for_status()
            ctype = r.headers.get("content-type", "")
            if ctype.startswith("text/html"):
                body = r.read()[:20000].decode("utf-8", "replace").lower()
                self._block(host, "captcha" if "captcha" in body else "html")
            data = bytearray()
            for chunk in r.iter_bytes():
                data += chunk
                if len(data) > MAX_DOWNLOAD_BYTES:
                    raise ValueError("image too large")
        path.write_bytes(bytes(data))
        return bytes(data)

    def _block(self, host: str, reason: str) -> None:
        self.blocked_until[host] = self._clock() + BLOCK_PAUSE_S
        e = ImageSourceBlocked(host, reason)
        self.blocked_events.append(e)
        raise e

    def blocks(self, urls: list[str], max_px: int, limit: int) -> list[dict]:
        out = []
        for url in urls[:limit]:
            try:
                out.append(image_block(resize_jpeg(self._original(url), max_px)))
            except ImageSourceBlocked:
                break  # stop asking that host; the assessment continues without images
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
