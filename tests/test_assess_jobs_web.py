from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from fyndjakt import jobs
from fyndjakt.ai.steps import Screening, Usage, Verification
from fyndjakt.assess import Deps, assess_listing
from fyndjakt.models import AICall, Assessment, Comp, Feedback, Job, Listing, SettingsRow, SourceHealth, WatchModel
from fyndjakt.services import IngestListing, enqueue, get_settings, health_problems, upsert_listing
from fyndjakt.sources.auctionet import SourceBlocked
from tests.conftest import NOW


class FakeTelegram:
    def __init__(self):
        self.alerts: list[tuple] = []
        self.texts: list[str] = []

    def send_alert(self, chat_id, text, markup, photo_url, silent):
        self.alerts.append((chat_id, text, markup, photo_url, silent))
        return 100 + len(self.alerts)

    def send_text(self, chat_id, text, silent=False):
        self.texts.append(text)

    def mark_handled(self, *a):
        pass


def _screen(designer="Yngve Ekström", model="Lamino"):
    def fn(client, model_id, title, price, images):
        return (
            Screening(
                reason="ok",
                is_collectible_design=True,
                designer=designer,
                manufacturer="Swedese",
                model_name=model,
                confidence="medel",
            ),
            Usage(model_id, 400, 80, 0, 0),
        )

    return fn


def _verify(candidate_id, match="yes", confidence="hög", strong_candidate=None):
    calls = []

    def fn(client, model_id, title, desc, price, images, cands):
        calls.append(model_id)
        cid = strong_candidate if (strong_candidate is not None and model_id == "claude-sonnet-5-5") else candidate_id
        return (
            Verification(
                evidence=["Böjda armstöd", "Etikett Swedese"],
                contradictions=["Ny klädsel"],
                replica_signals=[],
                label_ocr="SWEDESE",
                candidate_id=cid,
                match=match,
                condition_guess="gott",
                needs_underside_photo=False,
                confidence=confidence,
            ),
            Usage(model_id, 5000, 400, 0, 0),
        )

    fn.calls = calls
    return fn


@pytest.fixture
def world(session, config):
    s = get_settings(session)
    s.home_lat, s.home_lon = 57.49, 12.07  # Kungsbacka-ish
    m = WatchModel(
        designer="Yngve Ekström",
        manufacturer="Swedese",
        model_name="Lamino",
        category="stolar_fatoljer",
        aliases=["Lamino fåtölj"],
        replica_traps="Kopior utan Swedese-etikett",
        active=True,
    )
    session.add(m)
    session.flush()
    for i, p in enumerate((6000, 7000, 8000, 9000, 10000)):
        session.add(
            Comp(
                source="auctionet",
                external_id=str(i),
                model_id=m.id,
                designer="Yngve Ekström",
                title=f'YNGVE EKSTRÖM. Fåtölj "Lamino", Swedese {i}',
                hammer_sek=p,
                condition="gott",
                state="sold",
            )
        )
    listing = Listing(
        source="blocket_push",
        external_id="b1",
        title="Lamino fåtölj",
        price_sek=800,
        municipality="Kungsbacka",
        lat=57.49,
        lon=12.07,
        url="https://example.test/b1",
        image_urls=["https://img.example.test/1.jpg"],
    )
    session.add(listing)
    session.flush()
    return m, listing


FAKE_AI = object()


def _deps(config, tg=None, screen_fn=None, verify_fn=None, ai=FAKE_AI, now=NOW):
    return Deps(
        config=config, ai=ai, telegram=tg, now=lambda: now, screen_fn=screen_fn or _screen(), verify_fn=verify_fn
    )


