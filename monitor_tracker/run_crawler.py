"""
run_crawler.py -- GitHub Actions 실행 진입점

환경변수:
  SCRAPERAPI_KEY  ScraperAPI 키 (없으면 직접 요청)

사용법:
  python run_crawler.py              # 전체
  python run_crawler.py kenya_jumia  # 특정 사이트만
"""
from __future__ import annotations
import csv, logging, os, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from database.db_manager import DatabaseManager

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

CRAWLERS = {
    "kenya_jumia":     {"module": "crawler.kenya_jumia",    "class": "JumiaKenyaCrawler",   "label": "Jumia Kenya"},
    "nigeria_jumia":   {"module": "crawler.nigeria_jumia",  "class": "JumiaNigeriaCrawler", "label": "Jumia Nigeria"},
    "ghana_compughana":{"module": "crawler.ghana_compughana","class": "CompuGhanaCrawler",  "label": "CompuGhana"},
}

DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH = DATA_DIR / "monitors.csv"
DB       = DatabaseManager(DATA_DIR / "monitors.db")


def load_crawler(key: str):
    import importlib
    cfg = CRAWLERS[key]
    mod = importlib.import_module(cfg["module"])
    return getattr(mod, cfg["class"])(max_pages=int(os.environ.get("MAX_PAGES", "10")))


def append_csv(records: list[dict]):
    if not records:
        return
    write_header = not CSV_PATH.exists()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        if write_header:
            w.writeheader()
        w.writerows(records)


def main():
    site_filter = sys.argv[1] if len(sys.argv) > 1 else None
    key = os.environ.get("SCRAPERAPI_KEY", "")
    logger.info(f"Mode: {'ScraperAPI proxy' if key else 'Direct (residential IP only)'}")

    targets = {site_filter: CRAWLERS[site_filter]} if site_filter else CRAWLERS

    for site_key, cfg in targets.items():
        logger.info("=" * 60)
        logger.info(f"START: {cfg['label']}")
        started = datetime.now().isoformat()
        try:
            crawler  = load_crawler(site_key)
            products = crawler.scrape()
            logger.info(f"Scraped {len(products)} products")
            if products:
                new_c, upd_c = DB.bulk_upsert(products)
                append_csv(products)
                logger.info(f"DB: {new_c} new / {upd_c} updated")
                DB.log_crawl(site=site_key, country=crawler.country,
                             status="success", products_found=len(products), started_at=started)
            else:
                logger.warning(f"No products from {site_key}")
                DB.log_crawl(site=site_key, country="", status="empty", started_at=started)
        except Exception as e:
            logger.error(f"[{site_key}] FAILED: {e}", exc_info=True)
            DB.log_crawl(site=site_key, country="", status="error",
                         error_message=str(e), started_at=started)

    logger.info(f"DONE  DB_total={DB.total_products()}  CSV={CSV_PATH}")


if __name__ == "__main__":
    main()
