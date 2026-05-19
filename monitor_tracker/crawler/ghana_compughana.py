"""
CompuGhana crawler  —  compughana.com  (WooCommerce)

전략:
1. WooCommerce REST API 시도 (/wp-json/wc/v3/products) — 인증 없이 공개된 경우
2. WooCommerce Store API (/wp-json/wc/store/v1/products) — 최신 WC는 공개
3. HTML 파싱 (WooCommerce 표준 마크업)
"""
from __future__ import annotations

import json
import logging

import requests
from playwright.sync_api import sync_playwright

from crawler.base import BaseCrawler, _human_delay

logger = logging.getLogger(__name__)

BASE = "https://www.compughana.com"

# WooCommerce Store API (인증 불필요)
WC_STORE_API = f"{BASE}/wp-json/wc/store/v1/products"
WC_REST_API  = f"{BASE}/wp-json/wc/v3/products"

SEARCH_URLS = [
    f"{BASE}/product-category/monitors/",
    f"{BASE}/product-category/computer-monitors/",
    f"{BASE}/?s=monitor&post_type=product",
    f"{BASE}/?s=desktop+monitor&post_type=product",
    f"{BASE}/?s=LED+monitor&post_type=product",
]

# WooCommerce HTML selectors
SELECTORS = {
    "product":      "ul.products li.product",
    "title":        ".woocommerce-loop-product__title, h2.woocommerce-loop-product__title",
    "price":        ".price .woocommerce-Price-amount, .woocommerce-Price-amount",
    "link":         "a.woocommerce-loop-product__link, .woocommerce-LoopProduct-link",
    "image":        ".wp-post-image, img.attachment-woocommerce_thumbnail",
    "next_page":    "a.next.page-numbers",
    "stock":        ".stock",
}


