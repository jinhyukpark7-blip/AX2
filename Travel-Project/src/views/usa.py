import streamlit as st
import os

st.title("미국 🇺🇸")
st.caption("광활한 대자연과 세계적인 대도시가 공존하는 나라")

img_path = "assets/usa.jpg"
if os.path.exists(img_path):
    st.image(img_path, use_container_width=True, caption="미국 풍경")

st.markdown("""
### 📌 국가 개요
* **수도:** 워싱턴 D.C.
* **언어:** 영어
* **화폐:** 미국 달러 (USD)
* **주요 명소:** 뉴욕 타임스퀘어, 그랜드 캐니언, 요세미티 국립공원, 라스베이거스
""")

st.divider()
st.link_button("🌐 미국 공식 여행 사이트 방문 (Visit the USA)", "https://www.visittheusa.co.kr")