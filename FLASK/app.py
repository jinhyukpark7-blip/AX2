# """
# Flask 기초 인증키 없는 무료  API
# https://api.adviceslip.com/advice (인증키 없고, 무료)

# FLASL
#     - app.py  - 메뉴버튼 생성
#     - templates/
#         - index.html
#     - static/
#         - style.css


# """

from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route("/")
def home():
    url = "https://api.adviceslip.com/advice"
    advice_text = "명언을 불러오지 못했습니다."
    advice_id = None

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # API 응답 구조: {"slip": {"id": 123, "advice": "Quote text"}}
            advice_text = data["slip"]["advice"]
            advice_id = data["slip"]["id"]
    except Exception as e:
        print(f"Error: {e}")

    return render_template("index.html", advice=advice_text, advice_id=advice_id)


if __name__ == "__main__":
    app.run(debug=True, port=5000)