import streamlit as st

st.set_page_config(page_title="무역 직무 MBTI 진단기", page_icon="🚢", layout="centered")

# --- 버튼 텍스트 자동 줄바꿈 및 디자인 개선 CSS ---
st.markdown("""
<style>
div[data-testid="stButton"] > button {
    white-space: normal !important;
    word-break: keep-all !important;
    height: auto !important;
    min-height: 3.5rem !important;
    padding: 12px 18px !important;
    text-align: left !important;
    font-size: 1.05rem !important;
    line-height: 1.5 !important;
    display: flex !important;
    align-items: center !important;
    margin-bottom: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# 1. 직무 프로필 정의 (가중치 벡터: O, I, S, N, T, F, J, P)
JOB_PROFILES = {
    "해외영업 (Overseas Sales)": {
        "weights": {"O": 3, "I": 0, "S": 1, "N": 3, "T": 2, "F": 1, "J": 1, "P": 3},
        "desc": "새로운 글로벌 시장을 개척하고, 바이어와의 치열한 네고와 프레젠테이션을 주도하는 비즈니스 프론티어입니다.",
        "skills": ["글로벌 비즈니스 회화", "가격 협상 및 계약", "시장 조사", "해외 전시회 참가"]
    },
    "포워딩 오퍼레이션 (Forwarding Ops)": {
        "weights": {"O": 2, "I": 2, "S": 3, "N": 1, "T": 3, "F": 0, "J": 1, "P": 3},
        "desc": "항공·해상 운송 스케줄을 조율하고, 결항이나 선적 딜레이 등 돌발 변수를 신속하게 해결하는 물류 해결사입니다.",
        "skills": ["선사/항공사 부킹", "운임(Freight) 네고", "스케줄 트래킹", "트러블슈팅"]
    },
    "무역사무 및 영업관리 (Trade Admin)": {
        "weights": {"O": 0, "I": 3, "S": 3, "N": 0, "T": 1, "F": 3, "J": 3, "P": 0},
        "desc": "수출입 선적 서류(B/L, C/I, P/L, L/C)와 정산을 오차 없이 완벽하게 처리하며 고객사와의 신뢰를 지키는 살림꾼입니다.",
        "skills": ["선적 서류 작성", "ERP/수발주 시스템 관리", "바이어 CS", "수출입 대금 정산"]
    },
    "글로벌 SCM 및 물류기획 (Global SCM)": {
        "weights": {"O": 1, "I": 3, "S": 2, "N": 3, "T": 3, "F": 0, "J": 3, "P": 1},
        "desc": "데이터를 기반으로 전체 공급망 구조를 최적화하고, 물류비 절감 및 재고 회전율을 극대화하는 전략가입니다.",
        "skills": ["공급망 데이터 분석", "재고 관리", "물류 네트워크 설계", "원가 절감 기획"]
    },
    "해외 소싱 및 구매 (Global Procurement)": {
        "weights": {"O": 2, "I": 2, "S": 2, "N": 2, "T": 3, "F": 0, "J": 3, "P": 1},
        "desc": "글로벌 공급업체를 발굴·평가하고 단가 및 납기를 빈틈없이 협상하여 원가 경쟁력을 확보하는 구매 전문가입니다.",
        "skills": ["공급업체 평가 및 실사", "단가 네고", "품질 및 납기 관리", "원가 분석"]
    },
    "관세 및 통관 컴플라이언스 (Customs)": {
        "weights": {"O": 0, "I": 3, "S": 3, "N": 0, "T": 3, "F": 0, "J": 3, "P": 0},
        "desc": "HS Code 분류, FTA 원산지 증명서 발급, 수출입 통관 법규 준수를 통해 법적·세무적 리스크를 차단하는 규정 수호자입니다.",
        "skills": ["HS Code 분류", "FTA 원산지 판정", "관세 환급", "무역 법규 및 외환 검토"]
    }
}

# 2. 12개 질문 데이터
QUESTIONS = [
    {"q": "Q1. 업무 환경으로 더 선호하는 스타일은?", "dim_a": "O", "a": "새로운 해외 바이어나 공급사를 만나 직접 설득하고 협상하는 일", "dim_b": "I", "b": "사무실에서 수출입 시스템과 서류를 꼼꼼하게 검토하고 정리하는 일"},
    {"q": "Q2. 파트너사와의 문제가 발생했을 때 나의 방식은?", "dim_a": "O", "a": "즉시 유선 통화나 미팅으로 직접 부딪치며 조율한다", "dim_b": "I", "b": "계약서와 관련 규정을 먼저 꼼꼼히 확인한 후 서면으로 소통한다"},
    {"q": "Q3. 직무 성취감을 크게 느끼는 순간은?", "dim_a": "O", "a": "치열한 밀당 끝에 대형 계약/네고를 성공시켰을 때", "dim_b": "I", "b": "수많은 선적 서류와 데이터 사이에 오차 없이 완벽히 끝났을 때"},
    {"q": "Q4. 프로젝트를 시작할 때 먼저 주목하는 것은?", "dim_a": "S", "a": "정해진 규정, 품목 분류(HS Code), 명확한 수치 데이터", "dim_b": "N", "b": "글로벌 시장 트렌드, 새로운 물류 루트, 장기적 전략 방향"},
    {"q": "Q5. 복잡한 문제를 해결할 때 나의 무기는?", "dim_a": "S", "a": "표준 매뉴얼과 축적된 과거 데이터를 바탕으로 한 빈틈없는 분석", "dim_b": "N", "b": "기존 틀에서 벗어난 새로운 대안과 유연한 솔루션 탐색"},
    {"q": "Q6. 더 흥미롭게 느껴지는 업무는?", "dim_a": "S", "a": "원산지 규정 및 서류를 완벽히 검증해 리스크를 제로화하는 작업", "dim_b": "N", "b": "새로운 물류 거점을 발굴해 전체 공급망 구조를 개선하는 작업"},
    {"q": "Q7. 협상 테이블에서 가장 중요한 기준은?", "dim_a": "T", "a": "단 1센트라도 더 확보하는 명확한 수치적·비용적 이익", "dim_b": "F", "b": "장기적인 파트너십 유지를 위한 상호 윈-윈과 신뢰 형성"},
    {"q": "Q8. 협력사 담당자가 실수를 저질렀을 때?", "dim_a": "T", "a": "손실액과 원인을 명확히 짚고 계약상 절차에 따라 재발을 방지한다", "dim_b": "F", "b": "상대방의 입장을 먼저 이해하고 원만한 관계를 유지하며 수습을 돕는다"},
    {"q": "Q9. 공급사를 선정할 때 더 끌리는 조건은?", "dim_a": "T", "a": "단가, 납기 준수율 등 객관적으로 수치화된 지표", "dim_b": "F", "b": "지속적인 협력 가능성과 유연하고 적극적인 커뮤니케이션 태도"},
    {"q": "Q10. 선적 및 일정 관리를 할 때 나의 스타일은?", "dim_a": "J", "a": "마감일(Closing time) 며칠 전부터 타임라인을 단계별로 확정해둔다", "dim_b": "P", "b": "유동적인 스케줄 변동에 맞춰 그때그때 기민하게 조율한다"},
    {"q": "Q11. 선박 딜레이나 결항 등 돌발 상황이 발생했을 때?", "dim_a": "J", "a": "사전에 준비해둔 비상 대응 매뉴얼(Plan B)에 따라 체계적으로 처리한다", "dim_b": "P", "b": "당장 이용 가능한 대체 선편/항공편을 수소문해 즉각적으로 밀어붙인다"},
    {"q": "Q12. 나의 일상적인 업무 루틴은?", "dim_a": "J", "a": "To-Do 리스트를 우선순위별로 정렬하고 체크해가며 끝낸다", "dim_b": "P", "b": "수시로 쏟아지는 긴급 요청과 이슈를 빠르게 쳐내는 멀티태스킹에 강하다"}
]

# 3. Session State 초기화
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# 화면 1. 인트로 화면
if st.session_state.step == 0:
    st.title("🚢 무역 직무 MBTI 진단 테스트")
    st.write("12가지 문항을 통해 아래의 직무들 중 당신에게 가장 잘 맞는 무역·물류 직무를 추천해 드립니다.")
    st.divider()

    st.subheader("📋 추천 대상 직무")
    for job_title in JOB_PROFILES.keys():
        st.markdown(f"- **{job_title}**")

    st.write("")
    if st.button("🚀 테스트 시작하기", use_container_width=True):
        st.session_state.step = 1
        st.session_state.answers = []
        st.rerun()

# 화면 2 ~ 13. 질문 화면 (세로 배치 + 자동 줄바꿈)
elif 1 <= st.session_state.step <= len(QUESTIONS):
    q_idx = st.session_state.step - 1
    current_q = QUESTIONS[q_idx]

    # 상단 진행률 프로그레스 바
    progress = q_idx / len(QUESTIONS)
    st.progress(progress, text=f"진행 상황 ({st.session_state.step} / {len(QUESTIONS)})")
    st.write("")

    st.subheader(current_q["q"])
    st.write("")

    # 선택지 버튼을 위아래(세로)로 배치하여 모바일 및 작은 화면에서도 문장이 잘리지 않음
    if st.button(f"🅰️ {current_q['a']}", key=f"btn_a_{q_idx}", use_container_width=True):
        st.session_state.answers.append(current_q["dim_a"])
        st.session_state.step += 1
        st.rerun()

    if st.button(f"🅱️ {current_q['b']}", key=f"btn_b_{q_idx}", use_container_width=True):
        st.session_state.answers.append(current_q["dim_b"])
        st.session_state.step += 1
        st.rerun()

# 화면 14. 결과 화면
elif st.session_state.step > len(QUESTIONS):
    user_scores = {"O": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}
    for dim in st.session_state.answers:
        user_scores[dim] += 1

    job_rankings = []
    for job, data in JOB_PROFILES.items():
        score = sum(user_scores[dim] * weight for dim, weight in data["weights"].items())
        job_rankings.append((job, score, data["desc"], data["skills"]))

    job_rankings.sort(key=lambda x: x[1], reverse=True)
    top_job = job_rankings[0]

    st.balloons()
    st.header(f"🎯 당신에게 가장 적합한 직무는 **[{top_job[0]}]** 입니다!")
    st.info(top_job[2])

    st.subheader("💡 추천 역량 및 핵심 업무")
    for skill in top_job[3]:
        st.markdown(f"- {skill}")

    st.divider()
    st.subheader("📊 차순위 적합 직무")
    for job, score, desc, _ in job_rankings[1:3]:
        st.markdown(f"**{job}** (적합도 점수: {score}점)")
        st.caption(desc)

    st.write("")
    if st.button("🔄 다시 테스트하기", use_container_width=True):
        st.session_state.step = 0
        st.session_state.answers = []
        st.rerun()