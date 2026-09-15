from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# 글로벌 Overpass 미러 서버 목록 (차단/장애 시 순차 전환)
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/facilities", methods=["POST"])
def get_facilities():
    """브라우저 대신 Flask 서버가 미러 서버를 순차 호출하여 429 차단을 우회하는 프록시 엔드포인트"""
    data = request.get_json() or {}
    lat = data.get("lat")
    lng = data.get("lng")

    if not lat or not lng:
        return jsonify({"elements": [], "error": "Invalid coordinates"}), 400

    # 경량화되고 최적화된 QL 쿼리
    query = f"""
    [out:json][timeout:15];
    (
      node["railway"="station"](around:1500,{lat},{lng});
      way["railway"="station"](around:1500,{lat},{lng});
      node["station"="subway"](around:1500,{lat},{lng});
      way["station"="subway"](around:1500,{lat},{lng});

      node["highway"="bus_stop"](around:1500,{lat},{lng});
      node["public_transport"="platform"](around:1500,{lat},{lng});

      node["shop"="convenience"](around:1200,{lat},{lng});
      way["shop"="convenience"](around:1200,{lat},{lng});

      node["amenity"="parcel_locker"](around:1500,{lat},{lng});
      node["amenity"="locker"](around:1500,{lat},{lng});

      node["amenity"~"restaurant|fast_food|cafe|pub|bar"](around:1000,{lat},{lng});
      way["amenity"~"restaurant|fast_food|cafe|pub|bar"](around:1000,{lat},{lng});
    );
    out center 120;
    """

    # 여러 미러 서버 중 응답하는 곳을 찾아 호출
    headers = {
        "User-Agent": "FlaskNearbyHub/1.0 (Educational Project; Python/requests)"
    }

    for server_url in OVERPASS_SERVERS:
        try:
            response = requests.post(server_url, data=query.encode("utf-8"), headers=headers, timeout=8)
            if response.status_code == 200:
                return jsonify(response.json())
        except Exception:
            continue  # 다음 미러 서버로 자동 전환

    # 모든 서버 실패 시 빈 결과 반환
    return jsonify({"elements": []})

if __name__ == "__main__":
    app.run(debug=True, port=5000)