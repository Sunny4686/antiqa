"""Ongoing Auctionet lots as a deal source."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from sqlalchemy import func, select

from fyndjakt import jobs
from fyndjakt.assess import assess_listing
from fyndjakt.models import AICall, Assessment, Job, Listing
from fyndjakt.pipeline.geo import load_municipalities
from fyndjakt.services import enqueue
from fyndjakt.sources.auctionet import AuctionetClient, live_price
from tests.conftest import NOW
from tests.test_assess_jobs_web import _deps, _verify
from tests.test_assess_jobs_web import world as world  # noqa: F401  (pytest fixture)
from tests.test_pages_m3 import client as client  # noqa: F401  (pytest fixture)

MUNICIPALITIES = load_municipalities(Path(__file__).resolve().parents[1] / "data" / "kommuner.csv")


def test_live_price_uses_next_bid_premium_and_unmet_reserve():
    item = {"next_bid_amount": 1000, "bids": [{"amount": 900}], "reserve_amount": 2000, "reserve_met": True}
    assert live_price(item, 0.25) == (1250, 900)
    item["reserve_met"] = False
    assert live_price(item, 0.25) == (2500, 900)
    assert live_price({"starting_bid_amount": 300, "bids": []}, 0.2) == (360, None)
    assert live_price({}, 0.2) == (None, None)


def test_iter_live_stops_at_horizon(monkeypatch):
    monkeypatch.setattr("fyndjakt.sources.auctionet.time.sleep", lambda s: None)
    now = 1_800_000_000
    seen = []

    def handler(req):
        seen.append(dict(req.url.params))
        items = [{"id": i, "title": "x", "ends_at": now + i * 3600} for i in range(1, 4)]
        return httpx.Response(200, json={"items": items, "pagination": {"total_pages": 5}})

    client = AuctionetClient("ua", http=httpx.Client(transport=httpx.MockTransport(handler)))
    got = [i["id"] for i in client.iter_live(datetime.fromtimestamp(now + 2.5 * 3600, UTC), category_id=16)]
    assert got == [1, 2] and len(seen) == 1
    assert seen[0]["is"] == "ongoing" and seen[0]["order"] == "end_asc" and seen[0]["category_id"] == "16"


class LiveAuctionet:
    def __init__(self, lots):
        self.lots = lots

    def iter_live(self, horizon, **params):
        yield from self.lots


def _lot(lot_id, title, next_bid, ends_in_h=3):
    return {
        "id": lot_id,
        "title": title,
        "description": "<p>Ek och läder.</p>",
        "next_bid_amount": next_bid,
        "bids": [{"amount": next_bid - 100}],
        "reserve_met": True,
        "ends_at": int((NOW + timedelta(hours=ends_in_h)).timestamp()),
        "location": "Kungsbacka",
        "url": f"https://auctionet.com/sv/{lot_id}",
        "images": [{"w640": f"https://images.auctionet.com/{lot_id}.jpg"}],
    }


def test_live_job_keeps_watchlist_lots_and_reprices_without_new_ai(session, config, world):  # noqa: F811
    m, _listing = world
    lots = [
        _lot(1, 'YNGVE EKSTRÖM. Fåtölj "Lamino", Swedese.', 600),
        _lot(2, "FÅTÖLJ, 1960-tal.", 200),  # unattributed: goes to the image check
        _lot(3, "BYRÅ, gustaviansk, 1700-tal.", 900),  # another era: skipped
        _lot(4, "ARNE JACOBSEN. Stol, Fritz Hansen.", 300),  # attributed by the house, not on the watchlist
    ]
    enqueue(session, "auctionet_live", run_at=NOW - timedelta(seconds=1))
    session.commit()
    verify = _verify(m.id)
    deps = _deps(config, verify_fn=verify)
    deps.municipalities = MUNICIPALITIES
    jobs.run_one(deps, {"auctionet": LiveAuctionet(lots)})
    session.expire_all()
    live = list(session.scalars(select(Listing).where(Listing.source == "auctionet_live")))
    assert sorted(lst.external_id for lst in live) == ["1", "2"]
    lot = next(lst for lst in live if lst.external_id == "1")
    assert lot.price_sek == 750 and lot.current_bid_sek == 500 and lot.municipality == "Kungsbacka"
    assert lot.ends_at.replace(tzinfo=UTC) == NOW + timedelta(hours=3)
    nxt = session.scalar(select(Job).where(Job.kind == "auctionet_live", Job.status == "pending"))
    assert nxt.run_at.replace(tzinfo=UTC) == NOW + timedelta(minutes=30)

    queued = [j.payload["listing_id"] for j in session.scalars(select(Job).where(Job.kind == "assess"))]
    assert lot.id in queued and len(queued) == 2
    first = assess_listing(session, lot.id, deps)
    session.commit()
    assert first.decision == "FYND"
    ai_calls = session.scalar(select(func.count(AICall.id)))

    # A higher bid half an hour later: re-priced with the stored verdict, no new AI calls
    lots[0]["next_bid_amount"] = 4000
    later = NOW + timedelta(minutes=31)
    deps_later = _deps(config, verify_fn=verify, now=later)
    deps_later.municipalities = MUNICIPALITIES
    jobs.run_one(deps_later, {"auctionet": LiveAuctionet(lots)})
    session.expire_all()
    assert session.get(Listing, lot.id).price_sek == 5000 and session.get(Listing, lot.id).status == "new"
    assess_listing(session, lot.id, deps_later)
    session.commit()
    finals = list(
        session.scalars(
            select(Assessment)
            .where(Assessment.listing_id == lot.id, Assessment.stage == "final")
            .order_by(Assessment.id)
        )
    )
    assert len(finals) == 2 and finals[-1].decision != "FYND"
    assert session.scalar(select(func.count(AICall.id))) == ai_calls


def test_utvalt_shows_running_fynd_cards_soonest_first(client):
    from fyndjakt.db import session_scope

    now = datetime.now(UTC)
    with session_scope() as s:
        for ext, ends, decision in (
            ("late", 20, "FYND"),
            ("soon", 2, "FYND"),
            ("over", -1, "FYND"),
            ("no", 1, "INGET"),
        ):
            lst = Listing(
                source="auctionet_live",
                external_id=ext,
                title=f"Lot {ext}",
                price_sek=1000,
                ends_at=now + timedelta(hours=ends),
                image_urls=[f"https://images.auctionet.com/{ext}.jpg"],
            )
            s.add(lst)
            s.flush()
            s.add(Assessment(listing_id=lst.id, stage="final", decision=decision, net_margin_sek=2000))
    page = client.get("/utvalt").text
    assert page.index("Lot soon") < page.index("Lot late")
    assert "Lot over" not in page  # ended
    cards, table = page.split("Närmast fynd")
    assert "Lot no" not in cards and "Lot no" in table  # INGET lots are listed as watched, not as cards
    assert "https://images.auctionet.com/soon.jpg" in page and "slutar om 1 h" in page
    assert client.get("/", follow_redirects=False).headers["location"] == "/utvalt"
