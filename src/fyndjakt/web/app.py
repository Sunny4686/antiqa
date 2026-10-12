"""FastAPI app: Swedish UI behind Cloudflare Access, plus token-protected /ingest and /telegram endpoints."""

import hmac
import json
import logging
import re
import shutil
import threading
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import anthropic
from fastapi import Depends, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from fyndjakt import capture, importer
from fyndjakt.assess import Deps, remote_images_allowed
from fyndjakt.config import get_config
from fyndjakt.db import session_scope
from fyndjakt.images import LOCAL_PREFIX, ImageLoader, usable_urls
from fyndjakt.jobs import Worker
from fyndjakt.migrate import upgrade
from fyndjakt.models import Assessment, Feedback, Listing, SourceHealth, WatchModel
from fyndjakt.notify.telegram import FEEDBACK_BUTTONS, FEEDBACK_LABELS, TelegramClient, parse_callback
from fyndjakt.pipeline.geo import load_municipalities
from fyndjakt.services import IngestListing, enqueue, get_settings, upsert_listing
from fyndjakt.sources.auctionet import AuctionetClient
from fyndjakt.web.pages import build_router

log = logging.getLogger(__name__)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _kr(value: object) -> str:
    """12500 -> '12 500 kr' (narrow no-break space as thousands separator)."""
    if value is None or value == "":
        return "–"
    return f"{int(value):,}".replace(",", "\u202f") + "\u00a0kr"


def _thumb(listing: Listing | None) -> str | None:
    """First displayable picture of a listing: own uploads always, remote ones only where fetching is allowed."""
    if listing is None:
        return None
    urls = usable_urls(listing.image_urls or [], remote_images_allowed(listing.source, get_config()))
    if not urls:
        return None
    return "/bild/" + urls[0][len(LOCAL_PREFIX) :] if urls[0].startswith(LOCAL_PREFIX) else urls[0]


templates.env.filters["kr"] = _kr
templates.env.globals["thumb"] = _thumb
templates.env.globals["DECISION_LABEL"] = {"FYND": "FYND", "KOLLA_SJALV": "Kolla själv", "INGET": "Inget"}
FEEDBACK_TEXT = dict(FEEDBACK_BUTTONS)


