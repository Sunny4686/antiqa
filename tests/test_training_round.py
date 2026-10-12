"""Training rounds: answer key, one-click judgement, metrics, and no alerts."""

import io

import pytest
from PIL import Image
from sqlalchemy import select

from fyndjakt import training_eval as te
from fyndjakt.models import Assessment, Listing, WatchModel
from tests.test_assess_jobs_web import FakeTelegram, _deps, _verify
from tests.test_assess_jobs_web import world as world  # noqa: F401  (pytest fixture)
from tests.test_pages_m3 import client as client  # noqa: F401  (pytest fixture)


@pytest.mark.parametrize(
    ("expected", "decision", "label", "out"),
    [
        (None, "FYND", "x", None),
        ("inget", "FYND", "Ekström – Lamino", "falsklarm"),
        ("Inget", "INGET", None, "rätt_inget"),
        ("Lamino", "FYND", "Yngve Ekström – Lamino (Swedese)", "rätt"),
        ("Lamino", "KOLLA_SJALV", "Bruno Mathsson – Pernilla", "fel_modell"),
        ("Lamino", "INGET", None, "missad"),
        ("korrekt", "FYND", "x", "rätt"),
        ("inte_design", "KOLLA_SJALV", "x", "falsklarm"),
        ("missad", "INGET", None, "missad"),
    ],
)
def test_verdict(expected, decision, label, out):
    assert te.verdict(expected, decision, label) == out


def test_summarize():
    s = te.summarize(
        [
            ("FYND", "rätt", 0.02),
            ("KOLLA_SJALV", "falsklarm", 0.01),
            ("INGET", "rätt_inget", 0.005),
            ("INGET", "rätt_inget", 0.005),
            ("INGET", "missad", 0.005),
            ("FYND", None, 0.01),
        ]
    )
    assert (s.n, s.answered, s.alerts) == (6, 5, 3)
    assert s.precision == 0.5 and s.false_alarm_rate == pytest.approx(1 / 3) and s.recall == 0.5
    assert s.cost_usd == pytest.approx(0.055)


def test_training_listing_is_never_alerted(session, config, world):  # noqa: F811
    from fyndjakt.assess import assess_listing

    m, listing = world
    listing.training = True
    tg = FakeTelegram()
    a = assess_listing(session, listing.id, _deps(config, tg, verify_fn=_verify(m.id)))
    assert a.decision == "FYND" and tg.alerts == []


def _jpg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (80, 60), (90, 60, 30)).save(buf, "JPEG")
    return buf.getvalue()


def test_training_import_page_and_judgement(client):  # noqa: F811
    from fyndjakt.db import session_scope

    text = "Rubrik: Fåtölj\nPris: 500\nFacit: Lamino\nBilder: a.jpg\n---\nRubrik: Pinnstol\nPris: 50\nBilder: b.jpg\n"
    files = [
        ("files", ("annonser.txt", text.encode(), "text/plain")),
        ("files", ("a.jpg", _jpg(), "image/jpeg")),
        ("files", ("b.jpg", _jpg(), "image/jpeg")),
    ]
    r = client.post("/importera", data={"batch": "test omg 1", "training": "on"}, files=files, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/traning/test-omg-1"
    with session_scope() as s:
        rows = list(s.scalars(select(Listing).where(Listing.import_batch == "test-omg-1")))
        assert len(rows) == 2 and all(r.training for r in rows)
        expected = {r.title: r.expected for r in rows}
        assert expected == {"Fåtölj": "Lamino", "Pinnstol": None}
        # pretend the AI answered: chair -> Lamino (alert), pinnstol -> KOLLA on some model
        m = WatchModel(designer="Yngve Ekström", model_name="Lamino", active=True, aliases=[])
        s.add(m)
        s.flush()
        chair = next(r for r in rows if r.title == "Fåtölj")
        stool = next(r for r in rows if r.title == "Pinnstol")
        for lst, dec in ((chair, "FYND"), (stool, "KOLLA_SJALV")):
            lst.status = "assessed"
            s.add(Assessment(listing_id=lst.id, stage="final", decision=dec, model_candidate_id=m.id, cost_usd=0.01))
        stool_id = stool.id
    page = client.get("/traning/test-omg-1").text
    assert "✓ rätt" in page and "Precision" in page
    client.post(f"/traning/test-omg-1/{stool_id}", data={"verdict": "inte_design"})
    page = client.get("/traning/test-omg-1").text
    assert "✗ falsklarm" in page and "50 %" in page  # precision 1 of 2 alerts
    assert "test-omg-1" in client.get("/traning").text
    assert client.post(f"/traning/test-omg-1/{stool_id}", data={"verdict": "hack"}).status_code == 400
