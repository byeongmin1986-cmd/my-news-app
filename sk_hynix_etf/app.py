import json
import math
from datetime import datetime, timedelta

import pandas as pd
import pytz
import requests
import streamlit as st
from bs4 import BeautifulSoup

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
DEFAULT_THRESHOLD_RATE = 3.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# ── Tick / format helpers ─────────────────────────────────────────────────────
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


# ── Data fetching ─────────────────────────────────────────────────────────────
def fetch_naver(code: str):
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


# ── Investment math (dashboard) ───────────────────────────────────────────────
def calc_split(unit_budget, buy_price, sell_price, buy_fee_rate, sell_fee_rate, tax_rate):
    cost_per_share = buy_price * (1 + buy_fee_rate)
    qty = math.floor(unit_budget / cost_per_share)
    buy_principal = qty * buy_price
    buy_fee = qty * buy_price * buy_fee_rate
    total_cost = buy_principal + buy_fee
    remaining = unit_budget - total_cost
    gross_sell = qty * sell_price
    sell_fee = qty * sell_price * sell_fee_rate
    sell_tax = qty * sell_price * tax_rate
    net_sell = gross_sell - sell_fee - sell_tax
    pnl = net_sell - total_cost
    pnl_rate = (pnl / total_cost * 100) if total_cost > 0 else 0.0
    return dict(qty=qty, buy_principal=buy_principal, buy_fee=buy_fee,
                total_cost=total_cost, remaining=remaining, gross_sell=gross_sell,
                sell_fee=sell_fee, sell_tax=sell_tax, net_sell=net_sell,
                pnl=pnl, pnl_rate=pnl_rate)


# ── Journal helpers ───────────────────────────────────────────────────────────
def _empty_journal():
    return {
        "trades": [],
        "holdings": 0,
        "avg_cost": 0.0,
        "total_deployed": 0.0,
        "realized_pnl": 0.0,
        "splits_deployed": 0,   # 현재 사이클에서 몇 회차 매수 했는지
        "cycle": 1,             # 매도 후 리셋되는 사이클 번호
    }


def _record_trade(j, date_str, prev_close, today_close, threshold,
                  change_pct, action, qty, split_amount, split_count):
    if action == "매수":
        trade_amount = qty * today_close
        # 평균 단가 갱신
        total_cost_before = j["holdings"] * j["avg_cost"]
        j["holdings"] += qty
        j["avg_cost"] = (total_cost_before + trade_amount) / j["holdings"]
        j["total_deployed"] += trade_amount
        j["splits_deployed"] += 1
        realized_pnl = 0.0
    else:  # 매도
        trade_amount = qty * today_close
        cost_basis = qty * j["avg_cost"]
        realized_pnl = trade_amount - cost_basis
        j["realized_pnl"] += realized_pnl
        j["holdings"] = 0
        j["avg_cost"] = 0.0
        j["total_deployed"] = 0.0
        j["splits_deployed"] = 0
        j["cycle"] += 1

    j["trades"].append({
        "날짜": date_str,
        "사이클": j["cycle"] if action == "매수" else j["cycle"] - 1,
        "전일종가": prev_close,
        "오늘종가": today_close,
        "임계가": threshold,
        "등락률(%)": round(change_pct, 2),
        "액션": action,
        "수량(주)": qty,
        "거래금액": int(trade_amount),
        "보유수량": j["holdings"],
        "평균단가": round(j["avg_cost"], 0),
        "실현손익": int(realized_pnl),
        "누적실현손익": int(j["realized_pnl"]),
    })


