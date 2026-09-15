import os
from pathlib import Path
from dotenv import load_dotenv
import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

# ---------------- 1. API 키 로드 (Streamlit Secrets 및 .env 동시 지원) ----------------

# 1) 로컬 개발 환경용 .env 로드 (현재 폴더 및 상위 폴더 탐색)
current_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=current_dir / ".env")
load_dotenv(dotenv_path=current_dir.parent / ".env")
load_dotenv()

# 2) Streamlit Cloud(st.secrets) 우선 탐색 후 로컬 os.getenv 탐색
def get_api_key(key_name):
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return os.getenv(key_name)

KAKAO_REST_KEY = get_api_key("KAKAO_REST_API_KEY")
OPENWEATHER_KEY = get_api_key("OPENWEATHER_API_KEY")
EXCHANGERATE_KEY = get_api_key("EXCHANGERATE_API_KEY")

st.set_page_config(page_title="국내 여행 포털", page_icon="🇰🇷", layout="wide")
st.title("🇰🇷 대한민국 국내 여행 도우미 (명소 검색 · 현지 날씨 · 환율)")


# ---------------- 2. API 호출 함수 정의 ----------------

# 1) 카카오 로컬 REST API 키워드 검색
def search_places_kakao(query, api_key):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": query, "size": 15}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        return res.json().get("documents", []) if res.status_code == 200 else []
    except Exception:
        return []

# 2) OpenWeatherMap 실시간 날씨 API (위도/경도 기준)
def get_weather_by_coords(lat, lon, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric",  # 섭씨 온도
        "lang": "kr"         # 한국어 설명
    }
    try:
        res = requests.get(url, params=params, timeout=5)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None

# 3) ExchangeRate-API 실시간 환율 API
def get_exchange_rates(base_currency, api_key):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        return data.get("conversion_rates", {}) if data.get("result") == "success" else {}
    except Exception:
        return {}


# ---------------- 3. 사이드바: 환율 계산기 ----------------

with st.sidebar:
    st.header("💱 여행 경비 환율 계산기")
    st.caption("외국 통화를 실시간 원화(KRW)로 바로 환산합니다.")

    currency_map = {
        "미국 달러 (USD)": "USD",
        "일본 엔 (JPY, 100엔)": "JPY",
        "유럽 유로 (EUR)": "EUR",
        "중국 위안 (CNY)": "CNY"
    }
    selected_curr_label = st.selectbox("외국 통화 선택", list(currency_map.keys()))
    target_currency = currency_map[selected_curr_label]
    amount = st.number_input("외화 금액 입력", min_value=1.0, value=100.0, step=10.0)

    if EXCHANGERATE_KEY:
        rates = get_exchange_rates(target_currency, EXCHANGERATE_KEY)
        krw_rate = rates.get("KRW")
        if krw_rate:
            if target_currency == "JPY":
                total_krw = (amount / 100) * krw_rate
                st.success(f"**{amount:,.0f} JPY** ≈ **{total_krw:,.0f} 원 (KRW)**")
                st.caption(f"적용 환율: 100 JPY = {krw_rate:,.2f} KRW")
            else:
                total_krw = amount * krw_rate
                st.success(f"**{amount:,.2f} {target_currency}** ≈ **{total_krw:,.0f} 원 (KRW)**")
                st.caption(f"적용 환율: 1 {target_currency} = {krw_rate:,.2f} KRW")
        else:
            st.warning("환율 데이터를 불러오지 못했습니다.")
    else:
        st.info("💡 `EXCHANGERATE_API_KEY`를 설정하세요.")


# ---------------- 4. 메인 화면: 국내 여행지 검색 & 지도 / 날씨 연동 ----------------

st.subheader("📍 국내 관광지 / 명소 검색")
keyword = st.text_input("목적지를 입력하세요", value="강남역", placeholder="예: 강남역, 경복궁, 해운대, 성산일출봉")

