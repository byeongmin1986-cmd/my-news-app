"""
📈 주식 대시보드 — SOXL · FCEL · 삼성전자
초보자도 쉽게 보는 매일 자동 갱신 주식 분석 앱

⚠️ 이 앱은 참고용 정보만 제공합니다. 투자 결정은 본인 책임입니다.
"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv

from data_cache import TICKERS, get_hist_data, get_current_price_data
from news_fetcher import get_news_for_ticker
from ai_analyzer import analyze_with_ai

load_dotenv()

# ── Page configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="📈 주식 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Global ── */
html, body, [class*="css"] { font-family: 'Segoe UI', 'Apple SD Gothic Neo', sans-serif; }

/* ── Disclaimer banner ── */
.disclaimer-banner {
    background: rgba(255, 193, 7, 0.12);
    border-left: 4px solid #ffc107;
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 13px;
    color: #c8a400;
    margin-bottom: 12px;
}

/* ── Market summary card ── */
.market-card {
    background: #1a1a2e;
    border-radius: 10px;
    padding: 14px 18px;
    text-align: center;
    border: 1px solid #2a2a4a;
}

/* ── Section headers ── */
.section-title {
    font-size: 18px;
    font-weight: 700;
    margin: 16px 0 8px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid #4a9eff;
    display: inline-block;
}

/* ── News cards ── */
.news-card {
    background: #1a1a2e;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    border-left: 4px solid #4a9eff;
    font-size: 14px;
}
.news-card.positive { border-left-color: #00c87a; }
.news-card.negative { border-left-color: #ff4b4b; }
.news-card.neutral  { border-left-color: #888; }

/* ── Sentiment badges ── */
.badge {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
}
.badge-positive { background: rgba(0,200,122,0.2); color: #00c87a; }
.badge-negative { background: rgba(255,75,75,0.2);  color: #ff4b4b; }
.badge-neutral  { background: rgba(136,136,136,0.2); color: #aaa; }

/* ── AI analysis box ── */
.ai-box {
    background: #16213e;
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
    border: 1px solid #2a3a5e;
}
.ai-box h4 { margin: 0 0 8px 0; font-size: 14px; color: #4a9eff; }

/* ── Beginner summary ── */
.beginner-box {
    background: rgba(74,158,255,0.1);
    border: 1px solid #4a9eff;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 15px;
    margin-top: 12px;
}

/* ── Footer ── */
.footer {
    text-align: right;
    font-size: 11px;
    color: #555;
    margin-top: 24px;
    padding-top: 8px;
    border-top: 1px solid #222;
}

/* ── Tooltip definition list ── */
.tooltip-term {
    border-bottom: 1px dashed #888;
    cursor: help;
    font-size: 13px;
    color: #aaa;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_price(price: float | None, currency: str) -> str:
    if price is None:
        return "—"
    return f"₩{price:,.0f}" if currency == "KRW" else f"${price:,.2f}"


def fmt_change(change_pct: float | None) -> tuple[str, str]:
    """Returns (display_string, delta_color_for_st.metric)."""
    if change_pct is None:
        return "—", "off"
    sign = "+" if change_pct >= 0 else ""
    return f"{sign}{change_pct:.2f}%", "normal"


def fmt_volume(vol: int | None, currency: str) -> str:
    if vol is None:
        return "—"
    if currency == "KRW":
        return f"{vol:,} 주"
    if vol >= 1_000_000:
        return f"{vol / 1_000_000:.1f}M 주"
    if vol >= 1_000:
        return f"{vol / 1_000:.0f}K 주"
    return f"{vol:,} 주"


SENTIMENT_CONFIG = {
    "positive": ("🟢", "긍정", "positive"),
    "negative": ("🔴", "부정", "negative"),
    "neutral":  ("⚪", "중립", "neutral"),
}

GLOSSARY = {
    "52주 고점": "최근 52주(1년) 동안의 최고 가격",
    "52주 저점": "최근 52주(1년) 동안의 최저 가격",
    "등락률": "전날 종가 대비 오늘 가격이 얼마나 변했는지 %로 표시",
    "레버리지 ETF": "기준 지수의 2~3배로 움직이는 펀드. 수익과 손실 모두 증폭됩니다.",
    "ETF": "여러 주식을 묶어 하나처럼 거래하는 상품 (Exchange Traded Fund)",
    "거래량": "하루 동안 사고판 주식의 수량",
}


def glossary_tooltip(term: str) -> str:
    definition = GLOSSARY.get(term, "")
    if definition:
        return f'<span class="tooltip-term" title="{definition}">❔ {term}</span>'
    return term


# ── Chart builders ────────────────────────────────────────────────────────────

def _line_chart(hist: pd.DataFrame, name: str, label: str) -> go.Figure:
    closes = hist["Close"]
    color = "#00c87a" if closes.iloc[-1] >= closes.iloc[0] else "#ff4b4b"
    fill_color = "rgba(0,200,122,0.08)" if color == "#00c87a" else "rgba(255,75,75,0.08)"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=closes,
        mode="lines", name=name,
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=fill_color,
        hovertemplate="%{x|%Y-%m-%d}<br>종가: %{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        title=f"{name} ({label})",
        template="plotly_dark",
        height=360, margin=dict(l=0, r=0, t=36, b=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1a1a2e"),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _candle_chart(hist: pd.DataFrame, name: str, label: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"], high=hist["High"],
        low=hist["Low"],  close=hist["Close"],
        name=name,
        increasing_line_color="#00c87a",
        decreasing_line_color="#ff4b4b",
    ))
    if "Volume" in hist.columns:
        fig.add_trace(go.Bar(
            x=hist.index, y=hist["Volume"],
            name="거래량",
            marker_color="rgba(100,149,237,0.25)",
            yaxis="y2",
        ))
    fig.update_layout(
        title=f"{name} ({label})",
        template="plotly_dark",
        height=400, margin=dict(l=0, r=0, t=36, b=0),
        xaxis_rangeslider_visible=False,
        yaxis2=dict(overlaying="y", side="right", showgrid=False, showticklabels=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_chart(hist: pd.DataFrame | None, name: str, label: str, use_candle: bool) -> go.Figure | None:
    if hist is None or hist.empty:
        return None
    return _candle_chart(hist, name, label) if use_candle else _line_chart(hist, name, label)


# ── Per-ticker tab renderer ───────────────────────────────────────────────────

def render_ticker_tab(ticker: str, info: dict) -> None:
    name = info["name"]
    currency = info["currency"]

    # ── Price cards ──────────────────────────────────────────────────────────
    with st.spinner(f"{name} 데이터 불러오는 중..."):
        price = get_current_price_data(ticker)

    if price is None:
        st.error(
            f"⚠️ **{name}** 가격 데이터를 불러올 수 없습니다.  \n"
            "인터넷 연결을 확인하거나 잠시 후 새로고침 해주세요."
        )
        return

    change_str, delta_color = fmt_change(price.get("change_pct"))

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("현재가", fmt_price(price["current"], currency), change_str, delta_color=delta_color)
    with c2:
        st.metric("전일 종가", fmt_price(price["prev"], currency))
    with c3:
        st.metric("52주 고점 📈", fmt_price(price.get("week52_high"), currency))
    with c4:
        st.metric("52주 저점 📉", fmt_price(price.get("week52_low"), currency))
    with c5:
        st.metric("거래량", fmt_volume(price.get("volume"), currency))

    # Glossary row
    st.markdown(
        f'<small>{glossary_tooltip("등락률")} · {glossary_tooltip("52주 고점")} · '
        f'{glossary_tooltip("52주 저점")} · {glossary_tooltip("거래량")}</small>',
        unsafe_allow_html=True,
    )

    # ── Ticker description ────────────────────────────────────────────────────
    with st.expander("ℹ️ 이 종목은 무엇인가요?"):
        st.markdown(info.get("description", ""))
        if "ETF" in name or "ETF" in info.get("description", ""):
            st.markdown(
                f"> {glossary_tooltip('레버리지 ETF')} · {glossary_tooltip('ETF')}",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Chart ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 주가 차트</div>', unsafe_allow_html=True)
    st.markdown("")

    PERIOD_OPTIONS: dict[str, tuple[str, str, bool]] = {
        # label → (yfinance period, interval, use_candlestick)
        "1일":   ("1d",  "5m",  False),
        "5일":   ("5d",  "1h",  False),
        "1개월": ("1mo", "1d",  True),
        "6개월": ("6mo", "1wk", True),
        "1년":   ("1y",  "1d",  True),
    }

    selected = st.radio(
        "기간", list(PERIOD_OPTIONS.keys()),
        horizontal=True, key=f"period_{ticker}",
    )
    period_val, interval_val, use_candle = PERIOD_OPTIONS[selected]

    with st.spinner("차트 불러오는 중..."):
        hist = get_hist_data(ticker, period_val, interval_val)

    # Fallback: intraday (5m/1h) may fail for KRX → retry with daily
    if (hist is None or hist.empty) and interval_val in ("5m", "1h"):
        hist = get_hist_data(ticker, period_val, "1d")
        use_candle = False

    fig = build_chart(hist, name, selected, use_candle)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"⚠️ {selected} 차트 데이터를 불러올 수 없습니다. 잠시 후 다시 시도해주세요.")

    st.divider()

    # ── News ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📰 최근 뉴스</div>', unsafe_allow_html=True)
    st.markdown("")

    with st.spinner("뉴스 불러오는 중..."):
        news_items = get_news_for_ticker(ticker, info)

    if not news_items:
        st.info(
            "ℹ️ 뉴스를 불러올 수 없습니다.  \n"
            "• Finnhub API 키를 `.env`에 설정하면 더 정확한 뉴스를 볼 수 있습니다.  \n"
            "• 인터넷 연결 상태를 확인해주세요."
        )
    else:
        # Sentiment summary bar
        sentiments = [n.get("sentiment", "neutral") for n in news_items]
        pos = sentiments.count("positive")
        neg = sentiments.count("negative")
        neu = sentiments.count("neutral")
        st.markdown(
            f'<span class="badge badge-positive">🟢 긍정 {pos}</span>'
            f'<span class="badge badge-negative">🔴 부정 {neg}</span>'
            f'<span class="badge badge-neutral">⚪ 중립 {neu}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        for n in news_items[:6]:
            sent = n.get("sentiment", "neutral")
            emoji, label, css_class = SENTIMENT_CONFIG.get(sent, ("⚪", "중립", "neutral"))
            title = n.get("title", "제목 없음")
            summary = n.get("summary", "")
            source = n.get("source", "")
            date = n.get("date", "")
            url = n.get("url", "")

            badge_html = f'<span class="badge badge-{css_class}">{emoji} {label}</span>'
            header = f"{badge_html} **{title[:90]}{'...' if len(title) > 90 else ''}**"

            with st.expander(f"{emoji} {title[:80]}{'...' if len(title) > 80 else ''}"):
                st.markdown(badge_html, unsafe_allow_html=True)
                if summary:
                    st.markdown(f"**요약:** {summary}")
                meta = " · ".join(filter(None, [source, date]))
                if meta:
                    st.caption(meta)
                if url:
                    st.markdown(f"[🔗 기사 원문 보기]({url})")

    st.divider()

    # ── AI Analysis ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🤖 AI 분석</div>', unsafe_allow_html=True)
    st.markdown("")

    st.markdown("""
