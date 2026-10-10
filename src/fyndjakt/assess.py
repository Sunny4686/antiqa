"""Runs the assessment pipeline (steps 1-9) for one listing and sends the alert."""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import anthropic
from sqlalchemy import select
from sqlalchemy.orm import Session

from fyndjakt.ai import budget
from fyndjakt.ai.steps import CandidateSpec, Usage, Verification, screen, verify
from fyndjakt.config import Config
from fyndjakt.images import LOCAL_PREFIX, ImageLoader, usable_urls
from fyndjakt.models import AICall, Assessment, Listing, TelegramMessage, WatchModel
from fyndjakt.notify.telegram import AlertData, TelegramClient, format_alert, keyboard
from fyndjakt.pipeline import candidates as cand
from fyndjakt.pipeline import decide as dec
from fyndjakt.pipeline import geo
from fyndjakt.pipeline.margin import margin
from fyndjakt.pipeline.prefilter import prefilter, watch_terms
from fyndjakt.pipeline.valuation import value
from fyndjakt.services import comps_for_model, enqueue, get_settings, health_row, prior_comps

log = logging.getLogger(__name__)


@dataclass
class Deps:
    config: Config
    ai: anthropic.Anthropic | None = None
    telegram: TelegramClient | None = None
    images: ImageLoader | None = None
    municipalities: dict = field(default_factory=dict)
    now: Callable[[], datetime] = lambda: datetime.now(UTC)
    screen_fn: Callable = screen
    verify_fn: Callable = verify


def remote_images_allowed(source: str, cfg: Config) -> bool:
    """Auctionet's image CDN is part of its open API; other sites' images need ai_send_listing_images."""
    return source == "auctionet_live" or cfg.ai_send_listing_images


def model_label(m: WatchModel) -> str:
    return " – ".join(p for p in (m.designer, m.model_name and f'"{m.model_name}"', m.manufacturer) if p)


def notify_owner(session: Session, deps: Deps, key: str, text: str) -> None:
    """Owner alert, sent once per key until the key is reset (dedupe via source_health.alerted)."""
    row = health_row(session, key)
    if row.alerted:
        return
    row.alerted = True
    if deps.telegram and deps.config.telegram_chat_id:
        try:
            deps.telegram.send_text(deps.config.telegram_chat_id, text)
        except Exception:  # alerts must never break the pipeline
            log.exception("owner alert failed")


class _Spend:
    def __init__(self, session: Session, deps: Deps, daily_budget: float):
        self.session, self.deps, self.daily = session, deps, daily_budget
        self.tokens_in = self.tokens_out = 0
        self.cost = 0.0
        self.models: list[str] = []

    def can_spend(self) -> bool:
        if self.deps.ai is None:
            return False
        left = budget.budget_left(self.session, self.deps.now(), self.deps.config.timezone, self.daily)
        if left > 0:
            # Release the write lock before the network call; also keeps finished steps if a later one fails.
            self.session.commit()
            return True
        day = self.deps.now().astimezone(ZoneInfo(self.deps.config.timezone)).date().isoformat()
        notify_owner(
            self.session,
            self.deps,
            f"ai_budget:{day}",
            f"AI-budgeten ({self.daily} USD/dag) är slut. Bara förfiltret körs till midnatt.",
        )
        return False

    def log(self, purpose: str, u: Usage) -> None:
        c = budget.cost_usd(
            self.deps.config.model_prices, u.model, u.tokens_in, u.tokens_out, u.cache_read, u.cache_write
        )
        self.session.add(
            AICall(
                purpose=purpose,
                model=u.model,
                tokens_in=u.tokens_in,
                tokens_out=u.tokens_out,
                cache_read_tokens=u.cache_read,
                cache_write_tokens=u.cache_write,
                cost_usd=c,
            )
        )
        self.session.commit()  # the money is spent even if a later step fails and the job is retried
        self.tokens_in += u.tokens_in + u.cache_read + u.cache_write
        self.tokens_out += u.tokens_out
        self.cost += c
        self.models.append(u.model)


