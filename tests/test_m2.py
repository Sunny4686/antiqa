import io
import json
import os
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from PIL import Image
from sqlalchemy import select

from eval.run import Case, Outcome, summarize
from fyndjakt import jobs
from fyndjakt.ai import enrich
from fyndjakt.assess import Deps
from fyndjakt.images import ImageLoader, purge_old, resize_jpeg
from fyndjakt.models import AIBatch, AICall, Comp, Job, SourceHealth, WatchModel
from fyndjakt.services import enqueue, upsert_comp
from fyndjakt.sources.auctionet import CompData, SourceBlocked
from fyndjakt.watchlist import CompRow, link_comps, propose_models, refresh_watchlist
from tests.conftest import NOW

# --- watchlist ------------------------------------------------------------------------------------


def _rows():
    rows = [
        CompRow(i, "Yngve Ekström", "Swedese", "Lamino", "stolar_fatoljer", p)
        for i, p in enumerate((5000, 6000, 7000, 8000), 1)
    ]
    rows += [CompRow(10, "YNGVE EKSTRÖM", None, '"lamino"', None, 6500)]  # same group after normalising
    rows += [CompRow(20 + i, "Okänd", None, "Billig", None, 800) for i in range(5)]  # median too low
    rows += [CompRow(30 + i, "Alf Svensson", None, "Kontur", None, 9000) for i in range(2)]  # too few
    rows += [CompRow(40, None, None, "Lamino", None, 9000), CompRow(41, "X", None, None, None, 9000)]
    return rows


def test_propose_models_groups_and_thresholds():
    out = propose_models(_rows())
    assert len(out) == 1
    p = out[0]
    assert (p.designer, p.model_name, p.manufacturer, p.category) == (
        "Yngve Ekström",
        "Lamino",
        "Swedese",
        "stolar_fatoljer",
    )
    assert p.n_sales == 5 and p.median_sek == 6500 and p.comp_ids == (1, 2, 3, 4, 10)


def _comp(i, designer="Yngve Ekström", model="Lamino", price=6000, title=None, **kw):
    return Comp(
        source="auctionet",
        external_id=str(i),
        designer=designer,
        model_name=model,
        hammer_sek=price,
        state="sold",
        title=title or f'{designer}. Fåtölj "{model}"',
        **kw,
    )


def test_refresh_watchlist_creates_once_and_links(session):
    session.add_all([_comp(i, price=p) for i, p in enumerate((5000, 6000, 7000))])
    session.add(_comp(9, model=None, title='YNGVE EKSTRÖM. Fåtölj "Lamino", Swedese', price=7500))
    owner = WatchModel(
        designer="Bruno Mathsson", model_name="Eva", identifying_features="egen text", active=True, auto_generated=False
    )
    session.add(owner)
    session.flush()
    assert refresh_watchlist(session) == (1, 0)
    assert refresh_watchlist(session) == (0, 1)
    m = session.scalar(select(WatchModel).where(WatchModel.model_name == "Lamino"))
    assert m.auto_generated and m.n_sales == 3 and m.median_sek == 6000
    assert link_comps(session) == 1
    assert session.scalar(select(Comp).where(Comp.external_id == "9")).model_id == m.id


# --- title batches and model notes -----------------------------------------------------------------


def test_apply_title_result_keeps_rule_fields():
    c = Comp(title="t", manufacturer="Dux")
    enrich.apply_title_result(
        c, json.dumps({"designer": "Folke Ohlsson", "manufacturer": "Annan", "model_name": " Tellus "})
    )
    assert (c.designer, c.manufacturer, c.model_name, c.parse_status) == ("Folke Ohlsson", "Dux", "Tellus", "llm")
    c2 = Comp(title="t")
    enrich.apply_title_result(c2, json.dumps({"designer": None, "manufacturer": "", "model_name": None}))
    assert c2.parse_status == "none"
    c3 = Comp(title="t")
    enrich.apply_title_result(c3, "not json")
    assert c3.parse_status == "llm_failed"


class FakeBatches:
    def __init__(self):
        self.created = []
        self.status = "in_progress"
        self.results_list = []

    def create(self, requests):
        self.created.append(requests)
        return SimpleNamespace(id=f"batch_{len(self.created)}")

    def retrieve(self, batch_id):
        return SimpleNamespace(processing_status=self.status)

    def results(self, batch_id):
        return iter(self.results_list)


def _ok(custom_id, payload):
    usage = SimpleNamespace(
        input_tokens=300, output_tokens=40, cache_read_input_tokens=0, cache_creation_input_tokens=0
    )
    msg = SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(payload))], usage=usage)
    return SimpleNamespace(custom_id=custom_id, result=SimpleNamespace(type="succeeded", message=msg))