<div class="disclaimer-banner">
⚠️ <strong>투자 주의사항</strong>: 아래 AI 분석은 참고용 정보입니다.
매수/매도 추천이 아니며, 투자 결정은 반드시 본인이 신중하게 판단하세요.
과거 데이터와 뉴스를 기반으로 한 가능성 분석이며 결과를 보장하지 않습니다.
</div>
""", unsafe_allow_html=True)

    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
    has_openai = bool(os.getenv("OPENAI_API_KEY", "").strip())

    if not has_anthropic and not has_openai:
        st.info(
            "ℹ️ **AI 분석을 사용하려면** `.env` 파일에 API 키를 추가해주세요.  \n"
            "• `ANTHROPIC_API_KEY=...` (Claude, 권장)  \n"
            "• `OPENAI_API_KEY=...` (GPT-4o-mini, 대안)"
        )
        _show_demo_analysis(price, name)
        return

    # Run analysis
    session_key = f"analysis_{ticker}"
    if st.button(f"🔍 AI 분석 실행 ({name})", key=f"btn_{ticker}"):
        with st.spinner("AI 분석 중... (30초 정도 소요될 수 있습니다)"):
            result = analyze_with_ai(ticker, info, price, news_items)
        st.session_state[session_key] = result

    analysis = st.session_state.get(session_key)

    if analysis is None:
        st.caption("위 버튼을 눌러 AI 분석을 시작하세요.")
    elif not analysis:
        st.error(
            "AI 분석을 가져오지 못했습니다.  \n"
            "API 키가 올바른지 확인하고 다시 시도해주세요."
        )
    else:
        _show_ai_result(analysis)


def _show_demo_analysis(price: dict, name: str) -> None:
    """Show placeholder analysis when no API key is set."""
    change_pct = price.get("change_pct", 0)
    direction = "상승" if change_pct >= 0 else "하락"
    with st.expander("📊 분석 미리보기 (데모)", expanded=False):
        st.markdown(f"""