def test_assess_full_pipeline_sends_fynd(session, config, world):
    m, listing = world
    tg = FakeTelegram()
    verify = _verify(m.id)
    a = assess_listing(session, listing.id, _deps(config, tg, verify_fn=verify))
    assert a.stage == "final" and a.decision == "FYND"
    assert a.value_level == "model" and a.n_comps == 5
    assert a.value_p25 == 7000 and a.distance_km == 0.0
    assert a.net_margin_sek == round(7000 * 0.78 - 500 - 300 - 800)
    assert a.confidence == "hög"
    # escalated to the strong model because net >= 2 x min margin
    assert verify.calls == ["claude-haiku-4-5", "claude-sonnet-5-5"]
    assert len(tg.alerts) == 1 and tg.alerts[0][4] is False
    assert tg.alerts[0][3] is None  # images not sent while ai_send_listing_images is off
    stages = [x.stage for x in session.scalars(select(Assessment).where(Assessment.listing_id == listing.id))]
    assert stages == ["prefilter", "screen", "verify", "verify_strong", "final"]
    assert session.scalar(select(AICall.id).where(AICall.purpose == "verify_strong"))
    assert listing.status == "assessed"


def test_strong_model_disagreement_lowers_confidence(session, config, world):
    m, listing = world
    tg = FakeTelegram()
    a = assess_listing(session, listing.id, _deps(config, tg, verify_fn=_verify(m.id, strong_candidate=999)))
    assert a.confidence == "låg"
    assert a.decision == "KOLLA_SJALV"
    assert tg.alerts and tg.alerts[0][4] is True  # silent


def test_price_over_max_is_skipped_without_ai(session, config, world):
    _, listing = world
    listing.price_sek = 50000
    called = []
    a = assess_listing(session, listing.id, _deps(config, screen_fn=lambda *a: called.append(1)))
    assert a.decision == "INGET" and listing.status == "skipped" and not called


def test_budget_exhausted_runs_prefilter_only_and_alerts_once(session, config, world):
    _, listing = world
    session.add(AICall(purpose="screen", model="claude-haiku-4-5", cost_usd=5.0, created_at=NOW - timedelta(hours=1)))
    session.flush()
    tg = FakeTelegram()
    called = []
    deps = _deps(config, tg, screen_fn=lambda *a: called.append(1))
    a = assess_listing(session, listing.id, deps)
    assess_listing(session, listing.id, deps)
    assert a.decision == "INGET" and "AI" in a.note and not called
    assert len(tg.texts) == 1 and "AI-budgeten" in tg.texts[0]


def test_no_api_key_skips_ai(session, config, world):
    _, listing = world
    a = assess_listing(session, listing.id, _deps(config, ai=None))
    assert a.decision == "INGET"


def test_kolla_sjalv_is_held_back_in_quiet_hours(session, config, world):
    m, listing = world
    tg = FakeTelegram()
    night = datetime(2026, 10, 10, 1, 0, tzinfo=UTC)  # 03:00 Stockholm
    a = assess_listing(session, listing.id, _deps(config, tg, verify_fn=_verify(m.id, strong_candidate=999), now=night))
    assert a.decision == "KOLLA_SJALV" and tg.alerts == []


# --- ingest ---------------------------------------------------------------------------------------


def test_upsert_listing_new_then_price_change(session):
    payload = IngestListing(
        source="blocket_share",
        external_id="x1",
        title="Stol",
        price_sek=500,
        lat=57.123456,
        lon=12.987654,
        seller_name="Anna",
        phone="070",
    )
    listing, new, changed = upsert_listing(session, payload)
    assert new and not changed and (listing.lat, listing.lon) == (57.12, 12.99)
    assert not hasattr(listing, "seller_name")
    _, new, changed = upsert_listing(session, payload.model_copy(update={"price_sek": 400}))
    assert not new and changed
    _, new, changed = upsert_listing(session, payload.model_copy(update={"price_sek": 400}))
    assert not changed
    # the price change finds the first job still pending, so one assessment covers both versions
    assert len(list(session.scalars(select(Job).where(Job.kind == "assess")))) == 1


# --- jobs -----------------------------------------------------------------------------------------


def test_run_one_runs_assess_job(session, config, world):
    m, listing = world
    enqueue(session, "assess", {"listing_id": listing.id}, run_at=NOW - timedelta(seconds=1))
    session.commit()
    tg = FakeTelegram()
    assert jobs.run_one(_deps(config, tg, verify_fn=_verify(m.id)), {}) is True
    session.expire_all()
    job = session.scalar(select(Job).where(Job.kind == "assess"))
    assert job.status == "done" and tg.alerts
    assert jobs.run_one(_deps(config, tg, verify_fn=_verify(m.id)), {}) is False