def build_deps() -> Deps:
    cfg = get_config()
    return Deps(
        config=cfg,
        ai=anthropic.Anthropic(api_key=cfg.anthropic_api_key) if cfg.anthropic_api_key else None,
        telegram=TelegramClient(cfg.telegram_bot_token) if cfg.telegram_bot_token else None,
        municipalities=load_municipalities(cfg.municipalities_csv),
        # Always present for the owner's own uploads; remote listing images still need ai_send_listing_images.
        images=ImageLoader(cfg.image_cache_dir, cfg.user_agent),
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
MAX_UPLOADS = 4
MAX_SCREENSHOT_BYTES = 15 * 1024 * 1024
MAX_IMPORT_FILES = 200


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


def _utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def _left(d: timedelta) -> str:
    minutes = max(int(d.total_seconds() // 60), 0)
    if minutes < 60:
        return f"{minutes} min"
    hours = minutes // 60
    return f"{hours} h {minutes % 60} min" if hours < 24 else f"{hours // 24} d {hours % 24} h"


def _import_results(request: Request, session: Session, ids: list[int], screenshots: int, errors: list[str]):
    """One row per imported listing with its latest verdict; the page refreshes itself until all are assessed."""
    rows = []
    for lid in ids:
        lst = session.get(Listing, lid)
        if lst is None:
            continue
        final = session.scalar(
            select(Assessment)
            .where(Assessment.listing_id == lid, Assessment.stage == "final")
            .order_by(desc(Assessment.id))
            .limit(1)
        )
        rows.append({"l": lst, "a": final if final and lst.status != "new" else None})
    pending = any(r["a"] is None for r in rows)
    return templates.TemplateResponse(
        request,
        "import_resultat.html",
        {
            "rows": rows,
            "pending": pending,
            "screenshots": screenshots,
            "errors": errors,
            "ids": ",".join(str(i) for i in ids),
        },
    )


IMPORT_TEMPLATE_TXT = """Rubrik: Fåtölj i ek och fårskinn
Pris: 800 kr
Ort: Mölndal
Länk: https://www.blocket.se/...
Källa: blocket
Bilder: fatolj-1.jpg, fatolj-2.jpg
Beskrivning:
Fin fåtölj från farmors hus, lite slitet skinn.
---
Rubrik: Byrå i teak
Pris: 1 200 kr
Ort: Borås
Källa: facebook
Bilder: byra.jpg
Beskrivning:
Fyra lådor, nyckel finns.
"""

IMPORT_TEMPLATE_CSV = """rubrik,pris,ort,lank,kalla,bilder,beskrivning
Fåtölj i ek och fårskinn,800,Mölndal,https://www.blocket.se/...,blocket,fatolj-1.jpg|fatolj-2.jpg,Från farmors hus
Byrå i teak,1200,Borås,,facebook,byra.jpg,Fyra lådor
"""


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

    @r.post("/ingest/screenshot")
    async def ingest_screenshot(
        request: Request, authorization: str | None = Header(default=None), session: Session = Depends(db)
    ) -> dict:
        """From the browser extension: a screenshot of what the owner is looking at + the visible links."""
        _check_token(get_config().ingest_token, (authorization or "").removeprefix("Bearer ").strip() or None)
        form = await request.form()
        page_url = str(form.get("page_url", ""))
        if capture.source_for(page_url) is None:
            raise HTTPException(400, "Bara Blocket och Facebook Marketplace")
        image = form.get("image")
        data = await image.read() if hasattr(image, "read") else b""
        if not data or len(data) > MAX_SCREENSHOT_BYTES:
            raise HTTPException(400, "Skärmbild saknas eller är för stor")
        try:
            links = [capture.LinkBox(**lk).__dict__ for lk in json.loads(str(form.get("links", "[]")))[:400]]
        except (ValueError, TypeError):
            raise HTTPException(400, "Ogiltig länklista") from None
        folder = Path(get_config().capture_dir)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{uuid.uuid4().hex}.img"
        path.write_bytes(data)
        enqueue(session, "screen_capture", {"path": str(path), "page_url": page_url, "links": links})
        return {"queued": True}

    @r.post("/telegram/webhook")
    async def telegram_webhook(
        request: Request, x_telegram_bot_api_secret_token: str | None = Header(default=None)
    ) -> dict:
        _check_token(get_config().telegram_webhook_secret, x_telegram_bot_api_secret_token)
        handle_telegram_update(await request.json(), request.app.state.deps)
        return {"ok": True}

    @r.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse("/utvalt")

    @r.get("/utvalt", response_class=HTMLResponse)
    def utvalt(request: Request, session: Session = Depends(db)):
        now = datetime.now(UTC)
        latest = (
            select(func.max(Assessment.id))
            .where(Assessment.stage == "final")
            .group_by(Assessment.listing_id)
            .scalar_subquery()
        )
        rows = session.execute(
            select(Assessment, Listing)
            .join(Listing, Listing.id == Assessment.listing_id)
            .where(
                Assessment.id.in_(latest),
                Listing.status != "handled",
                or_(Listing.ends_at.is_(None), Listing.ends_at > now),
            )
            .limit(500)
        ).all()
        cfg = get_config()
        cards, watching = [], []
        for a, lst in rows:
            if a.decision not in ("FYND", "KOLLA_SJALV"):
                if lst.source == "auctionet_live" and a.net_margin_sek is not None:
                    ends = _utc(lst.ends_at)
                    watching.append({"a": a, "l": lst, "ends_in": _left(ends - now)})
                continue
            urls = usable_urls(lst.image_urls, remote_images_allowed(lst.source, cfg))
            img = (
                ("/bild/" + urls[0][len(LOCAL_PREFIX) :])
                if urls and urls[0].startswith(LOCAL_PREFIX)
                else (urls or [None])[0]
            )
            ends = _utc(lst.ends_at) if lst.ends_at else None
            cards.append({"a": a, "l": lst, "img": img, "ends": ends, "ends_in": _left(ends - now) if ends else None})
        far = datetime.max.replace(tzinfo=UTC)
        cards.sort(key=lambda c: (c["a"].decision != "FYND", c["ends"] or far, -(c["a"].net_margin_sek or 0)))
        health = session.get(SourceHealth, "auctionet")
        n_live = session.scalar(
            select(func.count(Listing.id)).where(Listing.source == "auctionet_live", Listing.ends_at > now)
        )
        n_models = session.scalar(select(func.count(WatchModel.id)).where(WatchModel.active.is_(True)))
        last = (
            _utc(health.last_success_at).astimezone(ZoneInfo(cfg.timezone))
            if health and health.last_success_at
            else None
        )
        return templates.TemplateResponse(
            request,
            "utvalt.html",
            {
                "cards": cards,
                "watching": sorted(watching, key=lambda w: -w["a"].net_margin_sek)[:25],
                "min_net": get_settings(session).min_net_margin_sek,
                "n_live": n_live,
                "n_models": n_models,
                "last_scan": last.strftime("%H:%M") if last else None,
            },
        )

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
                "images": usable_urls(listing.image_urls, remote_images_allowed(listing.source, get_config())),
                "pending": final is None and listing.status == "new",
            },
        )

    @r.get("/testa", response_class=HTMLResponse)
    def testa(request: Request):
        return templates.TemplateResponse(request, "testa.html", {})

    @r.post("/testa")
    async def testa_save(
        request: Request,
        title: str = Form(...),
        price_sek: str = Form(""),
        municipality: str = Form(""),
        description: str = Form(""),
        url: str = Form(""),
        session: Session = Depends(db),
    ):
        form = await request.form()
        deps: Deps = request.app.state.deps
        image_urls = []
        for f in form.getlist("images")[:MAX_UPLOADS]:
            data = await f.read() if hasattr(f, "read") else b""
            if not data:
                continue
            try:
                image_urls.append(deps.images.save_upload(data))
            except Exception:
                raise HTTPException(400, f"Kunde inte läsa bilden {getattr(f, 'filename', '')}") from None
        payload = IngestListing(
            source="manual",
            external_id=uuid.uuid4().hex,
            title=title.strip(),
            price_sek=int(price_sek) if price_sek.strip().isdigit() else None,
            municipality=municipality.strip() or None,
            description=description.strip() or None,
            url=url.strip() or None,
            image_urls=image_urls,
        )
        listing, _new, _changed = upsert_listing(session, payload)
        return RedirectResponse(f"/annons/{listing.id}", status_code=303)

    @r.get("/importera", response_class=HTMLResponse)
    def importera(request: Request):
        return templates.TemplateResponse(
            request, "importera.html", {"inbox": str(Path(get_config().inbox_dir).resolve()), "result": None}
        )

    @r.post("/importera", response_class=HTMLResponse)
    async def importera_save(request: Request, session: Session = Depends(db)):
        """Upload a zip, a CSV/JSON/TXT or loose images + a text file; imported right away."""
        form = await request.form()
        deps: Deps = request.app.state.deps
        training = form.get("training") == "on"
        batch = re.sub(r"[^\w.-]+", "-", str(form.get("batch") or "").strip())[:48].strip("-")
        batch = batch or f"{'traning' if training else 'import'}-{datetime.now(UTC):%Y%m%d-%H%M}"
        tmp = Path(get_config().inbox_dir) / f"_upload-{uuid.uuid4().hex}"
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            for f in form.getlist("files")[:MAX_IMPORT_FILES]:
                if not hasattr(f, "read") or not f.filename:
                    continue
                name = Path(f.filename).name
                data = await f.read()
                if len(data) > MAX_SCREENSHOT_BYTES * 4:
                    raise HTTPException(400, f"{name} är för stor")
                (tmp / name).write_bytes(data)
            zips = [p for p in tmp.iterdir() if p.suffix.lower() == ".zip"]
            result = importer.ImportResult()
            remote = get_config().ai_send_listing_images
            captures = Path(get_config().capture_dir)
            for z in zips:
                r = importer.import_zip(session, deps.images, z, remote, captures, batch, training)
                result.imported += r.imported
                result.errors += r.errors
                result.screenshots += r.screenshots
                z.unlink()
            if any(tmp.iterdir()):
                r = importer.import_path(session, deps.images, tmp, remote, captures, batch, training)
                result.imported += r.imported
                result.errors += r.errors
                result.screenshots += r.screenshots
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        session.flush()
        if training:
            return RedirectResponse(f"/traning/{batch}", status_code=303)
        return _import_results(request, session, result.imported, result.screenshots, result.errors)

    @r.get("/importera/resultat", response_class=HTMLResponse)
    def importera_resultat(request: Request, ids: str = "", skarmbilder: int = 0, session: Session = Depends(db)):
        listing_ids = [int(i) for i in ids.split(",") if i.strip().isdigit()][:MAX_IMPORT_FILES]
        return _import_results(request, session, listing_ids, skarmbilder, [])

    @r.get("/importera/mall.txt")
    def importera_mall_txt() -> Response:
        return Response(
            IMPORT_TEMPLATE_TXT,
            media_type="text/plain; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=annonser.txt"},
        )

    @r.get("/importera/mall.csv")
    def importera_mall_csv() -> Response:
        return Response(
            IMPORT_TEMPLATE_CSV,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=annonser.csv"},
        )

    @r.get("/bild/{ident}")
    def bild(request: Request, ident: str) -> Response:
        path = request.app.state.deps.images.local_path(LOCAL_PREFIX + ident)
        if path is None:
            raise HTTPException(404)
        return Response(path.read_bytes(), media_type="image/jpeg", headers={"Cache-Control": "private, max-age=3600"})

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
