"""
debug_crawler.py -- 각 사이트 URL 진단 스크립트
결과를 data/debug_results.json에 저장 → Streamlit에서 표시
"""
from __future__ import annotations
import json, logging, os, random, sys, time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

SCRAPERAPI_KEY = os.environ.get("SCRAPERAPI_KEY", "")
SCRAPERAPI_URL = "http://api.scraperapi.com/"
DATA_DIR       = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DEBUG_PATH     = DATA_DIR / "debug_results.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("debug_crawler")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}

# 각 사이트별 테스트 케이스
TEST_CASES: dict = {
    "ghana_compughana": {
        "label": "CompuGhana",
        "tests": [
            {
                "url": "https://www.compughana.com/wp-json/wc/store/v1/products?per_page=10",
                "method": "direct",
                "desc": "WC Store API — direct (no ScraperAPI)",
            },
            {
                "url": "https://www.compughana.com/wp-json/wc/store/v1/products?per_page=10",
                "method": "scraperapi",
                "desc": "WC Store API — ScraperAPI (기본)",
            },
            {
                "url": "https://www.compughana.com/wp-json/wc/store/v1/products?per_page=10",
                "method": "scraperapi_gh",
                "desc": "WC Store API — ScraperAPI country_code=gh",
            },
            {
                "url": "https://www.compughana.com/wp-json/wc/store/v1/products?search=monitor&per_page=10",
                "method": "direct",
                "desc": "WC Store API search=monitor — direct",
            },
            {
                "url": "https://www.compughana.com/wp-json/wc/store/v1/products?search=display&per_page=10",
                "method": "direct",
                "desc": "WC Store API search=display — direct",
            },
            {
                "url": "https://www.compughana.com/wp-json/wc/store/v1/products/categories",
                "method": "direct",
                "desc": "WC Store API — 카테고리 목록",
            },
            {
                "url": "https://www.compughana.com/product-category/monitors/",
                "method": "scraperapi_gh",
                "desc": "HTML 카테고리 /monitors/ (country_code=gh)",
            },
            {
                "url": "https://www.compughana.com/product-category/monitors/",
                "method": "scraperapi_render",
                "desc": "HTML 카테고리 /monitors/ (JS 렌더링)",
            },
        ],
    },
    "kenya_jumia": {
        "label": "Jumia Kenya",
        "tests": [
            {
                "url": "https://www.jumia.co.ke/monitors/",
                "method": "scraperapi",
                "desc": "카테고리 HTML — ScraperAPI 기본",
            },
            {
                "url": "https://www.jumia.co.ke/monitors/",
                "method": "scraperapi_ke",
                "desc": "카테고리 HTML — country_code=ke",
            },
            {
                "url": "https://www.jumia.co.ke/monitors/",
                "method": "scraperapi_render",
                "desc": "카테고리 HTML — JS 렌더링",
            },
            {
                "url": "https://www.jumia.co.ke/monitors/",
                "method": "scraperapi_premium",
                "desc": "카테고리 HTML — premium proxy",
            },
            {
                "url": "https://www.jumia.co.ke/catalog/?q=monitor",
                "method": "scraperapi_ke",
                "desc": "검색 /catalog/?q=monitor (country_code=ke)",
            },
            {
                "url": "https://www.jumia.co.ke/computer-monitors/",
                "method": "scraperapi_ke",
                "desc": "카테고리 /computer-monitors/ (country_code=ke)",
            },
        ],
    },
    "nigeria_jumia": {
        "label": "Jumia Nigeria",
        "tests": [
            {
                "url": "https://www.jumia.com.ng/monitors/",
                "method": "scraperapi",
                "desc": "카테고리 HTML — ScraperAPI 기본",
            },
            {
                "url": "https://www.jumia.com.ng/monitors/",
                "method": "scraperapi_ng",
                "desc": "카테고리 HTML — country_code=ng",
            },
            {
                "url": "https://www.jumia.com.ng/monitors/",
                "method": "scraperapi_render",
                "desc": "카테고리 HTML — JS 렌더링",
            },
            {
                "url": "https://www.jumia.com.ng/monitors/",
                "method": "scraperapi_premium",
                "desc": "카테고리 HTML — premium proxy",
            },
            {
                "url": "https://www.jumia.com.ng/catalog/?q=monitor",
                "method": "scraperapi_ng",
                "desc": "검색 /catalog/?q=monitor (country_code=ng)",
            },
        ],
    },
}

SCRAPERAPI_METHODS = {
    "scraperapi":        {},
    "scraperapi_ke":     {"country_code": "ke"},
    "scraperapi_ng":     {"country_code": "ng"},
    "scraperapi_gh":     {"country_code": "gh"},
    "scraperapi_render": {"render": "true"},
    "scraperapi_premium": {"premium": "true", "keep_headers": "true"},
}


