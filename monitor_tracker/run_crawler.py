"""
run_crawler.py  — GitHub Actions / 로컬 실행 진입점

환경변수:
  SCRAPERAPI_KEY  ScraperAPI 키 (없으면 직접 요청 — 로컬 PC에서만 동작)

사용법:
  python run_crawler.py              # 전체 실행
  python run_crawler.py kenya_jumia  # 특정 사이트만
"""
from __future__ import annotations

import csv
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from database.db_manager import DatabaseManager

# ── 로그 설정 ──────────────────────────────────────────────────
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("run_crawler")

# ── 크롤러 목록 ────────────────────────────────────────────────
CRAWLERS = {
    "kenya_jumia": {
        "module": "crawler.kenya_jumia",
        "class":  "JumiaKenyaCrawler",
        "label":  "Jumia Kenya",
    },
    "nigeria_jumia": {
        "module": "crawler.nigeria_jumia",
        "class":  "JumiaNigeriaCrawler",
        "label":  "Jumia Nigeria",
    },
    "ghana_compughana": {
        "module": "crawler.ghana_compughana",
        "class":  "CompuGhanaCrawler",
        "label":  "CompuGhana",
    },
}

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "monitors.csv"
DB = DatabaseManager(DATA_DIR / "monitors.db")


def load_crawler(key: str):
    import importlib
    cfg = CRAWLERS[key]
    mod = importlib.import_module(cfg["module"])
    cls = getattr(mod, cfg["class"])
    return cls(max_pages=int(os.environ.get("MAX_PAGES", "10")))


def append_csv(records: list[dict]):
    """수집 결과를 CSV에 추가 (없으면 생성)."""
    if not records:
        return
    fieldnames = list(records[0].keys())
    write_header = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(records)


def main():
    site_filter = sys.argv[1] if len(sys.argv) > 1 else None
    scraperapi_key = os.environ.get("SCRAPERAPI_KEY", "")

    if scraperapi_key:
        logger.info("Mode: ScraperAPI residential proxy (cloud runner OK)")
    else:
        logger.info("Mode: Direct request (로컬 PC residential IP 필요)")

    total_new = total_upd = 0
    run_start = datetime.now().isoformat()

    targets = (
        {site_filter: CRAWLERS[site_filter]} if site_filter else CRAWLERS
    )

    for key, cfg in targets.items():
        logger.info("=" * 60)
        logger.info(f"START: {cfg['label']}")
        started = datetime.now().isoformat()

        try:
            crawler  = load_crawler(key)
            products = crawler.scrape()
            logger.info(f"Scraped {len(products)} products")

            if products:
                new_c, upd_c = DB.bulk_upsert(products)
                append_csv(products)
                logger.info(f"DB: {new_c} new / {upd_c} updated")
                total_new += new_c
                total_upd += upd_c
                DB.log_crawl(site=key, country=crawler.country,
                             status="success", products_found=len(products),
                             started_at=started)
            else:
                logger.warning(f"No products from {key}")
                DB.log_crawl(site=key, country="",
                             status="empty", started_at=started)

        except Exception as e:
            logger.error(f"[{key}] FAILED: {e}", exc_info=True)
            DB.log_crawl(site=key, country="", status="error",
                         error_message=str(e), started_at=started)

    logger.info("=" * 60)
    logger.info(f"DONE  new={total_new}  updated={total_upd}  DB_total={DB.total_products()}")
    logger.info(f"CSV: {CSV_PATH}")
    logger.info(f"Log: {LOG_FILE}")


if __name__ == "__main__":
    main()
