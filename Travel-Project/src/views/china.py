import streamlit as st
import os

st.title("중국 🇨🇳")
st.caption("유구한 역사와 거대한 자연경관이 펼쳐지는 나라")

img_path = "assets/china.jpg"
if os.path.exists(img_path):
    st.image(img_path, use_container_width=True, caption="중국 풍경")

st.markdown("""
### 📌 국가 개요
* **수도:** 베이징
* **언어:** 중국어
* **화폐:** 위안화 (CNY)
* **주요 명소:** 만리장성, 자금성, 상하이 와이탄, 장가계
""")

st.divider()
st.link_button("🌐 중국 공식 관광 정보 사이트 방문", "http://www.cnto.or.kr")