import sqlite3
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from fyndjakt import stats
from fyndjakt.backup import backup_sqlite
from fyndjakt.db import session_scope
from fyndjakt.models import Comp, Deal, WatchModel


@pytest.fixture
def client(env):
    from fyndjakt.web.app import create_app

    with TestClient(create_app(run_worker=False)) as c:
        yield c


def test_watchlist_create_edit_and_csv_roundtrip(client):
    r = client.post(
        "/bevakningslista/0",
        data={
            "designer": "Alf Svensson",
            "model_name": "Kontur",
            "aliases": "Kontur fåtölj, Fritz Hansen Kontur",
            "active": "on",
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    mid = int(r.headers["location"].rsplit("/", 1)[1])
    page = client.get(f"/bevakningslista/{mid}")
    assert page.status_code == 200 and "Kontur fåtölj" in page.text
    assert client.get("/bevakningslista/999999").status_code == 404

    csv_text = client.get("/bevakningslista/export.csv").text
    assert csv_text.splitlines()[0].startswith("id,designer")
    assert f"{mid},Alf Svensson" in csv_text and "Kontur fåtölj|Fritz Hansen Kontur" in csv_text

    edited = csv_text.replace("Alf Svensson", "Alf Svensson (Dux)") + ",Nils Jonsson,,Kurva,,,,,,,1\n"
    r = client.post(
        "/bevakningslista/import", files={"file": ("w.csv", edited.encode(), "text/csv")}, follow_redirects=False
    )
    assert r.status_code == 303
    with session_scope() as s:
        names = sorted(m.designer for m in s.scalars(select(WatchModel)))
        assert names == ["Alf Svensson (Dux)", "Nils Jonsson"]
        assert s.get(WatchModel, mid).aliases == ["Kontur fåtölj", "Fritz Hansen Kontur"]
    assert "Nils Jonsson" in client.get("/bevakningslista").text


def test_sold_deal_becomes_own_sale_comp(client):
    with session_scope() as s:
        m = WatchModel(designer="Yngve Ekström", model_name="Lamino", active=True, aliases=[])
        s.add(m)
        s.flush()
        mid = m.id
    r = client.post(
        "/affarer",
        data={
            "title": "Lamino ek",
            "purchase_sek": "800",
            "costs_sek": "300",
            "sale_sek": "6500",
            "fees_sek": "1300",
            "hours": "4",
            "bought_at": "2026-09-01",
            "sold_at": "2026-10-01",
            "model_id": str(mid),
        },
        follow_redirects=False,
    )
    assert r.status_code == 303
    page = client.get("/affarer").text
    assert "Lamino ek" in page and "4100" in page and "1025" in page  # net and kr/h
    with session_scope() as s:
        deal = s.scalar(select(Deal))
        comp = s.scalar(select(Comp).where(Comp.source == "own_sale"))
        assert comp.external_id == str(deal.id) and comp.hammer_sek == 6500 and comp.model_id == mid
        assert comp.designer == "Yngve Ekström"
    # Editing the deal updates the same comp instead of adding a second one
    client.post("/affarer", data={"deal_id": "1", "title": "Lamino ek", "sale_sek": "7000", "sold_at": "2026-10-02"})
    with session_scope() as s:
        comps = list(s.scalars(select(Comp).where(Comp.source == "own_sale")))
        assert len(comps) == 1 and comps[0].hammer_sek == 7000


def test_comps_and_statistik_render(client):
    with session_scope() as s:
        s.add(
            Comp(
                source="auctionet",
                external_id="1",
                title='BRUNO MATHSSON. Fåtölj "Eva"',
                designer="Bruno Mathsson",
                model_name="Eva",
                hammer_sek=4000,
                state="sold",
                sold_at=datetime(2026, 9, 1, tzinfo=UTC),
            )
        )
    assert "Bruno Mathsson" in client.get("/comps?q=mathsson").text
    assert "Bruno Mathsson" not in client.get("/comps?q=malmsten").text.split("<table>")[1]
    page = client.get("/statistik")
    assert page.status_code == 200 and "Källhälsa" in page.text


# --- pure statistics ------------------------------------------------------------------------------

T0 = datetime(2026, 10, 5, 12, tzinfo=UTC)


def _a(lid, decision, minutes_after=5, published=True):
    return stats.AlertRow(
        lid, decision, T0 + timedelta(minutes=minutes_after), T0 if published else None, T0 + timedelta(minutes=1)
    )


def test_alerts_per_week_and_latency():
    alerts = [_a(1, "FYND", 4), _a(2, "KOLLA_SJALV", 10), _a(3, "INGET", 1), _a(4, "FYND", 6, published=False)]
    assert stats.alerts_per_week(alerts) == {"2026-v41": {"FYND": 2, "KOLLA_SJALV": 1}}
    assert stats.latency_minutes(alerts) == 5.0  # median of 4, 10 and 5 (from first seen)


def test_precision_counts_only_rated_fynd():
    alerts = [_a(1, "FYND"), _a(2, "FYND"), _a(3, "FYND"), _a(4, "KOLLA_SJALV")]
    fb = {1: "köpt", 2: "replika", 4: "köpt"}
    assert stats.precision(alerts, fb) == (0.5, 2)
    assert stats.precision([], {}) == (None, 0)


def test_profit_per_month():
    deals = [
        stats.DealRow(datetime(2026, 10, 1, tzinfo=UTC), 6500, 800, 300, 1300),
        stats.DealRow(datetime(2026, 10, 20, tzinfo=UTC), 2000, 1500, 0, 400),
        stats.DealRow(None, None, 900, 0, 0),
    ]
    assert stats.profit_per_month(deals) == {"2026-10": 4100 + 100}


def test_backup_keeps_newest(tmp_path):
    db = tmp_path / "live.db"
    con = sqlite3.connect(db)
    con.execute("create table t(x)")
    con.execute("insert into t values (1)")
    con.commit()
    con.close()
    for d in range(16):
        backup_sqlite(db, tmp_path / "bk", datetime(2026, 10, 1, tzinfo=UTC) + timedelta(days=d), keep=14)
    files = sorted((tmp_path / "bk").glob("*.db"))
    assert len(files) == 14 and files[0].name == "fyndjakt-20261003-0000.db"
    assert sqlite3.connect(files[-1]).execute("select x from t").fetchone() == (1,)