def assess_listing(session: Session, listing_id: int, deps: Deps) -> Assessment:
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise ValueError(f"listing {listing_id} not found")
    s = get_settings(session)
    cfg = deps.config
    models = list(session.scalars(select(WatchModel).where(WatchModel.active.is_(True))))
    by_id = {m.id: m for m in models}

    # 1. Prefilter
    pf = prefilter(
        listing.title,
        listing.description,
        listing.price_sek,
        s.max_listing_price_sek,
        [watch_terms(m.id, m.designer, m.manufacturer, m.model_name, m.aliases) for m in models],
    )
    session.add(
        Assessment(
            listing_id=listing.id,
            stage="prefilter",
            replica_signals=pf.replica_signals,
            note=pf.reason or ", ".join(pf.plus_signals) or None,
            raw={"matched_model_ids": pf.matched_model_ids},
        )
    )
    if not pf.passed:
        listing.status = "skipped"
        return _final(session, listing, decision=dec.INGET, note=pf.reason)

    spend = _Spend(session, deps, s.daily_ai_budget_usd)
    image_urls = usable_urls(listing.image_urls, remote_images_allowed(listing.source, cfg))
    use_images = deps.images is not None and bool(image_urls)

    def imgs(max_px: int, limit: int) -> list[dict]:
        if not use_images:
            return []
        out = deps.images.blocks(image_urls, max_px, limit)
        while deps.images.blocked_events:
            e = deps.images.blocked_events.pop()
            notify_owner(
                session,
                deps,
                f"images:{e.host}",
                f"Bildhämtning blockerad: {e.host} ({e.reason}). Pausad 6 h, inget kringgående.",
            )
        return out

    # A price change doesn't change what the object is: reuse the earlier verification instead of paying again.
    reused = _reusable_verdict(session, listing.id, by_id)
    strong: Verification | None = None
    if reused is not None:
        ver, strong, disagree = reused
        model = by_id[ver.candidate_id]
        picked_ids = {model.id}
        specs = [
            CandidateSpec(model.id, model_label(model), model.identifying_features, model.replica_traps, model.marks)
        ]
    else:
        # 2. Screening
        if not spend.can_spend():
            listing.status = "assessed"
            return _final(session, listing, decision=dec.INGET, note="AI hoppades över (budget eller saknad nyckel)")
        scr, usage = deps.screen_fn(deps.ai, cfg.model_fast, listing.title, listing.price_sek, imgs(512, 1))
        spend.log("screen", usage)
        session.add(
            Assessment(
                listing_id=listing.id,
                stage="screen",
                confidence=scr.confidence,
                note=scr.reason,
                llm_model=usage.model,
                raw=scr.model_dump(),
            )
        )

        # 3. Candidates
        refs = [cand.ModelRef(m.id, m.designer, m.manufacturer, m.model_name, tuple(m.aliases or [])) for m in models]
        picked = cand.select_candidates(refs, pf.matched_model_ids, scr.designer, scr.manufacturer, scr.model_name)
        if not picked:
            listing.status = "assessed"
            return _final(
                session,
                listing,
                decision=dec.INGET,
                spend=spend,
                note="Ingen kandidat i bevakningslistan" + (" (möjlig design)" if scr.is_collectible_design else ""),
            )

        specs = [
            CandidateSpec(
                r.id,
                model_label(by_id[r.id]),
                by_id[r.id].identifying_features,
                by_id[r.id].replica_traps,
                by_id[r.id].marks,
            )
            for r in picked
        ]

        # 4. Verification (fast)
        if not spend.can_spend():
            listing.status = "assessed"
            return _final(session, listing, decision=dec.INGET, spend=spend, note="AI-budget slut före verifiering")
        ver, usage = deps.verify_fn(
            deps.ai, cfg.model_fast, listing.title, listing.description, listing.price_sek, imgs(784, 4), specs
        )
        spend.log("verify", usage)
        picked_ids = {r.id for r in picked}
        session.add(
            Assessment(
                listing_id=listing.id,
                stage="verify",
                model_candidate_id=_known(ver.candidate_id, picked_ids),
                match=ver.match,
                confidence=ver.confidence,
                llm_model=usage.model,
                raw=ver.model_dump(),
            )
        )
        model = by_id.get(ver.candidate_id) if ver.candidate_id in picked_ids else None

    # 5-7. Value, geography, margin
    where = geo.locate(listing.lat, listing.lon, listing.municipality, deps.municipalities)
    distance = geo.haversine_km(s.home_lat, s.home_lon, where[0], where[1]) if where else None
    region = where[2] if where else None
    transport = (
        geo.transport_sek(distance, s.transport_base_sek, s.transport_sek_per_km) if distance is not None else None
    )

    def priced(condition_guess: str):  # noqa: ANN202
        condition = None if condition_guess == "okänt" else condition_guess
        v = (
            value(comps_for_model(session, model), prior_comps(session, model), condition)
            if model
            else value([], [], None)
        )
        lo = hi = None
        if v.p25 is not None and listing.price_sek is not None:
            t = transport if transport is not None else s.transport_base_sek
            lo = margin(v.p25, listing.price_sek, t, s.net_ratio, s.fixed_fees_sek)
            hi = margin(v.p75, listing.price_sek, t, s.net_ratio, s.fixed_fees_sek)
        return v, lo, hi

    val, m25, m75 = priced(ver.condition_guess)

    # 8. Escalation to the strong model (once per listing)
    final_ver = ver
    if reused is None:
        disagree = False
    escalate = strong is None and dec.should_escalate(ver.match, m25.net_sek if m25 else None, s.min_net_margin_sek)
    if escalate and spend.can_spend():
        strong, usage = deps.verify_fn(
            deps.ai, cfg.model_strong, listing.title, listing.description, listing.price_sek, imgs(784, 4), specs
        )
        spend.log("verify_strong", usage)
        session.add(
            Assessment(
                listing_id=listing.id,
                stage="verify_strong",
                model_candidate_id=_known(strong.candidate_id, picked_ids),
                match=strong.match,
                confidence=strong.confidence,
                llm_model=usage.model,
                raw=strong.model_dump(),
            )
        )
        disagree = strong.candidate_id != ver.candidate_id or strong.match == "no"
    if strong is not None and not disagree:
        final_ver = strong
        if strong.condition_guess != ver.condition_guess:
            val, m25, m75 = priced(strong.condition_guess)  # the decision uses the strong model's condition

    replica = pf.replica_flag or bool(final_ver.replica_signals)
    confidence = dec.combine_confidence(final_ver.confidence, final_ver.match, val.level, replica, disagree, val.n)

    # 9. Decision
    decision = dec.decide(
        dec.DecisionInput(
            m25.net_sek if m25 else None,
            m25.roi if m25 else None,
            distance,
            region,
            confidence,
            val.level,
            model is not None,
            m75.net_sek if m75 else None,
        ),
        dec.Thresholds(s.min_net_margin_sek, s.min_roi, s.max_distance_km, tuple(s.allowed_regions or [])),
    )
    final = _final(
        session,
        listing,
        decision=decision,
        spend=spend,
        model=model,
        ver=final_ver,
        val=val,
        transport=transport,
        m25=m25,
        distance=distance,
        confidence=confidence,
        replica=replica,
    )
    listing.status = "assessed"
    _maybe_notify(session, deps, s, listing, final, model)
    return final


