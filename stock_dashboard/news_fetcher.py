"""
News fetching for US stocks (Finnhub API or Google News RSS fallback)
and Korean stocks (Google News / Naver RSS).
Includes simple keyword-based sentiment tagging.
"""

import os
import re
import requests
import feedparser
import streamlit as st
from datetime import datetime, timedelta
from urllib.parse import quote

# ── Sentiment keyword lists ──────────────────────────────────────────────────

_POSITIVE = [
    "surge", "gain", "rise", "jump", "soar", "rally", "record", "beat",
    "strong", "growth", "profit", "bullish", "upgrade", "buy",
    "outperform", "exceed", "boost", "positive", "revenue", "demand",
    "상승", "급등", "호조", "실적", "성장", "매수", "긍정", "돌파", "역대",
    "수익", "강세", "신고", "확대", "상회", "개선",
]

_NEGATIVE = [
    "fall", "drop", "decline", "plunge", "crash", "loss", "miss", "weak",
    "bearish", "downgrade", "sell", "negative", "risk", "concern",
    "warning", "below", "disappoint", "cut", "layoff", "recall",
    "하락", "급락", "부진", "손실", "우려", "리스크", "매도", "하회",
    "부정", "적자", "감소", "충격", "경고", "위기", "악화",
]


def _sentiment(text: str) -> str:
    t = text.lower()
    pos = sum(1 for kw in _POSITIVE if kw in t)
    neg = sum(1 for kw in _NEGATIVE if kw in t)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def _clean_html(raw: str) -> str:
    return re.sub(r"<[^>]+>", "", raw or "").strip()


# ── Finnhub ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_finnhub(symbol: str, api_key: str) -> list[dict]:
    try:
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        resp = requests.get(
            "https://finnhub.io/api/v1/company-news",
            params={"symbol": symbol, "from": start, "to": end, "token": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json() or []
        result = []
        for it in items[:8]:
            title = it.get("headline", "")
            summary = it.get("summary", "")[:300]
            ts = it.get("datetime", 0)
            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else ""
            result.append({
                "title": title,
                "summary": summary + ("..." if len(summary) == 300 else ""),
                "source": it.get("source", ""),
                "date": date_str,
                "url": it.get("url", ""),
                "sentiment": _sentiment(title + " " + summary),
            })
        return result
    except Exception:
        return []


# ── Google News RSS ───────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_google_rss(query: str, hl: str = "en", gl: str = "US", ceid: str = "US:en") -> list[dict]:
    try:
        url = (
            f"https://news.google.com/rss/search"
            f"?q={quote(query)}&hl={hl}&gl={gl}&ceid={ceid}"
        )
        feed = feedparser.parse(url)
        result = []
        for entry in feed.entries[:8]:
            title = _clean_html(entry.get("title", ""))
            summary = _clean_html(entry.get("summary", ""))[:300]
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                date_str = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
            else:
                date_str = ""
            src = entry.get("source", {})
            source_name = src.get("title", "Google 뉴스") if isinstance(src, dict) else "Google 뉴스"
            result.append({
                "title": title,
                "summary": summary + ("..." if len(summary) == 300 else ""),
                "source": source_name,
                "date": date_str,
                "url": entry.get("link", ""),
                "sentiment": _sentiment(title + " " + summary),
            })
        return result
    except Exception:
        return []


# ── Naver News RSS ────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_naver_rss(query: str) -> list[dict]:
    """Naver News RSS search (no API key required)."""
    try:
        url = f"https://news.naver.com/search/results.nhn?query={quote(query)}&sm=tab_jum"
        # Naver RSS endpoint
        rss_url = f"https://news.naver.com/search/results.nhn?query={quote(query)}&field=0&sm=tab_jum&sort=0&photo=0&video=0&office_type=0&office_section_code=0&mnl_code=0&is_sug_officeid=0&office_category=0&service_area=0&rss=1"
        feed = feedparser.parse(rss_url)
        result = []
        for entry in feed.entries[:8]:
            title = _clean_html(entry.get("title", ""))
            summary = _clean_html(entry.get("summary", ""))[:300]
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                date_str = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
            else:
                date_str = ""
            result.append({
                "title": title,
                "summary": summary,
                "source": "네이버 뉴스",
                "date": date_str,
                "url": entry.get("link", ""),
                "sentiment": _sentiment(title + " " + summary),
            })
        return [r for r in result if r["title"]]
    except Exception:
        return []


# ── Public interface ──────────────────────────────────────────────────────────

def get_news_for_ticker(ticker: str, ticker_info: dict) -> list[dict]:
    """Return up to 8 news items for a ticker, using best available source."""
    finnhub_key = os.getenv("FINNHUB_API_KEY", "").strip()

    if ticker_info.get("market") == "KR":
        # Korean stock: try Google KR RSS, then Naver RSS
        news = _fetch_google_rss(
            ticker_info.get("news_query_ko", "삼성전자 주가"),
            hl="ko", gl="KR", ceid="KR:ko",
        )
        if not news:
            news = _fetch_naver_rss("삼성전자 주가")
        if not news:
            news = _fetch_google_rss(
                ticker_info.get("news_query_en", "Samsung Electronics"),
                hl="en", gl="US", ceid="US:en",
            )
        return news

    # US stocks: Finnhub → Google News RSS fallback
    if finnhub_key and ticker_info.get("finnhub_symbol"):
        news = _fetch_finnhub(ticker_info["finnhub_symbol"], finnhub_key)
        if news:
            return news

    return _fetch_google_rss(
        ticker_info.get("news_query_en", ticker + " stock"),
        hl="en", gl="US", ceid="US:en",
    )
