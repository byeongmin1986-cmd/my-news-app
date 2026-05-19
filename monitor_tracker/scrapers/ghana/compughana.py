"""
CompuGhana scraper (compughana.com)

WooCommerce 기반 사이트.
사이트 구조가 바뀌면 SELECTORS 딕셔너리만 수정하세요.
"""
import logging

from scrapers.base_scraper import BaseScraper
from config.settings import SCRAPER_CONFIG

logger = logging.getLogger(__name__)

# ─── 사이트 구조가 바뀌면 여기만 수정 ───────────────────────────
SELECTORS = {
    "product_list": "ul.products li.product, .products .product-item",
    "title": ".woocommerce-loop-product__title, h2.product-title, h3.product-title",
    "price": ".woocommerce-Price-amount, .price .amount, .product-price",
    "link": "a.woocommerce-loop-product__link, a.product-item-link, h2 a, h3 a",
    "image": "img.attachment-woocommerce_thumbnail, img.product-image, .wp-post-image",
    "availability": ".stock, .availability",
    "pagination_next": "a.next.page-numbers, .next-page a, a[rel='next']",
}

SEARCH_URLS = [
    "{base}/product-category/monitors/",
    "{base}/product-category/computer-monitors/",
    "{base}/?s=monitor&post_type=product",
    "{base}/?s=desktop+monitor&post_type=product",
    "{base}/?s=LED+monitor&post_type=product",
]
# ─────────────────────────────────────────────────────────────────


class CompuGhanaScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            country="Ghana",
            retailer="CompuGhana",
            base_url="https://www.compughana.com",
            currency="GHS",
        )

    def scrape(self) -> list[dict]:
        products = {}

        for url_template in SEARCH_URLS:
            start_url = url_template.format(base=self.base_url)
            logger.info(f"[CompuGhana] Crawling: {start_url}")
            found = self._scrape_listing(start_url)
            for p in found:
                products[p["product_url"]] = p
            logger.info(f"[CompuGhana] Subtotal so far: {len(products)}")

        result = list(products.values())
        logger.info(f"[CompuGhana] Total unique products: {len(result)}")
        return result

    def _scrape_listing(self, start_url: str) -> list[dict]:
        products = []
        url = start_url
        page = 1

        while url and page <= SCRAPER_CONFIG["max_pages"]:
            logger.debug(f"[CompuGhana] Page {page}: {url}")
            soup = self.fetch(url)
            if soup is None:
                break

            items = soup.select(SELECTORS["product_list"])
            if not items:
                logger.info(f"[CompuGhana] No products on page {page}, stopping.")
                break

            for item in items:
                product = self._parse_product(item)
                if product:
                    products.append(product)

            # 다음 페이지 찾기
            next_btn = soup.select_one(SELECTORS["pagination_next"])
            if next_btn and next_btn.get("href"):
                url = next_btn["href"]
                page += 1
            else:
                # WooCommerce 기본 페이지 번호 방식
                if "/page/" in url:
                    url = url.replace(f"/page/{page}/", f"/page/{page+1}/")
                else:
                    # URL에 /page/2/ 추가
                    base = url.rstrip("/")
                    url = f"{base}/page/{page+1}/"
                page += 1

        return products

    def _parse_product(self, item) -> dict | None:
        try:
            # 링크
            link_tag = item.select_one(SELECTORS["link"])
            if not link_tag:
                return None
            product_url = link_tag.get("href", "")
            if not product_url:
                return None
            if not product_url.startswith("http"):
                product_url = self.base_url + product_url

            # 제목
            title_tag = item.select_one(SELECTORS["title"])
            title = title_tag.get_text(strip=True) if title_tag else ""
            if not title:
                # 링크 텍스트 시도
                title = link_tag.get_text(strip=True)
            if not title or not self.is_monitor_product(title):
                return None

            # 가격 (WooCommerce는 ins 태그 안에 최종 가격)
            price_text = None
            price_container = item.select_one(SELECTORS["price"])
            if price_container:
                ins_tag = price_container.select_one("ins .woocommerce-Price-amount")
                if ins_tag:
                    price_text = ins_tag.get_text(strip=True)
                else:
                    price_text = price_container.get_text(strip=True)

            # 이미지
            img_tag = item.select_one(SELECTORS["image"])
            image_url = None
            if img_tag:
                image_url = (
                    img_tag.get("data-src")
                    or img_tag.get("data-lazy-src")
                    or img_tag.get("src")
                )

            # 재고 상태
            avail_tag = item.select_one(SELECTORS["availability"])
            availability = avail_tag.get_text(strip=True) if avail_tag else "unknown"

            return self.build_product(
                product_title=title,
                price=price_text,
                availability=availability,
                product_url=product_url,
                image_url=image_url,
                description=title,
            )

        except Exception as e:
            logger.warning(f"[CompuGhana] Parse error: {e}")
            return None
