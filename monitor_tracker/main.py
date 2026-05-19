"""
main.py - 모니터 가격 크롤러 실행 진입점

사용법:
  python main.py                         # 활성화된 모든 사이트 크롤링
  python main.py --country kenya         # 특정 국가만
  python main.py --site jumia_ke         # 특정 사이트만
  python main.py --dry-run               # DB 저장 없이 테스트
"""
import argparse
import importlib
import logging
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import SITES
from database.db_manager import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            Path(__file__).parent / "logs" / f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding="utf-8",
        ),
    ],
)
logger = logging.getLogger("main")


def load_scraper(country: str, site_key: str, site_cfg: dict):
    """설정에서 scraper 클래스를 동적으로 로드."""
    module_path = site_cfg["module"]
    class_name = site_cfg["class"]
    try:
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls()
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to load scraper {module_path}.{class_name}: {e}")
        return None


def run_scraper(scraper, db: DatabaseManager, site_key: str, country: str, dry_run: bool) -> int:
    """단일 scraper 실행 후 결과를 DB에 저장."""
    started_at = datetime.now().isoformat()
    logger.info(f"{'='*60}")
    logger.info(f"START: {country} / {site_key}")
    logger.info(f"{'='*60}")

    try:
        products = scraper.scrape()
        logger.info(f"Scraped {len(products)} products from {site_key}")

        if dry_run:
            logger.info("[DRY RUN] Skipping DB save. Sample:")
            for p in products[:3]:
                logger.info(f"  {p}")
            return len(products)

        if products:
            new_cnt, upd_cnt = db.bulk_upsert(products)
            logger.info(f"DB: {new_cnt} new, {upd_cnt} updated")
            db.log_crawl(
                site=site_key,
                country=country,
                status="success",
                products_found=len(products),
                started_at=started_at,
            )
        return len(products)

    except Exception as e:
        logger.error(f"Scraper error [{site_key}]: {e}", exc_info=True)
        if not dry_run:
            db.log_crawl(
                site=site_key,
                country=country,
                status="error",
                error_message=str(e),
                started_at=started_at,
            )
        return 0


def main():
    parser = argparse.ArgumentParser(description="Sub-Saharan Africa Monitor Price Tracker")
    parser.add_argument("--country", help="특정 국가만 크롤링 (예: kenya, ghana, nigeria)")
    parser.add_argument("--site", help="특정 사이트만 크롤링 (예: jumia_ke, compughana)")
    parser.add_argument("--dry-run", action="store_true", help="DB 저장 없이 테스트 실행")
    args = parser.parse_args()

    db = DatabaseManager()
    total_products = 0
    total_sites = 0

    # 로그 디렉토리 생성
    (Path(__file__).parent / "logs").mkdir(exist_ok=True)

    logger.info(f"Monitor Price Tracker started at {datetime.now()}")
    logger.info(f"DB: {db.db_path} | Total in DB: {db.total_products()}")

    for country, sites in SITES.items():
        # 국가 필터
        if args.country and country.lower() != args.country.lower():
            continue

        for site_key, site_cfg in sites.items():
            # 사이트 필터
            if args.site and site_key.lower() != args.site.lower():
                continue

            if not site_cfg.get("enabled", False):
                logger.info(f"SKIP (disabled): {country}/{site_key}")
                continue

            scraper = load_scraper(country, site_key, site_cfg)
            if scraper is None:
                continue

            count = run_scraper(scraper, db, site_key, country, args.dry_run)
            total_products += count
            total_sites += 1

    logger.info(f"{'='*60}")
    logger.info(f"DONE: {total_sites} sites, {total_products} products scraped")
    logger.info(f"Total in DB: {db.total_products()}")
    logger.info(f"{'='*60}")


if __name__ == "__main__":
    main()
