from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "monitors.db"
LOG_DIR = BASE_DIR / "logs"
EXPORT_DIR = BASE_DIR / "exports"

SCRAPER_CONFIG = {
    "delay_min": 2,
    "delay_max": 5,
    "max_pages": 10,
    "timeout": 30,
    "max_retries": 3,
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

SEARCH_TERMS = [
    "monitor",
    "desktop monitor",
    "computer monitor",
    "LED monitor",
    "LCD monitor",
]

SITES = {
    "kenya": {
        "jumia_ke": {
            "enabled": True,
            "retailer": "Jumia Kenya",
            "base_url": "https://www.jumia.co.ke",
            "currency": "KES",
            "module": "scrapers.kenya.jumia_ke",
            "class": "JumiaKenyaScraper",
        }
    },
    "ghana": {
        "compughana": {
            "enabled": True,
            "retailer": "CompuGhana",
            "base_url": "https://www.compughana.com",
            "currency": "GHS",
            "module": "scrapers.ghana.compughana",
            "class": "CompuGhanaScraper",
        }
    },
    "nigeria": {
        "jumia_ng": {
            "enabled": True,
            "retailer": "Jumia Nigeria",
            "base_url": "https://www.jumia.com.ng",
            "currency": "NGN",
            "module": "scrapers.nigeria.jumia_ng",
            "class": "JumiaNigeriaScraper",
        }
    },
    # 향후 추가 가능한 사이트들 (enabled: False)
    "tanzania": {
        "jiji_tz": {
            "enabled": False,
            "retailer": "Jiji Tanzania",
            "base_url": "https://jiji.co.tz",
            "currency": "TZS",
            "module": "scrapers.tanzania.jiji_tz",
            "class": "JijiTanzaniaScraper",
        }
    },
    "ethiopia": {
        "jiji_et": {
            "enabled": False,
            "retailer": "Jiji Ethiopia",
            "base_url": "https://jiji.com.et",
            "currency": "ETB",
            "module": "scrapers.ethiopia.jiji_et",
            "class": "JijiEthiopiaScraper",
        }
    },
}

BRAND_ALIASES = {
    "HP": ["hewlett packard", "hewlett-packard", "h.p.", "hp inc"],
    "Samsung": ["samsg", "samsung electronics"],
    "LG": ["lg electronics", "l.g", "l.g."],
    "Dell": ["dell technologies", "dell inc"],
    "Acer": ["acer inc"],
    "Asus": ["asustek", "asus republic of gamers", "rog"],
    "Lenovo": ["lenovo group"],
    "AOC": ["aoc monitor", "aoc international"],
    "ViewSonic": ["viewsonic corp", "viewsoniccorp"],
    "Philips": ["philips monitors", "mmid"],
    "BenQ": ["benq corporation"],
    "MSI": ["micro-star", "micro star", "msi gaming"],
    "Gigabyte": ["gigabyte technology"],
    "Huawei": ["huawei technologies"],
    "Xiaomi": ["mi", "redmi"],
    "Hisense": ["hisense group"],
    "TCL": ["tcl electronics"],
}
