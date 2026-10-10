"""FastAPI app: Swedish UI behind Cloudflare Access, plus token-protected /ingest and /telegram endpoints."""

import hmac
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

import anthropic
from fastapi import Depends, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from fyndjakt.assess import Deps
from fyndjakt.config import get_config
from fyndjakt.db import session_scope
from fyndjakt.images import ImageLoader
from fyndjakt.jobs import Worker
from fyndjakt.migrate import upgrade
from fyndjakt.models import Assessment, Feedback, Listing, WatchModel
from fyndjakt.notify.telegram import FEEDBACK_BUTTONS, FEEDBACK_LABELS, TelegramClient, parse_callback
from fyndjakt.pipeline.geo import load_municipalities
from fyndjakt.services import IngestListing, get_settings, upsert_listing
from fyndjakt.sources.auctionet import AuctionetClient
from fyndjakt.web.pages import build_router

log = logging.getLogger(__name__)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
FEEDBACK_TEXT = dict(FEEDBACK_BUTTONS)


def build_deps() -> Deps:
    cfg = get_config()
    return Deps(
        config=cfg,
        ai=anthropic.Anthropic(api_key=cfg.anthropic_api_key) if cfg.anthropic_api_key else None,
        telegram=TelegramClient(cfg.telegram_bot_token) if cfg.telegram_bot_token else None,
        municipalities=load_municipalities(cfg.municipalities_csv),
        images=ImageLoader(cfg.image_cache_dir, cfg.user_agent) if cfg.ai_send_listing_images else None,
    )


def handle_telegram_update(update: dict, deps: Deps) -> None:
    """A feedback button press. Ignores anything not from the owner's chat when TELEGRAM_CHAT_ID is set."""
    cq = update.get("callback_query")
    parsed = parse_callback(cq.get("data", "")) if cq else None
    if not parsed:
        return
    msg = cq.get("message") or {}
    owner = deps.config.telegram_chat_id
    if owner and str((msg.get("chat") or {}).get("id")) != str(owner):
        return
    listing_id, label = parsed
    with session_scope() as session:
        listing = session.get(Listing, listing_id)
        if listing is None:
            return
        session.add(Feedback(listing_id=listing_id, label=label))
        listing.status = "handled"
    if deps.telegram and msg:
        try:
            deps.telegram.mark_handled(str(msg["chat"]["id"]), msg["message_id"], FEEDBACK_TEXT[label], cq["id"])
        except Exception:
            log.exception("could not mark telegram message handled")


POLL_MAX_TRIES = 3


