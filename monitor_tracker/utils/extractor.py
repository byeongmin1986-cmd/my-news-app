import re

_SIZE_PATTERNS = [
    r'(\d{1,2}(?:\.\d)?)\s*"',
    r'(\d{1,2}(?:\.\d)?)\s*[\-\s]?(?:inch|inches|in\b)',
    r'(\d{1,2}(?:\.\d)?)\s*(?:\x27\x27|``)',
]
_RESOLUTION_ALIASES = {
    "4k": "3840x2160", "uhd": "3840x2160", "ultra hd": "3840x2160",
    "qhd": "2560x1440", "2k": "2560x1440", "wqhd": "2560x1440",
    "fhd": "1920x1080", "full hd": "1920x1080", "1080p": "1920x1080",
    "hd": "1366x768", "hd+": "1600x900",
}
_RESOLUTION_PATTERN = re.compile(r"(\d{3,4})\s*[x\xd7]\s*(\d{3,4})", re.IGNORECASE)
_REFRESH_PATTERN    = re.compile(r"(\d{2,3})\s*hz", re.IGNORECASE)


def extract_screen_size(text: str | None) -> float | None:
    if not text:
        return None
    for pattern in _SIZE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = float(m.group(1))
            if 10 <= val <= 99:
                return val
    return None


def extract_resolution(text: str | None) -> str | None:
    if not text:
        return None
    lower = text.lower()
    for alias, standard in _RESOLUTION_ALIASES.items():
        if alias in lower:
            return standard
    m = _RESOLUTION_PATTERN.search(text)
    if m:
        w, h = int(m.group(1)), int(m.group(2))
        if w < h:
            w, h = h, w
        return f"{w}x{h}"
    return None


def extract_refresh_rate(text: str | None) -> int | None:
    if not text:
        return None
    m = _REFRESH_PATTERN.search(text)
    if m:
        val = int(m.group(1))
        if 30 <= val <= 360:
            return val
    return None


def extract_model_from_title(title: str | None, brand: str | None) -> str | None:
    if not title:
        return None
    text = title
    if brand:
        text = re.sub(re.escape(brand), "", text, flags=re.IGNORECASE).strip()
    for pat in [
        r"\b([A-Z]{1,5}\d{2,6}[A-Z0-9\-]{0,6})\b",
        r"\b(\d{2,3}[A-Z]{1,5}\d{2,6}[A-Z0-9]*)\b",
    ]:
        m = re.search(pat, text)
        if m:
            c = m.group(1)
            if not re.fullmatch(r"\d+[A-Z]{0,3}", c):
                return c
    return None
