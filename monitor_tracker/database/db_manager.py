import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import DB_PATH
from database.models import (
    CREATE_MONITORS_TABLE,
    CREATE_CRAWL_LOGS_TABLE,
    CREATE_INDEXES,
    UPSERT_MONITOR,
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute(CREATE_MONITORS_TABLE)
            conn.execute(CREATE_CRAWL_LOGS_TABLE)
            for idx_sql in CREATE_INDEXES:
                conn.execute(idx_sql)

    def upsert_monitor(self, data: dict) -> bool:
        """Insert or update a monitor product. Returns True if new, False if updated."""
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "SELECT id FROM monitors WHERE product_url = ?",
                    (data["product_url"],),
                )
                is_new = cursor.fetchone() is None
                conn.execute(UPSERT_MONITOR, data)
                return is_new
        except sqlite3.Error as e:
            logger.error(f"DB upsert error for {data.get('product_url')}: {e}")
            return False

    def bulk_upsert(self, records: list[dict]) -> tuple[int, int]:
        """Bulk upsert. Returns (new_count, updated_count)."""
        new_count = updated_count = 0
        for record in records:
            if self.upsert_monitor(record):
                new_count += 1
            else:
                updated_count += 1
        return new_count, updated_count

    def log_crawl(
        self,
        site: str,
        country: str,
        status: str,
        products_found: int = 0,
        error_message: Optional[str] = None,
        started_at: Optional[str] = None,
    ):
        completed_at = datetime.now().isoformat()
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO crawl_logs
                   (site, country, status, products_found, error_message, started_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (site, country, status, products_found, error_message, started_at, completed_at),
            )

    def get_all_monitors(self) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM monitors ORDER BY crawl_date DESC").fetchall()
            return [dict(r) for r in rows]

    def get_monitors_by_country(self, country: str) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM monitors WHERE country = ? ORDER BY price ASC",
                (country,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_summary_stats(self) -> dict:
        with self._get_conn() as conn:
            stats = {}

            # 국가별 평균/최저가
            rows = conn.execute("""
                SELECT country, currency,
                       ROUND(AVG(price), 2) as avg_price,
                       MIN(price) as min_price,
                       MAX(price) as max_price,
                       COUNT(*) as total
                FROM monitors
                WHERE price IS NOT NULL AND price > 0
                GROUP BY country, currency
                ORDER BY country
            """).fetchall()
            stats["by_country"] = [dict(r) for r in rows]

            # 브랜드별 상품 수
            rows = conn.execute("""
                SELECT brand, COUNT(*) as count
                FROM monitors
                WHERE brand IS NOT NULL
                GROUP BY brand
                ORDER BY count DESC
                LIMIT 20
            """).fetchall()
            stats["by_brand"] = [dict(r) for r in rows]

            # 사이즈별 통계
            rows = conn.execute("""
                SELECT screen_size_inch,
                       ROUND(AVG(price), 2) as avg_price,
                       COUNT(*) as count
                FROM monitors
                WHERE screen_size_inch IS NOT NULL AND price IS NOT NULL AND price > 0
                GROUP BY screen_size_inch
                ORDER BY screen_size_inch
            """).fetchall()
            stats["by_size"] = [dict(r) for r in rows]

            # 사이트별 상품 수
            rows = conn.execute("""
                SELECT retailer, country, COUNT(*) as count,
                       MAX(crawl_date) as last_crawl
                FROM monitors
                GROUP BY retailer, country
                ORDER BY count DESC
            """).fetchall()
            stats["by_retailer"] = [dict(r) for r in rows]

            # 최근 크롤링 날짜
            row = conn.execute(
                "SELECT MAX(crawl_date) as last_crawl FROM monitors"
            ).fetchone()
            stats["last_crawl"] = row["last_crawl"] if row else None

            return stats

    def get_crawl_logs(self, limit: int = 50) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM crawl_logs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def total_products(self) -> int:
        with self._get_conn() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM monitors").fetchone()
            return row["cnt"]
