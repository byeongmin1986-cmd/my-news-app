"""
CompuGhana -- compughana.com (WooCommerce)
전략: 1순위 WC Store API (직접 + ScraperAPI), 2순위 HTML (ScraperAPI country_code=gh)
"""
from __future__ import annotations
import logging
import urllib.parse
import requests as _req
from crawler.base import BaseCrawler, SCRAPERAPI_KEY, SCRAPERAPI_URL
logger = logging.getLogger(__name__)

BASE     = "https://www.compughana.com"
WC_STORE = f"{BASE}/wp-json/wc/store/v1/products"
WC_REST  = f"{BASE}/wp-json/wc/v3/products"
SEARCH_URLS = [
    f"{BASE}/product-category/monitors/",
    f"{BASE}/product-category/computer-monitors/",
    f"{BASE}/?s=monitor&post_type=product",
    f"{BASE}/?s=display&post_type=product",
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
        for fn in [self._wc_store_api, self._wc_rest_api]:
            products = fn()
            if products:
                for p in products:
                    seen[p["product_url"]] = p
                logger.info(f"[CompuGhana] {fn.__name__} -> {len(products)}")
                break
        if not seen:
            logger.info("[CompuGhana] APIs failed -> HTML via ScraperAPI")
            for start in SEARCH_URLS:
                self._crawl_html(start, seen)
        logger.info(f"[CompuGhana] total: {len(seen)}")
        return list(seen.values())

    def _api_fetch(self, endpoint: str, params: dict) -> list | None:
        """WC REST/Store API 호출: direct 시도 후 ScraperAPI fallback."""
        # 1. Direct — WooCommerce Store API는 공개 엔드포인트라 WAF 없는 경우 많음
        try:
            r = _req.get(endpoint, params=params,
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
            logger.info(f"[CompuGhana] direct API HTTP {r.status_code} {endpoint}")
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    return data
        except Exception as e:
            logger.debug(f"[CompuGhana] direct API err: {e}")

        # 2. ScraperAPI fallback
        if SCRAPERAPI_KEY:
            full_url = endpoint + "?" + urllib.parse.urlencode(params)
            resp = self.get(full_url, country_code="gh")
            if resp and resp.status_code == 200:
                try:
                    data = resp.json()
                    if isinstance(data, list):
                        return data
                except Exception:
                    pass
        return None

    def _wc_store_api(self) -> list[dict]:
        products, page = [], 1
        while page <= self.max_pages:
            # No search filter first — get all products, filter locally
            data = self._api_fetch(WC_STORE, {"per_page": 100, "page": page})
            if data is None:
                # Retry with search=monitor
                data = self._api_fetch(WC_STORE, {"search": "monitor", "per_page": 100, "page": page})
            if not data:
                break
            found_this_page = 0
            for item in data:
                name = item.get("name", "")
                if not self._is_monitor_broad(name):
                    continue
                prices = item.get("prices", {})
                raw = prices.get("price") or item.get("price", "")
                try:
                    price = float(raw) / 100
                except (TypeError, ValueError):
                    price = None
                imgs = item.get("images", [])
                products.append(self.make_product(
                    product_title=name, price=price,
                    product_url=item.get("permalink", ""),
                    image_url=imgs[0].get("src") if imgs else None,
                ))
                found_this_page += 1
            logger.info(f"[CompuGhana] WC Store API pg {page}: {found_this_page} monitor items")
            if len(data) < 100:
                break
            page += 1
        return products

    def _wc_rest_api(self) -> list[dict]:
        products, page = [], 1
        while page <= self.max_pages:
            data = self._api_fetch(WC_REST, {"search": "monitor", "per_page": 100, "page": page})
            if data is None:
                data = self._api_fetch(WC_REST, {"per_page": 100, "page": page})
            if not data:
                break
            for item in data:
                name = item.get("name", "")
                if not self._is_monitor_broad(name):
                    continue
                imgs = item.get("images", [])
                products.append(self.make_product(
                    product_title=name,
                    price=item.get("price") or item.get("regular_price", ""),
                    product_url=item.get("permalink", ""),
                    image_url=imgs[0].get("src") if imgs else None,
                ))
            if len(data) < 100:
                break
            page += 1
        return products

    def _is_monitor_broad(self, title: str) -> bool:
        """CompuGhana 전용: Monitor/Display/Screen 포함하는지 넓게 확인."""
        kw = ["monitor", "display", "screen", "led", "lcd", "ips", "va ",
              "viewsonic", "benq", "dell", "lg monitor", "samsung monitor",
              "acer monitor", "hp monitor", "asus monitor",
              "24\"", "27\"", "32\"", "21.5", "23.8", "27 inch", "24 inch"]
        excl = ["television", " tv ", "phone", "tablet", "laptop", "projector",
                "printer", "keyboard", "mouse", "headphone", "speaker", "webcam"]
        t = f" {title.lower()} "
        return any(k in t for k in kw) and not any(e in t for e in excl)

    def _crawl_html(self, start_url: str, seen: dict):
        url, page_num = start_url, 1
        while url and page_num <= self.max_pages:
            soup = self.soup(url, country_code="gh")
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
                    tt   = item.select_one(SEL["title"])
                    title = tt.get_text(strip=True) if tt else link.get_text(strip=True)
                    if not title or not self._is_monitor_broad(title):
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
                        product_title=title, price=price_text,
                        product_url=purl, image_url=image_url,
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
