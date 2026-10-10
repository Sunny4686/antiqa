"""Nightly SQLite backup (online backup API, safe with WAL). Keeps the newest N copies."""

import sqlite3
from datetime import datetime
from pathlib import Path


def backup_sqlite(db_path: str | Path, backup_dir: str | Path, now: datetime, keep: int = 14) -> Path:
    out_dir = Path(backup_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"fyndjakt-{now:%Y%m%d-%H%M}.db"
    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(target)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    for old in sorted(out_dir.glob("fyndjakt-*.db"))[:-keep]:
        old.unlink(missing_ok=True)
    return target
