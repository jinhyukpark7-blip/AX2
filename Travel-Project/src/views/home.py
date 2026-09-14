import streamlit as st
import os

st.title("대한민국 🇰🇷")
st.caption("사계절의 아름다움과 K-컬처의 중심지")

# 이미지 표시 (assets 폴더에 korea.jpg가 있을 경우 출력)
img_path = "assets/korea.jpg"
if os.path.exists(img_path):
    st.image(img_path, use_container_width=True, caption="대한민국 대표 풍경")

st.markdown("""
### 📌 국가 개요
* **수도:** 서울
* **언어:** 한국어
* **화폐:** 대한민국 원 (KRW)
* **주요 명소:** 경복궁, 남산타워, 제주도, 부산 해운대
""")

st.divider()
st.link_button("🌐 대한민국 공식 관광 사이트 방문 (Visit Korea)", "https://korean.visitkorea.or.kr")