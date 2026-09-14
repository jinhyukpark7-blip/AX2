import streamlit as st
import os

st.title("일본 🇯🇵")
st.caption("전통과 현대가 조화를 이루며 온천과 미식이 가득한 나라")

img_path = "assets/japan.jpg"
if os.path.exists(img_path):
    st.image(img_path, use_container_width=True, caption="일본 풍경")

st.markdown("""
### 📌 국가 개요
* **수도:** 도쿄
* **언어:** 일본어
* **화폐:** 일본 엔 (JPY)
* **주요 명소:** 도쿄 타워, 교토 후시미 이나리 신사, 오사카 도톤보리, 삿포로
""")

st.divider()
st.link_button("🌐 일본 공식 관광청 사이트 방문 (JNTO)", "https://www.japan.travel/ko/kr/")