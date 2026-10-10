import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from fyndjakt import db
from fyndjakt.config import Config, get_config
from fyndjakt.migrate import upgrade

FIXTURES = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 10, 10, 12, 0, tzinfo=UTC)  # 14:00 in Stockholm


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # keep .env and data/ out of the repo
    for k, v in {
        "DATABASE_URL": f"sqlite:///{tmp_path}/test.db",
        "INGEST_TOKEN": "ingest-secret",
        "TELEGRAM_WEBHOOK_SECRET": "tg-secret",
        "TELEGRAM_CHAT_ID": "42",
        "ANTHROPIC_API_KEY": "",
        "TELEGRAM_BOT_TOKEN": "",
    }.items():
        monkeypatch.setenv(k, v)
    get_config.cache_clear()
    yield get_config()
    get_config.cache_clear()


@pytest.fixture
def config(env) -> Config:
    return env


@pytest.fixture
def session(env):
    upgrade(env.database_url)
    with db.session_scope() as s:
        yield s
