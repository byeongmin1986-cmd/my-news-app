import re

BRAND_ALIASES = {
    "HP":        ["hewlett packard", "hewlett-packard", "h.p.", "hp inc"],
    "Samsung":   ["samsg", "samsung electronics"],
    "LG":        ["lg electronics", "l.g"],
    "Dell":      ["dell technologies", "dell inc"],
    "Acer":      ["acer inc"],
    "Asus":      ["asustek", "asus republic of gamers", "rog"],
    "Lenovo":    ["lenovo group"],
    "AOC":       ["aoc monitor", "aoc international"],
    "ViewSonic": ["viewsonic corp"],
    "Philips":   ["philips monitors"],
    "BenQ":      ["benq corporation"],
    "MSI":       ["micro-star", "micro star", "msi gaming"],
    "Gigabyte":  ["gigabyte technology"],
}

_ALIAS_TO_BRAND: dict[str, str] = {}
for canonical, aliases in BRAND_ALIASES.items():
    _ALIAS_TO_BRAND[canonical.lower()] = canonical
    for alias in aliases:
        _ALIAS_TO_BRAND[alias.lower()] = canonical


def normalize_brand(raw: str | None) -> str | None:
    if not raw:
        return None
    cleaned = raw.strip()
    lookup  = cleaned.lower()
    if lookup in _ALIAS_TO_BRAND:
        return _ALIAS_TO_BRAND[lookup]
    for alias, canonical in _ALIAS_TO_BRAND.items():
        if alias in lookup:
            return canonical
    return cleaned.title()


def extract_brand_from_title(title: str) -> str | None:
    if not title:
        return None
    first_word = title.strip().split()[0] if title.strip() else ""
    return normalize_brand(first_word)


def normalize_condition(raw: str | None) -> str:
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


def clean_price(raw: str | None) -> float | None:
    if not raw:
        return None
    digits = re.sub(r"[^\d.]", "", raw.replace(",", ""))
    try:
        val = float(digits)
        return val if val > 0 else None
    except (ValueError, TypeError):
        return None
