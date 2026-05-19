"""
crawler/base.py
ScraperAPI 프록시를 통해 WAF를 우회하는 기반 클래스.

- SCRAPERAPI_KEY 환경변수가 있으면 ScraperAPI 경유 (GitHub Actions)
- 없으면 직접 요청 (로컬 PC residential IP)
"""
from __future__ import annotations

import logging
import os
import random
import time
from datetime import date

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "")
SCRAPERAPI_URL = "http://api.scraperapi.com/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class BaseCrawler:
    country: str  = ""
    retailer: str = ""
    base_url: str = ""
    currency: str = ""

    def __init__(self, max_pages: int = 10):
        self.max_pages  = max_pages
        self.crawl_date = date.today().isoformat()
        self._session   = requests.Session()
        self._session.headers.update(HEADERS)

    def get(self, url: str, render_js: bool = False) -> requests.Response | None:
        """ScraperAPI 경유 또는 직접 요청. 실패 시 None."""
        for attempt in range(1, 4):
            try:
                time.sleep(random.uniform(1.5, 3.5))
                if SCRAPERAPI_KEY:
                    params: dict = {"api_key": SCRAPERAPI_KEY, "url": url}
                    if render_js:
                        params["render"] = "true"
                    r = self._session.get(SCRAPERAPI_URL, params=params, timeout=60)
                else:
                    r = self._session.get(url, timeout=30)
                r.raise_for_status()
                logger.info(f"[{self.retailer}] {r.status_code} {url[:70]}")
                return r
            except requests.RequestException as e:
                wait = 2 ** attempt
                logger.warning(f"[{self.retailer}] attempt {attempt} failed: {e} -> retry {wait}s")
                time.sleep(wait)
        logger.error(f"[{self.retailer}] all retries failed: {url}")
        return None

    def soup(self, url: str, render_js: bool = False) -> BeautifulSoup | None:
        r = self.get(url, render_js=render_js)
        if r is None:
            return None
        return BeautifulSoup(r.text, "html.parser")

    def make_product(self, **kw) -> dict:
        from utils.extractor import (
            extract_model_from_title, extract_refresh_rate,
            extract_resolution, extract_screen_size,
        )
        from utils.normalizer import (
            clean_price, extract_brand_from_title,
            normalize_brand, normalize_condition,
        )
        title     = kw.get("product_title", "")
        raw_brand = kw.get("brand")
        brand     = normalize_brand(raw_brand) if raw_brand else extract_brand_from_title(title)
        text      = f"{title} {kw.get('description', '')}"
        price     = kw.get("price")
        if isinstance(price, str):
            price = clean_price(price)
        return {
            "country":          self.country,
            "retailer":         self.retailer,
            "product_title":    title,
            "brand":            brand,
            "model":            kw.get("model") or extract_model_from_title(title, brand),
            "screen_size_inch": kw.get("screen_size_inch") or extract_screen_size(text),
            "resolution":       kw.get("resolution") or extract_resolution(text),
            "refresh_rate":     kw.get("refresh_rate") or extract_refresh_rate(text),
            "panel_type":       kw.get("panel_type"),
            "condition":        normalize_condition(kw.get("condition")),
            "price":            price,
            "currency":         self.currency,
            "availability":     kw.get("availability", "unknown"),
            "product_url":      kw.get("product_url", ""),
            "image_url":        kw.get("image_url"),
            "crawl_date":       self.crawl_date,
        }

    def is_monitor(self, title: str) -> bool:
        kw   = ["monitor", "display", " led ", "lcd ", "ips ", "gaming monitor", "office monitor"]
        excl = ["television", " tv ", "phone", "tablet", "laptop", "projector", "tv stand"]
        t = f" {title.lower()} "
        return any(k in t for k in kw) and not any(e in t for e in excl)

    def scrape(self) -> list[dict]:
        raise NotImplementedError