**{name}** 은 오늘 **{abs(change_pct):.2f}% {direction}** 했습니다.

API 키를 설정하면 다음 항목을 분석해드립니다:
- 📈 상승 가능 요인 (거시경제, 뉴스, 섹터 동향)
- 📉 하락 가능 요인
- ⚠️ 주요 리스크
- 🌍 시장 맥락 설명
- 💡 초보자용 한 줄 해석
""")


def _show_ai_result(analysis: dict) -> None:
    """Render the structured AI analysis dict."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="ai-box"><h4>📈 상승 가능 요인</h4>', unsafe_allow_html=True)
        st.markdown(analysis.get("bullish_factors", "데이터 없음"))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ai-box"><h4>⚠️ 주요 리스크</h4>', unsafe_allow_html=True)
        st.markdown(analysis.get("risks", "데이터 없음"))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="ai-box"><h4>📉 하락 가능 요인</h4>', unsafe_allow_html=True)
        st.markdown(analysis.get("bearish_factors", "데이터 없음"))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ai-box"><h4>🌍 시장 맥락</h4>', unsafe_allow_html=True)
        st.markdown(analysis.get("market_context", "데이터 없음"))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="beginner-box">'
        f'💡 <strong>초보자용 한 줄 해석:</strong> {analysis.get("beginner_summary", "—")}'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── App layout ────────────────────────────────────────────────────────────────

