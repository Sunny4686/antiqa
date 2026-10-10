"""Process-level configuration (env / .env). Tunable business thresholds live in the DB `settings` row."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///data/fyndjakt.db"

    # Anthropic. Verify ids and prices against Anthropic's docs when changing them.
    anthropic_api_key: str | None = None
    # Screening + verification. Eval 2026-10-10 (40 cases, title masked to the furniture type, picture only):
    # Haiku 4.5 recall 5 %, Sonnet 5.5 recall 50 % (65 % right model among candidates), 0 false alarms on
    # ordinary furniture, 0.009 USD per listing. Recognising a model from the picture needs the stronger model.
    model_fast: str = "claude-sonnet-5-5"
    model_text: str = "claude-haiku-4-5"  # text-only work (comp title parsing in batches)
    model_strong: str = "claude-sonnet-5-5"
    # USD per million tokens: (input, output). Cache reads ~0.1x input, cache writes ~1.25x input.
    model_prices: dict[str, tuple[float, float]] = {
        "claude-haiku-4-5": (1.0, 5.0),
        "claude-sonnet-5-5": (2.0, 10.0),
    }
    # Downloads listing images (downscaled for the AI, URL to Telegram), i.e. requests to the listing
    # site's image CDN. Keep off unless that access is covered (see docs/recon/blocket_tillstand.md).
    ai_send_listing_images: bool = False
    image_cache_dir: str = "data/images"
    inbox_dir: str = "data/inbox"  # drop listing folders / CSV / zip here; see fyndjakt.importer
    capture_dir: str = "data/captures"  # screenshots from the browser extension, deleted once read

    # Telegram
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_webhook_secret: str | None = None
    # Local mode without a public URL: fetch button presses with getUpdates instead of the webhook.
    telegram_polling: bool = False

    # Ingest (/ingest/listing) bearer token
    ingest_token: str | None = None

    # Sources
    user_agent: str = "Fyndjakt/0.1 (internal furniture alerts)"
    auctionet_min_interval_s: float = 5.0
    # Ongoing Auctionet auctions as a deal source (same open API and pace as the comps).
    auctionet_live_enabled: bool = True
    auctionet_buyer_premium: float = 0.25  # buyer's premium incl. VAT; check the house's terms per lot
    auctionet_live_horizon_h: float = 48.0  # look at auctions ending within this window
    # Also image-screen lots the house didn't attribute ("FÅTÖLJ, 1960-tal"): the unknown-value case.
    auctionet_live_anonymous: bool = True
    # Blocket poller is not built. Stays false until permission is documented.
    blocket_enabled: bool = False

    municipalities_csv: str = "data/kommuner.csv"
    backup_dir: str = "data/backups"
    timezone: str = "Europe/Stockholm"


@lru_cache
def get_config() -> Config:
    return Config()
