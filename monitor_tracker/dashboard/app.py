"""
Streamlit 대시보드 - 사하라 이남 아프리카 모니터 가격 추적기
모바일 최적화 | Run Now 버튼 | 실시간 상태 표시
"""
from __future__ import annotations
import io, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Africa Monitor Prices",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

REPO          = "byeongmin1986-cmd/my-news-app"
BRANCH        = "main"
WORKFLOW_FILE = "crawler.yml"
RAW_CSV = (
    f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
    f"/monitor_tracker/data/monitors.csv"
)

@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, str]:
    """Returns (dataframe, error_message). error_message is empty string on success."""
    try:
        r = requests.get(RAW_CSV, timeout=10)
        if r.status_code == 404:
            return pd.DataFrame(), "csv_not_found"
        r.raise_for_status()
        from io import StringIO
        df = pd.read_csv(StringIO(r.text))
        df["price"]            = pd.to_numeric(df["price"],            errors="coerce")
        df["screen_size_inch"] = pd.to_numeric(df["screen_size_inch"], errors="coerce")
        return df, ""
    except Exception as e:
        return pd.DataFrame(), str(e)

def trigger_crawl(site: str = "", max_pages: str = "10") -> tuple[bool, str]:
    token = st.secrets.get("GITHUB_TOKEN", "")
    if not token:
        return False, "Streamlit Secrets에 GITHUB_TOKEN이 없습니다."
    r = requests.post(
        f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
        json={"ref": BRANCH, "inputs": {"site": site, "max_pages": max_pages}},
        timeout=15,
    )
    if r.status_code == 204:
        return True, "GitHub Actions 실행 시작! 약 5~10분 후 데이터가 업데이트됩니다."
    return False, f"오류 ({r.status_code}): {r.text[:200]}"

@st.cache_data(ttl=60)
def get_workflow_runs() -> list[dict]:
    token = st.secrets.get("GITHUB_TOKEN", "")
    if not token:
        return []
    try:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/runs",
            headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
            params={"per_page": 5}, timeout=10,
        )
        return r.json().get("workflow_runs", []) if r.status_code == 200 else []
    except Exception:
        return []

# ═══════════════════════════════════════
df, load_err = load_data()
runs         = get_workflow_runs()

st.title("🖥️ Africa Monitor Price Tracker")
st.caption("Kenya / Ghana / Nigeria — 실제 온라인 리테일러 가격 수집")

# ── KPI ───────────────────────────────
if not df.empty:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 상품",    f"{len(df):,}개")
    c2.metric("국가",       f"{df['country'].nunique()}개국")
    c3.metric("브랜드",     f"{df['brand'].nunique()}개")
    c4.metric("마지막 수집", df.get("crawl_date", pd.Series()).max() or "-")
elif load_err == "csv_not_found":
    st.warning(
        "**아직 수집된 데이터가 없습니다.**\n\n"
        "원인: GitHub Actions가 아직 실행되지 않았거나, "
        "`SCRAPERAPI_KEY`가 GitHub Secrets에 설정되지 않아 0개 수집 후 종료됨.\n\n"
        "**해결 방법:**\n"
        "1. GitHub repo → Settings → Secrets → Actions → `SCRAPERAPI_KEY` 추가\n"
        "2. 아래 **▶ 지금 전체 크롤링** 버튼 클릭\n"
        "3. 5~10분 후 이 페이지 새로고침"
    )
else:
    st.info("아래 버튼으로 크롤링을 실행하세요.")

st.divider()

# ── 크롤러 실행 컨트롤 ────────────────
st.subheader("🚀 크롤러 실행")

if runs:
    latest = runs[0]
    icons  = {"completed": "✅", "in_progress": "⏳", "failure": "❌", "cancelled": "⚠️"}
    icon   = icons.get(latest.get("status", ""), "❓")
    concl  = latest.get("conclusion") or latest.get("status", "unknown")
    run_t  = latest.get("created_at", "")[:16].replace("T", " ")
    st.caption(f"{icon} 마지막 실행: **{run_t} UTC** — 결과: **{concl}**")

col_btn, col_sel, col_info = st.columns([2, 2, 4])
with col_btn:
    if st.button("▶ 지금 전체 크롤링", type="primary", use_container_width=True):
        ok, msg = trigger_crawl()
        st.success(msg) if ok else st.error(msg)
        if ok: st.cache_data.clear()
