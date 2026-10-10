"""Regression tests for findings from the second-reviewer pass (ASTRA, 2026-10-10)."""

import io
import os
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from PIL import Image
from sqlalchemy import func, select

from fyndjakt.ai import budget
from fyndjakt.ai.steps import Usage, Verification
from fyndjakt.assess import assess_listing
from fyndjakt.images import RETENTION_S, ImageLoader
from fyndjakt.models import AIBatch, AICall
from fyndjakt.notify.telegram import TelegramClient, TelegramError
from fyndjakt.pipeline import decide as dec
from fyndjakt.services import IngestListing, scrub_contacts
from tests.conftest import NOW
from tests.test_assess_jobs_web import FakeTelegram, _deps
from tests.test_assess_jobs_web import world as world  # noqa: F401  (pytest fixture)
from tests.test_pages_m3 import client as client  # noqa: F401  (pytest fixture)


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


# --- budget, valuation and decision ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("now", "expected"),
    [
        (datetime(2026, 3, 29, 12, tzinfo=UTC), datetime(2026, 3, 29, 22, tzinfo=UTC)),  # after spring forward
        (datetime(2026, 10, 25, 21, 30, tzinfo=UTC), datetime(2026, 10, 25, 23, tzinfo=UTC)),  # 22:30 local, CET
        (datetime(2026, 10, 24, 12, tzinfo=UTC), datetime(2026, 10, 24, 22, tzinfo=UTC)),  # before fall back
    ],
)
def test_next_local_midnight_across_dst(now, expected):
    assert budget.next_local_midnight(now, "Europe/Stockholm") == expected


def test_open_batch_reserves_budget(session):
    session.add(AICall(purpose="screen", model="claude-haiku-4-5", cost_usd=0.5, created_at=NOW))
    session.add(AIBatch(batch_id="b1", purpose="comp_titles", model="claude-haiku-4-5", n_requests=1000))
    session.add(AIBatch(batch_id="b2", purpose="comp_titles", model="m", n_requests=999, status="collected"))
    session.flush()
    assert budget.spent_today(session, NOW, "Europe/Stockholm") == pytest.approx(0.5 + 1000 * 0.0004)


def test_free_listing_can_be_fynd():
    d = dec.DecisionInput(3000, None, 10.0, None, "hög", "model", True, 5000)
    assert dec.decide(d, dec.Thresholds(1500, 0.5, 120.0)) == dec.FYND


def _verify_with_strong_condition(candidate_id, strong_condition):
    def fn(client, model_id, title, desc, price, images, cands, **_kw):
        strong = model_id == "claude-sonnet-5-5"
        return (
            Verification(
                evidence=["Böjda armstöd"],
                contradictions=[],
                replica_signals=[],
                label_ocr=None,
                candidate_id=candidate_id,
                match="yes",
                condition_guess=strong_condition if strong else "gott",
                needs_underside_photo=False,
                confidence="hög",
            ),
            Usage(model_id, 5000, 400, 0, 0),
        )

    return fn


def test_strong_models_condition_drives_value_and_decision(session, config, world):  # noqa: F811
    m, listing = world
    listing.price_sek = 1300
    tg = FakeTelegram()
    a = assess_listing(
        session, listing.id, _deps(config, tg, verify_fn=_verify_with_strong_condition(m.id, "renoveringsobjekt"))
    )
    # gott: net 7000*0.78-800-1300 = 3360 (escalates, FYND); renoveringsobjekt: P25 7000/0.85*0.55 = 4529,
    # net 4529*0.78-800-1300 = 1433, below the 1500 minimum
    assert a.condition_guess == "renoveringsobjekt"
    assert a.value_p25 == round(7000 / 0.85 * 0.55)
    assert a.net_margin_sek < 1500 and a.decision != "FYND" and not tg.alerts


def test_ai_cost_survives_a_failing_later_step(session, config, world):  # noqa: F811
    m, listing = world

    def broken_verify(*a, **k):
        raise RuntimeError("API timeout")

    with pytest.raises(RuntimeError):
        assess_listing(session, listing.id, _deps(config, verify_fn=broken_verify))
    session.rollback()  # what session_scope does when the job fails
    assert session.scalar(select(func.count(AICall.id)).where(AICall.purpose == "screen")) == 1


def test_failed_alert_is_retried_as_job_without_new_ai_calls(session, config, world):  # noqa: F811
    from fyndjakt import jobs
    from fyndjakt.models import Job, TelegramMessage
    from tests.test_assess_jobs_web import _verify

    m, listing = world

    class FlakyTelegram(FakeTelegram):
        fail = True

        def send_alert(self, *a):
            if self.fail:
                raise TelegramError("sendMessage: HTTP 502")
            return super().send_alert(*a)

    tg = FlakyTelegram()
    verify = _verify(m.id)
    a = assess_listing(session, listing.id, _deps(config, tg, verify_fn=verify))
    assert a.decision == "FYND" and not tg.alerts
    session.commit()
    job = session.scalar(select(Job).where(Job.kind == "send_alert"))
    assert job.payload == {"assessment_id": a.id}
    tg.fail = False
    n_calls = len(verify.calls)
    later = NOW + timedelta(minutes=5)
    assert jobs.run_one(_deps(config, tg, verify_fn=verify, now=later), {})
    assert len(tg.alerts) == 1 and len(verify.calls) == n_calls
    session.expire_all()
    assert session.scalar(select(func.count(TelegramMessage.id))) == 1
    assert jobs.run_one(_deps(config, tg, verify_fn=verify, now=later), {}) is False  # nothing left to send