class CompuGhanaCrawler(BaseCrawler):
    country     = "Ghana"
    retailer    = "CompuGhana"
    base_url    = BASE
    currency    = "GHS"
    timezone_id = "Africa/Accra"

    def scrape(self) -> list[dict]:
        results: dict[str, dict] = {}

        # ── 1순위: WooCommerce Store API (공개 endpoint) ─────────
        api_products = self._try_wc_store_api()
        if api_products:
            logger.info(f"[CompuGhana] WC Store API → {len(api_products)} products")
            for p in api_products:
                results[p["product_url"]] = p
        else:
            logger.info("[CompuGhana] Store API failed, trying REST API...")
            api_products = self._try_wc_rest_api()
            if api_products:
                logger.info(f"[CompuGhana] WC REST API → {len(api_products)} products")
                for p in api_products:
                    results[p["product_url"]] = p

        # ── 2순위: Playwright HTML 파싱 ──────────────────────────
        if not results:
            logger.info("[CompuGhana] APIs unavailable, falling back to HTML scraping")
            html_products = self._scrape_html()
            for p in html_products:
                results[p["product_url"]] = p

        out = list(results.values())
        logger.info(f"[CompuGhana] Total: {len(out)}")
        return out

    # ── WooCommerce Store API (공개, 인증 불필요) ────────────────
    def _try_wc_store_api(self) -> list[dict]:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
        products = []
        page = 1
        while page <= self.max_pages:
            try:
                r = requests.get(
                    WC_STORE_API,
                    params={"search": "monitor", "per_page": 100, "page": page},
                    headers=headers,
                    timeout=20,
                )
                if r.status_code != 200:
                    logger.warning(f"[CompuGhana] Store API status {r.status_code}")
                    return []
                data = r.json()
                if not data:
                    break
                for item in data:
                    p = self._parse_wc_store_item(item)
                    if p:
                        products.append(p)
                page += 1
                _human_delay(1.0, 2.0)
            except Exception as e:
                logger.warning(f"[CompuGhana] Store API error: {e}")
                return []
        return products

    def _parse_wc_store_item(self, item: dict) -> dict | None:
        name = item.get("name", "")
        if not self.is_monitor(name):
            return None
        price_raw = item.get("prices", {}).get("price") or item.get("price", "")
        # WC Store API 가격은 minor unit (예: 120000 = GHS 1200.00)
        try:
            price = float(price_raw) / 100
        except (ValueError, TypeError):
            price = None
        link = item.get("permalink", "")
        images = item.get("images", [])
        image_url = images[0].get("src") if images else None

        return self.make_product(
            product_title=name,
            price=price,
            product_url=link,
            image_url=image_url,
            description=item.get("short_description", ""),
        )

    # ── WooCommerce REST API ─────────────────────────────────────
    def _try_wc_rest_api(self) -> list[dict]:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
        products = []
        page = 1
        while page <= self.max_pages:
            try:
                r = requests.get(
                    WC_REST_API,
                    params={"search": "monitor", "per_page": 100, "page": page},
                    headers=headers,
                    timeout=20,
                )
                if r.status_code == 401:
                    logger.info("[CompuGhana] REST API requires auth, skipping.")
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
                    price_raw = item.get("price", "") or item.get("regular_price", "")
                    link = item.get("permalink", "")
                    images = item.get("images", [])
                    image_url = images[0].get("src") if images else None
                    products.append(self.make_product(
                        product_title=name,
                        price=price_raw,
                        product_url=link,
                        image_url=image_url,
                        description=item.get("short_description", ""),
                    ))
                page += 1
                _human_delay(1.0, 2.0)
            except Exception as e:
                logger.warning(f"[CompuGhana] REST API error: {e}")
                return []
        return products

    # ── Playwright HTML 파싱 ─────────────────────────────────────
    def _scrape_html(self) -> list[dict]:
        results: dict[str, dict] = {}

        with sync_playwright() as pw:
            browser, ctx = self._new_context(pw)
            page = ctx.new_page()

            for start_url in SEARCH_URLS:
                url: str | None = start_url
                page_num = 1

                while url and page_num <= self.max_pages:
                    if not self.fetch_page(page, url):
                        break

                    found = self._extract_html(page)
                    logger.info(f"[CompuGhana] HTML page {page_num} → {len(found)} products")
                    for p in found:
                        if p.get("product_url"):
                            results[p["product_url"]] = p

                    # 다음 페이지
                    next_btn = page.query_selector(SELECTORS["next_page"])
                    if next_btn:
                        href = next_btn.get_attribute("href")
                        url = href if href and href.startswith("http") else None
                    else:
                        # WooCommerce /page/N/ 방식
                        if "/page/" in url:
                            url = url.replace(f"/page/{page_num}/", f"/page/{page_num + 1}/")
                        else:
                            url = url.rstrip("/") + f"/page/{page_num + 1}/"
                        # 실제 페이지가 없으면 다음 반복에서 fetch_page 실패로 종료

                    page_num += 1
                    _human_delay(2.0, 4.0)

            browser.close()

        return list(results.values())

    def _extract_html(self, page) -> list[dict]:
        products = []
        for item in page.query_selector_all(SELECTORS["product"]):
            try:
                link_el = item.query_selector(SELECTORS["link"])
                if not link_el:
                    continue
                url = link_el.get_attribute("href") or ""
                if not url.startswith("http"):
                    url = self.base_url + url

                title_el = item.query_selector(SELECTORS["title"])
                title = title_el.inner_text().strip() if title_el else (
                    link_el.inner_text().strip()
                )
                if not title or not self.is_monitor(title):
                    continue

                # WooCommerce: sale price는 ins 안에 있음
                price_text = None
                price_el = item.query_selector(SELECTORS["price"])
                if price_el:
                    ins = price_el.query_selector("ins .woocommerce-Price-amount")
                    price_text = ins.inner_text().strip() if ins else price_el.inner_text().strip()

                img_el = item.query_selector(SELECTORS["image"])
                image_url = None
                if img_el:
                    image_url = (
                        img_el.get_attribute("data-src")
                        or img_el.get_attribute("data-lazy-src")
                        or img_el.get_attribute("src")
                    )

                stock_el = item.query_selector(SELECTORS["stock"])
                availability = stock_el.inner_text().strip() if stock_el else "unknown"

                products.append(self.make_product(
                    product_title=title,
                    price=price_text,
                    product_url=url,
                    image_url=image_url,
                    availability=availability,
                ))
            except Exception as e:
                logger.debug(f"[CompuGhana] HTML parse error: {e}")
        return products
