import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 상위 폴더의 .env 파일 로드
load_dotenv(dotenv_path="../.env")

# 환율 API 키 불러오기
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

st.set_page_config(page_title="실시간 환율 계산기", page_icon="💱", layout="centered")
st.title("💱 실시간 환율 계산기")
st.caption("ExchangeRate-API를 활용한 실시간 통화 변환 서비스")

# 지원 통화 리스트
CURRENCY_LIST = [
    "KRW", "USD", "EUR", "JPY", "CNY", "GBP", 
    "AUD", "CAD", "CHF", "HKD", "SGD", "VND", "THB"
]

# 통화 이름 매핑 (표시용)
CURRENCY_NAMES = {
    "KRW": "대한민국 원 (KRW)",
    "USD": "미국 달러 (USD)",
    "EUR": "유로 (EUR)",
    "JPY": "일본 엔 (JPY)",
    "CNY": "중국 위안 (CNY)",
    "GBP": "영국 파운드 (GBP)",
    "AUD": "호주 달러 (AUD)",
    "CAD": "캐나다 달러 (CAD)",
    "CHF": "스위스 프랑 (CHF)",
    "HKD": "홍콩 달러 (HKD)",
    "SGD": "싱가포르 달러 (SGD)",
    "VND": "베트남 동 (VND)",
    "THB": "태국 바트 (THB)"
}

# API 응답 캐싱 (동일 요청 반복 호출 방지)
@st.cache_data(ttl=300)
def get_exchange_rate(api_key: str, from_curr: str, to_curr: str):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_curr}/{to_curr}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

if not EXCHANGE_API_KEY:
    st.error("⚠️ `.env` 파일에서 `EXCHANGERATE_API_KEY`를 찾을 수 없습니다. 키 설정을 확인해주세요.")
else:
    # 1. 입력 UI 구성
    col_amount, col_from, col_to = st.columns([2, 2, 2])
    
    with col_amount:
        amount = st.number_input(
            "환전할 금액",
            min_value=0.0,
            value=100.0,
            step=10.0,
            format="%.2f"
        )

    with col_from:
        from_curr = st.selectbox(
            "보내는 통화 (From)",
            options=CURRENCY_LIST,
            index=CURRENCY_LIST.index("USD"),
            format_func=lambda x: CURRENCY_NAMES.get(x, x)
        )

    with col_to:
        to_curr = st.selectbox(
            "받는 통화 (To)",
            options=CURRENCY_LIST,
            index=CURRENCY_LIST.index("KRW"),
            format_func=lambda x: CURRENCY_NAMES.get(x, x)
        )

    # 2. 환율 계산 및 결과 표시
    if from_curr == to_curr:
        st.info("동일한 통화가 선택되었습니다.")
        st.metric(label="변환 결과", value=f"{amount:,.2f} {to_curr}")
    else:
        data = get_exchange_rate(EXCHANGE_API_KEY, from_curr, to_curr)
        
        if data and data.get("result") == "success":
            conversion_rate = data["conversion_rate"]
            converted_amount = amount * conversion_rate
            last_update = data.get("time_last_update_utc", "N/A")
            
            st.divider()
            
            # 결과 카드
            st.subheader("📊 환전 계산 결과")
            
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.metric(
                    label=f"변환 금액 ({to_curr})",
                    value=f"{converted_amount:,.2f} {to_curr}",
                    delta=f"1 {from_curr} = {conversion_rate:,.4f} {to_curr}"
                )
            
            with r_col2:
                # 역방향 환율 (1 To = ? From)
                reverse_rate = 1 / conversion_rate if conversion_rate != 0 else 0
                st.metric(
                    label=f"역방향 환율 ({from_curr})",
                    value=f"1 {to_curr} = {reverse_rate:,.4f} {from_curr}"
                )
                
            st.caption(f"🕒 기준 시각(UTC): {last_update}")
        else:
            st.error("환율 정보를 불러오는 데 실패했습니다. API 키나 네트워크 상태를 확인해주세요.")