def _reusable_verdict(
    session: Session, listing_id: int, by_id: dict[int, WatchModel]
) -> tuple[Verification, Verification | None, bool] | None:
    """(fast verdict, strong verdict, disagree) from an earlier run, if it pointed at a still-active model."""
    rows = list(
        session.scalars(
            select(Assessment)
            .where(Assessment.listing_id == listing_id, Assessment.stage.in_(("verify", "verify_strong")))
            .order_by(Assessment.id.desc())
        )
    )
    fast = next((r for r in rows if r.stage == "verify"), None)
    if fast is None or not fast.raw:
        return None
    ver = Verification(**fast.raw)
    if ver.candidate_id not in by_id or fast.model_candidate_id != ver.candidate_id:
        return None
    strong_row = next((r for r in rows if r.stage == "verify_strong" and r.id > fast.id), None)
    strong = Verification(**strong_row.raw) if strong_row and strong_row.raw else None
    disagree = strong is not None and (strong.candidate_id != ver.candidate_id or strong.match == "no")
    return ver, strong, disagree


def _known(candidate_id: int | None, allowed: set[int]) -> int | None:
    """The model may answer with an id outside the candidate list; treat that as no candidate."""
    return candidate_id if candidate_id in allowed else None


def _final(
    session: Session,
    listing: Listing,
    decision: str,
    note: str | None = None,
    spend: _Spend | None = None,
    model: WatchModel | None = None,
    ver=None,
    val=None,
    transport=None,
    m25=None,
    distance=None,  # noqa: ANN001
    confidence: str | None = None,
    replica: bool = False,
) -> Assessment:
    a = Assessment(
        listing_id=listing.id,
        stage="final",
        decision=decision,
        note=note,
        model_candidate_id=model.id if model else None,
        match=ver.match if ver else None,
        evidence=ver.evidence if ver else [],
        contradictions=ver.contradictions if ver else [],
        replica_signals=ver.replica_signals if ver else [],
        label_ocr=ver.label_ocr if ver else None,
        condition_guess=ver.condition_guess if ver else None,
        needs_underside_photo=ver.needs_underside_photo if ver else False,
        value_p25=val.p25 if val else None,
        value_median=val.median if val else None,
        value_p75=val.p75 if val else None,
        n_comps=val.n if val else 0,
        value_level=val.level if val else None,
        transport_sek=transport,
        net_margin_sek=m25.net_sek if m25 else None,
        roi=m25.roi if m25 else None,
        distance_km=round(distance, 1) if distance is not None else None,
        confidence=confidence,
        llm_model=",".join(dict.fromkeys(spend.models)) if spend and spend.models else None,
        tokens_in=spend.tokens_in if spend else 0,
        tokens_out=spend.tokens_out if spend else 0,
        cost_usd=round(spend.cost, 6) if spend else 0.0,
        raw={"replica_flag": replica},
    )
    session.add(a)
    session.flush()
    return a


