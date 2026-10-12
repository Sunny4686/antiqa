"""Database schema. Kept portable: JSON columns, UTC datetimes, no SQLite-only types (Postgres later)."""

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (UniqueConstraint("source", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    # How it came in: blocket_push | blocket_share | blocket_ext | blocket_poll | tradera | manual | auctionet_live
    source: Mapped[str] = mapped_column(String(32))
    external_id: Mapped[str] = mapped_column(String(64))
    url: Mapped[str | None] = mapped_column(String(512))
    title: Mapped[str] = mapped_column(String(512))
    price_sek: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    municipality: Mapped[str | None] = mapped_column(String(128))
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    image_urls: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(16), default="new")  # new | assessed | skipped | handled
    # Auctions only: when bidding closes and the leading bid (price_sek is the all-in cost to win right now).
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_bid_sek: Mapped[int | None] = mapped_column(Integer)
    # Imports: which upload/folder it came in, whether it is a training round (no alerts), and the answer key:
    # a model name, "inget" (ordinary furniture), or the owner's verdict on the AI's answer afterwards.
    import_batch: Mapped[str | None] = mapped_column(String(64), index=True)
    training: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    expected: Mapped[str | None] = mapped_column(String(256))


class WatchModel(Base):
    """A row in the watchlist ("bevakningslistan")."""

    __tablename__ = "models"

    id: Mapped[int] = mapped_column(primary_key=True)
    designer: Mapped[str | None] = mapped_column(String(128))
    manufacturer: Mapped[str | None] = mapped_column(String(128))
    model_name: Mapped[str | None] = mapped_column(String(128))
    period: Mapped[str | None] = mapped_column(String(64))
    category: Mapped[str | None] = mapped_column(String(64))
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list)
    identifying_features: Mapped[str | None] = mapped_column(Text)
    replica_traps: Mapped[str | None] = mapped_column(Text)
    marks: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    n_sales: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    median_sek: Mapped[int | None] = mapped_column(Integer)
    notes_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Comp(Base):
    __tablename__ = "comps"
    __table_args__ = (UniqueConstraint("source", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int | None] = mapped_column(ForeignKey("models.id"))
    designer: Mapped[str | None] = mapped_column(String(128))
    manufacturer: Mapped[str | None] = mapped_column(String(128))
    model_name: Mapped[str | None] = mapped_column(String(128))
    category: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(32))  # auctionet | tradera | own_sale | ...
    external_id: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(512))
    state: Mapped[str] = mapped_column(String(16), default="sold")  # sold | unsold
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    hammer_sek: Mapped[int | None] = mapped_column(Integer)
    estimate_sek: Mapped[int | None] = mapped_column(Integer)
    auction_house: Mapped[str | None] = mapped_column(String(128))
    condition_text: Mapped[str | None] = mapped_column(Text)
    condition: Mapped[str | None] = mapped_column(String(32))  # utmärkt | gott | slitet | renoveringsobjekt
    url: Mapped[str | None] = mapped_column(String(512))
    image_urls: Mapped[list[str]] = mapped_column(JSON, default=list)
    # How designer/manufacturer/model were obtained: rules | llm_pending | llm | llm_failed | none
    parse_status: Mapped[str | None] = mapped_column(String(16), index=True)


