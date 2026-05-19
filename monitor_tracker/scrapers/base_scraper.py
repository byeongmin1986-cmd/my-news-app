import logging
import random
import time
import urllib.robotparser
from abc import ABC, abstractmethod
from datetime import date
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config.settings import SCRAPER_CONFIG
from utils.extractor import (
    extract_model_from_title,
    extract_refresh_rate,
    extract_resolution,
    extract_screen_size,
)
from utils.normalizer import (
    clean_price,
    extract_brand_from_title,
    normalize_brand,
    normalize_condition,
    normalize_panel_type,
)

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """모든 scraper의 기반 클래스."""

    def __init__(self, country: str, retailer: str, base_url: str, currency: str):
        self.country = country
        self.retailer = retailer
        self.base_url = base_url
        self.currency = currency
        self.crawl_date = date.today().isoformat()
        self.session = self._build_session()
        self._robots = self._load_robots()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": SCRAPER_CONFIG["user_agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        return session

    def _load_robots(self) -> urllib.robotparser.RobotFileParser:
        rp = urllib.robotparser.RobotFileParser()
        robots_url = f"{self.base_url}/robots.txt"
        try:
            rp.set_url(robots_url)
            rp.read()
        except Exception:
            logger.warning(f"Could not load robots.txt from {robots_url}")
        return rp

    def can_fetch(self, url: str) -> bool:
        """robots.txt 규칙 확인."""
        try:
            return self._robots.can_fetch(SCRAPER_CONFIG["user_agent"], url)
        except Exception:
            return True

    def delay(self):
        """요청 간 랜덤 딜레이."""
        seconds = random.uniform(
            SCRAPER_CONFIG["delay_min"],
            SCRAPER_CONFIG["delay_max"],
        )
        time.sleep(seconds)

    def fetch(self, url: str) -> BeautifulSoup | None:
        """URL에서 HTML을 가져와 BeautifulSoup으로 파싱."""
        if not self.can_fetch(url):
            logger.warning(f"robots.txt disallows: {url}")
            return None

        for attempt in range(1, SCRAPER_CONFIG["max_retries"] + 1):
            try:
                self.delay()
                resp = self.session.get(
                    url,
                    timeout=SCRAPER_CONFIG["timeout"],
                    allow_redirects=True,
                )
                resp.raise_for_status()
                return BeautifulSoup(resp.text, "html.parser")
            except requests.RequestException as e:
                wait = 2 ** attempt
                logger.warning(f"Attempt {attempt} failed for {url}: {e}. Retry in {wait}s")
                if attempt < SCRAPER_CONFIG["max_retries"]:
                    time.sleep(wait)
                else:
                    logger.error(f"All retries exhausted for {url}")
        return None

    def build_product(self, **kwargs) -> dict:
        """공통 필드를 채운 상품 dict 생성."""
        title = kwargs.get("product_title", "")
        raw_brand = kwargs.get("brand")
        brand = normalize_brand(raw_brand) if raw_brand else extract_brand_from_title(title)
        model = kwargs.get("model") or extract_model_from_title(title, brand)

        combined = f"{title} {kwargs.get('description', '')}"
        screen_size = kwargs.get("screen_size_inch") or extract_screen_size(combined)
        resolution = kwargs.get("resolution") or extract_resolution(combined)
        refresh_rate = kwargs.get("refresh_rate") or extract_refresh_rate(combined)
        panel_type = kwargs.get("panel_type") or normalize_panel_type(combined)
        condition = normalize_condition(kwargs.get("condition"))
        price = kwargs.get("price")
        if isinstance(price, str):
            price = clean_price(price)

        return {
            "country": self.country,
            "retailer": self.retailer,
            "product_title": title,
            "brand": brand,
            "model": model,
            "screen_size_inch": screen_size,
            "resolution": resolution,
            "refresh_rate": refresh_rate,
            "panel_type": panel_type,
            "condition": condition,
            "price": price,
            "currency": self.currency,
            "availability": kwargs.get("availability", "unknown"),
            "product_url": kwargs.get("product_url", ""),
            "image_url": kwargs.get("image_url"),
            "crawl_date": self.crawl_date,
        }

    def is_monitor_product(self, title: str) -> bool:
        """상품명이 모니터 관련인지 필터링."""
        keywords = [
            "monitor", "display", "screen", "led", "lcd",
            "ips", "gaming monitor", "office monitor",
        ]
        title_lower = title.lower()
        # 제외할 키워드 (TV, 스마트폰 등)
        exclude = ["television", "tv stand", "phone", "tablet", "laptop", "projector"]
        if any(ex in title_lower for ex in exclude):
            return False
        return any(kw in title_lower for kw in keywords)

    @abstractmethod
    def scrape(self) -> list[dict]:
        """사이트별 scraper에서 구현. 상품 dict 리스트를 반환."""
        raise NotImplementedError
