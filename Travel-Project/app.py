import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌍", layout="wide")

# 각 페이지 정의
home_page = st.Page("src/views/home.py", title="대한민국 (홈)", icon="🏠", default=True)
usa_page = st.Page("src/views/usa.py", title="미국", icon="🇺🇸")
china_page = st.Page("src/views/china.py", title="중국", icon="🇨🇳")
japan_page = st.Page("src/views/japan.py", title="일본", icon="🇯🇵")

# 사이드바 네비게이션 가동
pg = st.navigation(
    {
        "메인": [home_page],
        "여행지 안내": [usa_page, china_page, japan_page]
    }
)

pg.run()