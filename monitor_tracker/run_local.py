"""
run_local.py — 로컬 PC에서 크롤러 실행 진입점

반드시 로컬 PC(일반 인터넷)에서 실행해야 합니다.
클라우드 서버에서는 Jumia/CompuGhana WAF에 차단됩니다.

사용법:
  python run_local.py                        # 모든 사이트
  python run_local.py --site kenya_jumia     # 특정 사이트만
  python run_local.py --headless false       # 브라우저 창 표시 (디버그용)
  python run_local.py --pages 3             # 사이트당 최대 3페이지
  python run_local.py --push                # 완료 후 GitHub에 자동 push
"""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from database.db_manager import DatabaseManager

# 로그 설정
LOG_FILE = ROOT / "logs" / f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger("run_local")

# 사용 가능한 크롤러 목록
CRAWLERS = {
    "kenya_jumia": {
        "module": "crawler.kenya_jumia",
        "class":  "JumiaKenyaCrawler",
        "label":  "Jumia Kenya (jumia.co.ke)",
    },
    "nigeria_jumia": {
        "module": "crawler.nigeria_jumia",
        "class":  "JumiaNigeriaCrawler",
        "label":  "Jumia Nigeria (jumia.com.ng)",
    },
    "ghana_compughana": {
        "module": "crawler.ghana_compughana",
        "class":  "CompuGhanaCrawler",
        "label":  "CompuGhana (compughana.com)",
    },
}


def load_crawler(key: str, headless: bool, max_pages: int):
    import importlib
    cfg = CRAWLERS[key]
    mod = importlib.import_module(cfg["module"])
    cls = getattr(mod, cfg["class"])
    return cls(headless=headless, max_pages=max_pages)


def run_all(site_filter: str | None, headless: bool, max_pages: int) -> int:
    db = DatabaseManager()
    total = 0

    targets = (
        {site_filter: CRAWLERS[site_filter]}
        if site_filter
        else CRAWLERS
    )

    for key, cfg in targets.items():
        logger.info("=" * 60)
        logger.info(f"START: {cfg['label']}")
        logger.info("=" * 60)
        started = datetime.now().isoformat()

        try:
            crawler = load_crawler(key, headless, max_pages)
            products = crawler.scrape()
            logger.info(f"Scraped {len(products)} products")

            if products:
                new_c, upd_c = db.bulk_upsert(products)
                logger.info(f"DB: {new_c} new, {upd_c} updated")
                db.log_crawl(
                    site=key,
                    country=crawler.country,
                    status="success",
                    products_found=len(products),
                    started_at=started,
                )
                total += len(products)
            else:
                logger.warning(f"No products from {key}")
                db.log_crawl(site=key, country="", status="empty", started_at=started)

        except Exception as e:
            logger.error(f"Crawler [{key}] failed: {e}", exc_info=True)
            db.log_crawl(site=key, country="", status="error",
                         error_message=str(e), started_at=started)

    logger.info("=" * 60)
    logger.info(f"DONE — total scraped: {total} | DB total: {db.total_products()}")
    logger.info(f"Log: {LOG_FILE}")
    return total


def push_to_github():
    """DB 파일을 git commit & push."""
    logger.info("Pushing DB to GitHub...")
    repo = ROOT.parent
    cmds = [
        ["git", "-C", str(repo), "add", "monitor_tracker/data/monitors.db"],
        ["git", "-C", str(repo), "commit", "-m",
         f"data: weekly monitor price update {datetime.now().strftime('%Y-%m-%d')}"],
        ["git", "-C", str(repo), "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"git error: {result.stderr}")
        else:
            logger.info(f"git ok: {' '.join(cmd[3:])}")


def main():
    parser = argparse.ArgumentParser(description="Monitor Price Crawler — run on local PC")
    parser.add_argument("--site", choices=list(CRAWLERS.keys()), help="특정 사이트만 크롤링")
    parser.add_argument("--headless", default="true", choices=["true", "false"],
                        help="브라우저 창 숨김 여부 (false=디버그용 창 표시)")
    parser.add_argument("--pages", type=int, default=10, help="사이트당 최대 페이지 수")
    parser.add_argument("--push", action="store_true", help="완료 후 GitHub에 자동 push")
    args = parser.parse_args()

    headless = args.headless.lower() == "true"
    total = run_all(args.site, headless, args.pages)

    if args.push and total > 0:
        push_to_github()
        logger.info("GitHub push complete. Streamlit Cloud will update shortly.")
    elif args.push and total == 0:
        logger.warning("No data scraped — skipping GitHub push.")


if __name__ == "__main__":
    main()