# ── Dashboard tab ─────────────────────────────────────────────────────────────
def render_dashboard(ticker, stock_name, total_budget, split_count, buy_rate,
                     threshold_rate, tick_method, tick_label):

    if "price_data" not in st.session_state:
        with st.spinner("전일 종가 데이터를 가져오는 중…"):
            st.session_state.price_data = get_price_data(ticker)

    prev_auto, cur_auto, source, fetch_time, errors = st.session_state.price_data

    if prev_auto:
        st.success(f"✅ 출처: **{source}** | {fetch_time.strftime('%Y-%m-%d %H:%M:%S KST')}")
    else:
        st.warning("⚠️ 자동 조회 실패. 전일 종가를 직접 입력하세요.")
        with st.expander("🔍 오류 상세"):
            for src, err in errors.items():
                st.text(f"{src}: {err}")

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        suffix = " · 자동조회 성공" if prev_auto else " · ✏️ 직접 입력 필요"
        prev_close = st.number_input(
            f"전일 종가 (원){suffix}", value=prev_auto or 28_970,
            min_value=1, step=5, format="%d", key="dash_prev")
    with col_in2:
        current_price = st.number_input(
            "현재가 (원, 0 = 미표시)", value=cur_auto or 0,
            min_value=0, step=5, format="%d", key="dash_cur")

    # ── Price calculations
    buy_price = apply_tick(prev_close * (1 + buy_rate / 100), tick_method)
    sell_price = apply_tick(buy_price * (1 + threshold_rate / 100), tick_method)
    threshold_price = apply_tick(prev_close * (1 + threshold_rate / 100), tick_method)

    st.divider()
    st.subheader("📊 종목 정보")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("종목명", stock_name)
    c2.metric("종목코드", ticker)
    c3.metric("전일 종가", fmt(prev_close))
    if current_price > 0:
        chg = current_price - prev_close
        c4.metric("현재가", fmt(current_price), f"{chg:+,}원 ({chg/prev_close*100:+.2f}%)")
    else:
        c4.metric("현재가", "미입력")

    st.divider()
    st.subheader("🎯 매수/매도 기준가")

    pc1, pc2 = st.columns(2)
    with pc1:
        st.info(
            f"### 🟢 매수 기준가 &nbsp; {fmt(buy_price)}\n\n"
            f"전일 종가 {fmt(prev_close)} × {1 + buy_rate/100:.5f}  \n"
            f"→ 5원 단위 **{tick_label.split()[0]}** → **{fmt(buy_price)}**"
        )
        if current_price > 0:
            if current_price >= buy_price:
                st.success("🔔 **매수 기준 도달!**")
            else:
                st.warning(f"매수 기준까지 {fmt(buy_price - current_price)} 남음")
    with pc2:
        st.info(
            f"### 🔴 매도 목표가 &nbsp; {fmt(sell_price)}\n\n"
            f"매수가 {fmt(buy_price)} × {1 + threshold_rate/100:.5f}  \n"
            f"→ 5원 단위 **{tick_label.split()[0]}** → **{fmt(sell_price)}**"
        )
        if current_price > 0:
            if current_price >= sell_price:
                st.success("🔔 **매도 기준 도달!**")
            elif current_price >= buy_price:
                st.warning(f"매도 기준까지 {fmt(sell_price - current_price)} 남음")

    # ── Split investment table
    st.divider()
    st.subheader(f"💰 {split_count}분할 계획 (수수료 미포함)")

    unit_budget = total_budget / split_count
    s = calc_split(unit_budget, buy_price, sell_price, 0, 0, 0)
    qty_per, principal, net_sell_per = s["qty"], s["buy_principal"], s["net_sell"]
    pnl_per = s["pnl"]

    T_qty = qty_per * split_count
    T_cost = principal * split_count
    T_sell = net_sell_per * split_count
    T_pnl = pnl_per * split_count
    T_pnl_rate = (T_pnl / T_cost * 100) if T_cost > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("총 투자금", fmt(total_budget))
    m1.metric("1회 분할금액", fmt(unit_budget))
    m2.metric("1회 매수 수량", f"{qty_per:,}주")
    m2.metric(f"{split_count}회 총 수량", f"{T_qty:,}주")
    m3.metric("총 사용 금액", fmt(T_cost))
    m3.metric("잔여 현금", fmt(total_budget - T_cost))
    m4.metric("전량 매도 예상금액", fmt(T_sell))
    m4.metric("예상 수익금", fmt(T_pnl), f"{T_pnl_rate:+.2f}%",
              delta_color="normal" if T_pnl >= 0 else "inverse")

    # Buy / Sell tables
    buy_rows, sell_rows = [], []
    cum_qty = cum_cost = 0
    for i in range(1, split_count + 1):
        cum_qty += qty_per; cum_cost += principal
        buy_rows.append({"회차": f"제{i}회", "분할금액": fmt(unit_budget),
                         "매수기준가": fmt(buy_price), "매수수량(floor)": f"{qty_per:,}주",
                         "사용금액": fmt(principal), "남은현금": fmt(unit_budget - principal),
                         "누적수량": f"{cum_qty:,}주", "누적사용금액": fmt(cum_cost)})
        pnl = qty_per * sell_price - principal
        sell_rows.append({"회차": f"제{i}회", "보유수량": f"{qty_per:,}주",
                          "매도목표가": fmt(sell_price), "예상매도금액": fmt(qty_per * sell_price),
                          "투자원가": fmt(principal), "예상손익": f"{pnl:+,.0f}원",
                          "손익률": f"{pnl/principal*100:+.2f}%"})

    st.subheader("📋 매수 계획표")
    st.dataframe(pd.DataFrame(buy_rows), use_container_width=True, hide_index=True)
    st.subheader("📋 매도 계획표")
    st.dataframe(pd.DataFrame(sell_rows), use_container_width=True, hide_index=True)

    st.divider()
    st.warning(
        "⚠️ **투자 유의사항** — 본 대시보드는 가격 참고 및 계획 수립 도구입니다.  \n"
        "자동 주문 기능 없음. 모든 투자 판단은 본인이 직접 하시기 바랍니다."
    )