def test_title_batch_submit_collect_and_cost(session, config):
    session.add_all(
        [Comp(source="auctionet", external_id=str(i), title=f"FÅTÖLJ {i}", state="sold") for i in range(60)]
    )
    session.add(Comp(source="auctionet", external_id="r", title="x", state="sold", parse_status="rules"))
    enqueue(session, "title_batch", run_at=NOW - timedelta(seconds=1))
    session.commit()
    fake = FakeBatches()
    ai = SimpleNamespace(messages=SimpleNamespace(batches=fake))
    deps = Deps(config=config, ai=ai, now=lambda: NOW)

    jobs.run_one(deps, {})
    session.expire_all()
    assert len(fake.created) == 1 and len(fake.created[0]) == 60
    req = fake.created[0][0]["params"]
    assert req["model"] == "claude-haiku-4-5" and req["output_config"]["format"]["type"] == "json_schema"
    assert session.scalar(select(AIBatch)).status == "submitted"
    nxt = session.scalar(select(Job).where(Job.kind == "title_batch", Job.status == "pending"))
    assert nxt.run_at.replace(tzinfo=UTC) == NOW + timedelta(minutes=30)

    first = session.scalar(select(Comp).where(Comp.external_id == "0"))
    fake.status = "ended"
    fake.results_list = [
        _ok(f"comp-{first.id}", {"designer": "Carl Malmsten", "manufacturer": None, "model_name": "Lilla Åland"}),
        SimpleNamespace(custom_id="comp-999999", result=SimpleNamespace(type="errored")),
    ]
    nxt.run_at = NOW - timedelta(seconds=1)
    session.commit()
    jobs.run_one(deps, {})
    session.expire_all()
    first = session.scalar(select(Comp).where(Comp.external_id == "0"))
    assert (first.designer, first.model_name, first.parse_status) == ("Carl Malmsten", "Lilla Åland", "llm")
    call = session.scalar(select(AICall).where(AICall.purpose == "comp_titles"))
    assert call.cost_usd == pytest.approx((300 * 1.0 + 40 * 5.0) / 1e6 * 0.5)
    assert session.scalar(select(AIBatch)).status == "collected"


def test_title_batch_respects_budget(session, config):
    session.add_all([Comp(source="auctionet", external_id=str(i), title="t", state="sold") for i in range(60)])
    session.add(AICall(purpose="x", model="m", cost_usd=1.99, created_at=NOW - timedelta(minutes=5)))
    enqueue(session, "title_batch", run_at=NOW - timedelta(seconds=1))
    session.commit()
    fake = FakeBatches()
    jobs.run_one(Deps(config=config, ai=SimpleNamespace(messages=SimpleNamespace(batches=fake)), now=lambda: NOW), {})
    assert fake.created == []  # 0.01 USD left buys < 50 titles


def test_upsert_does_not_clobber_llm_fields(session):
    c = CompData(
        external_id="7",
        title="SOFFA",
        state="sold",
        hammer_sek=900,
        estimate_sek=None,
        sold_at=None,
        auction_house=None,
        category=None,
        condition_text=None,
        condition=None,
        url=None,
    )
    upsert_comp(session, "auctionet", c)
    session.flush()
    row = session.scalar(select(Comp))
    row.designer, row.parse_status = "Arne Norell", "llm"
    upsert_comp(session, "auctionet", c)
    assert row.designer == "Arne Norell" and row.parse_status == "llm"


def test_apply_notes_never_overwrites_owner_text():
    m = WatchModel(identifying_features="ägarens text", aliases=["Ovalen"])
    notes = enrich.ModelNotes(
        identifying_features="AI",
        marks="Brännmärke under sits",
        replica_traps="Kopior",
        aliases=["Ovalen", " Oval "],
        confidence="medel",
    )
    enrich.apply_notes(m, notes, NOW)
    assert m.identifying_features == "ägarens text" and m.marks == "Brännmärke under sits"
    assert m.aliases == ["Oval", "Ovalen"] and m.notes_generated_at == NOW


# --- backfill -------------------------------------------------------------------------------------


class FakeAuctionet:
    def __init__(self, fail_on=None):
        self.calls, self.fail_on = [], fail_on

    def pages(self, start_page, count, **params):
        self.calls.append(params)
        if params == self.fail_on:
            raise SourceBlocked("403")
        yield start_page, [{"id": len(self.calls) * 1000, "title": "BORD", "state": "sold", "bids": []}], True


