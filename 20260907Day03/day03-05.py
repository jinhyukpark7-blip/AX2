import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib import font_manager, rc

# 1. 파일 경로 설정
BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "titanic_cleaned.csv")
FONT_PATH = os.path.join(BASE_DIR, "SeochoBatang-Regular.ttf")

# 2. 한글 폰트 설정
if os.path.exists(FONT_PATH):
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    rc('font', family=font_prop.get_name())
    plt.rcParams['axes.unicode_minus'] = False
else:
    st.warning("⚠️ 지정한 폰트 파일을 찾을 수 없습니다.")

st.title("📊 인코딩 자동 감지 + 한글 폰트 막대그래프 (Titanic 연습)")
st.caption("여러 인코딩을 순서대로 시도해서 파일을 읽고, 객실등급별 생존율을 그래프로 그립니다.")

# 3. 인코딩 순차 시도 함수 정의
def load_csv_with_encodings(file_path: str) -> pd.DataFrame:
    encodings = ["utf-8-sig", "cp949", "euc-kr"]
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"파일을 읽는 도중 에러가 발생했습니다: {e}")
            return None
    st.error("모든 인코딩으로 파일을 읽을 수 없습니다.")
    return None

# 4. 데이터 로드
st.subheader("1) 인코딩 자동 감지")
df = load_csv_with_encodings(CSV_PATH)

if df is not None:
    st.success("데이터를 정상적으로 불러왔습니다!")
    st.dataframe(df.head())

    st.markdown("---")
    st.subheader("2) 객실등급(Pclass) 별 생존율 집계")

    # 객실등급별 생존율 계산 (%)
    pclass_survival_rate = (df.groupby("Pclass")["Survived"].mean() * 100).round(1).rename("생존율(%)")
    
    # 표 출력
    st.dataframe(pclass_survival_rate)

    # 5. 막대그래프 생성 및 저장
    st.subheader("3) 객실등급별 생존율 막대그래프")
    
    fig, ax = plt.subplots(figsize=(6, 4))
    x_labels = [f"{idx}등급" for idx in pclass_survival_rate.index]
    ax.bar(x_labels, pclass_survival_rate.values, color="skyblue", edgecolor="black")
    
    ax.set_title("객실 등급별 생존율", fontsize=14)
    ax.set_xlabel("객실 등급", fontsize=11)
    ax.set_ylabel("생존율 (%)", fontsize=11)
    ax.set_ylim(0, 100)

    # chart.png로 이미지 저장
    chart_save_path = os.path.join(BASE_DIR, "chart.png")
    fig.savefig(chart_save_path, dpi=300, bbox_inches="tight")

    # 화면에 그래프 출력
    st.pyplot(fig)
    st.caption("차트가 `chart.png`로 저장되었습니다.")