# ── Journal tab ───────────────────────────────────────────────────────────────
def render_journal(ticker, total_budget, split_count, threshold_rate, tick_method):
    # ── Session state init
    if "journal" not in st.session_state:
        st.session_state.journal = _empty_journal()
    j = st.session_state.journal

    split_amount = total_budget / split_count

    # ── Portfolio status
    st.subheader("📊 포트폴리오 현황")

    # Unrealized P&L: need last price — use journal's last logged today_close
    last_price = j["trades"][-1]["오늘종가"] if j["trades"] else 0
    unrealized = (last_price - j["avg_cost"]) * j["holdings"] if j["holdings"] > 0 and last_price > 0 else 0
    total_pnl = j["realized_pnl"] + unrealized

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("원금", fmt(total_budget))
    p1.metric("1회 분할금액", fmt(split_amount))
    p2.metric("현재 보유 수량", f"{j['holdings']:,}주")
    avg_label = fmt(j["avg_cost"]) if j["holdings"] > 0 else "없음"
    p2.metric("평균 매수 단가", avg_label)
    p3.metric("투입 자금 (현 사이클)", fmt(j["total_deployed"]))
    p3.metric(f"사용 분할 ({split_count}분할 기준)", f"{j['splits_deployed']}/{split_count}회")
    p4.metric("누적 실현 손익", f"{j['realized_pnl']:+,.0f}원")
    if j["holdings"] > 0:
        p4.metric("평가 손익 (미실현)", f"{unrealized:+,.0f}원",
                  delta_color="normal" if unrealized >= 0 else "inverse")

    # ── Daily entry form
    st.divider()
    st.subheader("📝 일별 매매 입력")

    c_date, c_prev, c_today = st.columns(3)
    with c_date:
        trade_date = st.date_input(
            "거래 날짜",
            value=datetime.now(KST).date(),
            key="j_date",
        )
    with c_prev:
        # Pre-fill from auto-fetch if available
        auto_prev = st.session_state.get("price_data", (None,))[0]
        prev_close_j = st.number_input(
            "전일 종가 (원)",
            value=auto_prev if auto_prev else 28_970,
            min_value=1, step=5, format="%d",
            key="j_prev",
            help="자동 조회된 값이 있으면 자동 입력됩니다.",
        )
    with c_today:
        today_close = st.number_input(
            "오늘 종가 (원)",
            value=0, min_value=0, step=5, format="%d",
            key="j_today",
            help="장 마감 후 오늘 종가를 입력하세요.",
        )

    # ── Guidance calculation
    if today_close > 0 and prev_close_j > 0:
        threshold = apply_tick(prev_close_j * (1 + threshold_rate / 100), tick_method)
        change_pct = (today_close - prev_close_j) / prev_close_j * 100
        action = "매도" if today_close >= threshold else "매수"

        # Calculate recommended quantity
        if action == "매수":
            remaining_splits = split_count - j["splits_deployed"]
            if remaining_splits <= 0:
                qty_guide = 0
                guide_note = f"⛔ 이미 {split_count}회 분할 완료. 매수 불가 (매도 대기)"
            else:
                qty_guide = math.floor(split_amount / today_close)
                trade_amt = qty_guide * today_close
                remain_cash = split_amount - trade_amt
                guide_note = (
                    f"🟢 **매수 권장** | 제{j['splits_deployed']+1}회차 분할  \n"
                    f"잔여 분할: {remaining_splits}회 남음"
                )
            pnl_est = 0.0
        else:
            qty_guide = j["holdings"]
            trade_amt = qty_guide * today_close
            cost_basis = qty_guide * j["avg_cost"] if j["holdings"] > 0 else 0
            pnl_est = trade_amt - cost_basis
            guide_note = (
                f"🔴 **매도 권장** | 보유 {qty_guide:,}주 전량 매도  \n"
                f"수익 사이클 #{j['cycle']} 종료"
            )
            remain_cash = 0.0

        # Display guidance boxes
        st.divider()
        st.subheader("💡 매매 가이드")

        g1, g2, g3, g4 = st.columns(4)
        g1.metric("전일 종가", fmt(prev_close_j))
        g1.metric("임계가 (전일 +" + f"{threshold_rate}%)", fmt(threshold))
        g2.metric("오늘 종가", fmt(today_close))
        pct_color = "normal" if change_pct >= 0 else "inverse"
        g2.metric("전일 대비 등락", f"{change_pct:+.2f}%",
                  "임계 초과 → 매도" if today_close >= threshold else f"임계까지 {(threshold - today_close)/prev_close_j*100:.2f}%p")
        g3.metric("권장 액션", "🔴 매도" if action == "매도" else "🟢 매수")
        g3.metric("권장 수량", f"{qty_guide:,}주" if qty_guide > 0 else "없음")
        if action == "매수" and qty_guide > 0:
            g4.metric("예상 매수 금액", fmt(qty_guide * today_close))
            g4.metric("이번 분할 잔여", fmt(split_amount - qty_guide * today_close))
        elif action == "매도" and qty_guide > 0:
            g4.metric("예상 매도 금액", fmt(qty_guide * today_close))
            g4.metric("예상 손익", f"{pnl_est:+,.0f}원",
                      delta_color="normal" if pnl_est >= 0 else "inverse")

        st.info(guide_note)

        # Threshold analysis
        with st.expander("📐 임계가 계산 상세"):
            st.markdown(
                f"""
| 항목 | 값 |
|------|-----|
| 전일 종가 | {fmt(prev_close_j)} |
| 임계 상승률 | {threshold_rate}% |
| 임계가 계산 | {prev_close_j:,} × {1+threshold_rate/100:.4f} = {prev_close_j*(1+threshold_rate/100):,.1f}원 |
| 임계가 (5원 올림) | **{fmt(threshold)}** |
| 오늘 종가 | {fmt(today_close)} |
| 판단 | {'오늘 종가 ≥ 임계가 → **매도**' if action == '매도' else '오늘 종가 < 임계가 → **매수**'} |
"""
            )

        # ── Log button
        st.divider()
        can_log = qty_guide > 0
        btn_label = f"✅ 오늘 매매 기록 저장 ({str(trade_date)} / {action} {qty_guide:,}주)"
        if not can_log:
            st.warning("기록할 수량이 없습니다.")
        else:
            # Check duplicate date
            existing_dates = [t["날짜"] for t in j["trades"]]
            date_str = str(trade_date)
            if date_str in existing_dates:
                st.warning(f"⚠️ {date_str} 날짜의 기록이 이미 존재합니다. 저장하면 중복 기록됩니다.")

            if st.button(btn_label, type="primary", use_container_width=True):
                _record_trade(j, date_str, prev_close_j, today_close, threshold,
                              change_pct, action, qty_guide, split_amount, split_count)
                st.success(f"✅ {date_str} {action} {qty_guide:,}주 기록 완료!")
                st.rerun()
    else:
        st.info("👆 전일 종가와 오늘 종가를 입력하면 매매 가이드가 표시됩니다.")

    # ── Trade history
    if j["trades"]:
        st.divider()
        st.subheader("📋 매매 내역")

        df = pd.DataFrame(j["trades"])
        # Color styling: 매수 → 파랑, 매도 → 빨강
        def highlight_action(row):
            color = "background-color: #e8f4fd" if row["액션"] == "매수" else "background-color: #fde8e8"
            return [color] * len(row)

        st.dataframe(
            df.style.apply(highlight_action, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        # Summary by cycle
        if df["사이클"].nunique() > 1 or len(df) > 1:
            st.subheader("📊 사이클별 요약")
            cycle_summary = (
                df.groupby("사이클")
                .agg(
                    거래횟수=("액션", "count"),
                    매수횟수=("액션", lambda x: (x == "매수").sum()),
                    매도횟수=("액션", lambda x: (x == "매도").sum()),
                    실현손익합계=("실현손익", "sum"),
                )
                .reset_index()
            )
            st.dataframe(cycle_summary, use_container_width=True, hide_index=True)

    # ── Last trade delete
    if j["trades"]:
        st.divider()
        col_del, _ = st.columns([1, 3])
        with col_del:
            if st.button("↩️ 마지막 기록 취소", use_container_width=True):
                last = j["trades"].pop()
                # Reverse the trade
                if last["액션"] == "매수":
                    qty = last["수량(주)"]
                    amt = last["거래금액"]
                    j["holdings"] -= qty
                    j["total_deployed"] -= amt
                    j["splits_deployed"] = max(0, j["splits_deployed"] - 1)
                    if j["holdings"] > 0:
                        j["avg_cost"] = (j["avg_cost"] * (j["holdings"] + qty) - amt) / j["holdings"]
                    else:
                        j["avg_cost"] = 0.0
                else:
                    # Restore from previous buy entries in same cycle
                    j["realized_pnl"] -= last["실현손익"]
                    j["cycle"] = max(1, j["cycle"] - 1)
                    # Reconstruct holdings from remaining trades
                    holdings = 0
                    avg_cost = 0.0
                    deployed = 0.0
                    splits = 0
                    for t in j["trades"]:
                        if t["액션"] == "매수":
                            old_total = holdings * avg_cost
                            holdings += t["수량(주)"]
                            avg_cost = (old_total + t["거래금액"]) / holdings
                            deployed += t["거래금액"]
                            splits += 1
                        else:
                            holdings = 0
                            avg_cost = 0.0
                            deployed = 0.0
                            splits = 0
                    j["holdings"] = holdings
                    j["avg_cost"] = avg_cost
                    j["total_deployed"] = deployed
                    j["splits_deployed"] = splits
                st.rerun()

    # ── Export / Import / Reset
    st.divider()
    st.subheader("💾 데이터 관리")
    col_ex, col_im, col_rst = st.columns(3)

    with col_ex:
        data_json = json.dumps(j, ensure_ascii=False, indent=2, default=str)
        st.download_button(
            "📥 내보내기 (JSON)",
            data=data_json,
            file_name=f"trading_journal_{datetime.now(KST).strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )
        if j["trades"]:
            csv_data = pd.DataFrame(j["trades"]).to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "📥 내보내기 (CSV)",
                data=csv_data,
                file_name=f"trading_journal_{datetime.now(KST).strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with col_im:
        uploaded = st.file_uploader("📂 JSON 불러오기", type=["json"], key="j_upload")
        if uploaded is not None:
            try:
                loaded = json.load(uploaded)
                st.session_state.journal = loaded
                st.success("불러오기 완료!")
                st.rerun()
            except Exception as exc:
                st.error(f"파일 오류: {exc}")

    with col_rst:
        st.write("")
        st.write("")
        if st.button("🗑️ 전체 초기화", use_container_width=True, type="secondary"):
            st.session_state.journal = _empty_journal()
            st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    st.title("📈 KODEX SK하이닉스단일종목레버리지 ETF")
    st.caption("⚠️ 가격 참고 및 매매 계획 도구 — 자동 주문 없음. 모든 투자 결정은 본인이 직접 하시기 바랍니다.")

    # ── Shared sidebar
    with st.sidebar:
        st.header("⚙️ 설정")

        ticker = st.text_input("종목코드", value=DEFAULT_TICKER)
        stock_name = st.text_input("종목명", value=DEFAULT_NAME)

        st.divider()
        st.subheader("원금 / 분할")
        total_budget = st.number_input(
            "원금 (원)", value=DEFAULT_TOTAL_BUDGET, step=1_000_000,
            min_value=1_000_000, format="%d",
        )
        split_count = int(st.number_input(
            "분할 수", value=DEFAULT_SPLIT_COUNT, min_value=1, max_value=20, step=1
        ))

        st.divider()
        st.subheader("수익률 기준")
        buy_rate = st.number_input(
            "매수 기준 상승률 (%)", value=DEFAULT_BUY_RATE, step=0.1, format="%.2f",
            help="대시보드 탭 전용 매수 기준가 계산용"
        )
        threshold_rate = st.number_input(
            "매매 임계 상승률 (%) ★",
            value=DEFAULT_THRESHOLD_RATE, step=0.1, format="%.2f",
            help="전일 종가 대비 이 비율 이상 오르면 매도, 미만이면 매수",
        )

        st.divider()
        st.subheader("호가 단위")
        tick_label = st.radio("5원 단위 처리", ["올림 (기본)", "반올림"], index=0)
        tick_method = "ceil" if "올림" in tick_label else "round"

        st.divider()
        if st.button("🔄 시세 새로고침", use_container_width=True):
            st.session_state.pop("price_data", None)
            st.rerun()

    # ── Tabs
    tab1, tab2 = st.tabs(["📊 가격 대시보드", "📔 매매 일지"])

    with tab1:
        render_dashboard(ticker, stock_name, total_budget, split_count,
                         buy_rate, threshold_rate, tick_method, tick_label)

    with tab2:
        render_journal(ticker, total_budget, split_count, threshold_rate, tick_method)


if __name__ == "__main__":
    main()
