# 어제
# 전전날 
# 왜 
# 유용해
# 뭔가 
# 전용 


# raw_trade_data.csv 파일 활용
# HS코드가 
# 85로 시작하는 (반도체류) + 국가명 미국 또는 베트남 + 수출금액 0보다 큰 수(실제 수출 실적이 있는) 행만
# 다중 조건으로 필터링 한 뒤, 수출금액 상위 10건을 화면에 보여주고 report.csv 로 저장.
# streamlit 사용 streamlit run day04-01.py

# day04-01.py
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="수출 실적 분석 리포트", layout="wide")
st.title("📊 수출 실적 상위 10건 리포트")

# 파일 경로 설정
DATA_PATH = r"C:\Users\user\AX2\common\raw_trade_data.csv"
OUTPUT_PATH = "report.csv"

if not os.path.exists(DATA_PATH):
    DATA_PATH = "raw_trade_data.csv"

if os.path.exists(DATA_PATH):
    # 1. 인코딩별 CSV 로드 시도
    df = None
    for enc in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:
        try:
            df = pd.read_csv(DATA_PATH, encoding=enc)
            break
        except UnicodeDecodeError:
            continue

    if df is not None:
        # 컬럼명 앞뒤 공백 제거
        df.columns = df.columns.astype(str).str.strip()

        # 2. 유연한 컬럼명 매핑 (HS코드, 국가명, 수출금액)
        hs_col = next(
            (
                c
                for c in df.columns
                if "HS" in c.upper() or "코드" in c
            ),
            None,
        )
        country_col = next(
            (c for c in df.columns if "국가" in c or "나라" in c or "COUNTRY" in c.upper()),
            None,
        )
        export_col = next(
            (
                c
                for c in df.columns
                if ("수출" in c or "금액" in c or "EXPORT" in c.upper() or "VALUE" in c.upper())
                and "구분" not in c and "TYPE" not in c.upper()
            ),
            None,
        )

        # 컬럼을 제대로 찾지 못했을 경우 화면에 안내
        if not (hs_col and country_col and export_col):
            st.error(
                f"❌ 필수 컬럼을 찾을 수 없습니다. 현재 파일의 컬럼 목록: {list(df.columns)}"
            )
            st.stop()

        # 3. 전처리 및 필터링
        # HS코드 문자열 변환 및 소수점(.0) 제거
        df[hs_col] = (
            df[hs_col]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )

        # 수출금액 숫자형 변환 (문자열/쉼표 등 제거)
        df[export_col] = (
            pd.to_numeric(
                df[export_col].astype(str).str.replace(",", "").str.strip(),
                errors="coerce",
            ).fillna(0)
        )

        # 다중 조건 필터링
        cond_hs = df[hs_col].str.startswith("85")
        cond_country = (
            df[country_col].astype(str).str.strip().isin(["미국", "베트남"])
        )
        cond_export = df[export_col] > 0

        filtered_df = df[cond_hs & cond_country & cond_export].copy()

        # 4. 정렬 및 상위 10건 추출
        top10_df = filtered_df.sort_values(
            by=export_col, ascending=False
        ).head(10)

        # 5. 로컬 저장 (report.csv)
        top10_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

        # 6. Streamlit 화면 출력
        st.subheader("🇺🇸 미국 & 🇻🇳 베트남 반도체류(HS 85) 수출 실적 TOP 10")
        st.dataframe(top10_df, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("추출 건수", f"{len(top10_df)}건")
        with col2:
            st.metric(
                "상위 10건 총 수출금액", f"{top10_df[export_col].sum():,.0f}"
            )

        st.success(f"✅ 결과가 '{OUTPUT_PATH}' 파일로 저장되었습니다.")

        # 다운로드 버튼
        st.download_button(
            label="📥 report.csv 다운로드",
            data=top10_df.to_csv(index=False, encoding="utf-8-sig").encode(
                "utf-8-sig"
            ),
            file_name="report.csv",
            mime="text/csv",
        )
    else:
        st.error("❌ 파일 인코딩을 읽는 데 실패했습니다.")
else:
    st.error(f"❌ 파일을 찾을 수 없습니다: {DATA_PATH}")