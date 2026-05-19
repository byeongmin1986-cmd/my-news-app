"""
Jumia Nigeria crawler  —  jumia.com.ng

Jumia Kenya와 동일 구조. timezone/locale만 다름.
"""
from __future__ import annotations

import json
import logging
import random

from playwright.sync_api import sync_playwright

from crawler.base import BaseCrawler, _human_delay

logger = logging.getLogger(__name__)

SEARCH_URLS = [
    "https://www.jumia.com.ng/monitors/",
    "https://www.jumia.com.ng/computer-monitors/",
    "https://www.jumia.com.ng/catalog/?q=monitor",
    "https://www.jumia.com.ng/catalog/?q=computer+monitor",
    "https://www.jumia.com.ng/catalog/?q=LED+monitor",
]

SELECTORS = {
    "product":   "article.prd-w",
    "title":     "h3.name",
    "price":     "div.prc",
    "link":      "a.core",
    "image":     "img.img-responsive",
    "next_page": "a[aria-label='Next Page']",
}


class JumiaNigeriaCrawler(BaseCrawler):
    country     = "Nigeria"
    retailer    = "Jumia Nigeria"
    base_url    = "https://www.jumia.com.ng"
    currency    = "NGN"
    timezone_id = "Africa/Lagos"

    def scrape(self) -> list[dict]:
        results: dict[str, dict] = {}

        with sync_playwright() as pw:
            browser, ctx = self._new_context(pw)
            page = ctx.new_page()

            for start_url in SEARCH_URLS:
                url = start_url
                page_num = 1

                while url and page_num <= self.max_pages:
                    if not self.fetch_page(page, url):
                        break

                    found = self._extract_json_ld(page) or self._extract_html(page)
                    logger.info(f"[Jumia NG] page {page_num} → {len(found)} products")
                    for p in found:
                        if p.get("product_url"):
                            results[p["product_url"]] = p

                    url = self._next_page_url(page, url, page_num)
                    page_num += 1
                    _human_delay(2.0, 4.0)

            browser.close()

        out = list(results.values())
        logger.info(f"[Jumia NG] Total: {len(out)}")
        return out

    def _extract_json_ld(self, page) -> list[dict]:
        products = []
        for sc in page.query_selector_all("script[type='application/ld+json']"):
            try:
                data = json.loads(sc.inner_text())
                items = []
                if isinstance(data, dict):
                    if data.get("@type") == "ItemList":
                        items = data.get("itemListElement", [])
                    elif data.get("@type") == "Product":
                        items = [data]
                for item in items:
                    prod = item.get("item", item)
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
                    image = prod.get("image")
                    if isinstance(image, list):
                        image = image[0] if image else None
                    products.append(self.make_product(
                        product_title=name,
                        price=offer.get("price"),
                        product_url=url,
                        image_url=image,
                        availability=offer.get("availability", "unknown"),
                    ))
            except Exception:
                continue
        return products

    def _extract_html(self, page) -> list[dict]:
        products = []
        for art in page.query_selector_all(SELECTORS["product"]):
            try:
                a = art.query_selector(SELECTORS["link"])
                if not a:
                    continue
                href = a.get_attribute("href") or ""
                url = href if href.startswith("http") else self.base_url + href

                t = art.query_selector(SELECTORS["title"])
                title = t.inner_text().strip() if t else ""
                if not title or not self.is_monitor(title):
                    continue

                p = art.query_selector(SELECTORS["price"])
                price_text = p.inner_text().strip() if p else None

                img = art.query_selector(SELECTORS["image"])
                image_url = None
                if img:
                    image_url = img.get_attribute("data-src") or img.get_attribute("src")

                products.append(self.make_product(
                    product_title=title, price=price_text,
                    product_url=url, image_url=image_url,
                ))
            except Exception as e:
                logger.debug(f"[Jumia NG] parse error: {e}")
        return products

    def _next_page_url(self, page, current_url: str, page_num: int) -> str | None:
        btn = page.query_selector(SELECTORS["next_page"])
        if btn:
            href = btn.get_attribute("href")
            if href:
                return href if href.startswith("http") else self.base_url + href
        if f"page={page_num}" in current_url:
            return current_url.replace(f"page={page_num}", f"page={page_num + 1}")
        return None
