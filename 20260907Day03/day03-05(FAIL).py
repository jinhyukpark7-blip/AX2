# 인코딩 자동 감지 + 한글 폰트 막대그래프
# 여러 인코딩("utf-8-sig", "cp949", "euc-kr") 순서대로 시도
# 내가 쓸 폰트 같은 경로에 있어야 함
# 객실 등급별 생존율 막대그래프 생성 후 그림으로 저장  chart.png
# 실행 streamlit run day03-05.py

import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib import font_manager


st.title("📊인코딩 자동 감지 + 한글 폰트 막대그래프 (Titanic 연습)")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실등급별 생존율을 그래프로 그립니다.")

CSV_PATH = os.path.join(os.path.dirname(__file__), "titanic_cleaned.csv")
FONT_PATH=os.path.join(os.path.dirname(__file__), "SeochoBatang-Regular.ttf")

import pandas as pd

def load_csv_with_encodings(file_path: str) -> pd.DataFrame:
    """
    utf-8-sig -> cp949 -> euc-kr 순서로 인코딩을 시도하여 CSV 파일을 불러오는 함수
    """
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            print(f"성공: '{enc}' 인코딩으로 파일을 정상적으로 불러왔습니다.")
            return df
        except UnicodeDecodeError:
            print(f"실패: '{enc}' 인코딩 디코딩 오류. 다음 인코딩을 시도합니다.")
        except Exception as e:
            # 인코딩 외의 에러(파일 경로 없음 등)가 발생한 경우 출력 후 중단
            print(f"오류 발생 ({enc}): {e}")
            raise e
            
    raise UnicodeDecodeError(f"모든 인코딩({', '.join(encodings)})으로 파일을 읽을 수 없습니다.")

# 사용 예시
if __name__ == "__main__":
    file_path = "titanic_cleaned.csv"  # 불러올 파일 경로
    
    df = load_csv_with_encodings(file_path)
    print(df.head())

    # 인코딩 자동 감지로 Csv 읽기
    st.subheader("1) 인코딩 자동 감지")

    df = load_csv_with_encodings(CSV_PATH)

    st.markdown("---")
    # 객실등급(Pclass) 별 생존율 집계
    # Survived 사망0 / 생존1 등급별 평균을 내면
    # 그대로가 등급의 생존 비율이 된다
    # 10명 남3 여자7
    # 1000 생존300 300/1000 30%


    # 아래 실패 코드 바로 밑으로 수정
    # pclass_survival_rate = df.groupby("Pclass")["Survived"].mean().sort_index()
    # st.dataframe(pclass_survival_rate * 100 ).round(1).rename("생존율(%)")
    # df_df = st.dataframe(pclass_survival_rate * 100 ).round(1).rename("생존율(%)")
    # st.write(df_df)

    # 1. 먼저 판다스로 계산, 반올림, 이름 변경을 완료합니다.
    pclass_survival_rate = (df.groupby("Pclass")["Survived"].mean().sort_index() * 100).round(1).rename("생존율(%)")

    # 2. 완성된 표를 화면에 출력합니다.
    st.dataframe(pclass_survival_rate)


    st.markdown("---")
    st.subheader("3) 객실등급별 생존율 막대그래프")
    try:

        # 폰트 파일이 없으면 FileNotFoundError 가 발생
        font_prop = font_manager.FontProperties(fname=FONT_PATH)
        # matplotlib font_manager에 폰트를 등록하고, 전역 폰트로 설정
        font_manager.fontManager.addfont(FONT_PATH)
        plt.rcParams["font.family"]= font_prop.get_name()
        st.write("NanumGothicEco 폰트를 적용했습니다")
    except FileNotFoundError:
        st.warning("폰트파일을 찾을수가 없습니다")


    fig, ax = plt.subplots(figsize=(8,5))
    (pclass_survival_rate * 100 ).plot(kind="bar", color="blue")
    ax.set_title("객실 등급별 생존율", fontproperties=font_prop, fontsize=14)
    ax.set_xlabel("객실등급(Pclass)", fontproperties=font_prop, fontsize=11)
    ax.set_ylabel("생존율(%)", fontproperties=font_prop, fontsize=11)

    st.pyplot(fig)

    output_png = os.path.join(os.path.dirname(__file__),"chart.png")
    fig.savefig(output_png)

    