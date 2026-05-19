"""
Streamlit 대시보드 - 사하라 이남 아프리카 데스크탑 모니터 가격 추적기

실행: streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

from database.db_manager import DatabaseManager

# ── 페이지 기본 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="Africa Monitor Price Tracker",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DB 연결 ───────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    return DatabaseManager()

@st.cache_data(ttl=300)  # 5분 캐시
def load_data():
    db = get_db()
    records = db.get_all_monitors()
    stats = db.get_summary_stats()
    logs = db.get_crawl_logs(limit=20)
    return records, stats, logs

db = get_db()
records, stats, logs = load_data()

df = pd.DataFrame(records) if records else pd.DataFrame()

# ── 사이드바 필터 ──────────────────────────────────────────────────
st.sidebar.title("🔍 필터")

if not df.empty:
    countries = ["전체"] + sorted(df["country"].unique().tolist())
    sel_country = st.sidebar.selectbox("국가", countries)

    brands = ["전체"] + sorted(df["brand"].dropna().unique().tolist())
    sel_brand = st.sidebar.selectbox("브랜드", brands)

    sizes = ["전체"] + sorted(df["screen_size_inch"].dropna().unique().tolist())
    sel_size = st.sidebar.selectbox("화면 크기 (인치)", sizes)

    conditions = ["전체"] + sorted(df["condition"].dropna().unique().tolist())
    sel_condition = st.sidebar.selectbox("상태", conditions)

    # 가격 범위
    if df["price"].notna().any():
        price_min = float(df["price"].min())
        price_max = float(df["price"].max())
        sel_price = st.sidebar.slider(
            "가격 범위",
            min_value=price_min,
            max_value=price_max,
            value=(price_min, price_max),
        )
    else:
        sel_price = (0, 9999999)

    # 필터 적용
    filtered = df.copy()
    if sel_country != "전체":
        filtered = filtered[filtered["country"] == sel_country]
    if sel_brand != "전체":
        filtered = filtered[filtered["brand"] == sel_brand]
    if sel_size != "전체":
        filtered = filtered[filtered["screen_size_inch"] == sel_size]
    if sel_condition != "전체":
        filtered = filtered[filtered["condition"] == sel_condition]
    if df["price"].notna().any():
        filtered = filtered[
            (filtered["price"] >= sel_price[0]) & (filtered["price"] <= sel_price[1])
        ]
else:
    filtered = df

# ── 헤더 ──────────────────────────────────────────────────────────
st.title("🖥️ 사하라 이남 아프리카 데스크탑 모니터 가격 추적기")
st.caption(f"마지막 크롤링: {stats.get('last_crawl', 'N/A')}  |  총 상품 수: {len(df):,}개")

# ── 핵심 지표 카드 ────────────────────────────────────────────────
if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 상품 수", f"{len(df):,}")
    col2.metric("수집 국가 수", df["country"].nunique())
    col3.metric("브랜드 수", df["brand"].nunique())
    col4.metric("수집 사이트 수", df["retailer"].nunique())

st.divider()

# ── 탭 구성 ───────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 국가별 분석",
    "🏷️ 브랜드 분석",
    "📐 사이즈별 비교",
    "📋 상품 목록",
    "📥 데이터 내보내기",
])

# ── Tab 1: 국가별 분석 ────────────────────────────────────────────
with tab1:
    st.subheader("국가별 가격 통계")

    if stats.get("by_country"):
        country_df = pd.DataFrame(stats["by_country"])
        country_df.columns = ["국가", "통화", "평균가격", "최저가격", "최고가격", "상품수"]

        col_a, col_b = st.columns(2)
        with col_a:
            st.dataframe(country_df, use_container_width=True, hide_index=True)
        with col_b:
            st.bar_chart(country_df.set_index("국가")["상품수"], use_container_width=True)

        # 국가별 평균가 바 차트 (통화가 다르므로 참고용)
        st.caption("⚠️ 통화가 다르므로 국가 간 직접 비교는 참고용입니다.")
    else:
        st.info("데이터가 없습니다. 먼저 크롤러를 실행해 주세요.")

    # 국가별 최저가 상품
    if not filtered.empty and "price" in filtered.columns:
        st.subheader("국가별 최저가 모니터")
        cheapest = (
            filtered[filtered["price"].notna()]
            .sort_values("price")
            .groupby("country")
            .first()
            .reset_index()
        )
        for _, row in cheapest.iterrows():
            with st.expander(f"🏆 {row['country']} 최저가: {row['currency']} {row['price']:,.0f}"):
                st.write(f"**상품명:** {row['product_title']}")
                st.write(f"**브랜드:** {row.get('brand', 'N/A')}")
                st.write(f"**사이트:** {row['retailer']}")
                if row.get("product_url"):
                    st.write(f"**링크:** {row['product_url']}")

# ── Tab 2: 브랜드 분석 ────────────────────────────────────────────
with tab2:
    st.subheader("브랜드별 상품 분포")

    if stats.get("by_brand"):
        brand_df = pd.DataFrame(stats["by_brand"])
        brand_df.columns = ["브랜드", "상품수"]

        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.dataframe(brand_df.head(15), use_container_width=True, hide_index=True)
        with col_b:
            st.bar_chart(brand_df.head(15).set_index("브랜드")["상품수"])

    # 브랜드별 평균 가격 (국가별)
    if not filtered.empty and filtered["price"].notna().any():
        st.subheader("브랜드별 평균 가격 (필터 기준)")
        brand_price = (
            filtered[filtered["price"].notna()]
            .groupby(["brand", "currency"])["price"]
            .agg(["mean", "count"])
            .reset_index()
        )
        brand_price.columns = ["브랜드", "통화", "평균가격", "상품수"]
        brand_price["평균가격"] = brand_price["평균가격"].round(0)
        st.dataframe(brand_price.sort_values("상품수", ascending=False), hide_index=True)

# ── Tab 3: 사이즈별 비교 ──────────────────────────────────────────
with tab3:
    st.subheader("화면 크기별 평균 가격")

    if stats.get("by_size"):
        size_df = pd.DataFrame(stats["by_size"])
        size_df.columns = ["화면크기(인치)", "평균가격", "상품수"]
        size_df = size_df.dropna(subset=["화면크기(인치)"])

        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.dataframe(size_df, use_container_width=True, hide_index=True)
        with col_b:
            if not size_df.empty:
                st.bar_chart(size_df.set_index("화면크기(인치)")["상품수"])

    # 사이트별 상품 수
    st.subheader("사이트별 수집 현황")
    if stats.get("by_retailer"):
        retailer_df = pd.DataFrame(stats["by_retailer"])
        retailer_df.columns = ["사이트", "국가", "상품수", "마지막크롤링"]
        st.dataframe(retailer_df, use_container_width=True, hide_index=True)

# ── Tab 4: 상품 목록 ──────────────────────────────────────────────
with tab4:
    st.subheader(f"상품 목록 ({len(filtered):,}개)")

    if not filtered.empty:
        # 표시할 컬럼 선택
        display_cols = [
            "country", "retailer", "product_title", "brand",
            "screen_size_inch", "resolution", "condition",
            "price", "currency", "availability", "crawl_date",
        ]
        display_cols = [c for c in display_cols if c in filtered.columns]

        col_labels = {
            "country": "국가",
            "retailer": "사이트",
            "product_title": "상품명",
            "brand": "브랜드",
            "screen_size_inch": "크기(인치)",
            "resolution": "해상도",
            "condition": "상태",
            "price": "가격",
            "currency": "통화",
            "availability": "재고",
            "crawl_date": "수집일",
        }

        display_df = filtered[display_cols].rename(columns=col_labels)
        st.dataframe(
            display_df.sort_values("가격", ascending=True) if "가격" in display_df.columns else display_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("필터 조건에 맞는 상품이 없습니다.")

# ── Tab 5: 데이터 내보내기 ────────────────────────────────────────
with tab5:
    st.subheader("데이터 내보내기")

    if not filtered.empty:
        col_a, col_b = st.columns(2)

        with col_a:
            st.write("**CSV 다운로드**")
            csv_data = filtered.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=f"monitors_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        with col_b:
            st.write("**Excel 다운로드**")
            import io
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                filtered.to_excel(writer, index=False, sheet_name="Monitors")
                if stats.get("by_country"):
                    pd.DataFrame(stats["by_country"]).to_excel(
                        writer, index=False, sheet_name="Country Stats"
                    )
            st.download_button(
                label="📥 Excel 다운로드",
                data=excel_buffer.getvalue(),
                file_name=f"monitors_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # 크롤링 로그
    st.subheader("최근 크롤링 로그")
    if logs:
        log_df = pd.DataFrame(logs)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("크롤링 로그가 없습니다.")

    # 새로고침 버튼
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
