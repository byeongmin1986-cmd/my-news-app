"""
Jumia Nigeria scraper (jumia.com.ng)

Jumia Kenya scraper와 거의 동일한 구조.
사이트 구조가 바뀌면 SELECTORS 딕셔너리만 수정하세요.
"""
import logging

from scrapers.base_scraper import BaseScraper
from config.settings import SCRAPER_CONFIG

logger = logging.getLogger(__name__)

# ─── 사이트 구조가 바뀌면 여기만 수정 ───────────────────────────
SELECTORS = {
    "product_list": "article.prd-w",
    "title": "h3.name",
    "price": "div.prc",
    "link": "a.core",
    "image": "img.img-responsive",
    "badge": "div.bdg",
    "pagination_next": "a[aria-label='Next Page']",
}

SEARCH_URLS = [
    "{base}/catalog/?q=monitor",
    "{base}/catalog/?q=computer+monitor",
    "{base}/catalog/?q=gaming+monitor",
    "{base}/monitors/",
    "{base}/computer-monitors/",
    "{base}/catalog/?q=LED+monitor",
]
# ─────────────────────────────────────────────────────────────────


class JumiaNigeriaScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            country="Nigeria",
            retailer="Jumia Nigeria",
            base_url="https://www.jumia.com.ng",
            currency="NGN",
        )

    def scrape(self) -> list[dict]:
        products = {}

        for url_template in SEARCH_URLS:
            start_url = url_template.format(base=self.base_url)
            logger.info(f"[Jumia NG] Crawling: {start_url}")
            found = self._scrape_listing(start_url)
            for p in found:
                products[p["product_url"]] = p
            logger.info(f"[Jumia NG] Subtotal so far: {len(products)}")

        result = list(products.values())
        logger.info(f"[Jumia NG] Total unique products: {len(result)}")
        return result

    def _scrape_listing(self, start_url: str) -> list[dict]:
        products = []
        url = start_url
        page = 1

        while url and page <= SCRAPER_CONFIG["max_pages"]:
            logger.debug(f"[Jumia NG] Page {page}: {url}")
            soup = self.fetch(url)
            if soup is None:
                break

            articles = soup.select(SELECTORS["product_list"])
            if not articles:
                logger.info(f"[Jumia NG] No products on page {page}, stopping.")
                break

            for article in articles:
                product = self._parse_article(article)
                if product:
                    products.append(product)

            # 다음 페이지
            next_btn = soup.select_one(SELECTORS["pagination_next"])
            if next_btn and next_btn.get("href"):
                href = next_btn["href"]
                url = href if href.startswith("http") else self.base_url + href
                page += 1
            else:
                if "?" in url:
                    if f"page={page}" in url:
                        url = url.replace(f"page={page}", f"page={page+1}")
                    else:
                        url = url + f"&page={page+1}"
                else:
                    url = url + f"?page={page+1}"
                page += 1

        return products

    def _parse_article(self, article) -> dict | None:
        try:
            link_tag = article.select_one(SELECTORS["link"])
            if not link_tag:
                return None
            href = link_tag.get("href", "")
            if not href:
                return None
            product_url = href if href.startswith("http") else self.base_url + href

            title_tag = article.select_one(SELECTORS["title"])
            title = title_tag.get_text(strip=True) if title_tag else ""
            if not title or not self.is_monitor_product(title):
                return None

            price_tag = article.select_one(SELECTORS["price"])
            price_text = price_tag.get_text(strip=True) if price_tag else None

            img_tag = article.select_one(SELECTORS["image"])
            image_url = None
            if img_tag:
                image_url = img_tag.get("data-src") or img_tag.get("src")

            badge = article.select_one(SELECTORS["badge"])
            badge_text = badge.get_text(strip=True) if badge else None

            return self.build_product(
                product_title=title,
                price=price_text,
                availability="in stock" if badge_text != "sold out" else "out of stock",
                product_url=product_url,
                image_url=image_url,
                condition=f"{title} {badge_text or ''}",
                description=title,
            )

        except Exception as e:
            logger.warning(f"[Jumia NG] Parse error: {e}")
            return None
