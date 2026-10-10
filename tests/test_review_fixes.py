"""Regression tests for findings from the second-reviewer pass (ASTRA, 2026-10-10)."""

import io
import os

import httpx
import pytest
from PIL import Image

from fyndjakt.images import RETENTION_S, ImageLoader
from fyndjakt.notify.telegram import TelegramClient, TelegramError
from fyndjakt.services import IngestListing, scrub_contacts


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (64, 64), (10, 20, 30)).save(buf, "PNG")
    return buf.getvalue()


def _loader(tmp_path, handler, clock):
    return ImageLoader(tmp_path, "ua", http=httpx.Client(transport=httpx.MockTransport(handler)), clock=clock)


# --- images: blocking, retention, size ------------------------------------------------------------


def test_image_host_block_stops_fetching_and_is_reported(tmp_path):
    hits = []

    def handler(req):
        hits.append(req.url.path)
        return httpx.Response(429)

    now = [1_000_000.0]
    loader = _loader(tmp_path, handler, lambda: now[0])
    assert loader.blocks(["https://img.test/a.jpg", "https://img.test/b.jpg"], 512, 2) == []
    assert hits == ["/a.jpg"]  # stops at the first block instead of trying the next image
    assert [(e.host, e.reason) for e in loader.blocked_events] == [("img.test", "429")]
    loader.blocks(["https://img.test/c.jpg"], 512, 1)
    assert hits == ["/a.jpg"]  # paused host: no request at all
    now[0] += 7 * 3600
    loader.blocks(["https://img.test/c.jpg"], 512, 1)
    assert hits == ["/a.jpg", "/c.jpg"]


def test_image_captcha_page_counts_as_block(tmp_path):
    def handler(req):
        return httpx.Response(200, headers={"content-type": "text/html"}, content=b"<html>captcha</html>")

    loader = _loader(tmp_path, handler, lambda: 0.0)
    assert loader.blocks(["https://img.test/a.jpg"], 512, 1) == []
    assert loader.blocked_events[0].reason == "captcha"


def test_image_cache_is_not_reused_after_retention(tmp_path):
    hits = []

    def handler(req):
        hits.append(1)
        return httpx.Response(200, content=_png())

    now = [2_000_000.0]
    loader = _loader(tmp_path, handler, lambda: now[0])
    loader.blocks(["https://img.test/a.jpg"], 512, 1)
    cached = next(tmp_path.glob("*.img"))
    os.utime(cached, (now[0], now[0]))
    now[0] += RETENTION_S + 1
    assert len(loader.blocks(["https://img.test/a.jpg"], 512, 1)) == 1
    assert len(hits) == 2


def test_image_size_limit_aborts_download(tmp_path, monkeypatch):
    monkeypatch.setattr("fyndjakt.images.MAX_DOWNLOAD_BYTES", 1000)

    def handler(req):
        return httpx.Response(200, content=b"x" * 5000)

    loader = _loader(tmp_path, handler, lambda: 0.0)
    assert loader.blocks(["https://img.test/big.jpg"], 512, 1) == []
    assert not list(tmp_path.glob("*.img"))


# --- seller contact details -----------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    ["Ring 070-123 45 67 efter 17", "mejla säljare@exempel.se", "+46 70 123 45 67", "tel 0701234567."],
)
def test_contacts_are_scrubbed(text):
    out = scrub_contacts(text)
    assert "[kontaktuppgift borttagen]" in out and not any(ch.isdigit() for ch in out.replace("17", ""))


def test_measurements_and_years_survive_scrubbing():
    text = "Höjd 80 cm, bredd 120, år 1962, pris 1500 kr. Lamino 1956 i ek 69x75"
    assert scrub_contacts(text) == text


def test_ingest_payload_scrubs_description():
    p = IngestListing(source="blocket_share", external_id="1", title="Byrå", description="Sms:a 0731234567")
    assert p.description == "Sms:a [kontaktuppgift borttagen]"


# --- Telegram errors never carry the token --------------------------------------------------------


def test_telegram_error_hides_token():
    def handler(req):
        return httpx.Response(409, json={"ok": False, "description": "Conflict: webhook is active"})

    tg = TelegramClient("123:SECRET", http=httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(TelegramError) as e:
        tg.get_updates(None)
    assert "SECRET" not in str(e.value) and "409" in str(e.value)
    assert e.value.__suppress_context__


def test_telegram_network_error_hides_token():
    def handler(req):
        raise httpx.ConnectError("boom", request=req)

    tg = TelegramClient("123:SECRET", http=httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(TelegramError) as e:
        tg.send_text("1", "hej")
    assert "SECRET" not in str(e.value)


def test_poller_acknowledges_update_only_after_handling(monkeypatch):
    from fyndjakt.web import app as webapp

    calls = []

    def flaky(update, deps):
        calls.append(update["update_id"])
        if len(calls) == 1:
            raise RuntimeError("database is locked")

    monkeypatch.setattr(webapp, "handle_telegram_update", flaky)

    class FakeTg:
        offsets: list = []

        def delete_webhook(self):
            pass

        def get_updates(self, offset):
            self.offsets.append(offset)
            if len(self.offsets) > 2:
                poller.stop()
                return []
            return [{"update_id": 5, "callback_query": {}}]

    class D:
        telegram = FakeTg()

    poller = webapp.TelegramPoller(D())
    poller._stop.wait = lambda _s: None
    poller.run()
    assert calls == [5, 5] and D.telegram.offsets == [None, None, 6]