class TelegramPoller(threading.Thread):
    """Local alternative to the webhook: long-polls getUpdates (removes any webhook first)."""

    def __init__(self, deps: Deps):
        super().__init__(daemon=True, name="telegram-poller")
        self.deps = deps
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        tg = self.deps.telegram
        offset = None
        try:
            tg.delete_webhook()
        except Exception:
            log.exception("could not delete telegram webhook")
        failures: dict[int, int] = {}
        while not self._stop.is_set():
            try:
                for update in tg.get_updates(offset):
                    uid = update["update_id"]
                    try:
                        handle_telegram_update(update, self.deps)
                    except Exception:
                        failures[uid] = failures.get(uid, 0) + 1
                        if failures[uid] < POLL_MAX_TRIES:
                            raise  # offset stays put, so Telegram hands the same update back
                        log.exception("dropping telegram update %s after %d tries", uid, failures[uid])
                    failures.pop(uid, None)
                    offset = uid + 1  # acknowledge only once handled (or given up on)
            except Exception as e:
                log.warning("telegram polling failed: %s", e)
                self._stop.wait(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    upgrade()
    deps = build_deps()
    app.state.deps = deps
    worker = poller = None
    if app.state.run_worker:
        cfg = deps.config
        worker = Worker(deps, {"auctionet": AuctionetClient(cfg.user_agent, cfg.auctionet_min_interval_s)})
        worker.start()
        if cfg.telegram_polling and deps.telegram:
            poller = TelegramPoller(deps)
            poller.start()
    yield
    if worker:
        worker.stop()
    if poller:
        poller.stop()


def create_app(run_worker: bool = True) -> FastAPI:
    app = FastAPI(title="Fyndjakt", lifespan=lifespan)
    app.state.run_worker = run_worker
    app.include_router(_routes())
    app.include_router(build_router(templates, db))
    return app


def db():
    with session_scope() as session:
        yield session


def _check_token(expected: str | None, given: str | None) -> None:
    if not expected or not given or not hmac.compare_digest(expected, given):
        raise HTTPException(status_code=401)


def _routes():
    from fastapi import APIRouter

    r = APIRouter()

    @r.get("/health")
    def health() -> dict:
        return {"ok": True}

    @r.post("/ingest/listing")
    def ingest(
        payload: IngestListing, authorization: str | None = Header(default=None), session: Session = Depends(db)
    ) -> dict:
        _check_token(get_config().ingest_token, (authorization or "").removeprefix("Bearer ").strip() or None)
        listing, is_new, price_changed = upsert_listing(session, payload)
        return {"id": listing.id, "new": is_new, "price_changed": price_changed}

    @r.post("/telegram/webhook")
    async def telegram_webhook(
        request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)
    ) -> dict:
        _check_token(get_config().telegram_webhook_secret, x_telegram_bot_api_secret_token)
        handle_telegram_update(await request.json(), request.app.state.deps)
        return {"ok": True}

    @r.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse("/inkorg")

    @r.get("/inkorg", response_class=HTMLResponse)
    def inkorg(request: Request, alla: bool = False, session: Session = Depends(db)):
        # Latest final assessment per listing first, then filter: a FYND that a re-assessment turned into
        # INGET must disappear rather than show its old verdict next to the new price.
        latest = (
            select(func.max(Assessment.id))
            .where(Assessment.stage == "final")
            .group_by(Assessment.listing_id)
            .scalar_subquery()
        )
        q = (
            select(Assessment, Listing)
            .join(Listing, Listing.id == Assessment.listing_id)
            .where(Assessment.id.in_(latest))
            .order_by(desc(Assessment.id))
            .limit(200)
        )
        if not alla:
            q = q.where(Assessment.decision.in_(("FYND", "KOLLA_SJALV")))
        rows = [tuple(r) for r in session.execute(q).all()]
        return templates.TemplateResponse(request, "inkorg.html", {"rows": rows, "alla": alla})

    @r.get("/annons/{listing_id}", response_class=HTMLResponse)
    def annons(request: Request, listing_id: int, session: Session = Depends(db)):
        listing = session.get(Listing, listing_id)
        if listing is None:
            raise HTTPException(404)
        assessments = list(
            session.scalars(select(Assessment).where(Assessment.listing_id == listing_id).order_by(Assessment.id))
        )
        feedback = list(session.scalars(select(Feedback).where(Feedback.listing_id == listing_id)))
        final = next((a for a in reversed(assessments) if a.stage == "final"), None)
        model = session.get(WatchModel, final.model_candidate_id) if final and final.model_candidate_id else None
        return templates.TemplateResponse(
            request,
            "annons.html",
            {
                "listing": listing,
                "assessments": assessments,
                "final": final,
                "model": model,
                "feedback": feedback,
                "buttons": FEEDBACK_BUTTONS,
                "show_images": get_config().ai_send_listing_images,
            },
        )

    @r.post("/annons/{listing_id}/feedback", response_class=HTMLResponse)
    def annons_feedback(listing_id: int, label: str = Form(...), session: Session = Depends(db)):
        if label not in FEEDBACK_LABELS or session.get(Listing, listing_id) is None:
            raise HTTPException(400)
        session.add(Feedback(listing_id=listing_id, label=label))
        session.get(Listing, listing_id).status = "handled"
        return HTMLResponse(f"<span class='done'>✓ {FEEDBACK_TEXT[label]}</span>")

    @r.get("/installningar", response_class=HTMLResponse)
    def installningar(request: Request, sparat: bool = False, session: Session = Depends(db)):
        return templates.TemplateResponse(
            request, "installningar.html", {"s": get_settings(session), "sparat": sparat, "fields": SETTINGS_FIELDS}
        )

    @r.post("/installningar")
    async def installningar_save(request: Request, session: Session = Depends(db)):
        form = await request.form()
        s = get_settings(session)
        for name, (_label, kind) in SETTINGS_FIELDS.items():
            raw = str(form.get(name, "")).strip()
            if raw == "" and not (kind == "list" and name in form):
                continue  # blank number: keep the old value; an emptied list field clears the list
            try:
                if kind == "list":
                    setattr(s, name, [p.strip() for p in raw.split(",") if p.strip()])
                else:
                    setattr(s, name, kind(raw.replace(",", ".") if kind is float else raw))
            except ValueError:
                raise HTTPException(400, f"Ogiltigt värde för {name}") from None
        return RedirectResponse("/installningar?sparat=1", status_code=303)

    return r


SETTINGS_FIELDS: dict[str, tuple[str, object]] = {
    "home_lat": ("Hem, latitud", float),
    "home_lon": ("Hem, longitud", float),
    "max_distance_km": ("Max avstånd (km)", float),
    "allowed_regions": ("Tillåtna län (kommaseparerade)", "list"),
    "min_net_margin_sek": ("Min nettomarginal (kr)", int),
    "min_roi": ("Min ROI (0,5 = 50 %)", float),
    "net_ratio": ("Nettokvot efter avgifter", float),
    "fixed_fees_sek": ("Fasta avgifter (kr)", int),
    "transport_base_sek": ("Transport, grund (kr)", int),
    "transport_sek_per_km": ("Transport, kr per km", float),
    "max_listing_price_sek": ("Max annonspris (kr)", int),
    "daily_ai_budget_usd": ("AI-budget per dag (USD)", float),
    "quiet_hours_start": ("Tyst från (timme)", int),
    "quiet_hours_end": ("Tyst till (timme)", int),
}

app = create_app()