def test_failed_job_is_retried_with_backoff(session, config):
    enqueue(session, "assess", {"listing_id": 12345}, run_at=NOW - timedelta(seconds=1))
    session.commit()
    jobs.run_one(_deps(config), {})
    session.expire_all()
    job = session.scalar(select(Job))
    assert job.status == "pending" and job.attempts == 1 and "12345" in job.last_error
    assert job.run_at.replace(tzinfo=UTC) == NOW + timedelta(minutes=2)


class BlockedAuctionet:
    def iter_new(self, known, **params):
        raise SourceBlocked("429")
        yield  # pragma: no cover


class OkAuctionet:
    def __init__(self, items):
        self.items, self.params = items, None

    def iter_new(self, known, **params):
        self.params = params
        yield from (i for i in self.items if str(i["id"]) not in known)


def test_auctionet_crawl_blocked_stops_source_and_alerts(session, config):
    tg = FakeTelegram()
    enqueue(session, "auctionet_crawl", run_at=NOW - timedelta(seconds=1))
    session.commit()
    jobs.run_one(_deps(config, tg), {"auctionet": BlockedAuctionet()})
    session.expire_all()
    row = session.get(SourceHealth, "auctionet")
    assert row.stopped_reason == "429" and row.stopped_until.replace(tzinfo=UTC) > NOW
    assert tg.texts and "Källan trasig: auctionet" in tg.texts[0]
    nxt = session.scalar(select(Job).where(Job.kind == "auctionet_crawl", Job.status == "pending"))
    assert nxt.run_at.replace(tzinfo=UTC) == datetime(2026, 10, 11, 1, 0, tzinfo=UTC)  # 03:00 Stockholm (CEST)


def test_auctionet_crawl_saves_comps(session, config):
    from tests.conftest import load_fixture

    items = load_fixture("auctionet_items_ended_furniture.json")["items"]
    client = OkAuctionet(items)
    enqueue(session, "auctionet_crawl", run_at=NOW - timedelta(seconds=1))
    session.commit()
    jobs.run_one(_deps(config), {"auctionet": client})
    session.expire_all()
    assert client.params == {"category_id": 16, "stop_before": None}  # first crawl: no mark yet
    assert len(list(session.scalars(select(Comp)))) == len(items)
    assert session.get(SourceHealth, "auctionet").consecutive_failures == 0


def test_health_problems_pure():
    now = NOW
    rows = [
        SourceHealth(source="a", consecutive_failures=3),
        SourceHealth(source="b", consecutive_failures=0, last_item_at=now - timedelta(hours=3)),
        SourceHealth(source="c", consecutive_failures=1),
    ]
    silence = {"b": timedelta(hours=2)}
    assert [r.source for r, _ in health_problems(rows, now, 14, silence)] == ["a", "b"]
    assert [r.source for r, _ in health_problems(rows, now, 23, silence)] == ["a"]  # night: silence is fine


def test_next_local_time_handles_dst():
    winter = datetime(2026, 12, 1, 12, tzinfo=UTC)
    assert jobs.next_local_time(winter, "Europe/Stockholm", 3) == datetime(2026, 12, 2, 2, tzinfo=UTC)


# --- web ------------------------------------------------------------------------------------------


@pytest.fixture
def client(env):
    from fyndjakt.web.app import create_app

    with TestClient(create_app(run_worker=False)) as c:
        yield c


def test_health_is_open(client):
    assert client.get("/health").json() == {"ok": True}


def test_ingest_requires_token(client):
    body = {"source": "blocket_push", "external_id": "p1", "title": "Teakbyrå", "price_sek": 900}
    assert client.post("/ingest/listing", json=body).status_code == 401
    assert client.post("/ingest/listing", json=body, headers={"Authorization": "Bearer fel"}).status_code == 401
    r = client.post("/ingest/listing", json=body, headers={"Authorization": "Bearer ingest-secret"})
    assert r.status_code == 200 and r.json()["new"] is True
    bad = body | {"source": "okänd"}
    auth = {"Authorization": "Bearer ingest-secret"}
    assert client.post("/ingest/listing", json=bad, headers=auth).status_code == 422


