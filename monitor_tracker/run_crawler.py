"""
run_crawler.py -- GitHub Actions 실행 진입점
각 사이트 결과를 crawl_status.json에 저장 → Streamlit에서 바로 확인 가능
"""
from __future__ import annotations
import csv, json, logging, os, sys
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
    "kenya_jumia":      {"module": "crawler.kenya_jumia",     "class": "JumiaKenyaCrawler",   "label": "Jumia Kenya"},
    "nigeria_jumia":    {"module": "crawler.nigeria_jumia",   "class": "JumiaNigeriaCrawler", "label": "Jumia Nigeria"},
    "ghana_compughana": {"module": "crawler.ghana_compughana","class": "CompuGhanaCrawler",   "label": "CompuGhana"},
}

DATA_DIR    = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
CSV_PATH    = DATA_DIR / "monitors.csv"
STATUS_PATH = DATA_DIR / "crawl_status.json"
DB          = DatabaseManager(DATA_DIR / "monitors.db")


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


def _count_csv_rows() -> int:
    if not CSV_PATH.exists():
        return 0
    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            return max(0, sum(1 for _ in f) - 1)
    except Exception:
        return 0


def update_status(site_key: str, site_label: str, products: int,
                  site_status: str, error: str | None = None):
    """사이트별 결과를 crawl_status.json에 누적 업데이트 (Streamlit에서 읽음)."""
    existing: dict = {}
    if STATUS_PATH.exists():
        try:
            with open(STATUS_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            pass

    sites: dict = existing.get("sites", {})
    sites[site_key] = {
        "label":    site_label,
        "status":   site_status,
        "products": products,
        "error":    error,
        "time":     datetime.now().isoformat(),
    }

    total    = sum(s["products"] for s in sites.values())
    statuses = [s["status"] for s in sites.values()]
    if total == 0:
        overall = "failed"
    elif all(s == "success" for s in statuses):
        overall = "success"
    else:
        overall = "partial"

    data = {
        "last_run":       datetime.now().isoformat(),
        "overall_status": overall,
        "total_products": total,
        "csv_exists":     CSV_PATH.exists(),
        "csv_rows":       _count_csv_rows(),
        "sites":          sites,
    }

    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"crawl_status.json: {overall} / 에 {total}개")


def main():
    site_filter = sys.argv[1] if len(sys.argv) > 1 else None
    api_key     = os.environ.get("SCRAPERAPI_KEY", "")

    if not api_key:
        logger.warning("=" * 60)
        logger.warning("SCRAPERAPI_KEY 없음 — 클라우드 IP는 WAF에 의해 차단됩니다")
        logger.warning("=" * 60)

    logger.info(f"Mode: {'ScraperAPI proxy' if api_key else 'Direct request (WAF will block)'}")

    targets        = {site_filter: CRAWLERS[site_filter]} if site_filter else CRAWLERS
    total_products = 0

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
                total_products += len(products)
                logger.info(f"DB: {new_c} new / {upd_c} updated")
                DB.log_crawl(site=site_key, country=crawler.country,
                             status="success", products_found=len(products), started_at=started)
                update_status(site_key, cfg["label"], len(products), "success")
            else:
                logger.warning(f"0 products from {site_key} — WAF 차단 또는 빈 카테고리")
                DB.log_crawl(site=site_key, country="", status="empty", started_at=started)
                update_status(site_key, cfg["label"], 0, "empty")

        except Exception as e:
            err = str(e)
            logger.error(f"[{site_key}] FAILED: {err}", exc_info=True)
            DB.log_crawl(site=site_key, country="", status="error",
                         error_message=err, started_at=started)
            update_status(site_key, cfg["label"], 0, "error", error=err[:500])

    logger.info("=" * 60)
    logger.info(f"DONE  total={total_products}  DB_total={DB.total_products()}  CSV={CSV_PATH}")

    if total_products == 0:
        logger.error("0개 수집 — exit code 1")
        sys.exit(1)


if __name__ == "__main__":
    main()
