# OpenAI + streamlit 앱
# 질문 하나 입력하면 OpenAI chat    Completions API 한번 호출
# 답변을 받아오는 가장 단순한 방법
# 대화 기록을 기억하지 않는 단발성 질문-답변
# streamlit run day05-2.py

import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="OpenAI + Streamlit", page_icon="🤖")

st.title("예제1 ) 나의 첫번째 챗봇")

st.caption("질문 하나 입력하면 OpenAI chat Completions API 한번 호출, 답변을 받아오는 가장 단순한 방법")

# ----------------------- 사이드바 API 모델 ------------------------

with st.sidebar:
        st.header("설정")
        api_key = st.text_input("OpenAI API Key", type="password", help="sk-로 시작하는 OpenAI API Key를 입력하세요.")
        model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o", "gpt-4.1 mini"])
        st.markdown("[api 발급 받기](https://platform.openai.com/api-keys)")



# ----------------- 메인 화면 --------------------------

# question = st.text_input("질문을 입력하세요", placeholder="예) 오늘 날씨가 어떤가요?")


# if st.button("질문하기"):
#         if not api_key:
#             st.error("OpenAI API Key를 입력하세요.")
#         elif not question:
#             st.error("질문을 입력하세요.")
#         else:
#               client = OpenAI(api_key=api_key)
#               답변을 생각하는 중...
#               주인님으로 시작하는 친절한 답변가

#               사용한 토큰 수 표시(비용감을 잡는 데 유용하게
#                       입력토큰, 출력토큰, 총토큰수)
#               오류가 있으면 있다고 메시지 출력

#               response = client.chat.completions.create(
                    
#               )


# ----------------- 메인 화면 --------------------------

question = st.text_input(
    "질문을 입력하세요", placeholder="예) 오늘 날씨가 어떤가요?"
)

if st.button("질문하기"):
    if not api_key:
        st.error("OpenAI API Key를 입력하세요.")
    elif not question:
        st.error("질문을 입력하세요.")
    else:
        try:
            client = OpenAI(api_key=api_key)

            # 로딩 스피너 표시
            with st.spinner("답변을 생각하는 중..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 사용자에게 항상 '주인님'으로 시작하며 친절하고 공손하게 대답하는 비서입니다.",
                        },
                        {"role": "user", "content": question},
                    ],
                )

            # 답변 출력
            answer = response.choices[0].message.content
            st.markdown("### 💬 답변")
            st.write(answer)

            # 토큰 사용량 표시 (입력 토큰, 출력 토큰, 총 토큰 수)
            usage = response.usage
            st.divider()
            st.caption("📊 **토큰 사용량 (비용 참고용)**")
            col1, col2, col3 = st.columns(3)
            col1.metric("입력 토큰 (Prompt)", f"{usage.prompt_tokens:,}개")
            col2.metric(
                "출력 토큰 (Completion)",
                f"{usage.completion_tokens:,}개",
            )
            col3.metric("총 사용 토큰", f"{usage.total_tokens:,}개")

        except Exception as e:
            # 오류 발생 시 에러 메시지 출력
            st.error(f"오류가 발생했습니다: {e}")