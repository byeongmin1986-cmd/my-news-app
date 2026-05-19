import re

# 화면 크기 패턴: "24-inch", '27"', "23.8 inch", "24IN"
_SIZE_PATTERNS = [
    r'(\d{1,2}(?:\.\d)?)\s*"',                           # 24", 23.8"
    r'(\d{1,2}(?:\.\d)?)\s*[\-\s]?(?:inch|inches|in\b)', # 24-inch, 23.8 inch, 24IN
    r'(\d{1,2}(?:\.\d)?)\s*(?:\'\'|``)',                  # 24'' (double tick)
]

# 해상도 패턴
_RESOLUTION_ALIASES = {
    "4k": "3840x2160",
    "uhd": "3840x2160",
    "ultra hd": "3840x2160",
    "qhd": "2560x1440",
    "2k": "2560x1440",
    "wqhd": "2560x1440",
    "fhd": "1920x1080",
    "full hd": "1920x1080",
    "1080p": "1920x1080",
    "hd": "1366x768",
    "hd+": "1600x900",
    "wxga": "1280x800",
    "wuxga": "1920x1200",
}
_RESOLUTION_PATTERN = re.compile(r"(\d{3,4})\s*[x×]\s*(\d{3,4})", re.IGNORECASE)

# 주사율 패턴: "144Hz", "60 Hz", "144HZ"
_REFRESH_PATTERN = re.compile(r"(\d{2,3})\s*hz", re.IGNORECASE)


def extract_screen_size(text: str | None) -> float | None:
    """텍스트에서 화면 크기(인치)를 추출하여 float으로 반환."""
    if not text:
        return None
    for pattern in _SIZE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            # 합리적 범위 체크 (10~99인치)
            if 10 <= val <= 99:
                return val
    return None


def extract_resolution(text: str | None) -> str | None:
    """텍스트에서 해상도를 표준 형식(WxH)으로 추출."""
    if not text:
        return None
    lower = text.lower()

    # 별칭 우선 검색
    for alias, standard in _RESOLUTION_ALIASES.items():
        if alias in lower:
            return standard

    # WxH 패턴 검색
    match = _RESOLUTION_PATTERN.search(text)
    if match:
        w, h = int(match.group(1)), int(match.group(2))
        # 가로가 더 크도록 보정
        if w < h:
            w, h = h, w
        return f"{w}x{h}"

    return None


def extract_refresh_rate(text: str | None) -> int | None:
    """텍스트에서 주사율(Hz)을 추출."""
    if not text:
        return None
    match = _REFRESH_PATTERN.search(text)
    if match:
        val = int(match.group(1))
        # 합리적 범위 체크 (30~360Hz)
        if 30 <= val <= 360:
            return val
    return None


def extract_model_from_title(title: str | None, brand: str | None) -> str | None:
    """상품명에서 모델 번호 추출 (영문+숫자 조합)."""
    if not title:
        return None
    text = title
    if brand:
        text = re.sub(re.escape(brand), "", text, flags=re.IGNORECASE).strip()

    # 우선순위 1: 영문+숫자 혼합 패턴 (E2416H, 27GL850, S2421HN, 24BK450)
    patterns = [
        r"\b([A-Z]{1,5}\d{2,6}[A-Z0-9\-]{0,6})\b",   # E2416H, S2421HN
        r"\b(\d{2,3}[A-Z]{1,5}\d{2,6}[A-Z0-9]*)\b",  # 27GL850, 24BK450
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            candidate = match.group(1)
            # 단순 숫자+인치 표기는 제외 (예: "24IN", "27FHD")
            if not re.fullmatch(r"\d+[A-Z]{0,3}", candidate):
                return candidate
    return None
