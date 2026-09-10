import streamlit as st
import random
from datetime import datetime

st.title("🤑 로또 번호 자동 생성기")
st.caption("버튼을 누르면 1~45 사이의 중복 없는 번호 6개짜리 세트를 생성합니다.")

# 번호에 따라 실제 로또 공 색상 이모지를 붙여주는 함수
def get_colored_ball(num: int) -> str:
    if num <= 10:
        return f"🟡 {num}"   # 1 ~ 10: 노란색
    elif num <= 20:
        return f"🔵 {num}"   # 11 ~ 20: 파란색
    elif num <= 30:
        return f"🔴 {num}"   # 21 ~ 30: 빨간색
    elif num <= 40:
        return f"⚫ {num}"   # 31 ~ 40: 검은/회색
    else:
        return f"🟢 {num}"   # 41 ~ 45: 초록색

# 중복 없는 번호 6개 뽑기
def lotto_one_set() -> list:
    numbers = set()
    while len(numbers) < 6:
        numbers.add(random.randint(1, 45))
    return sorted(numbers)

st.markdown("---")

# 버튼을 눌렀을 때만 아래 내용이 실행됨
if st.button("5세트 번호 생성하기", key="lotto_generate_btn"):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"생성 시각 : **{now_str}**")
    st.markdown("---")

    for set_index in range(1, 6):
        lotto_nums = lotto_one_set()
        # 번호 리스트를 색상 공 형태로 변환
        balls = " ".join([get_colored_ball(n) for n in lotto_nums])
        st.markdown(f"**{set_index}세트** : {balls}")