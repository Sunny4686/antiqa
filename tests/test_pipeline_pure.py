import math

import pytest

from fyndjakt.pipeline import decide as dec
from fyndjakt.pipeline.candidates import ModelRef, select_candidates
from fyndjakt.pipeline.geo import haversine_km, load_municipalities, locate, transport_sek
from fyndjakt.pipeline.margin import margin
from fyndjakt.pipeline.prefilter import normalize, prefilter, watch_terms
from fyndjakt.pipeline.valuation import CompPrice, quantile, value

WATCH = [
    watch_terms(1, "Bruno Mathsson", "Karl Mathsson", "Eva", ["Mathsson Eva"]),
    watch_terms(2, "Yngve Ekström", "Swedese", "Lamino", []),
]


# --- prefilter -------------------------------------------------------------------------------------


def test_normalize_keeps_swedish_letters_and_strips_other_accents():
    assert normalize("  Fåtölj  à la  Børge ") == "fåtölj a la børge"
    assert normalize("Café") == "cafe"


def test_prefilter_skips_only_on_price():
    r = prefilter("Fin fåtölj", None, 40000, 30000, WATCH)
    assert not r.passed and "40000" in r.reason
    assert prefilter("Pinnstol", None, None, 30000, WATCH).passed  # unknown price is kept


def test_prefilter_signals_and_watch_matches():
    r = prefilter("Lamino fåtölj, stämplad", "Från dödsbo, teak", 800, 30000, WATCH)
    assert r.passed and r.matched_model_ids == [2]
    assert {"stämplad", "dödsbo", "teak"} <= set(r.plus_signals)
    assert not r.replica_flag


@pytest.mark.parametrize(
    "text",
    [
        "Replika av Lamino",
        "Fåtölj i stil med Lamino",
        "Mathsson-stil stol",
        "Stol à la Mathsson",
        "inspirerad av Eames",
    ],
)
def test_prefilter_replica_flag(text):
    assert prefilter(text, None, 500, 30000, WATCH).replica_flag


def test_prefilter_word_boundaries():
    # "Eva" must not match inside "Evakuering"; designer surname still matches
    r = prefilter("Evakueringsstol", None, 100, 30000, WATCH)
    assert r.matched_model_ids == []


# --- candidates -----------------------------------------------------------------------------------

MODELS = [
    ModelRef(1, "Bruno Mathsson", "Karl Mathsson", "Eva"),
    ModelRef(2, "Yngve Ekström", "Swedese", "Lamino"),
    ModelRef(3, "Bruno Mathsson", "Dux", "Jetson"),
]


def test_candidates_rank_model_guess_over_designer():
    out = select_candidates(MODELS, [], "Bruno Mathsson", None, "Jetson")
    assert [m.id for m in out] == [3, 1]


def test_candidates_limit_and_empty():
    assert [m.id for m in select_candidates(MODELS, [1, 2, 3], None, None, None, limit=2)] == [1, 2]
    assert select_candidates(MODELS, [], None, None, None) == []


# --- valuation ------------------------------------------------------------------------------------


def test_quantile_interpolates():
    assert quantile([1, 2, 3, 4], 0.5) == 2.5
    assert quantile([10], 0.25) == 10


def test_value_model_level_normalises_condition():
    comps = [CompPrice(p, "utmärkt") for p in (4000, 5000, 6000, 7000, 8000)]
    v = value(comps, [], "utmärkt")
    assert (v.p25, v.median, v.p75, v.n, v.level) == (5000, 6000, 7000, 5, "model")
    worn = value(comps, [], "slitet")
    assert worn.median == round(6000 * 0.7)


def test_value_comp_condition_is_normalised_up():
    v = value([CompPrice(850, "gott")] * 5, [], "utmärkt")
    assert v.median == 1000


def test_value_shrinks_thin_model_towards_prior():
    model = [CompPrice(10000, "utmärkt")]
    prior = [CompPrice(p, "utmärkt") for p in (2000, 2000, 2000)]
    v = value(model, prior, "utmärkt")
    expected = math.exp((1 * math.log(10000) + 3 * math.log(2000)) / 4)
    assert v.level == "designer_category" and v.n == 1
    assert v.median == round(expected)


