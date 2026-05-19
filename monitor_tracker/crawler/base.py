"""
Playwright stealth base crawler.
모든 site-specific crawler가 이 클래스를 상속한다.

반드시 로컬 PC(residential IP)에서 실행해야 한다.
클라우드 서버 IP는 Jumia/CompuGhana WAF에서 차단된다.
"""
from __future__ import annotations

import logging
import random
import time
from datetime import date, datetime
from pathlib import Path
from typing import Generator

from playwright.sync_api import Page, sync_playwright

logger = logging.getLogger(__name__)

# ── 실제 Chrome 브라우저 fingerprint 목록 ──────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

VIEWPORTS = [
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
    {"width": 1536, "height": 864},
]

# stealth JS: webdriver 감지 우회
STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
window.chrome = { runtime: {} };
Object.defineProperty(navigator, 'permissions', {
  get: () => ({ query: () => Promise.resolve({ state: 'granted' }) })
});
"""


def _human_delay(min_s: float = 1.0, max_s: float = 3.5):
    time.sleep(random.uniform(min_s, max_s))


def _human_scroll(page: Page, steps: int = 4):
    """사람처럼 천천히 스크롤."""
    for _ in range(steps):
        dist = random.randint(200, 500)
        page.mouse.wheel(0, dist)
        time.sleep(random.uniform(0.4, 1.0))


class BaseCrawler:
    country: str = ""
    retailer: str = ""
    base_url: str = ""
    currency: str = ""
    timezone_id: str = "Africa/Nairobi"
    locale: str = "en-US"

    def __init__(self, headless: bool = True, max_pages: int = 10):
        self.headless = headless
        self.max_pages = max_pages
        self.crawl_date = date.today().isoformat()
        self._ua = random.choice(USER_AGENTS)
        self._vp = random.choice(VIEWPORTS)

    # ── Playwright context 빌드 ─────────────────────────────────
    def _new_context(self, playwright):
        browser = playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080",
            ],
        )
        ctx = browser.new_context(
            user_agent=self._ua,
            viewport=self._vp,
            locale=self.locale,
            timezone_id=self.timezone_id,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            },
        )
        ctx.add_init_script(STEALTH_JS)
        return browser, ctx

    def fetch_page(self, page: Page, url: str) -> bool:
        """URL 로드 후 human-like 동작. 성공하면 True."""
        try:
            logger.info(f"[{self.retailer}] GET {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            _human_delay(1.5, 3.0)
            _human_scroll(page, steps=random.randint(2, 4))
            return True
        except Exception as e:
            logger.error(f"[{self.retailer}] fetch error: {e}")
            return False

    # ── 공통 상품 dict 빌드 ─────────────────────────────────────
    def make_product(self, **kw) -> dict:
        from utils.extractor import extract_screen_size, extract_resolution, extract_refresh_rate, extract_model_from_title
        from utils.normalizer import normalize_brand, normalize_condition, clean_price, extract_brand_from_title

        title = kw.get("product_title", "")
        raw_brand = kw.get("brand")
        brand = normalize_brand(raw_brand) if raw_brand else extract_brand_from_title(title)
        text = f"{title} {kw.get('description', '')}"

        price = kw.get("price")
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
        kw = ["monitor", "display", "screen", "led", "lcd", "ips", "gaming monitor"]
        excl = ["television", "tv ", " tv", "phone", "tablet", "laptop", "projector", "stand"]
        t = title.lower()
        return any(k in t for k in kw) and not any(e in t for e in excl)

    # ── 서브클래스에서 구현 ─────────────────────────────────────
    def scrape(self) -> list[dict]:
        raise NotImplementedError
