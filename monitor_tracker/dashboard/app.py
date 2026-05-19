"""
Streamlit 대시보드 — 사하라 이남 아프리카 모니터 가격 추적기

기능:
- 국가/브랜드/사이즈 필터
- 지금 크롤링 실행 버튼 (GitHub Actions workflow_dispatch 호출)
- 마지막 실행 시간 / 실패 로그
- CSV / Excel 다운로드
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import io
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

# ── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(
    page_title="Africa Monitor Prices",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 상수 ─────────────────────────────────────────────────────
REPO   = "byeongmin1986-cmd/my-news-app"
BRANCH = "claude/monitor-price-scraper-9Z0nd"
WORKFLOW_FILE = "weekly_scraper.yml"
RAW_CSV = (
    f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
    f"/monitor_tracker/data/monitors.csv"
)

# ── 데이터 로드 (GitHub raw URL, 5분 캐시) ───────────────────
@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    try:
        df = pd.read_csv(RAW_CSV)
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["screen_size_inch"] = pd.to_numeric(df["screen_size_inch"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame()

# ── GitHub Actions workflow_dispatch 트리거 ───────────────────
def trigger_crawl() -> tuple[bool, str]:
    token = st.secrets.get("GITHUB_TOKEN", "")
    if not token:
        return False, "GITHUB_TOKEN이 Streamlit secrets에 설정되지 않았습니다."
    r = requests.post(
        f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        },
        json={"ref": BRANCH},
        timeout=15,
    )
    if r.status_code == 204:
        return True, "GitHub Actions 실행 시작! 약 5~10분 후 데이터가 업데이트됩니다."
    return False, f"오류 ({r.status_code}): {r.text[:200]}"

# ── GitHub Actions 최근 실행 상태 조회 ───────────────────────
@st.cache_data(ttl=60)
def get_workflow_runs() -> list[dict]:
    token = st.secrets.get("GITHUB_TOKEN", "")
    if not token:
        return []
    try:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/runs",
            headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
            params={"per_page": 5},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json().get("workflow_runs", [])
    except Exception:
        pass
    return []

# ═══════════════════════════════════════════════════════════════
df = load_data()

# ── 헤더 ─────────────────────────────────────────────────────
st.title("🖥️ 사하라 이남 아프리카 모니터 가격 추적기")

# ── 상단 KPI ─────────────────────────────────────────────────
if not df.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 상품 수",     f"{len(df):,}개")
    c2.metric("수집 국가",      f"{df['country'].nunique()}개국")
    c3.metric("브랜드 수",      f"{df['brand'].nunique()}개")
    c4.metric("마지막 수집일",  df["crawl_date"].max() if "crawl_date" in df.columns else "없음")
else:
    st.info("📭 아직 수집된 데이터가 없습니다. 아래 버튼으로 크롤링을 시작하세요.")

st.divider()

# ── 크롤러 실행 컨트롤 ───────────────────────────────────────
st.subheader("🚀 크롤러 실행")

runs = get_workflow_runs()
if runs:
    latest = runs[0]
    status_icon = {"completed": "✅", "in_progress": "⏳", "failure": "❌"}.get(
        latest.get("status", ""), "❓"
    )
    conclusion = latest.get("conclusion") or latest.get("status", "unknown")
    run_time   = latest.get("created_at", "")[:16].replace("T", " ")
    st.caption(f"{status_icon} 마지막 실행: **{run_time} UTC** — 결과: **{conclusion}**")

col_btn, col_info = st.columns([1, 3])
with col_btn:
    if st.button("▶ 지금 크롤링 실행", type="primary", use_container_width=True):
        ok, msg = trigger_crawl()
        if ok:
            st.success(msg)
            st.cache_data.clear()
        else:
            st.error(msg)
with col_info:
    st.caption(
        "버튼을 누르면 GitHub Actions가 실행됩니다.  \n"
        "수집 완료까지 **5~10분** 소요.  \n"
        "완료 후 이 페이지를 새로고침하면 데이터가 보입니다."
    )

if runs:
    with st.expander("최근 실행 내역"):
        for run in runs:
            icon = {"completed": "✅", "in_progress": "⏳", "failure": "❌"}.get(
                run.get("status", ""), "❓"
            )
            t = run.get("created_at", "")[:16].replace("T", " ")
            c = run.get("conclusion") or run.get("status", "—")
            st.write(f"{icon} {t} UTC  —  {c}")

st.divider()

# ── 사이드바 필터 ─────────────────────────────────────────────
if not df.empty:
    st.sidebar.title("🔍 필터")

    countries = ["전체"] + sorted(df["country"].dropna().unique().tolist())
    sel_country = st.sidebar.selectbox("국가", countries)

    brands = ["전체"] + sorted(df["brand"].dropna().unique().tolist())
    sel_brand = st.sidebar.selectbox("브랜드", brands)

    sizes = ["전체"] + sorted(df["screen_size_inch"].dropna().unique().tolist())
    sel_size = st.sidebar.selectbox("화면 크기 (인치)", sizes)

    conditions = ["전체"] + sorted(df["condition"].dropna().unique().tolist())
    sel_condition = st.sidebar.selectbox("상태 (신품/중고)", conditions)

    fdf = df.copy()
    if sel_country   != "전체": fdf = fdf[fdf["country"] == sel_country]
    if sel_brand     != "전체": fdf = fdf[fdf["brand"] == sel_brand]
    if sel_size      != "전체": fdf = fdf[fdf["screen_size_inch"] == sel_size]
    if sel_condition != "전체": fdf = fdf[fdf["condition"] == sel_condition]
else:
    fdf = df

# ── 탭 ───────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 국가별 분석", "🏷️ 브랜드/사이즈", "📋 상품 목록", "📥 내보내기"])

# Tab 1: 국가별
with tab1:
    if fdf.empty:
        st.info("데이터 없음")
    else:
        st.subheader("국가별 가격 통계")
        stats = (
            fdf[fdf["price"].notna() & (fdf["price"] > 0)]
            .groupby(["country", "currency"])["price"]
            .agg(평균가격="mean", 최저가=min, 최고가=max, 상품수="count")
            .reset_index()
        )
        stats["평균가격"] = stats["평균가격"].round(0)
        st.dataframe(stats, use_container_width=True, hide_index=True)

        st.subheader("국가별 상품 수")
        cnt = fdf.groupby("country").size().rename("상품수")
        st.bar_chart(cnt)

        st.subheader("국가별 최저가 상품")
        for country, grp in fdf[fdf["price"].notna()].groupby("country"):
            row = grp.nsmallest(1, "price").iloc[0]
            with st.expander(f"🏆 {country} 최저가: {row['currency']} {row['price']:,.0f}"):
                st.write(f"**{row['product_title']}**")
                st.write(f"브랜드: {row.get('brand','N/A')} | 사이트: {row['retailer']}")
                if row.get("product_url"):
                    st.markdown(f"[상품 링크]({row['product_url']})")

# Tab 2: 브랜드/사이즈
with tab2:
    if fdf.empty:
        st.info("데이터 없음")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("브랜드별 상품 수")
            brand_cnt = fdf["brand"].value_counts().head(15)
            st.bar_chart(brand_cnt)
        with col_b:
            st.subheader("화면 크기별 상품 수")
            size_cnt = fdf["screen_size_inch"].dropna().value_counts().sort_index()
            st.bar_chart(size_cnt)

        st.subheader("브랜드 × 사이즈 평균가격")
        pivot = (
            fdf[fdf["price"].notna() & fdf["screen_size_inch"].notna()]
            .groupby(["brand", "screen_size_inch"])["price"]
            .mean().round(0).reset_index()
        )
        pivot.columns = ["브랜드", "크기(인치)", "평균가격"]
        st.dataframe(pivot.sort_values("평균가격"), use_container_width=True, hide_index=True)

# Tab 3: 상품 목록
with tab3:
    if fdf.empty:
        st.info("데이터 없음")
    else:
        st.subheader(f"상품 목록 ({len(fdf):,}개)")
        show_cols = ["country","retailer","product_title","brand","screen_size_inch",
                     "resolution","condition","price","currency","availability","crawl_date"]
        show_cols = [c for c in show_cols if c in fdf.columns]
        st.dataframe(
            fdf[show_cols].sort_values("price", ascending=True) if "price" in show_cols else fdf[show_cols],
            use_container_width=True, hide_index=True,
        )

# Tab 4: 내보내기
with tab4:
    if fdf.empty:
        st.info("데이터 없음")
    else:
        col_c, col_d = st.columns(2)
        with col_c:
            st.download_button(
                "📥 CSV 다운로드",
                data=fdf.to_csv(index=False, encoding="utf-8-sig"),
                file_name=f"monitors_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_d:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                fdf.to_excel(writer, index=False, sheet_name="Monitors")
            st.download_button(
                "📥 Excel 다운로드",
                data=buf.getvalue(),
                file_name=f"monitors_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    st.subheader("🔄 새로고침")
    if st.button("데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
