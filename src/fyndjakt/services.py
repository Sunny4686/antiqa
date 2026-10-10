"""DB-touching helpers shared by jobs and web: settings, ingest, comps, source health, owner alerts."""

import re
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from fyndjakt.models import Comp, Job, Listing, SettingsRow, SourceHealth, WatchModel
from fyndjakt.pipeline.prefilter import contains_term, normalize
from fyndjakt.pipeline.valuation import CompPrice
from fyndjakt.sources.auctionet import CompData

PARSED_FIELDS = ("designer", "manufacturer", "model_name", "parse_status")
STOP_BACKOFF = (timedelta(minutes=30), timedelta(hours=2), timedelta(hours=8), timedelta(hours=24))


def get_settings(session: Session) -> SettingsRow:
    row = session.get(SettingsRow, 1)
    if row is None:
        row = SettingsRow(id=1)
        session.add(row)
        session.flush()
    return row


# --- jobs -----------------------------------------------------------------------------------------


def enqueue(session: Session, kind: str, payload: dict | None = None, run_at: datetime | None = None) -> Job:
    job = Job(kind=kind, payload=payload or {}, run_at=run_at or datetime.now(UTC))
    session.add(job)
    session.flush()
    return job


# --- ingest ---------------------------------------------------------------------------------------


# Seller contact details inside free text. Names can't be told apart reliably and are not attempted.
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_PHONE = re.compile(r"(?<![\d\w])(?:\+46|0046|0)[\s-]?\(?\d{1,3}\)?(?:[\s-]?\d){5,9}(?![\d\w])")
CONTACT_REMOVED = "[kontaktuppgift borttagen]"


def scrub_contacts(text: str | None) -> str | None:
    if not text:
        return text
    return _PHONE.sub(CONTACT_REMOVED, _EMAIL.sub(CONTACT_REMOVED, text))


class IngestListing(BaseModel):
    """Payload for /ingest/listing. Unknown fields (e.g. seller data) are dropped, never stored.
    Phone numbers and e-mail addresses in title/description are removed before storage and AI calls."""

    model_config = ConfigDict(extra="ignore")

    source: str = Field(pattern=r"^(blocket_push|blocket_share|blocket_ext|blocket_poll|tradera)$")
    external_id: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=512)
    url: str | None = None
    price_sek: int | None = Field(default=None, ge=0)
    description: str | None = None
    municipality: str | None = None
    lat: float | None = None
    lon: float | None = None
    published_at: datetime | None = None
    image_urls: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("title", "description")
    @classmethod
    def _no_contacts(cls, v: str | None) -> str | None:
        return scrub_contacts(v)


def upsert_listing(session: Session, data: IngestListing) -> tuple[Listing, bool, bool]:
    """Returns (listing, is_new, price_changed). New listings and price changes get (re)assessed."""
    listing = session.scalar(
        select(Listing).where(Listing.source == data.source, Listing.external_id == data.external_id)
    )
    fields = data.model_dump(exclude={"source", "external_id"})
    # Coordinates are rounded to ~1 km: enough for distance, not a seller's address.
    for k in ("lat", "lon"):
        if fields[k] is not None:
            fields[k] = round(fields[k], 2)
    if listing is None:
        listing = Listing(source=data.source, external_id=data.external_id, **fields)
        session.add(listing)
        session.flush()
        enqueue(session, "assess", {"listing_id": listing.id})
        return listing, True, False
    price_changed = data.price_sek is not None and data.price_sek != listing.price_sek
    for k, v in fields.items():
        if v not in (None, []):
            setattr(listing, k, v)
    if price_changed:
        listing.status = "new"
        enqueue(session, "assess", {"listing_id": listing.id})
    return listing, False, price_changed


# --- comps ----------------------------------------------------------------------------------------


def known_comp_ids(session: Session, source: str) -> set[str]:
    return set(session.scalars(select(Comp.external_id).where(Comp.source == source)))