def test_backfill_walks_plan_one_step_per_run(session, config):
    plan = jobs.backfill_plan(["Mathsson"])
    assert plan[0] == {"category_id": 18} and plan[-1] == {"category_id": 16, "q": "Mathsson"} and len(plan) == 11
    enqueue(session, "auctionet_backfill", {"todo": plan[:2]}, run_at=NOW - timedelta(seconds=1))
    session.commit()
    client = FakeAuctionet()
    clock = [NOW]
    deps = Deps(config=config, now=lambda: clock[0])
    for _ in range(4):
        jobs.run_one(deps, {"auctionet": client})
        clock[0] += timedelta(minutes=1)
    assert client.calls == plan[:2]
    assert len(list(session.scalars(select(Comp)))) == 2


def test_backfill_blocked_keeps_step(session, config):
    enqueue(session, "auctionet_backfill", {"todo": [{"category_id": 18}]}, run_at=NOW - timedelta(seconds=1))
    session.commit()
    jobs.run_one(Deps(config=config, now=lambda: NOW), {"auctionet": FakeAuctionet(fail_on={"category_id": 18})})
    session.expire_all()
    assert session.get(SourceHealth, "auctionet").stopped_reason == "403"
    nxt = session.scalar(select(Job).where(Job.kind == "auctionet_backfill", Job.status == "pending"))
    assert nxt.payload == {"todo": [{"category_id": 18}]}


def test_next_local_weekday():
    t = jobs.next_local_weekday(NOW, "Europe/Stockholm", 6, 5)  # NOW is Saturday 2026-10-10
    assert t == datetime(2026, 10, 11, 3, 0, tzinfo=UTC)


# --- images ---------------------------------------------------------------------------------------


def _png(w, h):
    buf = io.BytesIO()
    Image.new("RGBA", (w, h), (200, 100, 50, 255)).save(buf, "PNG")
    return buf.getvalue()


def test_resize_jpeg_fits_box():
    out = resize_jpeg(_png(1200, 1600), 512)
    with Image.open(io.BytesIO(out)) as im:
        assert im.format == "JPEG" and max(im.size) == 512 and im.size == (384, 512)


def test_image_loader_caches_and_skips_broken(tmp_path):
    import httpx

    hits = []

    def handler(req):
        hits.append(str(req.url))
        if "broken" in str(req.url):
            return httpx.Response(200, content=b"not an image")
        return httpx.Response(200, content=_png(800, 600))

    loader = ImageLoader(tmp_path, "ua", http=httpx.Client(transport=httpx.MockTransport(handler)))
    blocks = loader.blocks(["https://x.test/a.jpg", "https://x.test/broken.jpg", "https://x.test/c.jpg"], 784, 2)
    assert len(blocks) == 1 and blocks[0]["source"]["media_type"] == "image/jpeg"
    loader.blocks(["https://x.test/a.jpg"], 512, 1)
    assert hits.count("https://x.test/a.jpg") == 1


def test_purge_old(tmp_path):
    old, new = tmp_path / "a.img", tmp_path / "b.img"
    old.write_bytes(b"x")
    new.write_bytes(b"y")
    now = 1_000_000_000.0
    os.utime(old, (now - 8 * 86400, now - 8 * 86400))
    os.utime(new, (now - 86400, now - 86400))
    assert purge_old(tmp_path, now) == 1 and not old.exists() and new.exists()


# --- eval summary ---------------------------------------------------------------------------------


def test_eval_summarize():
    def o(kind, true, pred, source="comp"):
        return Outcome(Case(kind, source, 1, "t", None, None, [], true), pred, None, False, 0.01, 1.0)

    s = summarize(
        [
            o("positive", 1, 1),
            o("positive", 2, None),
            o("positive", 3, 9),
            o("negative", None, 4, "feedback:replika"),
            o("negative", None, None),
        ]
    )
    assert s["true_positive"] == 1 and s["wrong_model"] == 1
    assert s["precision"] == round(1 / 3, 3) and s["recall"] == round(1 / 3, 3)
    assert s["false_positives_by_source"] == {"feedback:replika": 1}
    assert s["cost_usd"] == 0.05


def test_backfill_continues_a_long_step_in_page_chunks(session, config):
    class Paged:
        def __init__(self):
            self.starts = []

        def pages(self, start_page, count, **params):
            self.starts.append(start_page)
            for p in range(start_page, min(start_page + count, 26)):
                yield p, [{"id": p, "title": "BORD", "state": "sold", "bids": []}], p == 25

    enqueue(session, "auctionet_backfill", {"todo": [{"category_id": 18}]}, run_at=NOW - timedelta(seconds=1))
    session.commit()
    client, clock = Paged(), [NOW]
    deps = Deps(config=config, now=lambda: clock[0])
    for _ in range(4):
        jobs.run_one(deps, {"auctionet": client})
        clock[0] += timedelta(minutes=1)
    assert client.starts == [1, 11, 21]
    assert len(list(session.scalars(select(Comp)))) == 25
    assert session.scalar(select(Job).where(Job.kind == "auctionet_backfill", Job.status == "pending")) is None
