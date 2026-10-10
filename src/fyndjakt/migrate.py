"""Run Alembic migrations programmatically (on app start and from the CLI)."""

from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig

from fyndjakt.config import get_config
from fyndjakt.db import configure

ROOT = Path(__file__).resolve().parent / "migrations"


def alembic_config(url: str | None = None) -> AlembicConfig:
    cfg = AlembicConfig()
    cfg.set_main_option("script_location", str(ROOT))
    cfg.set_main_option("sqlalchemy.url", url or get_config().database_url)
    return cfg


def upgrade(url: str | None = None) -> None:
    configure(url)
    command.upgrade(alembic_config(url), "head")
