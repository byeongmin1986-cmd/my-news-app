"""
CompuGhana  —  compughana.com  (WooCommerce)

전략:
  1순위: WooCommerce Store API  /wp-json/wc/store/v1/products  (공개)
  2순위: WooCommerce REST  API  /wp-json/wc/v3/products        (공개이면)
  3순위: HTML 파싱 (ScraperAPI 경유)
"""
from __future__ import annotations

import logging

import requests

from crawler.base import BaseCrawler, SCRAPERAPI_KEY, SCRAPERAPI_URL

logger = logging.getLogger(__name__)

BASE = "https://www.compughana.com"
WC_STORE = f"{BASE}/wp-json/wc/store/v1/products"
WC_REST  = f"{BASE}/wp-json/wc/v3/products"

SEARCH_URLS = [
    f"{BASE}/product-category/monitors/",
    f"{BASE}/product-category/computer-monitors/",
    f"{BASE}/?s=monitor&post_type=product",
    f"{BASE}/?s=LED+monitor&post_type=product",
    f"{BASE}/?s=desktop+monitor&post_type=product",
]
SEL = {
    "product":   "ul.products li.product",
    "title":     ".woocommerce-loop-product__title",
    "price":     ".price .woocommerce-Price-amount",
    "link":      "a.woocommerce-loop-product__link",
    "image":     ".wp-post-image, img.attachment-woocommerce_thumbnail",
    "next_page": "a.next.page-numbers",
    "stock":     ".stock",
}


class CompuGhanaCrawler(BaseCrawler):
    country  = "Ghana"
    retailer = "CompuGhana"
    base_url = BASE
    currency = "GHS"

    def scrape(self) -> list[dict]:
        seen: dict[str, dict] = {}

        # 1순위: WC Store API (인증 불필요, 직접 요청)
        products = self._wc_store_api()
        if products:
            logger.info(f"[CompuGhana] WC Store API → {len(products)}")
            for p in products:
                seen[p["product_url"]] = p

        # 2순위: WC REST API
        if not seen:
            products = self._wc_rest_api()
            if products:
                logger.info(f"[CompuGhana] WC REST API → {len(products)}")
                for p in products:
                    seen[p["product_url"]] = p

        # 3순위: HTML (ScraperAPI 경유)
        if not seen:
            logger.info("[CompuGhana] APIs failed → HTML scraping via ScraperAPI")
            for start in SEARCH_URLS:
                self._crawl_html(start, seen)

        logger.info(f"[CompuGhana] total unique: {len(seen)}")
        return list(seen.values())

    # ── WooCommerce Store API ────────────────────────────────
    def _wc_store_api(self) -> list[dict]:
        products, page = [], 1
        while page <= self.max_pages:
            try:
                r = requests.get(WC_STORE,
                    params={"search": "monitor", "per_page": 100, "page": page},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=20)
                if r.status_code != 200:
                    logger.warning(f"[CompuGhana] Store API {r.status_code}")
                    return []
                data = r.json()
                if not data:
                    break
                for item in data:
                    p = self._from_store_item(item)
                    if p:
                        products.append(p)
                page += 1
            except Exception as e:
                logger.warning(f"[CompuGhana] Store API err: {e}")
                return []
        return products

    def _from_store_item(self, item: dict) -> dict | None:
        name = item.get("name", "")
        if not self.is_monitor(name):
            return None
        prices = item.get("prices", {})
        raw = prices.get("price") or item.get("price", "")
        try:
            # WC Store API는 최소 단위로 반환 (e.g. 120000 = 1200.00 GHS)
            price = float(raw) / 100
        except (TypeError, ValueError):
            price = None
        imgs = item.get("images", [])
        return self.make_product(
            product_title=name,
            price=price,
            product_url=item.get("permalink", ""),
            image_url=imgs[0].get("src") if imgs else None,
            description=item.get("short_description", ""),
        )

    # ── WooCommerce REST API ─────────────────────────────────
    def _wc_rest_api(self) -> list[dict]:
        products, page = [], 1
        while page <= self.max_pages:
            try:
                r = requests.get(WC_REST,
                    params={"search": "monitor", "per_page": 100, "page": page},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=20)
                if r.status_code == 401:
                    logger.info("[CompuGhana] REST API requires auth")
                    return []
                if r.status_code != 200:
                    return []
                data = r.json()
                if not data:
                    break
                for item in data:
                    name = item.get("name", "")
                    if not self.is_monitor(name):
                        continue
                    imgs = item.get("images", [])
                    products.append(self.make_product(
                        product_title=name,
                        price=item.get("price") or item.get("regular_price", ""),
                        product_url=item.get("permalink", ""),
                        image_url=imgs[0].get("src") if imgs else None,
                        description=item.get("short_description", ""),
                    ))
                page += 1
            except Exception as e:
                logger.warning(f"[CompuGhana] REST API err: {e}")
                return []
        return products

    # ── HTML 파싱 (ScraperAPI 경유) ──────────────────────────
    def _crawl_html(self, start_url: str, seen: dict):
        url, page_num = start_url, 1
        while url and page_num <= self.max_pages:
            soup = self.soup(url)
            if soup is None:
                break
            items = soup.select(SEL["product"])
            if not items:
                break
            found = []
            for item in items:
                try:
                    link = item.select_one(SEL["link"])
                    if not link:
                        continue
                    href = link.get("href", "")
                    purl = href if href.startswith("http") else self.base_url + href

                    tt = item.select_one(SEL["title"])
                    title = tt.get_text(strip=True) if tt else link.get_text(strip=True)
                    if not title or not self.is_monitor(title):
                        continue

                    pe = item.select_one(SEL["price"])
                    price_text = None
                    if pe:
                        ins = pe.select_one("ins .woocommerce-Price-amount")
                        price_text = (ins or pe).get_text(strip=True)

                    img = item.select_one(SEL["image"])
                    image_url = None
                    if img:
                        image_url = img.get("data-src") or img.get("data-lazy-src") or img.get("src")

                    st = item.select_one(SEL["stock"])
                    found.append(self.make_product(
                        product_title=title,
                        price=price_text,
                        product_url=purl,
                        image_url=image_url,
                        availability=st.get_text(strip=True) if st else "unknown",
                    ))
                except Exception as e:
                    logger.debug(f"[CompuGhana] item err: {e}")

            logger.info(f"[CompuGhana] HTML pg {page_num}: {len(found)}")
            for p in found:
                if p.get("product_url"):
                    seen[p["product_url"]] = p

            nxt = soup.select_one(SEL["next_page"])
            if nxt and nxt.get("href"):
                url = nxt["href"]
            elif "/page/" in url:
                url = url.replace(f"/page/{page_num}/", f"/page/{page_num+1}/")
            else:
                url = url.rstrip("/") + f"/page/{page_num+1}/"
            page_num += 1
