import os
import webbrowser
import folium

places = [
    {"name": "서울시청", "lat": 37.5665, "lon": 126.9780},
    {"name": "경복궁", "lat": 37.5796, "lon": 126.9770},
    {"name": "남산서울타워", "lat": 37.5512, "lon": 126.9882},
    {"name": "강남역", "lat": 37.4979, "lon": 127.0276},
]

seoul_center = [37.5665, 126.9780]

# API 키 없이 사용 가능한 VWorld 한국 타일맵 적용
m = folium.Map(
    location=seoul_center,
    zoom_start=12,
    tiles="https://xdworld.vworld.kr/2d/Base/service/{z}/{x}/{y}.png",
    attr="VWorld",
)

for place in places:
    folium.Marker(
        location=[place["lat"], place["lon"]],
        popup=folium.Popup(place["name"], max_width=200),
        tooltip=place["name"],
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

html_file = "basic_map.html"
m.save(html_file)

file_path = os.path.abspath(html_file)
webbrowser.open(f"file://{file_path}")