# Header
st.markdown("""
<h1 style='text-align:center; margin-bottom:4px;'>📈 주식 대시보드</h1>
<p style='text-align:center; color:#888; font-size:14px; margin-top:0;'>
SOXL &nbsp;·&nbsp; FCEL &nbsp;·&nbsp; 삼성전자 &nbsp;|&nbsp; 초보자를 위한 쉬운 주식 분석
</p>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-banner">
⚠️ 이 대시보드는 <strong>참고용 정보만</strong> 제공합니다.
투자 결정은 반드시 본인의 책임 하에 신중하게 하시고, 필요 시 전문 금융 상담사에게 조언을 구하세요.
<strong>과거 수익이 미래 수익을 보장하지 않습니다.</strong>
</div>
""", unsafe_allow_html=True)

# ── Market summary ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🌍 전체 시장 요약</div>', unsafe_allow_html=True)
st.markdown("")

summary_cols = st.columns(len(TICKERS))
for col, (ticker, info) in zip(summary_cols, TICKERS.items()):
    with col:
        price = get_current_price_data(ticker)
        if price:
            change_str, delta_color = fmt_change(price.get("change_pct"))
            st.metric(
                label=info["short_name"],
                value=fmt_price(price["current"], info["currency"]),
                delta=change_str,
                delta_color=delta_color,
            )
        else:
            st.metric(label=info["short_name"], value="—")

st.divider()

# ── Ticker tabs ───────────────────────────────────────────────────────────────
tab_labels = [f"📊 {v['short_name']}" for v in TICKERS.values()]
tabs = st.tabs(tab_labels)

for tab, (ticker, info) in zip(tabs, TICKERS.items()):
    with tab:
        render_ticker_tab(ticker, info)

# ── Footer ────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
st.markdown(
    f'<div class="footer">🕐 현재 시각: {now_str} &nbsp;|&nbsp; 데이터 캐시: 최대 6시간 유지 &nbsp;|&nbsp; '
    f'데이터 출처: Yahoo Finance, Google News, Finnhub</div>',
    unsafe_allow_html=True,
)