def classify(status: int | None, content_type: str, body: str, error: str | None) -> str:
    if error:
        if "Timeout" in error or "timeout" in error:
            return "TIMEOUT"
        if "Connection" in error:
            return "CONNECTION_ERROR"
        return "REQUEST_FAILED"
    if status is None:
        return "NO_RESPONSE"
    if status == 200:
        ct = content_type.lower()
        b_lower = body.lower()
        if "json" in ct or body.lstrip().startswith(("[", "{")):
            try:
                data = json.loads(body)
                count = len(data) if isinstance(data, list) else 0
                if count > 0:
                    return f"JSON_OK_{count}_ITEMS"
                return "JSON_EMPTY"
            except Exception:
                pass
        if "<html" in b_lower:
            if any(w in b_lower for w in ["cloudflare", "just a moment", "checking your browser", "ddos-guard", "ray id"]):
                return "HTTP_200_WAF_CHALLENGE"
            import re
            prd = len(re.findall(r'article[^>]*prd-w|class=["\'][^"\']*prd-w', body))
            woo = len(re.findall(r'li[^>]*product[^>]*type-product', body))
            if prd:
                return f"HTML_OK_{prd}_PRD-W_ELEMENTS"
            if woo:
                return f"HTML_OK_{woo}_WOO_PRODUCTS"
            if "woocommerce" in b_lower:
                return "HTML_OK_WOOCOMMERCE_NO_PRODUCTS"
            return "HTML_OK_NO_PRODUCTS_FOUND"
        return "HTTP_200_OK"
    if status == 403:
        return "HTTP_403_WAF_BLOCKED"
    if status == 404:
        return "HTTP_404_NOT_FOUND"
    if status == 429:
        return "HTTP_429_RATE_LIMITED"
    if status == 503:
        return "HTTP_503_UNAVAILABLE"
    return f"HTTP_{status}_UNKNOWN"


def do_request(test: dict) -> dict:
    method = test["method"]
    url    = test["url"]

    result: dict = {
        "url":          url,
        "method":       method,
        "desc":         test["desc"],
        "status":       None,
        "content_type": "",
        "body_preview": "",
        "classification": "PENDING",
        "error":        None,
        "item_count":   0,
        "time":         datetime.now().isoformat(),
    }

    if method != "direct" and not SCRAPERAPI_KEY:
        result["classification"] = "SKIPPED_NO_SCRAPERAPI_KEY"
        return result

    sess = requests.Session()
    sess.headers.update(HEADERS)

    try:
        time.sleep(random.uniform(0.5, 1.5))

        if method == "direct":
            r = sess.get(url, timeout=30)
        else:
            extra = SCRAPERAPI_METHODS.get(method, {})
            params = {"api_key": SCRAPERAPI_KEY, "url": url, **extra}
            timeout = 120 if extra.get("render") else 60
            r = sess.get(SCRAPERAPI_URL, params=params, timeout=timeout)

        result["status"]       = r.status_code
        result["content_type"] = r.headers.get("Content-Type", "")
        result["body_preview"] = r.text[:500]
        result["classification"] = classify(
            r.status_code, result["content_type"], r.text, None
        )

        # Count items
        if r.status_code == 200:
            body = r.text
            if body.lstrip().startswith(("[", "{")):
                try:
                    data = r.json()
                    result["item_count"] = len(data) if isinstance(data, list) else 0
                except Exception:
                    pass
            else:
                import re
                result["item_count"] = len(re.findall(
                    r'article[^>]*prd-w|li[^>]*product[^>]*type-product', body
                ))

    except requests.exceptions.Timeout:
        result["error"]          = "Timeout"
        result["classification"] = "TIMEOUT"
    except requests.exceptions.ConnectionError as e:
        result["error"]          = f"ConnectionError: {str(e)[:120]}"
        result["classification"] = "CONNECTION_ERROR"
    except Exception as e:
        result["error"]          = f"Exception: {str(e)[:120]}"
        result["classification"] = "REQUEST_FAILED"

    logger.info(f"  [{method:25s}] {result['classification']:<35s} | {url[:60]}")
    return result


def pick_best(tests: list[dict]) -> str:
    for t in tests:
        c = t.get("classification", "")
        if "JSON_OK" in c and t.get("item_count", 0) > 0:
            return f"{c} via {t['method']}"
    for t in tests:
        c = t.get("classification", "")
        if "HTML_OK" in c and "PRODUCT" in c:
            return f"{c} via {t['method']}"
    for t in tests:
        if t.get("classification", "") in ("HTTP_200_OK", "HTML_OK_WOOCOMMERCE_NO_PRODUCTS"):
            return f"{t['classification']} via {t['method']}"
    return "NO_SUCCESS"


def main():
    site_filter = sys.argv[1] if len(sys.argv) > 1 else None

    if not SCRAPERAPI_KEY:
        logger.warning("=" * 60)
        logger.warning("SCRAPERAPI_KEY 없음 — scraperapi_* 메서드는 모두 SKIPPED")
        logger.warning("=" * 60)

    targets = (
        {site_filter: TEST_CASES[site_filter]}
        if site_filter and site_filter in TEST_CASES
        else TEST_CASES
    )

    output: dict = {
        "run_at":              datetime.now().isoformat(),
        "scraperapi_key_set":  bool(SCRAPERAPI_KEY),
        "sites":               {},
    }

    for site_key, cfg in targets.items():
        logger.info("=" * 60)
        logger.info(f"Testing: {cfg['label']}")
        site_tests = []
        for test in cfg["tests"]:
            res = do_request(test)
            site_tests.append(res)

        output["sites"][site_key] = {
            "label":  cfg["label"],
            "tests":  site_tests,
            "best":   pick_best(site_tests),
        }
        logger.info(f"  → best: {output['sites'][site_key]['best']}")

    with open(DEBUG_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"\n✅ debug_results.json saved: {DEBUG_PATH}")


if __name__ == "__main__":
    main()
