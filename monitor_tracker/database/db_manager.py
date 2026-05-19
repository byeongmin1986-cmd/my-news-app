import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from database.models import (
    CREATE_MONITORS_TABLE, CREATE_CRAWL_LOGS_TABLE,
    CREATE_INDEXES, UPSERT_MONITOR,
)

logger = logging.getLogger(__name__)

_DEFAULT_DB = Path(__file__).parent.parent / "data" / "monitors.db"


class DatabaseManager:
    def __init__(self, db_path: Path = _DEFAULT_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute(CREATE_MONITORS_TABLE)
            conn.execute(CREATE_CRAWL_LOGS_TABLE)
            for idx in CREATE_INDEXES:
                conn.execute(idx)

    def upsert_monitor(self, data: dict) -> bool:
        try:
            with self._get_conn() as conn:
                cur = conn.execute("SELECT id FROM monitors WHERE product_url = ?", (data["product_url"],))
                is_new = cur.fetchone() is None
                conn.execute(UPSERT_MONITOR, data)
                return is_new
        except sqlite3.Error as e:
            logger.error(f"DB upsert error: {e}")
            return False

    def bulk_upsert(self, records: list[dict]) -> tuple[int, int]:
        new_c = upd_c = 0
        for r in records:
            if self.upsert_monitor(r):
                new_c += 1
            else:
                upd_c += 1
        return new_c, upd_c

    def log_crawl(self, site: str, country: str, status: str,
                  products_found: int = 0, error_message: Optional[str] = None,
                  started_at: Optional[str] = None):
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO crawl_logs
                   (site, country, status, products_found, error_message, started_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (site, country, status, products_found, error_message,
                 started_at, datetime.now().isoformat()),
            )

    def total_products(self) -> int:
        with self._get_conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM monitors").fetchone()[0]
