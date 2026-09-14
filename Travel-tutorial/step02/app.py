import streamlit as st

st.set_page_config(page_title="세계 여행 포털", page_icon="🌍")

# 사이드 바
menu = st.sidebar.radio("메뉴", ["홈", "미국", "중국", "일본"])

if menu == "홈":
    st.title("대한민국 🇰🇷")
    st.write("사계절이 아름답고 유구한 역사와 현대 문화가 공존하는 나라입니다.")

elif menu == "미국":
    st.title("미국 🇺🇸")
    st.write(
        "다양한 문화와 광활한 대자연, 세계적인 대도시들이 가득한 나라입니다."
    )
    st.link_button(
        "미국 공식 사이트 방문", "https://www.visittheusa.co.kr"
    )

elif menu == "중국":
    st.title("중국 🇨🇳")
    st.write("오랜 역사와 거대한 자연경관, 다채로운 먹거리가 있는 나라입니다.")

elif menu == "일본":
    st.title("일본 🇯🇵")
    st.write(
        "전통과 현대가 조화를 이루며 온천, 미식, 쇼핑 등 볼거리가 풍부한 나라입니다."
    )