with col_sel:
    site_opt = st.selectbox(
        "특정 사이트만",
        ["", "kenya_jumia", "nigeria_jumia", "ghana_compughana"],
        format_func=lambda x: "전체" if x == "" else x,
    )
    if st.button("▶ 선택 사이트만", use_container_width=True) and site_opt:
        ok, msg = trigger_crawl(site=site_opt)
        st.success(msg) if ok else st.error(msg)
with col_info:
    st.caption(
        "버튼 클릭 → GitHub Actions 실행 → ScraperAPI 프록시로 WAF 우회 → CSV 저장 → 여기 업데이트  \n"
        "완료까지 약 5~10분 소요. 완료 후 **데이터 새로고침** 버튼 누르세요."
    )

if runs:
    with st.expander("📜 최근 실행 내역"):
        for run in runs:
            icon  = {"completed": "✅", "in_progress": "⏳", "failure": "❌"}.get(run.get("status",""), "❓")
            t     = run.get("created_at","")[:16].replace("T"," ")
            concl = run.get("conclusion") or run.get("status","-")
            url   = run.get("html_url","")
            st.write(f"{icon} {t} UTC — {concl}  [{'로그 보기' if url else ''}]({url})")

st.divider()

# ── 사이드바 필터 ──────────────────────
if not df.empty:
    with st.sidebar:
        st.title("🔍 필터")
        sel_country   = st.selectbox("국가",   ["전체"] + sorted(df["country"].dropna().unique().tolist()))
        sel_brand     = st.selectbox("브랜드", ["전체"] + sorted(df["brand"].dropna().unique().tolist()))
        sel_condition = st.selectbox("상태",   ["전체"] + sorted(df["condition"].dropna().unique().tolist()))
        if st.button("🔄 데이터 새로고침", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    fdf = df.copy()
    if sel_country   != "전체": fdf = fdf[fdf["country"]   == sel_country]
    if sel_brand     != "전체": fdf = fdf[fdf["brand"]     == sel_brand]
    if sel_condition != "전체": fdf = fdf[fdf["condition"] == sel_condition]
else:
    fdf = df.copy()

# ── 탭 ─────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 국가별", "🏷️ 브랜드/사이즈", "📋 상품 목록", "📥 내보내기"])

with tab1:
    if fdf.empty:
        st.info("데이터 없음")
    else:
        stats = (
            fdf[fdf["price"].notna() & (fdf["price"] > 0)]
            .groupby(["country","currency"])["price"]
            .agg(평균가격="mean", 최저가=min, 최고가=max, 상품수="count")
            .reset_index()
        )
        stats["평균가격"] = stats["평균가격"].round(0)
        st.dataframe(stats, use_container_width=True, hide_index=True)
        st.bar_chart(fdf.groupby("country").size().rename("상품수"))
        st.subheader("국가별 최저가 모니터")
        for country, grp in fdf[fdf["price"].notna()].groupby("country"):
            row = grp.nsmallest(1,"price").iloc[0]
            with st.expander(f"🏆 {country}: {row['currency']} {row['price']:,.0f}"):
                st.write(f"**{row['product_title']}**")
                st.write(f"브랜드: {row.get('brand','N/A')} | 사이트: {row['retailer']}")
                if row.get("product_url"): st.markdown(f"[상품 링크]({row['product_url']})")

with tab2:
    if not fdf.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("브랜드별 상품 수")
            st.bar_chart(fdf["brand"].value_counts().head(15))
        with c2:
            st.subheader("화면 크기별 상품 수")
            st.bar_chart(fdf["screen_size_inch"].dropna().value_counts().sort_index())

with tab3:
    if fdf.empty:
        st.info("데이터 없음")
    else:
        cols = ["country","retailer","product_title","brand","screen_size_inch",
                "resolution","condition","price","currency","availability","crawl_date"]
        cols = [c for c in cols if c in fdf.columns]
        st.dataframe(
            fdf[cols].sort_values("price",ascending=True) if "price" in cols else fdf[cols],
            use_container_width=True, hide_index=True,
        )

with tab4:
    if not fdf.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 CSV 다운로드",
                data=fdf.to_csv(index=False, encoding="utf-8-sig"),
                file_name=f"monitors_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        with c2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                fdf.to_excel(w, index=False, sheet_name="Monitors")
            st.download_button("📥 Excel 다운로드",
                data=buf.getvalue(),
                file_name=f"monitors_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
    else:
        st.info("데이터가 없습니다. 크롤러를 먼저 실행해 주세요.")
