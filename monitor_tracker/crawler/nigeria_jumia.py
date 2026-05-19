"""
Jumia Nigeria -- jumia.com.ng
Jumia Kenya와 동일 구조, URL/통화만 다름.
"""
from __future__ import annotations
import json, logging
from crawler.base import BaseCrawler
logger = logging.getLogger(__name__)

SEARCH_URLS = [
    "https://www.jumia.com.ng/monitors/",
    "https://www.jumia.com.ng/computer-monitors/",
    "https://www.jumia.com.ng/catalog/?q=monitor",
    "https://www.jumia.com.ng/catalog/?q=computer+monitor",
    "https://www.jumia.com.ng/catalog/?q=LED+monitor",
]
SEL = {
    "product":   "article.prd-w",
    "title":     "h3.name",
    "price":     "div.prc",
    "link":      "a.core",
    "image":     "img.img-responsive",
    "next_page": "a[aria-label='Next Page']",
}

class JumiaNigeriaCrawler(BaseCrawler):
    country  = "Nigeria"
    retailer = "Jumia Nigeria"
    base_url = "https://www.jumia.com.ng"
    currency = "NGN"

    def scrape(self) -> list[dict]:
        seen: dict[str, dict] = {}
        for start_url in SEARCH_URLS:
            self._crawl_listing(start_url, seen)
        logger.info(f"[Jumia NG] total unique: {len(seen)}")
        return list(seen.values())

    def _crawl_listing(self, start_url: str, seen: dict):
        url, page_num = start_url, 1
        while url and page_num <= self.max_pages:
            soup = self.soup(url)
            if soup is None:
                break
            found = self._try_json_ld(soup) or self._parse_html(soup)
            logger.info(f"[Jumia NG] pg {page_num}: {len(found)} products")
            for p in found:
                if p.get("product_url"):
                    seen[p["product_url"]] = p
            url = self._next_url(soup, url, page_num)
            page_num += 1

    def _try_json_ld(self, soup) -> list[dict]:
        products = []
        for sc in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(sc.string or "")
                items = []
                if isinstance(data, dict):
                    if data.get("@type") == "ItemList":
                        items = [e.get("item", e) for e in data.get("itemListElement", [])]
                    elif data.get("@type") == "Product":
                        items = [data]
                for prod in items:
                    if prod.get("@type") != "Product":
                        continue
                    name = prod.get("name", "")
                    if not self.is_monitor(name):
                        continue
                    offer = prod.get("offers", {})
                    if isinstance(offer, list):
                        offer = offer[0] if offer else {}
                    url = prod.get("url", "")
                    if url and not url.startswith("http"):
                        url = self.base_url + url
                    img = prod.get("image")
                    products.append(self.make_product(
                        product_title=name,
                        price=offer.get("price"),
                        product_url=url,
                        image_url=(img[0] if isinstance(img, list) else img),
                        availability=offer.get("availability", "unknown"),
                    ))
            except Exception:
                continue
        return products

    def _parse_html(self, soup) -> list[dict]:
        products = []
        for art in soup.select(SEL["product"]):
            try:
                a = art.select_one(SEL["link"])
                if not a:
                    continue
                href = a.get("href", "")
                url  = href if href.startswith("http") else self.base_url + href
                t = art.select_one(SEL["title"])
                title = t.get_text(strip=True) if t else ""
                if not title or not self.is_monitor(title):
                    continue
                p   = art.select_one(SEL["price"])
                img = art.select_one(SEL["image"])
                products.append(self.make_product(
                    product_title=title,
                    price=p.get_text(strip=True) if p else None,
                    product_url=url,
                    image_url=img.get("data-src") or img.get("src") if img else None,
                ))
            except Exception as e:
                logger.debug(f"[Jumia NG] parse err: {e}")
        return products

    def _next_url(self, soup, current: str, page_num: int) -> str | None:
        btn = soup.select_one(SEL["next_page"])
        if btn and btn.get("href"):
            h = btn["href"]
            return h if h.startswith("http") else self.base_url + h
        if f"page={page_num}" in current:
            return current.replace(f"page={page_num}", f"page={page_num+1}")
        return None
