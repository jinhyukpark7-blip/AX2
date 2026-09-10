# 날씨 API 실습
# openWeatherMap 현재 날씨 API 로 특정 도시의 날씨를 가져와 출력한다
# 사전준비 openWeatherMap 회원가입 후 API 발급
# pip install requests python=dotenv
# .env 파일을 생성하고 이곳에 OPENWEATHER_API_KEY=발급받은_API_키
# .env.example OPENWEATHER_API_KEY=your_key
# .env.example 받아서 .env로 이름 바꾸고 자기 API를 채운다.


import os
import requests
import streamlit as st
from dotenv import load_dotenv



# load_dotenv() # .env 파일을 읽어 환경 변수로 등록한다

# API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 상위 폴더의 .env 파일 로드
load_dotenv(dotenv_path="../.env")

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

st.set_page_config(page_title="날씨 & 환율 대시보드", page_icon="🌍", layout="wide")
st.title("🌍 실시간 날씨 및 환율 대시보드")

# 세션 상태 초기화
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "exchange_data" not in st.session_state:
    st.session_state.exchange_data = None

col_left, col_right = st.columns(2)

# ==================== [왼쪽: 날씨 정보] ====================
with col_left:
    st.subheader("🌤️ 도시별 날씨 조회")
    city = st.text_input("도시 이름 입력 (영어)", value="Seoul", key="weather_city")
    
    if st.button("날씨 확인", key="weather_btn"):
        if not WEATHER_API_KEY:
            st.error("OpenWeatherMap API 키가 설정되지 않았습니다.")
        else:
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=kr"
            res = requests.get(weather_url)
            if res.status_code == 200:
                st.session_state.weather_data = res.json()
            else:
                st.error(f"날씨 정보를 불러오지 못했습니다. (코드: {res.status_code})")

    # 저장된 날씨 데이터가 있으면 화면에 렌더링
    if st.session_state.weather_data:
        data = st.session_state.weather_data
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        
        st.success(f"📍 **{data['name']}** 날씨")
        m1, m2, m3 = st.columns(3)
        m1.metric("현재 기온", f"{temp} °C")
        m2.metric("체감 기온", f"{feels_like} °C")
        m3.metric("습도", f"{humidity} %")
        st.info(f"상태: {weather_desc}")

# ==================== [오른쪽: 환율 정보] ====================
with col_right:
    st.subheader("💱 실시간 환율 조회")
    base_currency = st.selectbox(
        "기준 통화 선택",
        options=["USD", "KRW", "EUR", "JPY", "CNY", "GBP"],
        index=0,
        key="base_curr"
    )
    
    if st.button("환율 확인", key="exchange_btn"):
        if not EXCHANGE_API_KEY:
            st.error("ExchangeRate API 키가 설정되지 않았습니다.")
        else:
            exchange_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base_currency}"
            res = requests.get(exchange_url)
            if res.status_code == 200:
                st.session_state.exchange_data = (base_currency, res.json())
            else:
                st.error(f"환율 정보를 불러오지 못했습니다. (코드: {res.status_code})")

    # 저장된 환율 데이터가 있으면 화면에 렌더링
    if st.session_state.exchange_data:
        curr, data = st.session_state.exchange_data
        if data.get("result") == "success":
            rates = data["conversion_rates"]
            
            st.success(f"기준: **1 {curr}**")
            e1, e2 = st.columns(2)
            e1.metric("대한민국 원 (KRW)", f"{rates.get('KRW', 0):,.2f} 원")
            e1.metric("미국 달러 (USD)", f"{rates.get('USD', 0):,.4f} $")
            e1.metric("일본 엔 (JPY)", f"{rates.get('JPY', 0):,.2f} ¥")
            
            e2.metric("유로 (EUR)", f"{rates.get('EUR', 0):,.4f} €")
            e2.metric("중국 위안 (CNY)", f"{rates.get('CNY', 0):,.2f} ¥")
            e2.metric("영국 파운드 (GBP)", f"{rates.get('GBP', 0):,.4f} £")
            
            st.caption(f"기준 시각: {data.get('time_last_update_utc', 'N/A')}")