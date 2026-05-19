"""
Jumia Kenya crawler  —  jumia.co.ke

전략:
1. 카탈로그 페이지 HTML에서 embedded JSON 추출 (script[type=application/ld+json])
2. JSON 없으면 article.prd-w HTML 파싱
3. Playwright stealth mode로 WAF 우회 (로컬 PC 실행 필수)

사이트 구조가 바뀌면 SELECTORS만 수정.
"""
from __future__ import annotations

import json
import logging
import random

from playwright.sync_api import sync_playwright

from crawler.base import BaseCrawler, _human_delay

logger = logging.getLogger(__name__)

# ── 사이트 구조 변경 시 여기만 수정 ────────────────────────────
SEARCH_URLS = [
    "https://www.jumia.co.ke/monitors/",
    "https://www.jumia.co.ke/computer-monitors/",
    "https://www.jumia.co.ke/catalog/?q=monitor",
    "https://www.jumia.co.ke/catalog/?q=computer+monitor",
    "https://www.jumia.co.ke/catalog/?q=LED+monitor",
]

SELECTORS = {
    "product":        "article.prd-w",
    "title":          "h3.name",
    "price":          "div.prc",
    "link":           "a.core",
    "image":          "img.img-responsive",
    "next_page":      "a[aria-label='Next Page']",
    "no_result":      ".no-result, .-mtm",
}
# ───────────────────────────────────────────────────────────────


class JumiaKenyaCrawler(BaseCrawler):
    country    = "Kenya"
    retailer   = "Jumia Kenya"
    base_url   = "https://www.jumia.co.ke"
    currency   = "KES"
    timezone_id = "Africa/Nairobi"

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

                    # 1순위: embedded JSON-LD (스펙 데이터 풍부)
                    found = self._extract_json_ld(page)
                    if not found:
                        # 2순위: HTML 파싱
                        found = self._extract_html(page)

                    logger.info(f"[Jumia KE] page {page_num} → {len(found)} products")
                    for p in found:
                        if p.get("product_url"):
                            results[p["product_url"]] = p

                    # 다음 페이지
                    url = self._next_page_url(page, url, page_num)
                    page_num += 1
                    _human_delay(2.0, 4.0)

            browser.close()

        out = list(results.values())
        logger.info(f"[Jumia KE] Total unique products: {len(out)}")
        return out

    # ── JSON-LD 추출 ────────────────────────────────────────────
    def _extract_json_ld(self, page) -> list[dict]:
        products = []
        scripts = page.query_selector_all("script[type='application/ld+json']")
        for sc in scripts:
            try:
                data = json.loads(sc.inner_text())
                items = []
                if isinstance(data, dict):
                    if data.get("@type") == "ItemList":
                        items = data.get("itemListElement", [])
                    elif data.get("@type") == "Product":
                        items = [data]

                for item in items:
                    product = item.get("item", item)
                    if product.get("@type") != "Product":
                        continue
                    name = product.get("name", "")
                    if not self.is_monitor(name):
                        continue

                    offer = product.get("offers", {})
                    if isinstance(offer, list):
                        offer = offer[0] if offer else {}
                    price = offer.get("price")
                    url = product.get("url", "")
                    if url and not url.startswith("http"):
                        url = self.base_url + url
                    image = product.get("image")
                    if isinstance(image, list):
                        image = image[0] if image else None

                    products.append(self.make_product(
                        product_title=name,
                        price=price,
                        product_url=url,
                        image_url=image,
                        availability=offer.get("availability", "unknown"),
                    ))
            except Exception:
                continue
        return products

    # ── HTML 파싱 ────────────────────────────────────────────────
    def _extract_html(self, page) -> list[dict]:
        products = []
        articles = page.query_selector_all(SELECTORS["product"])
        for art in articles:
            try:
                # link / url
                a = art.query_selector(SELECTORS["link"])
                if not a:
                    continue
                href = a.get_attribute("href") or ""
                url = href if href.startswith("http") else self.base_url + href
                if not url:
                    continue

                # title
                t = art.query_selector(SELECTORS["title"])
                title = t.inner_text().strip() if t else ""
                if not title or not self.is_monitor(title):
                    continue

                # price
                p = art.query_selector(SELECTORS["price"])
                price_text = p.inner_text().strip() if p else None

                # image
                img = art.query_selector(SELECTORS["image"])
                image_url = None
                if img:
                    image_url = img.get_attribute("data-src") or img.get_attribute("src")

                products.append(self.make_product(
                    product_title=title,
                    price=price_text,
                    product_url=url,
                    image_url=image_url,
                ))
            except Exception as e:
                logger.debug(f"[Jumia KE] article parse error: {e}")
        return products

    # ── 다음 페이지 URL ─────────────────────────────────────────
    def _next_page_url(self, page, current_url: str, page_num: int) -> str | None:
        btn = page.query_selector(SELECTORS["next_page"])
        if btn:
            href = btn.get_attribute("href")
            if href:
                return href if href.startswith("http") else self.base_url + href

        # 페이지네이션이 없으면 ?page=N 방식 시도
        if "?" in current_url:
            sep = "&"
        else:
            sep = "?"
        if f"page={page_num}" in current_url:
            return current_url.replace(f"page={page_num}", f"page={page_num + 1}")
        return None  # 더 이상 페이지 없음
