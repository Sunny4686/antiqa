"""Browser-extension screenshots: read into listings, never kept, no requests to the listing sites."""

import io
from datetime import timedelta
from pathlib import Path

from PIL import Image
from sqlalchemy import select

from fyndjakt import capture, jobs
from fyndjakt.ai.steps import Usage
from fyndjakt.assess import Deps
from fyndjakt.capture import CapturedCard, CapturedPage, LinkBox
from fyndjakt.images import ImageLoader
from fyndjakt.models import AICall, Job, Listing
from fyndjakt.services import enqueue
from tests.conftest import NOW
from tests.test_pages_m3 import client as client  # noqa: F401  (pytest fixture)


def _screenshot(w=1200, h=800) -> bytes:
    im = Image.new("RGB", (w, h), (240, 240, 240))
    im.paste((120, 60, 20), (100, 100, 400, 400))  # a "photo" in the top-left card
    buf = io.BytesIO()
    im.save(buf, "JPEG")
    return buf.getvalue()


def test_pure_helpers():
    assert capture.source_for("https://www.blocket.se/recommerce/forsale/search?category=0.78") == "blocket_ext"
    assert capture.source_for("https://www.facebook.com/marketplace/gothenburg/") == "fb_ext"
    assert capture.source_for("https://evil.example/blocket.se") is None
    assert capture.item_id("https://www.blocket.se/recommerce/forsale/item/12345678") == "12345678"
    assert capture.item_id("https://www.facebook.com/marketplace/item/998877665544/?ref=x") == "998877665544"
    links = [
        LinkBox("https://www.blocket.se/recommerce/forsale/item/111", 0.05, 0.1, 0.4, 0.6),
        LinkBox("https://www.blocket.se/", 0.0, 0.0, 1.0, 1.0),  # page-wide link without an item id
    ]
    assert capture.link_for([0.1, 0.15, 0.3, 0.45], links).endswith("/111")
    assert capture.link_for([0.6, 0.6, 0.9, 0.9], links) is None
    jpeg = capture.crop(_screenshot(), [100 / 1200, 100 / 800, 400 / 1200, 400 / 800])
    with Image.open(io.BytesIO(jpeg)) as im:
        assert im.size == (300, 300)
    assert capture.crop(_screenshot(), [0.1, 0.1, 0.11, 0.11]) is None  # too small
    assert capture.fallback_id("Fåtölj ", 500, "Mölndal") == capture.fallback_id("fåtölj", 400, "mölndal")


def test_screenshot_endpoint_requires_token_and_known_site(client, tmp_path):  # noqa: F811
    from fyndjakt.db import session_scope

    files = {"image": ("s.jpg", _screenshot(), "image/jpeg")}
    data = {"page_url": "https://www.blocket.se/recommerce/forsale/search", "links": "[]"}
    assert client.post("/ingest/screenshot", data=data, files=files).status_code == 401
    auth = {"Authorization": "Bearer ingest-secret"}
    bad = {**data, "page_url": "https://www.example.com/"}
    assert client.post("/ingest/screenshot", data=bad, files=files, headers=auth).status_code == 400
    r = client.post("/ingest/screenshot", data=data, files=files, headers=auth)
    assert r.status_code == 200
    with session_scope() as s:
        job = s.scalar(select(Job).where(Job.kind == "screen_capture"))
        assert Path(job.payload["path"]).exists() and job.payload["page_url"].startswith("https://www.blocket.se")


def test_capture_job_creates_listings_and_deletes_screenshot(session, config, tmp_path):
    shot = tmp_path / "captures" / "a.img"
    shot.parent.mkdir()
    shot.write_bytes(_screenshot())
    page = CapturedPage(
        cards=[
            CapturedCard(
                title="Fåtölj ek",
                price_sek=400,
                place="Mölndal",
                is_furniture=True,
                image_box=[100 / 1200, 100 / 800, 400 / 1200, 400 / 800],
            ),
            CapturedCard(
                title="Volvo V70", price_sek=30000, place=None, is_furniture=False, image_box=[0.5, 0.5, 0.9, 0.9]
            ),
        ]
    )
    seen_images = []

    def fake_read(client, model, image_block):
        seen_images.append(image_block["source"]["media_type"])
        return page, Usage(model, 1500, 300, 0, 0)

    links = [
        {"href": "https://www.blocket.se/recommerce/forsale/item/4242", "x0": 0.05, "y0": 0.1, "x1": 0.4, "y1": 0.6}
    ]
    enqueue(
        session,
        "screen_capture",
        {"path": str(shot), "page_url": "https://www.blocket.se/recommerce/forsale/search", "links": links},
        run_at=NOW - timedelta(seconds=1),
    )
    session.commit()
    deps = Deps(
        config=config, ai=object(), images=ImageLoader(tmp_path / "img", "ua"), now=lambda: NOW, capture_fn=fake_read
    )
    assert jobs.run_one(deps, {})
    session.expire_all()
    listings = list(session.scalars(select(Listing)))
    assert len(listings) == 1
    lst = listings[0]
    assert (lst.source, lst.external_id, lst.title, lst.price_sek) == ("blocket_ext", "4242", "Fåtölj ek", 400)
    assert lst.url.endswith("/item/4242") and lst.image_urls[0].startswith("local:")
    assert not shot.exists()  # the screenshot is gone once read
    assert seen_images == ["image/jpeg"]
    assert session.scalar(select(AICall).where(AICall.purpose == "capture")).cost_usd > 0
    assert session.scalar(select(Job).where(Job.kind == "assess")).payload == {"listing_id": lst.id}


def test_imported_screenshot_uses_given_source(session, config, tmp_path):
    shot = tmp_path / "b.img"
    shot.write_bytes(_screenshot())
    card = CapturedCard(
        title="Byrå teak",
        price_sek=900,
        place="Borås",
        is_furniture=True,
        image_box=[100 / 1200, 100 / 800, 400 / 1200, 400 / 800],
    )
    enqueue(
        session,
        "screen_capture",
        {"path": str(shot), "source": "fb_import", "page_url": "", "links": []},
        run_at=NOW - timedelta(seconds=1),
    )
    session.commit()
    deps = Deps(
        config=config,
        ai=object(),
        images=ImageLoader(tmp_path / "img", "ua"),
        now=lambda: NOW,
        capture_fn=lambda c, m, b: (CapturedPage(cards=[card]), Usage(m, 1000, 200, 0, 0)),
    )
    assert jobs.run_one(deps, {})
    session.expire_all()
    lst = session.scalar(select(Listing))
    assert (lst.source, lst.title, lst.price_sek) == ("fb_import", "Byrå teak", 900) and not shot.exists()