def test_value_thin_without_prior_stays_model_level_and_none_when_empty():
    assert value([CompPrice(3000)], [], None).level == "model"
    assert value([], [CompPrice(3000)], None) == value([], [], None)
    assert value([], [], None).level == "none"


# --- geo + margin ---------------------------------------------------------------------------------


def test_haversine_stockholm_goteborg():
    assert haversine_km(59.3293, 18.0686, 57.7089, 11.9746) == pytest.approx(398, abs=5)


def test_transport_is_round_trip():
    assert transport_sek(100, 300, 3.0) == 900


def test_locate_prefers_coordinates_and_falls_back_to_municipality(tmp_path):
    csv = tmp_path / "k.csv"
    csv.write_text("kommun,lat,lon,lan\nLidingö,59.36,18.15,Stockholms län\n", encoding="utf-8")
    muni = load_municipalities(csv)
    assert locate(None, None, "Lidingö kommun", muni) == (59.36, 18.15, "Stockholms län")
    assert locate(59.0, 18.0, "Lidingö", muni) == (59.0, 18.0, "Stockholms län")
    assert locate(None, None, "Okänd", muni) is None
    assert load_municipalities(tmp_path / "missing.csv") == {}


def test_margin():
    m = margin(p25_sek=10000, price_sek=2000, transport_sek=900, net_ratio=0.78, fixed_fees_sek=500)
    assert m.net_sek == 7800 - 500 - 900 - 2000
    assert m.roi == pytest.approx(4400 / 2000)
    assert margin(1000, 0, 0, 0.78, 0).roi is None


# --- escalation, confidence, decision -------------------------------------------------------------

T = dec.Thresholds(min_net_margin_sek=1500, min_roi=0.5, max_distance_km=150, allowed_regions=("Hallands län",))


def _d(**kw):
    base = dict(
        net_sek=3000,
        roi=1.0,
        distance_km=50,
        region=None,
        confidence="medel",
        value_level="model",
        watched_candidate=True,
        upside_net_sek=5000,
    )
    return dec.DecisionInput(**(base | kw))


def test_should_escalate():
    assert dec.should_escalate("yes", 3000, 1500)
    assert dec.should_escalate("uncertain", 3000, 1500)
    assert not dec.should_escalate("yes", 2999, 1500)
    assert not dec.should_escalate("no", 10000, 1500)
    assert not dec.should_escalate("yes", None, 1500)


def test_combine_confidence_caps():
    assert dec.combine_confidence("hög", "yes", "model", False) == "hög"
    assert dec.combine_confidence("hög", "uncertain", "model", False) == "medel"
    assert dec.combine_confidence("hög", "yes", "designer_category", False) == "medel"
    assert dec.combine_confidence("hög", "yes", "model", True) == "låg"
    assert dec.combine_confidence("hög", "yes", "none", False) == "låg"
    assert dec.combine_confidence("hög", "yes", "model", False, strong_disagrees=True) == "låg"
    assert dec.combine_confidence("hög", "no", "model", False) == "låg"


def test_decide_fynd_and_its_gates():
    assert dec.decide(_d(), T) == dec.FYND
    assert dec.decide(_d(net_sek=1499), T) != dec.FYND
    assert dec.decide(_d(roi=0.49), T) != dec.FYND
    assert dec.decide(_d(confidence="låg"), T) != dec.FYND
    assert dec.decide(_d(distance_km=400), T) != dec.FYND
    assert dec.decide(_d(distance_km=400, region="Hallands län"), T) == dec.FYND
    assert dec.decide(_d(distance_km=None), T) != dec.FYND


def test_decide_kolla_sjalv():
    assert dec.decide(_d(confidence="låg"), T) == dec.KOLLA_SJALV
    assert dec.decide(_d(net_sek=None, roi=None, value_level="none", upside_net_sek=None), T) == dec.KOLLA_SJALV
    assert dec.decide(_d(confidence="låg", upside_net_sek=1000), T) == dec.INGET
    assert dec.decide(_d(confidence="låg", watched_candidate=False), T) == dec.INGET


@pytest.mark.parametrize(("hour", "quiet"), [(23, True), (3, True), (7, False), (12, False), (22, True)])
def test_quiet_hours_wrap_midnight(hour, quiet):
    assert dec.in_quiet_hours(hour, 22, 7) is quiet
