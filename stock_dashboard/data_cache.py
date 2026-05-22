"""
Stock data fetching with 6-hour cache.
Uses yfinance for all tickers: SOXL, FCEL, 005930.KS (Samsung).
"""

import yfinance as yf
import pandas as pd
import streamlit as st

TICKERS: dict[str, dict] = {
    "SOXL": {
        "name": "Direxion 반도체 3X ETF",
        "short_name": "SOXL",
        "currency": "USD",
        "market": "US",
        "description": "미국 반도체 기업들의 주가를 3배로 추종하는 레버리지 ETF입니다. 반도체 시장이 오르면 3배로 오르고, 내리면 3배로 내립니다.",
        "finnhub_symbol": "SOXL",
        "news_query_en": "SOXL semiconductor ETF stock",
        "news_query_ko": None,
    },
    "FCEL": {
        "name": "FuelCell Energy",
        "short_name": "FCEL",
        "currency": "USD",
        "market": "US",
        "description": "수소 연료전지 기술을 개발하는 청정 에너지 기업입니다. 탄소 중립, 친환경 에너지 트렌드에 연동됩니다.",
        "finnhub_symbol": "FCEL",
        "news_query_en": "FCEL FuelCell Energy stock",
        "news_query_ko": None,
    },
    "005930.KS": {
        "name": "삼성전자",
        "short_name": "삼성전자",
        "currency": "KRW",
        "market": "KR",
        "description": "대한민국 최대 전자 기업으로 반도체(메모리/파운드리), 스마트폰, 가전제품 등을 생산합니다.",
        "finnhub_symbol": None,
        "news_query_en": "Samsung Electronics stock KRX",
        "news_query_ko": "삼성전자 주가",
    },
}


def _strip_tz(df: pd.DataFrame) -> pd.DataFrame:
    """Remove timezone info from DataFrame index for Plotly compatibility."""
    if df is None or df.empty:
        return df
    if hasattr(df.index, "tz") and df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def get_hist_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame | None:
    """Fetch OHLCV history. Returns None on failure."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval, auto_adjust=True)
        if hist is None or hist.empty:
            return None
        return _strip_tz(hist)
    except Exception:
        return None


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def get_current_price_data(ticker: str) -> dict | None:
    """
    Returns current price, daily change, volume, and 52-week range.
    All values are plain Python floats/ints so they serialize cleanly.
    """
    try:
        hist_5d = get_hist_data(ticker, "5d", "1d")
        if hist_5d is None or len(hist_5d) < 1:
            return None

        current = float(hist_5d["Close"].iloc[-1])
        prev = float(hist_5d["Close"].iloc[-2]) if len(hist_5d) >= 2 else current
        change = current - prev
        change_pct = (change / prev * 100) if prev != 0 else 0.0
        volume = int(hist_5d["Volume"].iloc[-1]) if "Volume" in hist_5d.columns else 0

        hist_1y = get_hist_data(ticker, "1y", "1d")
        week52_high = float(hist_1y["High"].max()) if hist_1y is not None else None
        week52_low = float(hist_1y["Low"].min()) if hist_1y is not None else None

        return {
            "current": current,
            "prev": prev,
            "change": change,
            "change_pct": change_pct,
            "volume": volume,
            "week52_high": week52_high,
            "week52_low": week52_low,
        }
    except Exception:
        return None