# --- web ------------------------------------------------------------------------------------------


def test_inbox_hides_fynd_that_a_reassessment_dropped(client):  # noqa: F811
    from fyndjakt.db import session_scope
    from fyndjakt.models import Assessment, Listing

    with session_scope() as s:
        lst = Listing(source="blocket_share", external_id="r1", title="Lamino fåtölj", price_sek=900)
        s.add(lst)
        s.flush()
        s.add(Assessment(listing_id=lst.id, stage="final", decision="FYND"))
        s.flush()
        s.add(Assessment(listing_id=lst.id, stage="final", decision="INGET"))
    assert "Lamino fåtölj" not in client.get("/inkorg").text
    assert "Lamino fåtölj" in client.get("/inkorg?alla=1").text


def test_allowed_regions_can_be_cleared(client):  # noqa: F811
    from fyndjakt.db import session_scope
    from fyndjakt.services import get_settings

    client.post("/installningar", data={"allowed_regions": "Hallands län, Skåne län"})
    client.post("/installningar", data={"allowed_regions": "", "min_roi": ""})
    with session_scope() as s:
        st = get_settings(s)
        assert st.allowed_regions == [] and st.min_roi == 0.5


def test_csv_import_rejects_short_rows_and_unknown_ids(client):  # noqa: F811
    from fyndjakt.db import session_scope
    from fyndjakt.models import WatchModel

    client.post("/bevakningslista/0", data={"designer": "Alf Svensson", "model_name": "Kontur", "notes": "x"})
    header = client.get("/bevakningslista/export.csv").text.splitlines()[0]
    short = f"{header}\n1\n"
    r = client.post("/bevakningslista/import", files={"file": ("w.csv", short.encode(), "text/csv")})
    assert r.status_code == 400 and "rad 2" in r.text
    cols = header.count(",")
    unknown = f"{header}\n999" + "," * cols + "\n"
    r = client.post("/bevakningslista/import", files={"file": ("w.csv", unknown.encode(), "text/csv")})
    assert r.status_code == 400 and "okänt id 999" in r.text
    with session_scope() as s:
        models = list(s.scalars(select(WatchModel)))
        assert len(models) == 1 and models[0].designer == "Alf Svensson"


def test_deal_can_be_edited_and_unsold_removes_own_comp(client):  # noqa: F811
    from fyndjakt.db import session_scope
    from fyndjakt.models import Comp, Deal

    client.post("/affarer", data={"title": "Lamino", "purchase_sek": "800", "bought_at": "2026-09-01"})
    with session_scope() as s:
        did = s.scalar(select(Deal.id))
    page = client.get(f"/affarer?redigera={did}").text
    assert f'name="deal_id" value="{did}"' in page and 'value="800"' in page
    assert client.get("/affarer?redigera=999").status_code == 404
    client.post("/affarer", data={"deal_id": str(did), "title": "Lamino", "sale_sek": "6000", "sold_at": "2026-10-01"})
    with session_scope() as s:
        assert s.scalar(select(func.count(Comp.id)).where(Comp.source == "own_sale")) == 1
    client.post("/affarer", data={"deal_id": str(did), "title": "Lamino", "sale_sek": "", "sold_at": ""})
    with session_scope() as s:
        assert s.scalar(select(func.count(Comp.id)).where(Comp.source == "own_sale")) == 0
        assert s.scalar(select(func.count(Deal.id))) == 1


def test_testa_page_saves_upload_and_queues_assessment(client):  # noqa: F811
    from fyndjakt.db import session_scope
    from fyndjakt.images import usable_urls
    from fyndjakt.models import Job, Listing

    assert "Testa en annons" in client.get("/testa").text
    r = client.post(
        "/testa",
        data={"title": "Fåtölj i ek, ring 0701234567", "price_sek": "900", "municipality": "Kungsbacka"},
        files=[("images", ("a.png", _png(), "image/png")), ("images", ("empty.png", b"", "image/png"))],
        follow_redirects=False,
    )
    assert r.status_code == 303
    lid = int(r.headers["location"].rsplit("/", 1)[1])
    with session_scope() as s:
        lst = s.get(Listing, lid)
        assert lst.source == "manual" and "0701234567" not in lst.title
        assert len(lst.image_urls) == 1 and lst.image_urls[0].startswith("local:")
        assert usable_urls(lst.image_urls, remote_allowed=False) == lst.image_urls
        assert s.scalar(select(Job).where(Job.kind == "assess")).payload == {"listing_id": lid}
        ident = lst.image_urls[0][6:]
    page = client.get(f"/annons/{lid}").text
    assert f"/bild/{ident}" in page and "Bedöms nu" in page
    img = client.get(f"/bild/{ident}")
    assert img.status_code == 200 and img.headers["content-type"] == "image/jpeg"
    assert client.get("/bild/../../etc").status_code == 404
    assert client.get("/bild/" + "0" * 64).status_code == 404
