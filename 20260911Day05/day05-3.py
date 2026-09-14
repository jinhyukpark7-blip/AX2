# 대화 기록을 기억하는 멀티턴 챗봇 (스트리밍 응답)
# st.session_state에 대화 기록을 저장해서, 이전 대화 맥락을 기억하는 챗봇
# st.chat_message / st.chat_input 같은 Streamlit의 채팅 전용 위젯을 사용합니다.
# stream=True 옵션으로 답변이 실시간으로 타이핑되듯 출력됩니다.
# streamlit run day05-3.py

# 시스템 메시지를 사용자가 설정 하도록
# 대화 기록 초기화 버튼

from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="멀티턴 챗봇", page_icon="🤖")

st.title("🤖 멀티턴 AI 챗봇")
st.caption(
    "이전 대화 맥락을 기억하며 실시간 스트리밍으로 답변하는 챗봇입니다."
)

# ----------------------- 사이드바 설정 ------------------------
with st.sidebar:
    st.header("설정")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="sk-로 시작하는 OpenAI API Key를 입력하세요.",
    )
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o"])

    # 사용자가 직접 지정하는 시스템 프롬프트 설정
    system_prompt = st.text_area(
        "시스템 메시지 (역할 부여)",
        value="당신은 친절하고 명확하게 답변해 주는 AI 비서입니다.",
        help="챗봇의 성격이나 역할을 지정하세요.",
    )

    st.markdown("[API 키 발급 받기](https://platform.openai.com/api-keys)")
    st.divider()

    # 대화 기록 초기화 버튼
    if st.button("🗑️ 대화 기록 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------- 세션 상태(대화 기록) 초기화 -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------- 기존 대화 기록 화면 출력 --------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------- 채팅 입력 및 응답 생성 ----------------------
prompt = st.chat_input("메시지를 입력하세요...")

if prompt:
    if not api_key:
        st.error("사이드바에 OpenAI API Key를 먼저 입력해주세요.")
    else:
        # 1. 사용자 질문을 세션 상태에 추가 및 화면 출력
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. 모델에 보낼 메시지 구성 (시스템 메시지 + 이전 대화 기록 전체)
        messages_to_send = [{"role": "system", "content": system_prompt}] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # 3. AI 답변 스트리밍 생성 및 화면 출력
        with st.chat_message("assistant"):
            try:
                client = OpenAI(api_key=api_key)
                response_stream = client.chat.completions.create(
                    model=model, messages=messages_to_send, stream=True
                )
                # st.write_stream을 사용하여 스트리밍 데이터를 실시간 렌더링
                full_response = st.write_stream(response_stream)

                # 4. 생성된 완성 답변을 대화 기록에 저장
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")