class AIBatch(Base):
    """Message Batches submitted to Anthropic (half price, async)."""

    __tablename__ = "ai_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(64), unique=True)
    purpose: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(64))
    n_requests: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="submitted")  # submitted | collected | failed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    stage: Mapped[str] = mapped_column(String(32))  # prefilter | screen | verify | verify_strong | final
    model_candidate_id: Mapped[int | None] = mapped_column(ForeignKey("models.id"))
    match: Mapped[str | None] = mapped_column(String(16))
    evidence: Mapped[list[str]] = mapped_column(JSON, default=list)
    contradictions: Mapped[list[str]] = mapped_column(JSON, default=list)
    replica_signals: Mapped[list[str]] = mapped_column(JSON, default=list)
    label_ocr: Mapped[str | None] = mapped_column(Text)
    condition_guess: Mapped[str | None] = mapped_column(String(32))
    needs_underside_photo: Mapped[bool] = mapped_column(Boolean, default=False)
    value_p25: Mapped[int | None] = mapped_column(Integer)
    value_median: Mapped[int | None] = mapped_column(Integer)
    value_p75: Mapped[int | None] = mapped_column(Integer)
    n_comps: Mapped[int] = mapped_column(Integer, default=0)
    value_level: Mapped[str | None] = mapped_column(String(32))
    transport_sek: Mapped[int | None] = mapped_column(Integer)
    net_margin_sek: Mapped[int | None] = mapped_column(Integer)
    roi: Mapped[float | None] = mapped_column(Float)
    distance_km: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[str | None] = mapped_column(String(8))
    decision: Mapped[str | None] = mapped_column(String(16))  # FYND | KOLLA_SJALV | INGET
    note: Mapped[str | None] = mapped_column(Text)
    llm_model: Mapped[str | None] = mapped_column(String(64))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    raw: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    label: Mapped[str] = mapped_column(String(32))  # köpt | ej_intressant | fel_modell | replika | bra_men_såld
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int | None] = mapped_column(ForeignKey("listings.id"))
    model_id: Mapped[int | None] = mapped_column(ForeignKey("models.id"))
    title: Mapped[str] = mapped_column(String(512))
    bought_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    purchase_sek: Mapped[int] = mapped_column(Integer, default=0)
    costs_sek: Mapped[int] = mapped_column(Integer, default=0)
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sale_sek: Mapped[int | None] = mapped_column(Integer)
    fees_sek: Mapped[int] = mapped_column(Integer, default=0)
    hours: Mapped[float] = mapped_column(Float, default=0.0)
    note: Mapped[str | None] = mapped_column(Text)


class SettingsRow(Base):
    """Single-row table with the owner's tunable thresholds."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    home_lat: Mapped[float] = mapped_column(Float, default=57.7089)  # Göteborg until set
    home_lon: Mapped[float] = mapped_column(Float, default=11.9746)
    max_distance_km: Mapped[float] = mapped_column(Float, default=150.0)
    allowed_regions: Mapped[list[str]] = mapped_column(JSON, default=list)
    min_net_margin_sek: Mapped[int] = mapped_column(Integer, default=1500)
    min_roi: Mapped[float] = mapped_column(Float, default=0.5)
    net_ratio: Mapped[float] = mapped_column(Float, default=0.78)
    fixed_fees_sek: Mapped[int] = mapped_column(Integer, default=500)
    transport_base_sek: Mapped[int] = mapped_column(Integer, default=300)
    transport_sek_per_km: Mapped[float] = mapped_column(Float, default=3.0)
    max_listing_price_sek: Mapped[int] = mapped_column(Integer, default=30000)
    daily_ai_budget_usd: Mapped[float] = mapped_column(Float, default=2.0)
    quiet_hours_start: Mapped[int] = mapped_column(Integer, default=22)
    quiet_hours_end: Mapped[int] = mapped_column(Integer, default=7)


class SourceHealth(Base):
    __tablename__ = "source_health"

    source: Mapped[str] = mapped_column(String(32), primary_key=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_item_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)
    stopped_reason: Mapped[str | None] = mapped_column(String(32))  # 403 | 429 | captcha | ...
    stopped_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    alerted: Mapped[bool] = mapped_column(Boolean, default=False)


class AICall(Base):
    __tablename__ = "ai_calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    purpose: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(64))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    cache_read_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cache_write_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)


class Job(Base):
    """SQLite-backed job queue (no Redis/Celery)."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)  # pending|running|done|failed
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class TelegramMessage(Base):
    """Maps sent alerts to listings so button presses can be recorded and marked handled."""

    __tablename__ = "telegram_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    chat_id: Mapped[str] = mapped_column(String(64))
    message_id: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
