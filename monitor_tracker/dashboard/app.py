"""
Streamlit 대시보드 - 아프리카 모니터 가격 추적기
GitHub Actions 로그 없이 Streamlit 화면에서 모든 상태 확인 가능
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
RAW_BASE      = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/monitor_tracker/data"
RAW_CSV       = f"{RAW_BASE}/monitors.csv"
RAW_STATUS    = f"{RAW_BASE}/crawl_status.json"

# ── 데이터 로드 함수들 ────────────────────────────────

@st.cache_data(ttl=60)
def load_crawl_status() -> dict:
    """crawl_status.json 로드 — 크롤러가 실행될 때마다 업데이트됨."""
    try:
        r = requests.get(RAW_STATUS, timeout=10)
        if r.status_code == 404:
            return {"_error": "not_found"}
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"_error": str(e)}

@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, str]:
    """monitors.csv 로드."""
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

@st.cache_data(ttl=60)
def get_workflow_runs(token: str) -> list[dict]:
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

@st.cache_data(ttl=120)
def check_secret_exists(token: str, secret_name: str) -> str:
    """GitHub Secret 이름이 존재하는지 확인 (값은 볼 수 없음)."""
    if not token:
        return "unknown"
    try:
        r = requests.get(
            f"https://api.github.com/repos/{REPO}/actions/secrets/{secret_name}",
            headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
            timeout=10,
        )
        if r.status_code == 200:
            return "exists"
        if r.status_code == 404:
            return "missing"
        return "unknown"
    except Exception:
        return "unknown"

def trigger_crawl(token: str, site: str = "", max_pages: str = "10") -> tuple[bool, str]:
    if not token:
        return False, "Streamlit Secrets에 GITHUB_TOKEN이 없습니다."
    r = requests.post(
        f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches",
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
        json={"ref": BRANCH, "inputs": {"site": site, "max_pages": max_pages}},
        timeout=15,
    )
    if r.status_code == 204:
        return True, "✅ GitHub Actions 실행 시작! 약 5~10분 후 아래 상태가 업데이트됩니다."
    return False, f"❌ 오류 ({r.status_code}): {r.text[:300]}"

# ══════════════════════════════════════════════════════
token  = st.secrets.get("GITHUB_TOKEN", "")
status = load_crawl_status()
df, load_err = load_data()
runs   = get_workflow_runs(token)

st.title("🖥️ Africa Monitor Price Tracker")
st.caption("Kenya / Ghana / Nigeria — 실제 온라인 리테일러 가격 수집")

# ════════════════════════════════════════════════
# 섹션 1: 시스템 설정 상태
# ════════════════════════════════════════════════
st.subheader("🔧 시스템 설정 상태")

c1, c2 = st.columns(2)

with c1:
    if token:
        st.success("**GITHUB_TOKEN** ✅ 설정됨\n\n(Streamlit Secrets)")
    else:
        st.error(
            "**GITHUB_TOKEN** ❌ 없음\n\n"
            "Streamlit Cloud → 앱 Settings → Secrets에 추가:\n"
            "```\nGITHUB_TOKEN = \"ghp_...\"\n```"
        )

with c2:
    scraper_state = check_secret_exists(token, "SCRAPERAPI_KEY")
    if scraper_state == "exists":
        st.success("**SCRAPERAPI_KEY** ✅ 설정됨\n\n(GitHub Secrets)")
    elif scraper_state == "missing":
        st.error(
            "**SCRAPERAPI_KEY** ❌ 없음\n\n"
            "GitHub repo → Settings → Secrets → Actions\n"
            "→ New repository secret → 이름: `SCRAPERAPI_KEY`"
        )
    else:
        st.warning(
            "**SCRAPERAPI_KEY** ⚠️ 확인 불가\n\n"
            "GITHUB_TOKEN에 `secrets:read` 권한이 필요합니다.\n"
            "또는 GITHUB_TOKEN이 없습니다."
        )

st.divider()

# ════════════════════════════════════════════════
# 섹션 2: 크롤러 실행
# ════════════════════════════════════════════════
st.subheader("🚀 크롤러 실행")

col_btn, col_sel = st.columns([1, 1])
with col_btn:
    if st.button("▶ 지금 전체 크롤링 실행", type="primary", use_container_width=True):
        ok, msg = trigger_crawl(token)
        if ok:
            st.success(msg)
            st.info("5~10분 후 아래 **화면 새로고침** 버튼을 눈러 결과를 확인하세요.")
            st.cache_data.clear()
        else:
            st.error(msg)

with col_sel:
    site_opt = st.selectbox(
        "특정 사이트만 실행",
        ["", "kenya_jumia", "nigeria_jumia", "ghana_compughana"],
        format_func=lambda x: "전체 (기본)" if x == "" else x,
    )
    if site_opt and st.button("▶ 선택 사이트만 실행", use_container_width=True):
        ok, msg = trigger_crawl(token, site=site_opt)
        st.success(msg) if ok else st.error(msg)

if st.button("🔄 화면 새로고침", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.divider()

# ════════════════════════════════════════════════
# 섹션 3: 마지막 크롤링 결과 (crawl_status.json)
# ════════════════════════════════════════════════
st.subheader("📊 마지막 크롤링 결과")

if "_error" in status:
    if status["_error"] == "not_found":
        st.warning(
            "**아직 크롤링이 한 번도 실행되지 않았습니다.**\n\n"
            "위 **▶ 지금 전체 크롤링 실행** 버튼을 눌러 첫 번째 크롤링을 시작하세요."
        )
    else:
        st.error(f"상태 파일 로드 실패: {status['_error']}")
else:
    overall    = status.get("overall_status", "unknown")
    total      = status.get("total_products", 0)
    csv_exists = status.get("csv_exists", False)
    csv_rows   = status.get("csv_rows", 0)
    last_run   = status.get("last_run", "")[:16].replace("T", " ")
    sites      = status.get("sites", {})

    OVERALL = {
        "success": ("✅", "성공 — 모든 사이트에서 상품 수집됨",  "success"),
        "partial": ("⚠️", "부분 성공 — 일부 사이트 실패",        "warning"),
        "failed":  ("❌", "실패 — 0개 수집 (SCRAPERAPI_KEY 확인 필요)", "error"),
    }
    icon, label, kind = OVERALL.get(overall, ("❓", overall, "info"))

    if kind == "success":
        st.success(f"**{icon} {label}**")
    elif kind == "warning":
        st.warning(f"**{icon} {label}**")
    elif kind == "error":
        st.error(
            f"**{icon} {label}**\n\n"
            "확인 사항:\n"
            "1. SCRAPERAPI_KEY가 GitHub Secrets에 올바르게 설정됨 → 위 섹션 확인\n"
            "2. scraperapi.com 로그인 → 잔여 크레딧이 0이 아닌지 확인\n"
            "3. SCRAPERAPI_KEY 값을 복사해서 GitHub Secrets에서 Update 클릭 후 다시 붙여넣기"
        )
    else:
        st.info(f"**{icon} {label}**")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("수집 상품 수", f"{total:,}개")
    k2.metric("CSV 파일",    f"{'있음' if csv_exists else '없음'} ({csv_rows}행)")
    success_n = sum(1 for s in sites.values() if s.get("status") == "success")
    k3.metric("성공 사이트", f"{success_n} / {len(sites)}개")
    k4.metric("마지막 실행", last_run + " UTC" if last_run else "없음")

    st.markdown("**사이트별 수집 결과**")
    for site_key, info in sites.items():
        s_status   = info.get("status", "unknown")
        s_products = info.get("products", 0)
        s_label    = info.get("label", site_key)
        s_error    = info.get("error")
        s_time     = info.get("time", "")[:16].replace("T", " ")

        if s_status == "success":
            st.success(f"✅ **{s_label}** — {s_products}개 수집 ({s_time} UTC)")
        elif s_status == "empty":
            st.warning(
                f"⚠️ **{s_label}** — 0개 수집\n\n"
                f"원인: WAF 차단 또는 해당 카테고리에 모니터 상품 없음 ({s_time} UTC)"
            )
        elif s_status == "error":
            with st.expander(f"❌ **{s_label}** — 오류 발생 ({s_time} UTC) — 클릭하여 오류 내용 보기"):
                st.code(s_error or "오류 내용 없음", language="text")
        else:
            st.info(f"❓ **{s_label}** — {s_status}")

st.divider()

# ════════════════════════════════════════════════
# 섹션 4: GitHub Actions 실행 내역
# ════════════════════════════════════════════════
st.subheader("⚡ GitHub Actions 실행 내역")

if not token:
    st.info("GITHUB_TOKEN을 설정하면 여기에 Actions 실행 기록이 표시됩니다.")
elif not runs:
    st.info("아직 실행 기록이 없거나 불러올 수 없습니다.")
else:
    latest = runs[0]
    raw_status     = latest.get("status", "")
    raw_conclusion = latest.get("conclusion") or raw_status
    run_time       = latest.get("created_at", "")[:16].replace("T", " ")

    overall_from_json = status.get("overall_status", "") if "_error" not in status else ""
    display_conclusion = raw_conclusion
    if raw_conclusion == "success" and overall_from_json == "failed":
        display_conclusion = "failed: 0 products collected"

    CONCL_MAP = {
        "success":  "✅ 성공",
        "failure":  "❌ 실패",
        "cancelled": "⚠️ 취소됨",
        "failed: 0 products collected": "❌ 실패: 0개 수집",
    }

    run_label = CONCL_MAP.get(display_conclusion, display_conclusion)

    if "❌" in run_label or "실패" in run_label:
        st.error(f"**마지막 실행**: {run_time} UTC — {run_label}")
    elif "✅" in run_label:
        st.success(f"**마지막 실행**: {run_time} UTC — {run_label}")
    else:
        st.info(f"**마지막 실행**: {run_time} UTC — {run_label}")

    with st.expander("최근 5회 실행 내역 보기"):
        for run in runs:
            r_status = run.get("status", "")
            r_concl  = run.get("conclusion") or r_status
            r_time   = run.get("created_at", "")[:16].replace("T", " ")
            r_label  = CONCL_MAP.get(r_concl, r_concl)
            r_icon   = "✅" if "성공" in r_label else ("❌" if "실패" in r_label else "⏳")
            st.write(f"{r_icon} {r_time} UTC — {r_label}")

st.divider()

# ════════════════════════════════════════════════
# 섹션 5: 데이터 보기 및 다운로드
# ════════════════════════════════════════════════
if df.empty:
    st.info("데이터가 없습니다. 크롤링을 먼저 실행하세요.")
else:
    with st.sidebar:
        st.title("🔍 필터")
        sel_country   = st.selectbox("국가",   ["전체"] + sorted(df["country"].dropna().unique().tolist()))
        sel_brand     = st.selectbox("브랜드", ["전체"] + sorted(df["brand"].dropna().unique().tolist()))
        sel_condition = st.selectbox("상태",   ["전체"] + sorted(df["condition"].dropna().unique().tolist()))

    fdf = df.copy()
    if sel_country   != "전체": fdf = fdf[fdf["country"]   == sel_country]
    if sel_brand     != "전체": fdf = fdf[fdf["brand"]     == sel_brand]
    if sel_condition != "전체": fdf = fdf[fdf["condition"] == sel_condition]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("수집 상품",    f"{len(df):,}개")
    c2.metric("국가",       f"{df['country'].nunique()}개국")
    c3.metric("브랜드",     f"{df['brand'].nunique()}개")
    c4.metric("마지막 수집", df["crawl_date"].max() if "crawl_date" in df.columns else "-")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 국가별", "🏷️ 브랜드/사이즈", "📋 상품 목록", "📥 내보내기"])

    with tab1:
        stats = (
            fdf[fdf["price"].notna() & (fdf["price"] > 0)]
            .groupby(["country", "currency"])["price"]
            .agg(평균가격="mean", 최저가=min, 최고가=max, 상품수="count")
            .reset_index()
        )
        stats["평균가격"] = stats["평균가격"].round(0)
        st.dataframe(stats, use_container_width=True, hide_index=True)
        st.bar_chart(fdf.groupby("country").size().rename("상품수"))
        st.subheader("국가별 최저가 모니터")
        for country, grp in fdf[fdf["price"].notna()].groupby("country"):
            row = grp.nsmallest(1, "price").iloc[0]
            with st.expander(f"🏆 {country}: {row['currency']} {row['price']:,.0f}"):
                st.write(f"**{row['product_title']}**")
                st.write(f"브랜드: {row.get('brand', 'N/A')} | 사이트: {row['retailer']}")
                if row.get("product_url"):
                    st.markdown(f"[상품 링크]({row['product_url']})")

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
        cols = ["country", "retailer", "product_title", "brand", "screen_size_inch",
                "resolution", "condition", "price", "currency", "availability", "crawl_date"]
        cols = [c for c in cols if c in fdf.columns]
        st.dataframe(
            fdf[cols].sort_values("price", ascending=True) if "price" in cols else fdf[cols],
            use_container_width=True, hide_index=True,
        )

    with tab4:
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "📥 CSV 다운로드",
                data=fdf.to_csv(index=False, encoding="utf-8-sig"),
                file_name=f"monitors_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True,
            )
        with c2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                fdf.to_excel(w, index=False, sheet_name="Monitors")
            st.download_button(
                "📥 Excel 다운로드",
                data=buf.getvalue(),
                file_name=f"monitors_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