def upsert_comp(session: Session, source: str, c: CompData) -> bool:
    existing = session.scalar(select(Comp).where(Comp.source == source, Comp.external_id == c.external_id))
    values = {k: v for k, v in vars(c).items() if k != "external_id"}
    if existing and existing.parse_status and existing.parse_status.startswith("llm"):
        for k in PARSED_FIELDS:  # keep what the LLM parser found
            values.pop(k, None)
    if existing:
        for k, v in values.items():
            setattr(existing, k, v)
        return False
    session.add(Comp(source=source, external_id=c.external_id, **values))
    return True


def comps_for_model(session: Session, m: WatchModel) -> list[CompPrice]:
    rows = list(session.scalars(select(Comp).where(Comp.model_id == m.id, Comp.hammer_sek.is_not(None))))
    if m.designer:
        names = [normalize(n) for n in (m.model_name, *(m.aliases or [])) if n and len(n) >= 3]
        seen = {r.id for r in rows}
        for c in session.scalars(
            select(Comp).where(Comp.designer.ilike(f"%{m.designer}%"), Comp.hammer_sek.is_not(None))
        ):
            if c.id not in seen and any(contains_term(normalize(c.title), n) for n in names):
                rows.append(c)
    return [CompPrice(r.hammer_sek, r.condition) for r in rows if r.hammer_sek]


def prior_comps(session: Session, m: WatchModel) -> list[CompPrice]:
    """Designer x category comps used to shrink thin model-level estimates."""
    if not m.designer:
        return []
    q = select(Comp).where(Comp.designer.ilike(f"%{m.designer}%"), Comp.hammer_sek.is_not(None))
    if m.category:
        q = q.where(Comp.category == m.category)
    return [CompPrice(r.hammer_sek, r.condition) for r in session.scalars(q)]


# --- source health ---------------------------------------------------------------------------------


def health_row(session: Session, source: str) -> SourceHealth:
    row = session.get(SourceHealth, source)
    if row is None:
        row = SourceHealth(source=source, consecutive_failures=0, alerted=False)
        session.add(row)
        session.flush()
    return row


def record_success(session: Session, source: str, now: datetime, got_items: bool) -> None:
    row = health_row(session, source)
    row.last_success_at = now
    row.consecutive_failures = 0
    row.last_error = None
    row.stopped_reason = None
    row.stopped_until = None
    row.alerted = False
    if got_items:
        row.last_item_at = now


def record_failure(
    session: Session, source: str, now: datetime, error: str, blocked_reason: str | None
) -> SourceHealth:
    row = health_row(session, source)
    row.consecutive_failures += 1
    row.last_error = error[:2000]
    if blocked_reason:
        step = STOP_BACKOFF[min(row.consecutive_failures - 1, len(STOP_BACKOFF) - 1)]
        row.stopped_reason = blocked_reason
        row.stopped_until = now + step
    return row


def is_stopped(session: Session, source: str, now: datetime) -> bool:
    row = session.get(SourceHealth, source)
    return bool(row and row.stopped_until and _aware(row.stopped_until) > now)


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def health_problems(
    rows: list[SourceHealth],
    now: datetime,
    local_hour: int,
    silence: dict[str, timedelta],
    daytime: tuple[int, int] = (8, 22),
) -> list[tuple[SourceHealth, str]]:
    """Pure check: >= 3 failures in a row, a blocked source, or no new items for too long in daytime."""
    out = []
    for r in rows:
        if r.consecutive_failures >= 3 or r.stopped_reason:
            out.append((r, r.stopped_reason or f"{r.consecutive_failures} fel i rad"))
            continue
        limit = silence.get(r.source)
        if limit and daytime[0] <= local_hour < daytime[1] and r.last_item_at and now - _aware(r.last_item_at) > limit:
            out.append((r, f"inga nya objekt på {limit}"))
    return out
