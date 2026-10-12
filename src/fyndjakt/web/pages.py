"""Watchlist (incl. CSV import/export), comps, deal ledger and statistics pages."""

import csv
import io
from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from fyndjakt import stats, training_eval
from fyndjakt.assess import model_label
from fyndjakt.models import AICall, Assessment, Comp, Deal, Feedback, Listing, SourceHealth, WatchModel

CSV_FIELDS = (
    "id",
    "designer",
    "manufacturer",
    "model_name",
    "period",
    "category",
    "aliases",
    "identifying_features",
    "replica_traps",
    "marks",
    "active",
)
TEXT_FIELDS = (
    "designer",
    "manufacturer",
    "model_name",
    "period",
    "category",
    "identifying_features",
    "replica_traps",
    "marks",
)


def build_router(templates: Jinja2Templates, db) -> APIRouter:  # noqa: ANN001
    r = APIRouter()

    # --- watchlist --------------------------------------------------------------------------------

    @r.get("/bevakningslista", response_class=HTMLResponse)
    def watchlist(request: Request, session: Session = Depends(db)):
        models = list(
            session.scalars(
                select(WatchModel).order_by(
                    WatchModel.active.desc(), WatchModel.median_sek.desc().nulls_last(), WatchModel.designer
                )
            )
        )
        return templates.TemplateResponse(request, "bevakningslista.html", {"models": models})

    @r.get("/bevakningslista/export.csv")
    def watchlist_export(session: Session = Depends(db)) -> Response:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(CSV_FIELDS)
        for m in session.scalars(select(WatchModel).order_by(WatchModel.id)):
            w.writerow(
                [
                    m.id,
                    *(getattr(m, f) or "" for f in CSV_FIELDS[1:6]),
                    "|".join(m.aliases or []),
                    *(getattr(m, f) or "" for f in CSV_FIELDS[7:10]),
                    "1" if m.active else "0",
                ]
            )
        return Response(
            buf.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=bevakningslista.csv"},
        )

    @r.post("/bevakningslista/import")
    async def watchlist_import(file: UploadFile, session: Session = Depends(db)):
        text = (await file.read()).decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
        # Validate everything before changing anything: a short row would otherwise blank existing fields,
        # and an unknown id would silently create a duplicate.
        errors = []
        for n, row in enumerate(rows, start=2):
            if None in row.values() or None in row:
                errors.append(f"rad {n}: fel antal kolumner")
                continue
            rid = (row.get("id") or "").strip()
            if rid and (not rid.isdigit() or session.get(WatchModel, int(rid)) is None):
                errors.append(f"rad {n}: okänt id {rid} (lämna id tomt för en ny modell)")
        if errors:
            raise HTTPException(400, "Importen avbröts, inget ändrades. " + "; ".join(errors[:20]))
        for row in rows:
            rid = (row.get("id") or "").strip()
            m = session.get(WatchModel, int(rid)) if rid else None
            if m is None:
                m = WatchModel(auto_generated=False)
                session.add(m)
            for f in TEXT_FIELDS:
                if f in row:
                    setattr(m, f, (row[f] or "").strip() or None)
            if "aliases" in row:
                m.aliases = [a.strip() for a in (row["aliases"] or "").split("|") if a.strip()]
            if "active" in row:
                m.active = (row["active"] or "1").strip() not in ("0", "nej", "false")
        return RedirectResponse("/bevakningslista", status_code=303)

    @r.get("/bevakningslista/{model_id}", response_class=HTMLResponse)
    def watchlist_edit(request: Request, model_id: int, session: Session = Depends(db)):
        m = session.get(WatchModel, model_id) if model_id else WatchModel(active=True, aliases=[])
        if m is None:
            raise HTTPException(404)
        comps = (
            list(session.scalars(select(Comp).where(Comp.model_id == model_id).order_by(desc(Comp.sold_at)).limit(50)))
            if model_id
            else []
        )
        return templates.TemplateResponse(request, "modell.html", {"m": m, "comps": comps, "fields": TEXT_FIELDS})

    @r.post("/bevakningslista/{model_id}")
    async def watchlist_save(request: Request, model_id: int, session: Session = Depends(db)):
        form = await request.form()
        m = session.get(WatchModel, model_id) if model_id else None
        if m is None:
            if model_id:
                raise HTTPException(404)
            m = WatchModel(auto_generated=False)
            session.add(m)
        for f in TEXT_FIELDS:
            setattr(m, f, str(form.get(f, "")).strip() or None)
        m.aliases = [a.strip() for a in str(form.get("aliases", "")).split(",") if a.strip()]
        m.active = form.get("active") == "on"
        session.flush()
        return RedirectResponse(f"/bevakningslista/{m.id}", status_code=303)

    # --- comps ------------------------------------------------------------------------------------

    @r.get("/comps", response_class=HTMLResponse)
    def comps(request: Request, q: str = "", session: Session = Depends(db)):
        query = select(Comp).order_by(desc(Comp.sold_at)).limit(300)
        if q:
            like = f"%{q}%"
            query = query.where(or_(Comp.title.ilike(like), Comp.designer.ilike(like), Comp.model_name.ilike(like)))
        total = session.scalar(select(func.count(Comp.id)))
        return templates.TemplateResponse(
            request, "comps.html", {"comps": list(session.scalars(query)), "q": q, "total": total}
        )

    # --- deals ------------------------------------------------------------------------------------

    @r.get("/affarer", response_class=HTMLResponse)
    def deals(request: Request, redigera: int | None = None, session: Session = Depends(db)):
        rows = list(session.scalars(select(Deal).order_by(desc(Deal.id))))
        editing = session.get(Deal, redigera) if redigera else None
        if redigera and editing is None:
            raise HTTPException(404)
        return templates.TemplateResponse(
            request,
            "affarer.html",
            {"deals": rows, "net": stats.deal_net, "today": date.today().isoformat(), "d": editing},
        )

    @r.post("/affarer")
    def deal_save(
        title: str = Form(...),
        purchase_sek: int = Form(0),
        costs_sek: int = Form(0),
        sale_sek: str = Form(""),
        fees_sek: int = Form(0),
        hours: float = Form(0.0),
        bought_at: str = Form(""),
        sold_at: str = Form(""),
        deal_id: str = Form(""),
        model_id: str = Form(""),
        note: str = Form(""),
        session: Session = Depends(db),
    ):
        d = session.get(Deal, int(deal_id)) if deal_id.isdigit() else None
        if d is None:
            d = Deal(title=title)
            session.add(d)
        d.title, d.purchase_sek, d.costs_sek, d.fees_sek, d.hours = title, purchase_sek, costs_sek, fees_sek, hours
        d.sale_sek = int(sale_sek) if sale_sek.strip() else None
        d.bought_at = _date(bought_at)
        d.sold_at = _date(sold_at)
        d.model_id = int(model_id) if model_id.isdigit() else None
        d.note = note or None
        session.flush()
        # A sold deal becomes a comp (source own_sale) so our own prices feed the valuation.
        own = session.scalar(select(Comp).where(Comp.source == "own_sale", Comp.external_id == str(d.id)))
        if (d.sale_sek is None or d.sold_at is None) and own is not None:
            session.delete(own)  # sale undone: its price must stop feeding the valuation
        if d.sale_sek is not None and d.sold_at is not None:
            m = session.get(WatchModel, d.model_id) if d.model_id else None
            values = {
                "title": d.title,
                "hammer_sek": d.sale_sek,
                "sold_at": d.sold_at,
                "model_id": d.model_id,
                "designer": m.designer if m else None,
                "model_name": m.model_name if m else None,
                "parse_status": "rules",
                "state": "sold",
            }
            if own is None:
                session.add(Comp(source="own_sale", external_id=str(d.id), **values))
            else:
                for k, v in values.items():
                    setattr(own, k, v)
        return RedirectResponse("/affarer", status_code=303)

    # --- training rounds ----------------------------------------------------------------------------

    def _round_rows(session: Session, batch: str) -> list[dict]:
        rows = []
        listings = session.scalars(
            select(Listing).where(Listing.import_batch == batch, Listing.training.is_(True)).order_by(Listing.id)
        )
        for lst in listings:
            final = session.scalar(
                select(Assessment)
                .where(Assessment.listing_id == lst.id, Assessment.stage == "final")
                .order_by(desc(Assessment.id))
                .limit(1)
            )
            model = session.get(WatchModel, final.model_candidate_id) if final and final.model_candidate_id else None
            label = model_label(model) if model else None
            decision = final.decision if final and lst.status != "new" else None
            rows.append(
                {
                    "l": lst,
                    "a": final if decision else None,
                    "label": label,
                    "verdict": training_eval.verdict(lst.expected, decision, label),
                    "img": ("/bild/" + lst.image_urls[0][6:])
                    if lst.image_urls and lst.image_urls[0].startswith("local:")
                    else None,
                }
            )
        return rows

    @r.get("/traning", response_class=HTMLResponse)
    def training_rounds(request: Request, session: Session = Depends(db)):
        batches = session.execute(
            select(Listing.import_batch, func.count(Listing.id), func.min(Listing.first_seen_at))
            .where(Listing.training.is_(True), Listing.import_batch.is_not(None))
            .group_by(Listing.import_batch)
            .order_by(desc(func.min(Listing.first_seen_at)))
        ).all()
        return templates.TemplateResponse(request, "traning.html", {"batches": batches})

    @r.get("/traning/{batch}", response_class=HTMLResponse)
    def training_round(request: Request, batch: str, session: Session = Depends(db)):
        rows = _round_rows(session, batch)  # empty at first when only screenshots were sent: they are being read
        stats_ = training_eval.summarize(
            [(r["a"].decision if r["a"] else None, r["verdict"], r["a"].cost_usd if r["a"] else 0.0) for r in rows]
        )
        pending = sum(1 for r in rows if r["a"] is None) or (0 if rows else 1)
        return templates.TemplateResponse(
            request,
            "traning_omgang.html",
            {"batch": batch, "rows": rows, "s": stats_, "pending": pending, "choices": training_eval.MANUAL},
        )

    @r.post("/traning/{batch}/{listing_id}")
    def training_judge(batch: str, listing_id: int, verdict: str = Form(...), session: Session = Depends(db)):
        lst = session.get(Listing, listing_id)
        if lst is None or lst.import_batch != batch or verdict not in training_eval.MANUAL:
            raise HTTPException(400)
        lst.expected = verdict
        return RedirectResponse(f"/traning/{batch}#l{listing_id}", status_code=303)

    # --- statistics -------------------------------------------------------------------------------

    @r.get("/statistik", response_class=HTMLResponse)
    def statistik(request: Request, session: Session = Depends(db)):
        since = datetime.now(UTC) - timedelta(weeks=12)
        alerts = [
            stats.AlertRow(
                a.listing_id, a.decision, _utc(a.created_at), _utc(lst.published_at), _utc(lst.first_seen_at)
            )
            for a, lst in session.execute(
                select(Assessment, Listing)
                .join(Listing, Listing.id == Assessment.listing_id)
                .where(Assessment.stage == "final", Assessment.created_at >= since)
            )
        ]
        feedback = {f.listing_id: f.label for f in session.scalars(select(Feedback).order_by(Feedback.id))}
        deals = [
            stats.DealRow(_utc(d.sold_at), d.sale_sek, d.purchase_sek, d.costs_sek, d.fees_sek)
            for d in session.scalars(select(Deal))
        ]
        costs: dict[str, float] = {}
        for created, cost in session.execute(select(AICall.created_at, AICall.cost_usd)):
            key = created.strftime("%Y-%m")
            costs[key] = costs.get(key, 0.0) + cost
        cost_rows = sorted(costs.items())
        prec, n_rated = stats.precision(alerts, feedback)
        return templates.TemplateResponse(
            request,
            "statistik.html",
            {
                "per_week": stats.alerts_per_week(alerts),
                "precision": prec,
                "n_rated": n_rated,
                "latency": stats.latency_minutes(alerts),
                "costs": cost_rows,
                "profit": stats.profit_per_month(deals),
                "health": list(session.scalars(select(SourceHealth).where(~SourceHealth.source.contains(":")))),
                "n_assessed": len(alerts),
            },
        )

    return r


def _date(s: str) -> datetime | None:
    s = s.strip()
    return datetime.fromisoformat(s).replace(tzinfo=UTC) if s else None


def _utc(dt: datetime | None) -> datetime | None:
    return dt.replace(tzinfo=UTC) if dt is not None and dt.tzinfo is None else dt
