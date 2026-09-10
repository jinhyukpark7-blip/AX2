import streamlit as st
import random
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="럭키 로또 생성기",
    page_icon="🔮",
    layout="centered"
)

# 커스텀 CSS 스타일 정의 (로또 공 및 컨테이너 디자인)
st.markdown("""
    <style>
    .lotto-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        background-color: #f8f9fa;
        padding: 15px 20px;
        border-radius: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #ff4b4b;
    }
    .set-label {
        font-size: 18px;
        font-weight: bold;
        color: #333333;
        width: 80px;
        min-width: 80px;
    }
    .balls-group {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    .lotto-ball {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        color: white;
        font-weight: 800;
        font-size: 18px;
        box-shadow: inset -4px -4px 6px rgba(0,0,0,0.4), 2px 2px 4px rgba(0,0,0,0.3);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    /* 1 ~ 10: 노란색 */
    .ball-yellow {
        background: radial-gradient(circle at 30% 30%, #fff176, #fbc400 60%, #f57f17);
    }
    /* 11 ~ 20: 파란색 */
    .ball-blue {
        background: radial-gradient(circle at 30% 30%, #64b5f6, #1e88e5 60%, #1565c0);
    }
    /* 21 ~ 30: 빨간색 */
    .ball-red {
        background: radial-gradient(circle at 30% 30%, #ef5350, #e53935 60%, #b71c1c);
    }
    /* 31 ~ 40: 회색 */
    .ball-gray {
        background: radial-gradient(circle at 30% 30%, #e0e0e0, #757575 60%, #424242);
    }
    /* 41 ~ 45: 초록색 */
    .ball-green {
        background: radial-gradient(circle at 30% 30%, #aed581, #7cb342 60%, #558b2f);
    }
    </style>
""", unsafe_allow_html=True)

# 타이틀 및 인트로
st.title("🔮 럭키 3D 로또 번호 생성기")
st.markdown("버튼을 누르면 당첨 기운이 가득 담긴 **5세트의 로또 추천 번호**를 즉시 생성합니다!")
st.write("")

# 1~45 사이 중복 없는 6개 숫자 정렬 리스트 반환 함수
def generate_lotto_set() -> list:
    numbers = set()
    while len(numbers) < 6:
        numbers.add(random.randint(1, 45))
    return sorted(list(numbers))

# 번호에 대응하는 볼의 CSS 클래스를 반환하는 함수
def get_ball_class(num: int) -> str:
    if num <= 10:
        return "ball-yellow"
    elif num <= 20:
        return "ball-blue"
    elif num <= 30:
        return "ball-red"
    elif num <= 40:
        return "ball-gray"
    else:
        return "ball-green"

# 로또 번호 한 세트를 HTML 문자열로 생성하는 함수
def make_lotto_html(set_index: int, numbers: list) -> str:
    balls_html = ""
    for num in numbers:
        bg_class = get_ball_class(num)
        balls_html += f'<div class="lotto-ball {bg_class}">{num}</div>'
    
    return f"""
    <div class="lotto-container">
        <div class="set-label">🎯 {set_index}세트</div>
        <div class="balls-group">
            {balls_html}
        </div>
    </div>
    """

# 세션 상태에 번호 및 시간 저장하기 (새로고침 시 사라지는 것 방지)
if "lotto_results" not in st.session_state:
    st.session_state.lotto_results = None
if "generation_time" not in st.session_state:
    st.session_state.generation_time = None

# 번호 생성 버튼
if st.button("✨ 로또 번호 5세트 생성하기", type="primary", use_container_width=True):
    results = []
    for i in range(1, 6):
        results.append(generate_lotto_set())
    st.session_state.lotto_results = results
    st.session_state.generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown("---")

# 결과 출력
if st.session_state.lotto_results:
    st.success(f"🍀 행운의 추천 번호 생성이 완료되었습니다! (생성 시각: {st.session_state.generation_time})")
    
    # 5개 세트 출력
    for idx, nums in enumerate(st.session_state.lotto_results, 1):
        html_code = make_lotto_html(idx, nums)
        st.markdown(html_code, unsafe_allow_html=True)
        
    st.info("💡 **로또 공 색상 가이드**\n"
            "- 🟡 **1 ~ 10** | 🔵 **11 ~ 20** | 🔴 **21 ~ 30** | ⚫ **31 ~ 40** | 🟢 **41 ~ 45**")
else:
    st.info("👉 위의 **로또 번호 5세트 생성하기** 버튼을 클릭하여 행운의 번호를 확인해 보세요!")
