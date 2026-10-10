import httpx
import pytest

from fyndjakt.sources import auctionet
from fyndjakt.sources.auctionet import (
    AuctionetClient,
    SourceBlocked,
    classify_condition,
    hammer,
    parse_item,
    parse_title,
)
from tests.conftest import load_fixture


def test_parse_ended_furniture_fixture():
    items = load_fixture("auctionet_items_ended_furniture.json")["items"]
    c = parse_item(items[0])
    assert c.external_id == "5398293"
    assert c.state == "sold"
    assert c.hammer_sek == 5000  # highest bid; 'hammered' is false on online lots
    assert c.designer == "Børge Mogensen"
    assert c.manufacturer == "Karl Andersson & söner"
    assert c.category == "skåp_hyllor"
    assert c.sold_at is not None and c.sold_at.year == 2026
    assert c.image_urls and all(u.startswith("https://images.auctionet.com/") for u in c.image_urls)
    assert c.condition_text and "<p>" not in c.condition_text


def test_parse_query_fixture_sold_and_unsold():
    items = load_fixture("auctionet_items_query_mathsson.json")["items"]
    parsed = [parse_item(i) for i in items]
    sold = [p for p in parsed if p.state == "sold"]
    unsold = [p for p in parsed if p.state == "unsold"]
    assert sold and all(p.hammer_sek for p in sold)
    assert unsold and all(p.hammer_sek is None for p in unsold)
    assert any(p.model_name == "Maria Flap" for p in parsed)


def test_fixtures_contain_no_bidder_identity():
    for name in ("auctionet_items_ended_furniture.json", "auctionet_items_query_mathsson.json"):
        for item in load_fixture(name)["items"]:
            for bid in item.get("bids") or []:
                assert isinstance(bid["bidder"], int)  # anonymised sequence number only


@pytest.mark.parametrize(
    ("title", "designer", "manufacturer", "model"),
    [
        ('BRUNO MATHSSON. Foldable Table "Maria Flap". Firma Karl Mathsson 1936', "Bruno Mathsson", None, "Maria Flap"),
        (
            'TABLE "SUPERELLIPSE", Bruno Mathsson & Piet Hein for Fritz Hansen.',
            "Bruno Mathsson & Piet Hein",
            "Fritz Hansen",
            "SUPERELLIPSE",
        ),
        ("SIDEBOARD, trä, gustaviansk stil.", None, None, None),
        ("CARL JOHAN BOMAN, Stolar, 2 st. Wilh. Schauman Ab formgivna 1962.", "Carl Johan Boman", None, None),
        ("SKINNFÅTÖLJ MED FOTPALL, IMG COMFORT OF NORWAY.", None, None, None),
        ('FÅTÖLJ, "Pernilla", Bruno Mathsson, Dux.', None, None, "Pernilla"),
        ("SKINNFÅTÖLJ MED FOTPALL. Brun läder.", None, None, None),
        ("ARKIVSKÅP, ek, tidigt 1900-tal.", None, None, None),
    ],
)
def test_parse_title(title, designer, manufacturer, model):
    p = parse_title(title)
    assert p.designer == designer
    assert p.manufacturer == manufacturer
    assert p.model_name == model


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Mycket gott skick.", "utmärkt"),
        ("Normalt bruksslitage, repor.", "gott"),
        ("Större skador på fanér.", "slitet"),
        ("Renoveringsobjekt, lös fot.", "renoveringsobjekt"),
        (None, None),
        ("Se bilder.", None),
    ],
)
def test_classify_condition(text, expected):
    assert classify_condition(text) == expected


def test_hammer_ignores_unsold():
    assert hammer({"state": "unsold", "bids": [{"amount": 900}]}) is None
    assert hammer({"state": "sold", "bids": []}) is None


class _Clock:
    def __init__(self):
        self.t = 1000.0
        self.slept: list[float] = []

    def monotonic(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


@pytest.fixture
def clock(monkeypatch):
    c = _Clock()
    monkeypatch.setattr(auctionet.time, "monotonic", c.monotonic)
    monkeypatch.setattr(auctionet.time, "sleep", c.sleep)
    return c


def _client(handler, min_interval=5.0):
    http = httpx.Client(transport=httpx.MockTransport(handler))
    return AuctionetClient("test-agent", min_interval, http=http)


def _page(ids, total_pages=3):
    return {
        "items": [{"id": i, "title": f"t{i}", "state": "sold", "bids": []} for i in ids],
        "pagination": {"total_pages": total_pages},
    }


def test_iter_new_stops_at_known_id_and_respects_rate(clock):
    pages = {1: _page([10, 9, 8]), 2: _page([7, 6, 5]), 3: _page([4, 3])}
    seen_params = []

    def handler(req):
        seen_params.append(dict(req.url.params))
        return httpx.Response(200, json=pages[int(req.url.params["page"])])

    client = _client(handler, min_interval=1.0)  # below the guardrail: must be raised to 5 s
    got = [i["id"] for i in client.iter_new({"6"}, category_id=16)]
    assert got == [10, 9, 8, 7, 5]
    assert [p["page"] for p in seen_params] == ["1", "2"]
    assert seen_params[0]["is"] == "ended" and seen_params[0]["category_id"] == "16"
    assert clock.slept and all(s == pytest.approx(5.0) for s in clock.slept)


@pytest.mark.parametrize("status", [403, 429])
def test_blocking_status_raises(clock, status):
    client = _client(lambda req: httpx.Response(status))
    with pytest.raises(SourceBlocked) as e:
        client.get_page(1)
    assert e.value.reason == str(status)


def test_non_json_page_counts_as_block(clock):
    client = _client(
        lambda req: httpx.Response(200, text="<html>captcha</html>", headers={"content-type": "text/html"})
    )
    with pytest.raises(SourceBlocked) as e:
        client.get_page(1)
    assert e.value.reason == "captcha"


def test_page_cap_redirect_ends_iteration(clock):
    client = _client(lambda req: httpx.Response(302, headers={"location": "/"}))
    assert list(client.iter_new(set())) == []
