"""Process-level configuration (env / .env). Tunable business thresholds live in the DB `settings` row."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///data/fyndjakt.db"

    # Anthropic. Verify ids and prices against Anthropic's docs when changing them.
    anthropic_api_key: str | None = None
    model_fast: str = "claude-haiku-4-5"
    model_strong: str = "claude-sonnet-5-5"
    # USD per million tokens: (input, output). Cache reads ~0.1x input, cache writes ~1.25x input.
    model_prices: dict[str, tuple[float, float]] = {
        "claude-haiku-4-5": (1.0, 5.0),
        "claude-sonnet-5-5": (2.0, 10.0),
    }
    # Sending listing image URLs to the AI (and Telegram) makes those services fetch images from
    # the listing site. Keep off unless that access is covered (see docs/recon/blocket_tillstand.md).
    ai_send_listing_images: bool = False

    # Telegram
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_webhook_secret: str | None = None

    # Ingest (/ingest/listing) bearer token
    ingest_token: str | None = None

    # Sources
    user_agent: str = "Fyndjakt/0.1 (internal furniture alerts)"
    auctionet_min_interval_s: float = 5.0
    # Blocket poller is not built. Stays false until permission is documented.
    blocket_enabled: bool = False

    municipalities_csv: str = "data/kommuner.csv"
    timezone: str = "Europe/Stockholm"


@lru_cache
def get_config() -> Config:
    return Config()