if keyword:
    if not KAKAO_REST_KEY:
        st.error("⚠️ `KAKAO_REST_API_KEY`가 설정되어 있지 않습니다. (.env 또는 Streamlit Cloud Settings > Secrets 확인)")
        st.stop()

    with st.spinner(f"'{keyword}' 검색 중..."):
        places = search_places_kakao(keyword, KAKAO_REST_KEY)

    if not places:
        st.warning("검색 결과가 없습니다. 다른 키워드로 검색해보세요.")
    else:
        # 검색 결과 DataFrame 구성
        df_places = pd.DataFrame([
            {
                "관광지명": p["place_name"],
                "주소": p["road_address_name"] or p["address_name"],
                "전화번호": p.get("phone") or "정보 없음",
                "lat": float(p["y"]),
                "lon": float(p["x"]),
                "url": p["place_url"]
            }
            for p in places
        ])

        # 선택 인덱스 세션 상태 관리
        if "selected_idx" not in st.session_state or st.session_state.selected_idx >= len(df_places):
            st.session_state.selected_idx = 0

        # 현재 선택된 목적지 정보 추출
        current_place = df_places.iloc[st.session_state.selected_idx]
        target_lat = current_place["lat"]
        target_lon = current_place["lon"]
        target_name = current_place["관광지명"]
        target_address = current_place["주소"]

        # --- 목적지 실시간 날씨 표시 (상단 위젯) ---
        st.markdown(f"### 🌤️ **[{target_name}]** 현지 실시간 날씨")
        
        if OPENWEATHER_KEY:
            weather = get_weather_by_coords(target_lat, target_lon, OPENWEATHER_KEY)
            if weather and "main" in weather:
                temp = weather["main"]["temp"]
                feels_like = weather["main"]["feels_like"]
                humidity = weather["main"]["humidity"]
                desc = weather["weather"][0]["description"]
                icon = weather["weather"][0]["icon"]
                icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"

                w1, w2, w3, w4 = st.columns([1, 2, 2, 3])
                with w1:
                    st.image(icon_url, width=65)
                with w2:
                    st.metric("현재 기온", f"{temp:.1f} °C", delta=desc)
                with w3:
                    st.metric("체감 온도", f"{feels_like:.1f} °C")
                with w4:
                    st.write(f"**습도:** {humidity}%")
                    st.write(f"**주소:** {target_address}")
            else:
                st.warning("선택된 목적지의 날씨 정보를 가져올 수 없습니다.")
        else:
            st.info("💡 `OPENWEATHER_API_KEY`를 설정하면 실시간 날씨가 표시됩니다.")

        st.divider()

        # 좌우 균등 칼럼 배치 (1:1)
        col_map, col_list = st.columns([1, 1])

        # --- 좌측: Folium 지도 (높이 380px) ---
        with col_map:
            st.subheader("🗺️ 목적지 위치 지도")
            
            m = folium.Map(
                location=[target_lat, target_lon],
                zoom_start=15,
                tiles="https://xdworld.vworld.kr/2d/Base/service/{z}/{x}/{y}.png",
                attr="VWorld",
            )

            for idx, row in df_places.iterrows():
                is_selected = (idx == st.session_state.selected_idx)
                marker_color = "red" if is_selected else "blue"

                popup_html = f"""
                <div style="font-family: sans-serif; font-size: 13px; min-width: 140px;">
                    <b>{row['관광지명']}</b><br/>
                    <span style="color: gray;">{row['주소']}</span><br/>
                    <a href="{row['url']}" target="_blank" style="color: #007bff; text-decoration: none;">🔗 카카오맵 길찾기</a>
                </div>
                """

                folium.Marker(
                    location=[row["lat"], row["lon"]],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{'⭐️ [선택됨] ' if is_selected else ''}{row['관광지명']}",
                    icon=folium.Icon(color=marker_color, icon="info-sign"),
                ).add_to(m)

            st_folium(m, width="100%", height=380, returned_objects=[])

        # --- 우측: 주변 검색 목록 (지도와 동일하게 높이 380px) ---
        with col_list:
            st.subheader("📋 주변 검색 목록")
            st.caption("👇 표에서 원하는 행을 클릭하면 해당 위치의 날씨와 지도 마커가 변경됩니다.")
            
            event = st.dataframe(
                df_places[["관광지명", "주소", "전화번호"]],
                use_container_width=True,
                hide_index=True,
                height=380,
                on_select="rerun",
                selection_mode="single-row"
            )

            # 표 행 클릭 이벤트 처리
            selected_rows = event.selection.get("rows", [])
            if selected_rows:
                st.session_state.selected_idx = selected_rows[0]