import re
from config.settings import BRAND_ALIASES

# 정규화된 브랜드명 → alias 목록 매핑을 역방향으로 구축
_ALIAS_TO_BRAND: dict[str, str] = {}
for canonical, aliases in BRAND_ALIASES.items():
    _ALIAS_TO_BRAND[canonical.lower()] = canonical
    for alias in aliases:
        _ALIAS_TO_BRAND[alias.lower()] = canonical


def normalize_brand(raw: str | None) -> str | None:
    """HP, Hewlett Packard, SAMSUNG → 정규화된 브랜드명 반환."""
    if not raw:
        return None
    cleaned = raw.strip()
    lookup = cleaned.lower()
    # 정확히 일치
    if lookup in _ALIAS_TO_BRAND:
        return _ALIAS_TO_BRAND[lookup]
    # 부분 일치 (타이틀에서 추출 시 사용)
    for alias, canonical in _ALIAS_TO_BRAND.items():
        if alias in lookup:
            return canonical
    # 첫 글자만 대문자로 반환
    return cleaned.title()


def extract_brand_from_title(title: str) -> str | None:
    """상품명에서 브랜드명 추출."""
    if not title:
        return None
    first_word = title.strip().split()[0] if title.strip() else ""
    return normalize_brand(first_word)


def normalize_condition(raw: str | None) -> str:
    """new / used / refurbished / unknown 중 하나로 정규화."""
    if not raw:
        return "unknown"
    text = raw.lower()
    if any(w in text for w in ["new", "brand new", "sealed", "original"]):
        return "new"
    if any(w in text for w in ["used", "second hand", "secondhand", "fairly", "pre-owned"]):
        return "used"
    if any(w in text for w in ["refurb", "renewed", "reconditioned", "open box"]):
        return "refurbished"
    return "unknown"


def normalize_panel_type(raw: str | None) -> str | None:
    """IPS / TN / VA / OLED 등 패널 타입 정규화."""
    if not raw:
        return None
    text = raw.upper()
    for panel in ["IPS", "TN", "VA", "OLED", "QLED", "LED", "LCD"]:
        if panel in text:
            return panel
    return None


def clean_price(raw: str | None) -> float | None:
    """'KSh 12,500' → 12500.0 형태로 변환."""
    if not raw:
        return None
    # 숫자와 소수점만 남기기
    digits = re.sub(r"[^\d.]", "", raw.replace(",", ""))
    try:
        val = float(digits)
        return val if val > 0 else None
    except (ValueError, TypeError):
        return None