def test_telegram_webhook_records_feedback(client):
    from fyndjakt.db import session_scope

    r = client.post(
        "/ingest/listing",
        json={"source": "blocket_push", "external_id": "p2", "title": "Stol"},
        headers={"Authorization": "Bearer ingest-secret"},
    )
    lid = r.json()["id"]
    upd = {
        "callback_query": {"id": "cb1", "data": f"fb:{lid}:replika", "message": {"message_id": 5, "chat": {"id": 42}}}
    }
    assert client.post("/telegram/webhook", json=upd).status_code == 401
    assert (
        client.post("/telegram/webhook", json=upd, headers={"X-Telegram-Bot-Api-Secret-Token": "tg-secret"}).status_code
        == 200
    )
    with session_scope() as s:
        fb = s.scalar(select(Feedback).where(Feedback.listing_id == lid))
        assert fb.label == "replika" and s.get(Listing, lid).status == "handled"


def test_ui_pages_render_and_settings_save(client):
    from fyndjakt.db import session_scope

    r = client.post(
        "/ingest/listing",
        json={"source": "blocket_share", "external_id": "p3", "title": "Fåtölj"},
        headers={"Authorization": "Bearer ingest-secret"},
    )
    lid = r.json()["id"]
    assert "Inkorg" in client.get("/inkorg").text
    assert client.get("/inkorg?alla=1").status_code == 200
    page = client.get(f"/annons/{lid}")
    assert page.status_code == 200 and "Fåtölj" in page.text
    assert client.get("/annons/99999").status_code == 404
    assert client.post(f"/annons/{lid}/feedback", data={"label": "köpt"}).status_code == 200
    assert client.post(f"/annons/{lid}/feedback", data={"label": "x"}).status_code == 400
    assert "Min nettomarginal" in client.get("/installningar").text
    r = client.post(
        "/installningar",
        data={"min_net_margin_sek": "2000", "min_roi": "0,6", "allowed_regions": "Hallands län, Västra Götalands län"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    with session_scope() as s:
        row = s.get(SettingsRow, 1)
        assert (row.min_net_margin_sek, row.min_roi) == (2000, 0.6)
        assert row.allowed_regions == ["Hallands län", "Västra Götalands län"]


def test_telegram_ignores_other_chats_and_poller_handles_updates(client):
    from fyndjakt.db import session_scope
    from fyndjakt.web.app import TelegramPoller

    r = client.post(
        "/ingest/listing",
        json={"source": "blocket_push", "external_id": "p4", "title": "Byrå"},
        headers={"Authorization": "Bearer ingest-secret"},
    )
    lid = r.json()["id"]
    hdr = {"X-Telegram-Bot-Api-Secret-Token": "tg-secret"}
    stranger = {
        "callback_query": {"id": "x", "data": f"fb:{lid}:köpt", "message": {"message_id": 1, "chat": {"id": 7}}}
    }
    assert client.post("/telegram/webhook", json=stranger, headers=hdr).status_code == 200
    with session_scope() as s:
        assert s.scalar(select(Feedback).where(Feedback.listing_id == lid)) is None

    class FakeTg:
        def __init__(self):
            self.calls, self.offsets = [], []

        def delete_webhook(self):
            self.calls.append("deleteWebhook")

        def get_updates(self, offset):
            self.offsets.append(offset)
            if len(self.offsets) == 1:
                cq = {"id": "c", "data": f"fb:{lid}:ej_intressant", "message": {"message_id": 3, "chat": {"id": 42}}}
                return [{"update_id": 10, "callback_query": cq}]
            poller.stop()
            return []

        def mark_handled(self, chat_id, message_id, label, callback_id):
            self.calls.append(("mark", chat_id, message_id))

    deps = client.app.state.deps
    fake = FakeTg()
    deps.telegram = fake
    poller = TelegramPoller(deps)
    poller.run()
    assert fake.offsets == [None, 11] and fake.calls == ["deleteWebhook", ("mark", "42", 3)]
    with session_scope() as s:
        assert s.scalar(select(Feedback).where(Feedback.listing_id == lid)).label == "ej_intressant"
