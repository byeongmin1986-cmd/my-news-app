import math
from datetime import datetime, timedelta

import pandas as pd
import pytz
import requests
import streamlit as st
from bs4 import BeautifulSoup

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SK하이닉스 ETF 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

KST = pytz.timezone("Asia/Seoul")

DEFAULT_TICKER = "0193T0"
DEFAULT_NAME = "KODEX SK하이닉스단일종목레버리지"
DEFAULT_TOTAL_BUDGET = 30_000_000
DEFAULT_SPLIT_COUNT = 7
DEFAULT_BUY_RATE = 3.6
DEFAULT_SELL_RATE = 3.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ── Tick helpers ──────────────────────────────────────────────────────────────
def ceil_to_5(price: float) -> int:
    return int(math.ceil(price / 5) * 5)


def round_to_5(price: float) -> int:
    return int(round(price / 5) * 5)


def apply_tick(price: float, method: str = "ceil") -> int:
    return ceil_to_5(price) if method == "ceil" else round_to_5(price)


def fmt(amount: float) -> str:
    return f"{int(amount):,}원"


def _parse_int(text: str):
    try:
        return int(str(text).replace(",", "").replace("원", "").strip())
    except (ValueError, AttributeError):
        return None


# ── Data fetching (priority: Naver → Daum → pykrx) ───────────────────────────
def fetch_naver(code: str):
    """Naver Finance HTML scraping."""
    try:
        url = f"https://finance.naver.com/item/main.nhn?code={code}"
        resp = requests.get(url, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        current = None
        now_el = soup.select_one("em#_nowVal")
        if now_el:
            current = _parse_int(now_el.get_text())

        prev = None
        pc_el = soup.select_one("em#_pcost")
        if pc_el:
            prev = _parse_int(pc_el.get_text())

        if prev:
            return prev, current, None
        return None, None, "전일종가 요소 미발견"
    except Exception as exc:
        return None, None, str(exc)


def fetch_daum(code: str):
    """Daum Finance JSON API."""
    try:
        headers = {**HEADERS, "Referer": "https://finance.daum.net"}
        url = f"https://finance.daum.net/api/quotes/A{code}"
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            prev = data.get("prevClosingPrice") or data.get("basePrice")
            cur = data.get("tradePrice")
            if prev:
                return int(prev), (int(cur) if cur else None), None
        return None, None, f"HTTP {resp.status_code}"
    except Exception as exc:
        return None, None, str(exc)


def fetch_pykrx(code: str):
    """pykrx – direct KRX query."""
    try:
        from pykrx import stock  # noqa: PLC0415

        today = datetime.now(KST)
        start = (today - timedelta(days=10)).strftime("%Y%m%d")
        end = today.strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, end, code)
        if not df.empty:
            return int(df["종가"].iloc[-1]), None, None
        return None, None, "데이터 없음"
    except Exception as exc:
        return None, None, str(exc)