def _maybe_notify(
    session: Session,
    deps: Deps,
    s,
    listing: Listing,
    a: Assessment,  # noqa: ANN001
    model: WatchModel | None,
) -> None:
    if a.decision == dec.INGET or not (deps.telegram and deps.config.telegram_chat_id):
        return
    hour = deps.now().astimezone(ZoneInfo(deps.config.timezone)).hour
    if a.decision == dec.KOLLA_SJALV and dec.in_quiet_hours(hour, s.quiet_hours_start, s.quiet_hours_end):
        return  # stays in the inbox; quiet hours never hold back a FYND
    try:
        send_alert_for(session, deps, a.id)
    except Exception as e:
        # A lost FYND is the worst failure: retry delivery as its own job, without re-running the AI steps.
        log.warning("telegram alert failed for listing %s, retrying as a job: %s", listing.id, e)
        enqueue(session, "send_alert", {"assessment_id": a.id}, run_at=deps.now() + timedelta(minutes=1))


def send_alert_for(session: Session, deps: Deps, assessment_id: int) -> None:
    """Send the Telegram alert for a final assessment (once). Raises when Telegram fails."""
    a = session.get(Assessment, assessment_id)
    listing = session.get(Listing, a.listing_id)
    if not (deps.telegram and deps.config.telegram_chat_id):
        return
    # One alert per listing and verdict: a rising bid or a retry must not repeat it.
    sent = session.scalar(
        select(TelegramMessage.id).where(TelegramMessage.listing_id == listing.id, TelegramMessage.kind == a.decision)
    )
    if sent:
        return
    model = session.get(WatchModel, a.model_candidate_id) if a.model_candidate_id else None
    data = AlertData(
        listing_id=listing.id,
        kind=a.decision,
        title=listing.title,
        url=listing.url,
        price_sek=listing.price_sek,
        p25=a.value_p25,
        median=a.value_median,
        p75=a.value_p75,
        n_comps=a.n_comps,
        net_sek=a.net_margin_sek,
        roi=a.roi,
        distance_km=a.distance_km,
        municipality=listing.municipality,
        confidence=a.confidence or "låg",
        candidate=model_label(model) if model else None,
        evidence=a.evidence,
        contradictions=a.contradictions,
        needs_underside_photo=a.needs_underside_photo,
    )
    remote = [u for u in listing.image_urls if not u.startswith(LOCAL_PREFIX)]
    photo = remote[0] if remote_images_allowed(listing.source, deps.config) and remote else None
    msg_id = deps.telegram.send_alert(
        deps.config.telegram_chat_id,
        format_alert(data),
        keyboard(listing.id, listing.url),
        photo,
        a.decision == dec.KOLLA_SJALV,
    )
    session.add(
        TelegramMessage(listing_id=listing.id, chat_id=deps.config.telegram_chat_id, message_id=msg_id, kind=a.decision)
    )
