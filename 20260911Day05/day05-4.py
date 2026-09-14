# 좌측 사이드바
# -OpenAI API Key는 그대로
# -모델 선택도 그대로
# -요약 옵션(택 1)
# * 짧게 (3줄)
# * 보통 (5~7줄)
# * 자세히(bullet point)
# -요약 스타일
# * 일반
# * 기타 (격식체, 어린이용 등 선택/입력)

# 본 페이지
# 제목: 예제 3) 파일 업로드 문서 요약 앱
# 텍스트 파일을 업로드하면 OpenAI API가 원하는 스타일로 요약해줍니다
# 요약할 텍스트 파일을 업로드하세요
# (txt 파일 업로드하는 항목)
# 업로드한 문서 미리보기
# 원문(앞부분)
# 요약하기 버튼 (Primary 강조형 버튼)

from openai import OpenAI
import streamlit as st

st.set_page_config(page_title="문서 요약 앱", page_icon="📄")

# ----------------------- 사이드바 설정 ------------------------
with st.sidebar:
    st.header("설정")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="sk-로 시작하는 OpenAI API Key를 입력하세요.",
    )
    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o"])

    st.divider()

    # 요약 길이 옵션 선택
    length_option = st.radio(
        "요약 옵션",
        ["짧게 (3줄)", "보통 (5~7줄)", "자세히 (bullet point)"],
        index=1,
    )

    # 요약 스타일 선택
    style_option = st.selectbox(
        "요약 스타일", ["일반", "격식체 (보고서형)", "친근한 설명체", "어린이용 (쉽게 설명)"]
    )

    st.markdown("[API 키 발급 받기](https://platform.openai.com/api-keys)")

# ----------------------- 메인 화면 ------------------------
st.title("예제 3) 파일 업로드 문서 요약 앱")
st.caption("텍스트 파일을 업로드하면 OpenAI API가 원하는 스타일로 요약해줍니다.")

# 텍스트 파일 업로더
uploaded_file = st.file_uploader(
    "요약할 텍스트 파일을 업로드하세요", type=["txt"]
)

if uploaded_file is not None:
    # 텍스트 파일 읽기 (UTF-8 인코딩)
    try:
        raw_text = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        raw_text = uploaded_file.read().decode("cp949", errors="ignore")

    # 업로드한 문서 미리보기
    st.markdown("### 📄 업로드한 문서 미리보기")
    with st.expander("원문 (앞부분 500자 미리보기)", expanded=True):
        st.write(raw_text[:500] + ("..." if len(raw_text) > 500 else ""))

    # 요약하기 버튼 (Streamlit의 type="primary"는 테마 강조 색상(빨간색 계열)으로 렌더링됩니다)
    if st.button("🚀 요약하기", type="primary"):
        if not api_key:
            st.error("좌측 사이드바에 OpenAI API Key를 먼저 입력해주세요.")
        elif not raw_text.strip():
            st.error("업로드된 파일 내용이 비어 있습니다.")
        else:
            system_instruction = (
                f"당신은 전문 요약 비서입니다. "
                f"요약 길이는 '{length_option}'에 맞추고, "
                f"요약 스타일은 '{style_option}'으로 작성하세요."
            )

            prompt = f"다음 문서를 요청된 규칙에 맞게 요약해주세요:\n\n{raw_text}"

            st.markdown("### 📝 요약 결과")
            with st.chat_message("assistant"):
                try:
                    client = OpenAI(api_key=api_key)
                    response_stream = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt},
                        ],
                        stream=True,
                    )
                    st.write_stream(response_stream)
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")