def get_price_data(code: str):
    """Try each source; return first success."""
    now = datetime.now(KST)
    errors: dict = {}
    for label, fn in [
        ("네이버 금융", fetch_naver),
        ("Daum 금융", fetch_daum),
        ("pykrx (KRX)", fetch_pykrx),
    ]:
        prev, cur, err = fn(code)
        if prev and prev > 0:
            return prev, cur, label, now, errors
        errors[label] = err or "알 수 없는 오류"
    return None, None, None, now, errors


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    st.title("📈 KODEX SK하이닉스단일종목레버리지 ETF 대시보드")
    st.caption(
        "⚠️ 본 대시보드는 가격 참고 및 매수/매도 계획 수립을 위한 도구입니다. "
        "모든 투자 결정은 반드시 본인이 직접 판단하시기 바랍니다."
    )

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ 설정")

        ticker = st.text_input("종목코드", value=DEFAULT_TICKER)
        stock_name = st.text_input("종목명", value=DEFAULT_NAME)

        st.divider()
        st.subheader("목표 수익률")
        buy_rate = st.number_input(
            "매수 기준 상승률 (%)", value=DEFAULT_BUY_RATE, step=0.1, format="%.2f"
        )
        sell_rate = st.number_input(
            "매도 목표 상승률 (%)", value=DEFAULT_SELL_RATE, step=0.1, format="%.2f"
        )

        st.divider()
        st.subheader("호가 단위")
        tick_label = st.radio("5원 단위 처리", ["올림 (기본)", "반올림"], index=0)
        tick_method = "ceil" if "올림" in tick_label else "round"

        st.divider()
        st.subheader("투자 설정")
        total_budget = st.number_input(
            "총 투자금 (원)",
            value=DEFAULT_TOTAL_BUDGET,
            step=1_000_000,
            min_value=1_000_000,
            format="%d",
        )
        split_count = int(
            st.number_input("분할 수", value=DEFAULT_SPLIT_COUNT, min_value=1, max_value=20, step=1)
        )

        st.divider()
        if st.button("🔄 데이터 새로고침", use_container_width=True):
            st.session_state.pop("price_data", None)
            st.rerun()

    # ── Price fetching ────────────────────────────────────────────────────────
    if "price_data" not in st.session_state:
        with st.spinner("전일 종가 데이터를 가져오는 중…"):
            st.session_state.price_data = get_price_data(ticker)

    prev_auto, cur_auto, source, fetch_time, errors = st.session_state.price_data

    if prev_auto:
        st.success(
            f"✅ 데이터 출처: **{source}** | "
            f"업데이트: {fetch_time.strftime('%Y-%m-%d %H:%M:%S KST')}"
        )
    else:
        st.warning("⚠️ 자동 데이터 조회 실패. 전일 종가를 직접 입력해주세요.")
        with st.expander("🔍 오류 상세"):
            for src, err in errors.items():
                st.text(f"{src}: {err}")

    # ── Manual inputs ─────────────────────────────────────────────────────────
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        suffix = " · 자동조회 성공" if prev_auto else " · ✏️ 직접 입력 필요"
        prev_close = st.number_input(
            f"전일 종가 (원){suffix}",
            value=prev_auto if prev_auto else 28_970,
            min_value=1,
            step=5,
            format="%d",
        )
    with col_in2:
        current_price = st.number_input(
            "현재가 (원, 0 입력 시 미표시)",
            value=cur_auto if cur_auto else 0,
            min_value=0,
            step=5,
            format="%d",
        )

    # ── Price calculations ────────────────────────────────────────────────────
    buy_price = apply_tick(prev_close * (1 + buy_rate / 100), tick_method)
    # Sell target based on actual purchase price → profit-generating structure
    sell_price = apply_tick(buy_price * (1 + sell_rate / 100), tick_method)
    # Reference only: sell based on prev_close (loss structure when buy_rate > sell_rate)
    sell_price_ref = apply_tick(prev_close * (1 + sell_rate / 100), tick_method)

    # ── Stock info ────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 종목 정보")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("종목명", stock_name)
    c2.metric("종목코드", ticker)
    c3.metric("전일 종가", fmt(prev_close))
    if current_price > 0:
        chg = current_price - prev_close
        chg_pct = chg / prev_close * 100
        c4.metric("현재가", fmt(current_price), f"{chg:+,}원 ({chg_pct:+.2f}%)")
    else:
        c4.metric("현재가", "미입력")

    # ── Buy / Sell target prices ──────────────────────────────────────────────
    st.divider()
    st.subheader("🎯 매수/매도 기준가")

    with st.expander("ℹ️ 매도 기준가 계산 방식 안내 (클릭하여 펼치기)"):
        st.markdown(
            f"""
**⚠️ 전일 종가 기준 매도 시 손실 구조 주의**

| 구분 | 가격 |
|------|------|
| 매수 기준가 (전일 종가 +{buy_rate:.1f}%) | {fmt(buy_price)} |
| 매도가 – 전일 종가 기준 +{sell_rate:.1f}% | {fmt(sell_price_ref)} |

→ 매도가 {fmt(sell_price_ref)} < 매수가 {fmt(buy_price)} → **❌ 손실 구조**

**✅ 본 앱 적용 방식: 실제 매수가 기준 매도**

매도 목표가 = 매수가 {fmt(buy_price)} × {1 + sell_rate / 100:.4f} = **{fmt(sell_price)}** → **수익 구조**
"""
        )

    pc1, pc2 = st.columns(2)
    with pc1:
        st.info(
            f"### 🟢 매수 기준가 &nbsp; {fmt(buy_price)}\n\n"
            f"전일 종가 {fmt(prev_close)} × {1 + buy_rate / 100:.4f}  \n"
            f"= {prev_close * (1 + buy_rate / 100):,.1f}원  \n"
            f"→ 5원 단위 **{tick_label.split(' ')[0]}** → **{fmt(buy_price)}**"
        )
        if current_price > 0:
            if current_price >= buy_price:
                st.success("🔔 **매수 기준 도달!**")
            else:
                st.warning(f"매수 기준까지 {fmt(buy_price - current_price)} 남음")

    with pc2:
        st.info(
            f"### 🔴 매도 목표가 &nbsp; {fmt(sell_price)}\n\n"
            f"매수가 {fmt(buy_price)} × {1 + sell_rate / 100:.4f}  \n"
            f"= {buy_price * (1 + sell_rate / 100):,.1f}원  \n"
            f"→ 5원 단위 **{tick_label.split(' ')[0]}** → **{fmt(sell_price)}**"
        )
        if current_price > 0:
            if current_price >= sell_price:
                st.success("🔔 **매도 기준 도달!**")
            elif current_price >= buy_price:
                st.warning(f"매도 기준까지 {fmt(sell_price - current_price)} 남음")

    # ── Investment calculations ───────────────────────────────────────────────
    unit_budget = total_budget / split_count
    qty_per = math.floor(unit_budget / buy_price)
    used_per = qty_per * buy_price
    remaining_per = unit_budget - used_per

    total_qty = qty_per * split_count
    total_used = used_per * split_count
    # Remaining = per-split leftovers + any budget not distributed (floating point)
    total_remaining = total_budget - total_used

    total_sell_val = total_qty * sell_price
    profit = total_sell_val - total_used
    profit_rate = (profit / total_used * 100) if total_used > 0 else 0.0
    profit_rate_on_budget = (profit / total_budget * 100) if total_budget > 0 else 0.0

    st.divider()
    st.subheader(f"💰 {split_count}분할 매수/매도 계획")

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("총 투자금", fmt(total_budget))
    s1.metric("1회 분할금액", fmt(unit_budget))
    s2.metric("1회 매수 수량", f"{qty_per:,}주")
    s2.metric(f"{split_count}회 총 수량", f"{total_qty:,}주")
    s3.metric("총 투자 원가", fmt(total_used))
    s3.metric("잔여 현금 (미사용)", fmt(total_remaining))
    s4.metric("전량 매도 예상금액", fmt(total_sell_val))

    delta_color = "normal" if profit >= 0 else "inverse"
    s4.metric(
        "예상 수익금",
        fmt(profit),
        f"{profit_rate:+.2f}% (원가 대비)",
        delta_color=delta_color,
    )

    # ── Buy table ─────────────────────────────────────────────────────────────
    st.subheader("📋 매수 계획표")
    buy_rows = []
    cum_qty = 0
    cum_used = 0.0
    for i in range(1, split_count + 1):
        cum_qty += qty_per
        cum_used += used_per
        buy_rows.append(
            {
                "회차": f"제{i}회",
                "분할금액": f"{unit_budget:,.0f}원",
                "매수기준가": f"{buy_price:,}원",
                "매수수량": f"{qty_per:,}주",
                "사용금액": f"{used_per:,.0f}원",
                "남은현금": f"{remaining_per:,.0f}원",
                "누적수량": f"{cum_qty:,}주",
                "누적사용금액": f"{cum_used:,.0f}원",
            }
        )
    st.dataframe(pd.DataFrame(buy_rows), use_container_width=True, hide_index=True)

    # ── Sell table ────────────────────────────────────────────────────────────
    st.subheader("📋 매도 계획표")
    sell_rows = []
    cum_sell = 0.0
    for i in range(1, split_count + 1):
        sell_val = qty_per * sell_price
        cost_val = qty_per * buy_price
        pnl = sell_val - cost_val
        pnl_r = (pnl / cost_val * 100) if cost_val else 0.0
        cum_sell += sell_val
        sell_rows.append(
            {
                "회차": f"제{i}회",
                "보유수량": f"{qty_per:,}주",
                "매수기준가": f"{buy_price:,}원",
                "매도목표가": f"{sell_price:,}원",
                "예상매도금액": f"{sell_val:,.0f}원",
                "투자원가": f"{cost_val:,.0f}원",
                "예상손익": f"{pnl:+,.0f}원",
                "손익률": f"{pnl_r:+.2f}%",
            }
        )
    st.dataframe(pd.DataFrame(sell_rows), use_container_width=True, hide_index=True)

    # ── Final summary table ───────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 최종 요약")

    col_l, col_r = st.columns(2)
    with col_l:
        st.table(
            pd.DataFrame(
                {
                    "항목": [
                        "총 투자금",
                        f"{split_count}분할 1회 금액",
                        "매수 기준가",
                        "1회 매수 가능 수량",
                        "1회 사용 금액",
                        "1회 잔여 현금",
                        f"{split_count}회 총 매수 수량",
                        "총 사용 금액",
                        "총 잔여 현금 (미사용)",
                    ],
                    "값": [
                        fmt(total_budget),
                        fmt(unit_budget),
                        fmt(buy_price),
                        f"{qty_per:,}주",
                        fmt(used_per),
                        fmt(remaining_per),
                        f"{total_qty:,}주",
                        fmt(total_used),
                        fmt(total_remaining),
                    ],
                }
            )
        )
    with col_r:
        st.table(
            pd.DataFrame(
                {
                    "항목": [
                        "매도 목표가 (매수가 기준)",
                        "전량 매도 예상금액",
                        "예상 수익금",
                        "예상 수익률 (원가 대비)",
                        "예상 수익률 (총투자금 대비)",
                        "데이터 출처",
                        "업데이트 시간",
                    ],
                    "값": [
                        fmt(sell_price),
                        fmt(total_sell_val),
                        f"{profit:+,.0f}원",
                        f"{profit_rate:+.2f}%",
                        f"{profit_rate_on_budget:+.2f}%",
                        source if source else "수동 입력",
                        fetch_time.strftime("%Y-%m-%d %H:%M:%S KST"),
                    ],
                }
            )
        )

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.divider()
    st.warning(
        "⚠️ **투자 유의사항**  \n"
        "본 대시보드는 가격 참고 및 매수·매도 계획 수립을 위한 도구로만 제공됩니다.  \n"
        "과거 수익률이 미래 수익을 보장하지 않으며, 투자 손실의 책임은 투자자 본인에게 있습니다.  \n"
        "ETF 가격은 실시간으로 변동되며 제공 데이터는 지연될 수 있습니다.  \n"
        "자동 주문 기능은 포함되어 있지 않으며, 모든 투자 판단은 본인이 직접 하시기 바랍니다."
    )


if __name__ == "__main__":
    main()
