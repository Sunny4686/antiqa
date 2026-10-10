from datetime import UTC, datetime, timedelta

import pytest

from fyndjakt.ai.budget import cost_usd, spent_today
from fyndjakt.models import AICall
from fyndjakt.notify.telegram import AlertData, format_alert, keyboard, parse_callback

PRICES = {"claude-haiku-4-5": (1.0, 5.0), "claude-sonnet-5-5": (2.0, 10.0)}


def _alert(**kw):
    base = dict(
        listing_id=7,
        kind="FYND",
        title="Lamino <fåtölj>",
        url="https://example.test/7",
        price_sek=800,
        p25=6000,
        median=7500,
        p75=9000,
        n_comps=12,
        net_sek=3180,
        roi=3.975,
        distance_km=42.4,
        municipality="Kungsbacka",
        confidence="medel",
        candidate='Yngve Ekström – "Lamino"',
        evidence=["Tygklädd sits", "Etikett Swedese", "tredje"],
        contradictions=["Ny klädsel"],
        needs_underside_photo=True,
    )
    return AlertData(**(base | kw))


def test_format_alert_contents_and_escaping():
    text = format_alert(_alert())
    assert "🔥 <b>FYND</b>: Lamino &lt;fåtölj&gt;" in text
    assert "Värde: 6 000 kr–9 000 kr (median 7 500 kr), n=12" in text
    assert "Netto: 3 180 kr, ROI 398%" in text
    assert "Avstånd: 42 km, Kungsbacka" in text
    assert text.count("✓") == 2 and "✗ Ny klädsel" in text
    assert "Be om foto av undersidan" in text


def test_format_alert_without_value():
    text = format_alert(
        _alert(
            kind="KOLLA_SJALV",
            p25=None,
            median=None,
            p75=None,
            net_sek=None,
            roi=None,
            distance_km=None,
            municipality=None,
            needs_underside_photo=False,
        )
    )
    assert text.startswith("👀 <b>Kolla själv</b>")
    assert "inga jämförelseobjekt" in text and "okänd ort" in text and "Netto" not in text


def test_keyboard_and_callback_roundtrip():
    kb = keyboard(7, "https://example.test/7")["inline_keyboard"]
    assert kb[0][0] == {"text": "Öppna annons", "url": "https://example.test/7"}
    datas = [b["callback_data"] for row in kb[1:] for b in row]
    assert len(datas) == 5 and all(len(d.encode()) <= 64 for d in datas)  # Telegram limit
    assert {parse_callback(d) for d in datas} == {
        (7, k) for k in ("köpt", "ej_intressant", "fel_modell", "replika", "bra_men_såld")
    }
    assert parse_callback("fb:x:köpt") is None and parse_callback("noop") is None
    assert parse_callback("fb:7:hackad") is None


def test_cost_usd():
    assert cost_usd(PRICES, "claude-haiku-4-5", 1_000_000, 0) == pytest.approx(1.0)
    assert cost_usd(PRICES, "claude-sonnet-5-5", 0, 100_000) == pytest.approx(1.0)
    assert cost_usd(PRICES, "claude-haiku-4-5", 0, 0, cache_read=1_000_000) == pytest.approx(0.1)


def test_spent_today_uses_local_day(session):
    # 2026-10-10 00:30 Stockholm = 2026-10-09 22:30 UTC
    now = datetime(2026, 10, 10, 10, 0, tzinfo=UTC)
    session.add_all(
        [
            AICall(purpose="screen", model="m", cost_usd=0.5, created_at=datetime(2026, 10, 9, 22, 30, tzinfo=UTC)),
            AICall(purpose="screen", model="m", cost_usd=0.25, created_at=datetime(2026, 10, 9, 21, 30, tzinfo=UTC)),
            AICall(purpose="screen", model="m", cost_usd=1.0, created_at=now - timedelta(hours=1)),
        ]
    )
    session.flush()
    assert spent_today(session, now, "Europe/Stockholm") == pytest.approx(1.5)
