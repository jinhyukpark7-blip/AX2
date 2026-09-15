import streamlit as st
import streamlit.components.v1 as components
import requests
import json

st.set_page_config(
    page_title="스마트 생활권 & 경유 대중교통 길잡이",
    page_icon="📍",
    layout="wide"
)

# 기존에 완성한 HTML + CSS + JS 통합 코드
HTML_CODE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>스마트 생활권 & 경유 대중교통 길잡이</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif; color: #1e293b; padding: 12px; }
        .dashboard-container { max-width: 1400px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }
        .top-section { display: flex; gap: 16px; min-height: 380px; }
        .map-card { flex: 0 0 42%; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; position: relative; display: flex; flex-direction: column; }
        .map-header { padding: 10px 14px; background: #ffffff; display: flex; gap: 8px; border-bottom: 1px solid #e2e8f0; z-index: 10; }
        .search-box { flex: 1; }
        .search-box form { display: flex; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; }
        .search-box input { flex: 1; border: none; background: transparent; padding: 8px 12px; font-size: 0.88rem; outline: none; }
        .search-box button { background: #4f46e5; color: white; border: none; padding: 0 14px; font-size: 0.85rem; font-weight: 600; cursor: pointer; }
        .lock-btn { display: flex; align-items: center; gap: 4px; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 0 12px; font-size: 0.85rem; font-weight: 700; cursor: pointer; }
        .lock-btn.locked { background: #ef4444; color: white; border-color: #dc2626; }
        .map-top-notice-bar { background: #f8fafc; color: #475569; font-size: 0.8rem; padding: 7px 12px; border-bottom: 1px solid #e2e8f0; line-height: 1.35; transition: all 0.3s ease; }
        .map-top-notice-bar.locked { background: #fef2f2; color: #b91c1c; border-bottom-color: #fecaca; }
        #map { flex: 1; width: 100%; min-height: 270px; }
        .facility-summary-card { flex: 1; background: #ffffff; border-radius: 16px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; display: flex; flex-direction: column; }
        .section-title-box { display: flex; justify-content: space-between; align-items: center; }
        .section-title-box h3 { font-size: 1.15rem; color: #0f172a; }
        .status-tag { font-size: 0.75rem; padding: 3px 8px; border-radius: 6px; font-weight: 700; }
        .status-tag.unlocked { background: #dbeafe; color: #1e40af; }
        .status-tag.locked { background: #fee2e2; color: #991b1b; }
        .picked-name { font-size: 0.9rem; color: #64748b; margin: 4px 0 16px 0; }
        .facility-mini-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; flex: 1; }
        .mini-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px; display: flex; flex-direction: column; justify-content: space-between; }
        .mini-card .icon { font-size: 1.3rem; }
        .mini-card .info strong { display: block; font-size: 0.78rem; color: #6366f1; margin-top: 4px; }
        .mini-card .info .name { font-size: 0.85rem; font-weight: 600; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .mini-nav { display: block; text-align: center; background: #e0e7ff; color: #3730a3; text-decoration: none; font-size: 0.75rem; font-weight: 600; padding: 4px; border-radius: 4px; margin-top: 6px; }
        .mini-nav.disabled { background: #f1f5f9; color: #94a3b8; pointer-events: none; }
        .food-convenience-section { background: #ffffff; border-radius: 16px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }
        .food-tabs-header { display: flex; gap: 8px; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; }
        .tab-menu { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px 16px; font-size: 0.9rem; font-weight: 700; color: #475569; cursor: pointer; transition: all 0.2s; }
        .tab-menu.active { background: #4f46e5; color: #ffffff; border-color: #4338ca; }
        .food-tab-content { margin-top: 16px; }
        .tab-desc { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .tab-desc h4 { font-size: 0.95rem; color: #334155; }
        .count-badge { background: #eef2ff; color: #4f46e5; font-size: 0.8rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; }
        .meal-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; max-height: 280px; overflow-y: auto; padding-right: 4px; }
        .food-item-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; }
        .food-item-card .title-row { display: flex; justify-content: space-between; align-items: flex-start; }
        .food-item-card h5 { font-size: 0.9rem; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px; }
        .food-type-tag { font-size: 0.72rem; background: #e2e8f0; color: #475569; padding: 2px 6px; border-radius: 4px; }
        .food-item-card .dist-text { font-size: 0.8rem; color: #64748b; margin: 6px 0; }
        .food-actions { display: flex; gap: 6px; }
        .food-actions a { flex: 1; text-align: center; font-size: 0.75rem; padding: 5px; border-radius: 6px; text-decoration: none; font-weight: 600; }
        .btn-route { background: #e0e7ff; color: #3730a3; }
        .btn-review { background: #f1f5f9; color: #475569; }
        .roulette-layout { display: flex; gap: 30px; align-items: center; justify-content: center; padding: 10px 0; }
        .roulette-box { position: relative; display: flex; flex-direction: column; align-items: center; }
        .roulette-pointer { position: absolute; top: -12px; font-size: 1.5rem; color: #ef4444; z-index: 10; }
        #roulette-canvas { border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.15); background: #ffffff; }
        .spin-btn { margin-top: 14px; background: #4f46e5; color: #fff; border: none; padding: 10px 24px; border-radius: 24px; font-size: 1rem; font-weight: 700; cursor: pointer; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }
        .spin-btn:disabled { background: #cbd5e1; cursor: not-allowed; }
        .roulette-result-box { flex: 1; max-width: 320px; background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 20px; text-align: center; }
        .roulette-result-box h3 { font-size: 1.05rem; color: #334155; margin-bottom: 12px; }
        .winner-card { min-height: 90px; display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .winner-name { font-size: 1.25rem; font-weight: 800; color: #4f46e5; margin-bottom: 6px; }
        .cvs-util-banner { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .cvs-util-banner p { font-size: 0.85rem; color: #475569; }
        .cvs-quick-links { display: flex; gap: 8px; }
        .cvs-badge { text-decoration: none; font-size: 0.78rem; font-weight: 700; padding: 5px 10px; border-radius: 6px; }
        .cvs-badge.cu { background: #dcfce7; color: #166534; }
        .cvs-badge.gs { background: #dbeafe; color: #1e40af; }
        .cvs-badge.seven { background: #fee2e2; color: #991b1b; }
        .bottom-transit-section { background: #ffffff; border-radius: 16px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0; }
        .transit-banner h2 { font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .badge-transit { background: #eef2ff; color: #4f46e5; font-size: 0.85rem; padding: 3px 10px; border-radius: 20px; }
        .transit-banner p { color: #64748b; font-size: 0.88rem; margin-top: 4px; margin-bottom: 20px; }
        .transit-form-container { background: #f8fafc; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; }
        .route-inputs { display: flex; align-items: center; gap: 12px; }
        .input-group { flex: 1; display: flex; flex-direction: column; gap: 6px; }
        .input-group label { font-size: 0.82rem; font-weight: 700; color: #475569; }
        .input-group input { padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; outline: none; }
        .input-arrow { font-size: 1.2rem; color: #94a3b8; margin-top: 20px; font-weight: bold; }
        .option-tabs { display: flex; gap: 16px; margin: 20px 0 14px 0; }
        .tab-radio { display: flex; align-items: center; gap: 8px; background: #ffffff; border: 1px solid #cbd5e1; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-size: 0.9rem; font-weight: 600; transition: all 0.2s; }
        .tab-radio input:checked + .tab-label { color: #4f46e5; }
        .cheapest-detail-box { background: #ffffff; border: 1px dashed #6366f1; border-radius: 8px; padding: 14px; margin-bottom: 16px; }
        .hidden { display: none !important; }
        .sub-info-row { display: flex; gap: 16px; margin-bottom: 8px; }
        .sub-input { flex: 1; display: flex; flex-direction: column; gap: 4px; }
        .sub-input label { font-size: 0.8rem; font-weight: 600; color: #334155; }
        .sub-input select, .sub-input input { padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.88rem; }
        .transfer-notice { font-size: 0.82rem; color: #4338ca; background: #eef2ff; padding: 8px 12px; border-radius: 6px; }
        .calc-btn { width: 100%; padding: 12px; background: #4f46e5; color: #ffffff; border: none; border-radius: 8px; font-size: 1rem; font-weight: 700; cursor: pointer; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25); transition: background 0.2s; }
        .calc-btn:hover { background: #4338ca; }
        .route-result-container { margin-top: 20px; }
        .result-card { background: #ffffff; border: 2px solid #e0e7ff; border-radius: 12px; padding: 20px; }
        .route-step-box { display: flex; flex-direction: column; gap: 16px; margin-top: 14px; }
        .step-item { background: #f8fafc; border-radius: 8px; padding: 14px; border-left: 4px solid #4f46e5; }
        .step-item.transfer-guide { border-left-color: #10b981; background: #f0fdf4; }
        .step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
        .step-header h4 { font-size: 0.95rem; color: #1e293b; }
        .step-link-btn { display: inline-block; padding: 6px 12px; background: #4f46e5; color: #fff; text-decoration: none; font-size: 0.8rem; border-radius: 6px; font-weight: 600; }
        @media (max-width: 960px) { .top-section { flex-direction: column; } .map-card { flex: auto; height: 320px; } .roulette-layout { flex-direction: column; } .route-inputs { flex-direction: column; } .input-arrow { transform: rotate(90deg); margin: 0; } }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <section class="top-section">
            <div class="map-card">
                <div class="map-header">
                    <div class="search-box">
                        <form id="search-form" onsubmit="searchLocation(event)">
                            <input type="text" id="search-keyword" placeholder="지하철역/동/건물명 검색" autocomplete="off">
                            <button type="submit">검색</button>
                        </form>
                    </div>
                    <button type="button" id="lock-btn" class="lock-btn" onclick="toggleLocationLock()">
                        <span id="lock-icon">🔓</span>
                        <span id="lock-text">고정</span>
                    </button>
                </div>
                <div class="map-top-notice-bar" id="map-top-notice">
                    ⏳ <b>안내:</b> 원하는 위치를 지정하고 <b>[고정]</b>을 누르세요. (위치 고정 후 검색까지 시간이 약간 걸릴 수 있습니다)
                </div>
                <div id="map"></div>
            </div>

            <div class="facility-summary-card">
                <div class="section-title-box">
                    <h3>📍 핀 위치 주변 주요 시설</h3>
                    <span id="status-tag" class="status-tag unlocked">수정 가능</span>
                </div>
                <p id="picked-location-name" class="picked-name">서울특별시청</p>

                <div class="facility-mini-grid">
                    <div class="mini-card" id="card-subway">
                        <span class="icon">🚇</span>
                        <div class="info"><strong>지하철역</strong><p class="name">-</p></div>
                        <a href="#" target="_blank" class="mini-nav disabled">길찾기</a>
                    </div>
                    <div class="mini-card" id="card-bus">
                        <span class="icon">🚏</span>
                        <div class="info"><strong>버스정류장</strong><p class="name">-</p></div>
                        <a href="#" target="_blank" class="mini-nav disabled">길찾기</a>
                    </div>
                    <div class="mini-card" id="card-cs">
                        <span class="icon">🏪</span>
                        <div class="info"><strong>편의점</strong><p class="name">-</p></div>
                        <a href="#" target="_blank" class="mini-nav disabled">길찾기</a>
                    </div>
                    <div class="mini-card" id="card-locker">
                        <span class="icon">📦</span>
                        <div class="info"><strong>무인택배함</strong><p class="name">-</p></div>
                        <a href="#" target="_blank" class="mini-nav disabled">길찾기</a>
                    </div>
                    <div class="mini-card" id="card-food-24">
                        <span class="icon">🍲</span>
                        <div class="info"><strong>24시 식당</strong><p class="name">-</p></div>
                        <a href="#" target="_blank" class="mini-nav disabled">길찾기</a>
                    </div>
                    <div class="mini-card" id="card-food">
                        <span class="icon">🍴</span>
                        <div class="info"><strong>일반 식당</strong><p class="name">-</p></div>
                        <a href="#" target="_blank" class="mini-nav disabled">길찾기</a>
                    </div>
                </div>
            </div>
        </section>

        <section class="food-convenience-section">
            <div class="food-tabs-header">
                <button class="tab-menu active" onclick="switchFoodTab('tab-meal')">🍴 오늘의 한끼 (도보 10분)</button>
                <button class="tab-menu" onclick="switchFoodTab('tab-roulette')">🎰 오늘은 뭐 먹지? (룰렛)</button>
                <button class="tab-menu" onclick="switchFoodTab('tab-cvs')">🏪 오늘의 편의점 & 재고찾기</button>
            </div>

            <div id="tab-meal" class="food-tab-content">
                <div class="tab-desc">
                    <h4>🚶‍♂️ 핀 기준 도보 10분(약 800m) 이내 식당 리스트</h4>
                    <span id="meal-count-badge" class="count-badge">0곳 발견</span>
                </div>
                <div id="meal-list-container" class="meal-grid">
                    <p class="empty-msg">주변 식당을 탐색 중입니다...</p>
                </div>
            </div>

            <div id="tab-roulette" class="food-tab-content hidden">
                <div class="roulette-layout">
                    <div class="roulette-box">
                        <div class="roulette-pointer">▼</div>
                        <canvas id="roulette-canvas" width="340" height="340"></canvas>
                        <button id="roulette-spin-btn" class="spin-btn" onclick="spinRoulette()">🎯 룰렛 돌리기!</button>
                    </div>
                    <div class="roulette-result-box">
                        <h3>🎉 오늘 추천된 식당</h3>
                        <div id="roulette-winner-card" class="winner-card">
                            <p class="winner-placeholder">룰렛 돌리기 버튼을 눌러보세요!</p>
                        </div>
                    </div>
                </div>
            </div>

            <div id="tab-cvs" class="food-tab-content hidden">
                <div class="cvs-util-banner">
                    <p>💡 <b>편의점 상품/재고 & 좌석 안내</b>: 브랜드별 공식 앱/웹을 통해 매장별 행사 및 재고를 확인해보세요.</p>
                    <div class="cvs-quick-links">
                        <a href="https://cu.bgfretail.com/store/list.do" target="_blank" class="cvs-badge cu">CU 매장/재고 ↗</a>
                        <a href="https://woodongs.page.link/find" target="_blank" class="cvs-badge gs">GS25 우리동네GS ↗</a>
                        <a href="https://www.7-eleven.co.kr/store/list.asp" target="_blank" class="cvs-badge seven">세븐일레븐 매장 ↗</a>
                    </div>
                </div>
                <div id="cvs-list-container" class="meal-grid">
                    <p class="empty-msg">주변 편의점을 탐색 중입니다...</p>
                </div>
            </div>
        </section>

        <section class="bottom-transit-section">
            <div class="transit-banner">
                <h2>🚌 어디에 들렸다가 약속 장소에 가셔야 하나요? 그럴 때는 여기! <span class="badge-transit">[대중교통 전용]</span></h2>
                <p>출발지에서 경유지를 거쳐 최종 목적지까지 가는 최적의 대중교통 경로와 환승할인 절약 공략법을 안내합니다.</p>
            </div>

            <div class="transit-form-container">
                <div class="route-inputs">
                    <div class="input-group">
                        <label>🚩 출발지 (A)</label>
                        <input type="text" id="route-start" placeholder="예: 강남역 2호선" value="강남역">
                    </div>
                    <div class="input-arrow">➔</div>
                    <div class="input-group">
                        <label>📍 경유지 (B)</label>
                        <input type="text" id="route-via" placeholder="예: 고속터미널 다이소" value="반포한강공원">
                    </div>
                    <div class="input-arrow">➔</div>
                    <div class="input-group">
                        <label>🎯 최종 목적지 (C)</label>
                        <input type="text" id="route-end" placeholder="예: 홍대입구역 9번출구" value="여의도 한강공원">
                    </div>
                </div>

                <div class="option-tabs">
                    <label class="tab-radio">
                        <input type="radio" name="route-option" value="fastest" checked onchange="toggleOptionView()">
                        <span class="tab-label">⚡ 옵션 1 : 최단시간 경로 (구간별 최적 연계)</span>
                    </label>
                    <label class="tab-radio">
                        <input type="radio" name="route-option" value="cheapest" onchange="toggleOptionView()">
                        <span class="tab-label">💰 옵션 2 : 최소 비용 (30분 환승할인 극대화)</span>
                    </label>
                </div>

                <div id="cheapest-detail-box" class="cheapest-detail-box hidden">
                    <div class="sub-info-row">
                        <div class="sub-input">
                            <label>🚌 A➔B 구간에 이용할(또는 타고 온) 교통수단:</label>
                            <select id="prev-transport-type">
                                <option value="subway">지하철</option>
                                <option value="blue-bus">간선(파랑) 버스</option>
                                <option value="green-bus">지선(초록) 버스</option>
                                <option value="town-bus">마을버스</option>
                            </select>
                        </div>
                        <div class="sub-input">
                            <label>노선 번호 / 호선 (선택):</label>
                            <input type="text" id="prev-transport-num" placeholder="예: 740번, 2호선">
                        </div>
                    </div>
                    <div class="transfer-notice">
                        💡 <b>수도권 환승할인 팁</b>: 경유지에서 하차 후 <b>30분 이내</b> 다른 번호의 버스나 지하철로 환승 시 기본요금(1,400~1,500원)이 면제됩니다.
                    </div>
                </div>

                <button class="calc-btn" onclick="calculateTransitRoute()">🚀 대중교통 경로 찾기</button>
            </div>

            <div id="route-result-container" class="route-result-container hidden">
                <div class="result-card" id="result-content"></div>
            </div>
        </section>
    </div>

    <script>
        let map, myPinMarker;
        let isLocationLocked = false;
        let resultMarkers = [];
        let nearbyRestaurants = [];
        let nearbyConveniences = [];
        let isSpinning = false;
        let currentRotation = 0;
        let fetchTimeout = null;

        const OVERPASS_SERVERS = [
            "https://overpass-api.de/api/interpreter",
            "https://lz4.overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter"
        ];

        const INITIAL_LAT = 37.5665;
        const INITIAL_LNG = 126.9780;

        document.addEventListener("DOMContentLoaded", () => {
            initMap();
        });

        function initMap() {
            map = L.map('map').setView([INITIAL_LAT, INITIAL_LNG], 16);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap' }).addTo(map);
            myPinMarker = L.marker([INITIAL_LAT, INITIAL_LNG], { draggable: true }).addTo(map);

            map.on('click', (e) => {
                if (isLocationLocked) return;
                updateLocation(e.latlng.lat, e.latlng.lng, "선택한 위치");
            });

            myPinMarker.on('dragend', () => {
                if (isLocationLocked) return;
                const pos = myPinMarker.getLatLng();
                updateLocation(pos.lat, pos.lng, "지정된 핀 위치");
            });

            updateLocation(INITIAL_LAT, INITIAL_LNG, "서울특별시청");
        }

        async function searchLocation(e) {
            e.preventDefault();
            if (isLocationLocked) { alert("위치가 고정되어 있습니다. [고정 해제]를 먼저 눌러주세요."); return; }
            const keyword = document.getElementById("search-keyword").value.trim();
            if (!keyword) return;

            try {
                const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(keyword)}&countrycodes=kr&limit=1`);
                const data = await res.json();
                if (data && data.length > 0) {
                    const lat = parseFloat(data[0].lat);
                    const lon = parseFloat(data[0].lon);
                    updateLocation(lat, lon, data[0].display_name.split(",")[0]);
                    map.flyTo([lat, lon], 16, { animate: true, duration: 1.0 });
                } else { alert("검색 결과를 찾을 수 없습니다."); }
            } catch (err) { console.error(err); }
        }

        function toggleLocationLock() {
            isLocationLocked = !isLocationLocked;
            const btn = document.getElementById("lock-btn");
            const icon = document.getElementById("lock-icon");
            const text = document.getElementById("lock-text");
            const statusTag = document.getElementById("status-tag");
            const topNotice = document.getElementById("map-top-notice");

            if (isLocationLocked) {
                myPinMarker.dragging.disable();
                btn.classList.add("locked");
                icon.innerText = "🔒";
                text.innerText = "해제";
                statusTag.className = "status-tag locked";
                statusTag.innerText = "고정됨";
                topNotice.classList.add("locked");
                topNotice.innerHTML = "🔒 <b>위치가 고정되었습니다.</b> (검색 및 데이터 조회까지 1~3초 정도 소요될 수 있습니다)";
            } else {
                myPinMarker.dragging.enable();
                btn.classList.remove("locked");
                icon.innerText = "🔓";
                text.innerText = "고정";
                statusTag.className = "status-tag unlocked";
                statusTag.innerText = "수정 가능";
                topNotice.classList.remove("locked");
                topNotice.innerHTML = "⏳ <b>안내:</b> 원하는 위치를 지정하고 <b>[고정]</b>을 누르세요. (위치 고정 후 검색까지 시간이 약간 걸릴 수 있습니다)";
            }
        }

        function updateLocation(lat, lng, labelName) {
            myPinMarker.setLatLng([lat, lng]);
            document.getElementById("picked-location-name").innerText = labelName || "지정된 위치";
            clearResultMarkers();
            if (fetchTimeout) clearTimeout(fetchTimeout);
            setLoadingState();
            fetchTimeout = setTimeout(() => { fetchNearbyFacilities(lat, lng); }, 300);
        }

        async function fetchNearbyFacilities(lat, lng) {
            const query = `[out:json][timeout:15];(
              node["railway"="station"](around:1500,${lat},${lng});
              way["railway"="station"](around:1500,${lat},${lng});
              node["highway"="bus_stop"](around:1500,${lat},${lng});
              node["shop"="convenience"](around:1200,${lat},${lng});
              node["amenity"="parcel_locker"](around:1500,${lat},${lng});
              node["amenity"~"restaurant|fast_food|cafe|pub"](around:1000,${lat},${lng});
            );out center 80;`;

            for (let server of OVERPASS_SERVERS) {
                try {
                    const response = await fetch(server, { method: "POST", body: query });
                    if (response.ok) {
                        const data = await response.json();
                        renderFacilities(data.elements || [], lat, lng);
                        return;
                    }
                } catch(e) { continue; }
            }
            renderFacilities([], lat, lng);
        }

        function setLoadingState() {
            ['card-subway', 'card-bus', 'card-cs', 'card-locker', 'card-food-24', 'card-food'].forEach(id => {
                const card = document.getElementById(id);
                card.querySelector('.name').innerText = "탐색 중...";
                const btn = card.querySelector('.mini-nav');
                btn.classList.add('disabled');
                btn.href = "#";
            });
            document.getElementById('meal-list-container').innerHTML = `<p class="empty-msg">주변 식당 목록을 불러오는 중입니다...</p>`;
            document.getElementById('cvs-list-container').innerHTML = `<p class="empty-msg">주변 편의점 목록을 불러오는 중입니다...</p>`;
        }

        function renderFacilities(elements, originLat, originLng) {
            const list = elements.map(el => {
                const itemLat = el.lat || (el.center && el.center.lat);
                const itemLon = el.lon || (el.center && el.center.lon);
                let name = (el.tags && (el.tags['name:ko'] || el.tags.name || el.tags['name:en'])) || "";
                return {
                    name: name,
                    lat: itemLat,
                    lon: itemLon,
                    tags: el.tags || {},
                    dist: (itemLat && itemLon) ? getDistanceMeters(originLat, originLng, itemLat, itemLon) : 99999
                };
            }).filter(el => el.lat && el.lon).sort((a, b) => a.dist - b.dist);

            bindCard('card-subway', list.find(el => el.tags.railway === 'station' || el.name.endsWith('역')), originLat, originLng, "지하철역");
            bindCard('card-bus', list.find(el => el.tags.highway === 'bus_stop'), originLat, originLng, "버스정류장");
            bindCard('card-cs', list.find(el => el.tags.shop === 'convenience'), originLat, originLng, "편의점");
            bindCard('card-locker', list.find(el => el.tags.amenity === 'parcel_locker'), originLat, originLng, "무인택배함");
            bindCard('card-food-24', list.find(el => el.tags.amenity && (el.tags.opening_hours === '24/7' || el.name.includes('24'))), originLat, originLng, "24시 식당");
            bindCard('card-food', list.find(el => ['restaurant', 'fast_food', 'cafe', 'pub'].includes(el.tags.amenity)), originLat, originLng, "식당");

            nearbyRestaurants = list.filter(el => ['restaurant', 'fast_food', 'cafe', 'pub'].includes(el.tags.amenity) && el.dist <= 800 && el.name.trim() !== "");
            renderMealList(nearbyRestaurants);
            drawRoulette(nearbyRestaurants);

            nearbyConveniences = list.filter(el => el.tags.shop === 'convenience' && el.dist <= 1200);
            renderCvsList(nearbyConveniences);
        }

        function bindCard(cardId, item, originLat, originLng, fallbackType) {
            const card = document.getElementById(cardId);
            const nameEl = card.querySelector('.name');
            const navBtn = card.querySelector('.mini-nav');

            if (item && item.dist <= 2000) {
                const displayName = item.name || `${fallbackType} (이름 미표기)`;
                nameEl.innerText = `${displayName} (${item.dist}m)`;
                navBtn.href = `https://map.kakao.com/link/to/${encodeURIComponent(displayName)},${item.lat},${item.lon}`;
                navBtn.classList.remove('disabled');

                const marker = L.circleMarker([item.lat, item.lon], { radius: 5, fillColor: "#4f46e5", color: "#fff", weight: 2, fillOpacity: 0.9 }).addTo(map);
                marker.bindPopup(`<b>${displayName}</b><br>거리: 약 ${item.dist}m`);
                resultMarkers.push(marker);
            } else {
                nameEl.innerText = "주변 정보 없음";
                navBtn.classList.add('disabled');
            }
        }

        function clearResultMarkers() { resultMarkers.forEach(m => map.removeLayer(m)); resultMarkers = []; }
        function getDistanceMeters(lat1, lon1, lat2, lon2) {
            const R = 6371e3;
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
            return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
        }

        function switchFoodTab(tabId) {
            document.querySelectorAll('.tab-menu').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.food-tab-content').forEach(tab => tab.classList.add('hidden'));
            event.target.classList.add('active');
            document.getElementById(tabId).classList.remove('hidden');
            if (tabId === 'tab-roulette') drawRoulette(nearbyRestaurants);
        }

        function renderMealList(restaurants) {
            const container = document.getElementById('meal-list-container');
            document.getElementById('meal-count-badge').innerText = `${restaurants.length}곳 발견`;
            if (restaurants.length === 0) { container.innerHTML = `<p class="empty-msg">도보 10분(800m) 내 식당 정보가 없습니다.</p>`; return; }
            container.innerHTML = restaurants.map(r => `
                <div class="food-item-card">
                    <div class="title-row"><h5>🍴 ${r.name}</h5><span class="food-type-tag">${r.tags.cuisine || r.tags.amenity || '식당'}</span></div>
                    <p class="dist-text">도보 약 ${Math.ceil(r.dist / 80)}분 (${r.dist}m)</p>
                    <div class="food-actions">
                        <a href="https://map.kakao.com/link/to/${encodeURIComponent(r.name)},${r.lat},${r.lon}" target="_blank" class="btn-route">길찾기</a>
                        <a href="https://m.map.kakao.com/actions/searchView?q=${encodeURIComponent(r.name)}" target="_blank" class="btn-review">메뉴/리뷰 ↗</a>
                    </div>
                </div>
            `).join('');
        }

        function renderCvsList(cvsList) {
            const container = document.getElementById('cvs-list-container');
            if (cvsList.length === 0) { container.innerHTML = `<p class="empty-msg">주변 편의점 정보가 없습니다.</p>`; return; }
            container.innerHTML = cvsList.map(c => `
                <div class="food-item-card">
                    <div class="title-row"><h5>🏪 ${c.name || '편의점'}</h5><span class="food-type-tag">${c.tags.brand || '24시'}</span></div>
                    <p class="dist-text">도보 약 ${Math.ceil(c.dist / 80)}분 (${c.dist}m)</p>
                    <div class="food-actions">
                        <a href="https://map.kakao.com/link/to/${encodeURIComponent(c.name || '편의점')},${c.lat},${c.lon}" target="_blank" class="btn-route">길찾기</a>
                        <a href="https://m.map.kakao.com/actions/searchView?q=${encodeURIComponent(c.name || '편의점')}" target="_blank" class="btn-review">좌석/정보 ↗</a>
                    </div>
                </div>
            `).join('');
        }

        const colors = ["#6366f1", "#ec4899", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6", "#14b8a6", "#f97316"];
        function drawRoulette(restaurants) {
            const canvas = document.getElementById("roulette-canvas");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            const list = restaurants.slice(0, 8);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (list.length === 0) {
                ctx.fillStyle = "#94a3b8"; ctx.font = "14px sans-serif"; ctx.textAlign = "center";
                ctx.fillText("주변 식당 탐색 후 표시됩니다", canvas.width / 2, canvas.height / 2); return;
            }
            const arc = (2 * Math.PI) / list.length;
            const centerX = canvas.width / 2; const centerY = canvas.height / 2; const radius = centerX - 10;
            ctx.save(); ctx.translate(centerX, centerY); ctx.rotate(currentRotation);
            list.forEach((item, i) => {
                const angle = i * arc;
                ctx.beginPath(); ctx.fillStyle = colors[i % colors.length];
                ctx.moveTo(0, 0); ctx.arc(0, 0, radius, angle, angle + arc); ctx.lineTo(0, 0); ctx.fill();
                ctx.save(); ctx.fillStyle = "#ffffff"; ctx.font = "bold 13px sans-serif"; ctx.textAlign = "right";
                ctx.rotate(angle + arc / 2); ctx.fillText(item.name.substring(0, 7), radius - 20, 5); ctx.restore();
            });
            ctx.restore();
        }

        function spinRoulette() {
            if (isSpinning || nearbyRestaurants.length === 0) return;
            isSpinning = true;
            const list = nearbyRestaurants.slice(0, 8);
            document.getElementById("roulette-spin-btn").disabled = true;
            const spinAngle = Math.floor(Math.random() * 360) + 1440;
            const duration = 3000; const start = performance.now(); const initialRot = currentRotation;
            function animate(time) {
                const elapsed = time - start; const progress = Math.min(elapsed / duration, 1);
                const easeOut = 1 - Math.pow(1 - progress, 3);
                currentRotation = initialRot + (spinAngle * Math.PI / 180) * easeOut;
                drawRoulette(list);
                if (progress < 1) { requestAnimationFrame(animate); }
                else { isSpinning = false; document.getElementById("roulette-spin-btn").disabled = false; selectWinner(list); }
            }
            requestAnimationFrame(animate);
        }

        function selectWinner(list) {
            const arc = (2 * Math.PI) / list.length;
            const normalizedRotation = (currentRotation % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
            let winningIndex = Math.floor(((3 * Math.PI / 2) - normalizedRotation + 2 * Math.PI) % (2 * Math.PI) / arc);
            const winner = list[winningIndex % list.length];
            document.getElementById("roulette-winner-card").innerHTML = `
                <div class="winner-name">🏆 ${winner.name}</div>
                <p style="font-size:0.85rem; color:#64748b; margin-bottom:8px;">도보 약 ${Math.ceil(winner.dist / 80)}분 (${winner.dist}m)</p>
                <a href="https://map.kakao.com/link/to/${encodeURIComponent(winner.name)},${winner.lat},${winner.lon}" target="_blank" class="step-link-btn">식당으로 길찾기 ↗</a>
            `;
        }

        function toggleOptionView() {
            const selectedOption = document.querySelector('input[name="route-option"]:checked').value;
            const detailBox = document.getElementById("cheapest-detail-box");
            if (selectedOption === "cheapest") detailBox.classList.remove("hidden");
            else detailBox.classList.add("hidden");
        }

        function calculateTransitRoute() {
            const start = document.getElementById("route-start").value.trim();
            const via = document.getElementById("route-via").value.trim();
            const end = document.getElementById("route-end").value.trim();
            const option = document.querySelector('input[name="route-option"]:checked').value;
            if (!start || !via || !end) { alert("출발지, 경유지, 최종 목적지를 모두 입력해주세요!"); return; }

            const resultContainer = document.getElementById("route-result-container");
            const resultContent = document.getElementById("result-content");
            resultContainer.classList.remove("hidden");

            const linkSection1 = `https://map.kakao.com/?sName=${encodeURIComponent(start)}&eName=${encodeURIComponent(via)}`;
            const linkSection2 = `https://map.kakao.com/?sName=${encodeURIComponent(via)}&eName=${encodeURIComponent(end)}`;

            if (option === "fastest") {
                resultContent.innerHTML = `
                    <div class="result-header">
                        <h3>⚡ [최단시간] ${start} ➔ (경유: ${via}) ➔ ${end}</h3>
                        <p style="color:#64748b; font-size:0.88rem; margin-top:4px;">대중교통 배차 간격 및 경유지 도착 후 환승 시간을 고려하여 2개 구간으로 분할 안내합니다.</p>
                    </div>
                    <div class="route-step-box">
                        <div class="step-item">
                            <div class="step-header"><h4>1단계 구간: <b>${start}</b> ➔ <b>${via}</b></h4><a href="${linkSection1}" target="_blank" class="step-link-btn">대중교통 경로 ↗</a></div>
                        </div>
                        <div class="step-item">
                            <div class="step-header"><h4>2단계 구간: <b>${via}</b> ➔ <b>${end}</b></h4><a href="${linkSection2}" target="_blank" class="step-link-btn">대중교통 경로 ↗</a></div>
                        </div>
                    </div>`;
            } else {
                const transportType = document.getElementById("prev-transport-type").value;
                const transportNum = document.getElementById("prev-transport-num").value.trim() || "이용 노선";
                let transferGuide = transportType === "subway" 
                    ? "<li>⚠️ 지하철 재탑승 시 요금 부과 ➔ 시내/마을버스로 환승 시 기본요금 0원</li>"
                    : `<li>⚠️ 동일 버스(${transportNum}) 재탑승 불가 ➔ 지하철 또는 다른 버스 환승 시 0원</li>`;
                resultContent.innerHTML = `
                    <div class="result-header">
                        <h3>💰 [최소 비용 30분 환승 공략] ${start} ➔ ${via} ➔ ${end}</h3>
                    </div>
                    <div class="route-step-box">
                        <div class="step-item transfer-guide">
                            <h4 style="color:#065f46; margin-bottom:6px;">⏱️ 30분 환승 골든타임 팁</h4>
                            <ul style="font-size:0.85rem; padding-left:16px;">${transferGuide}</ul>
                        </div>
                        <div class="step-item">
                            <div class="step-header"><h4>1단계 이동: <b>${start}</b> ➔ <b>${via}</b> (${transportNum})</h4><a href="${linkSection1}" target="_blank" class="step-link-btn">1구간 길찾기 ↗</a></div>
                        </div>
                        <div class="step-item">
                            <div class="step-header"><h4>2단계 환승: <b>${via}</b> ➔ <b>${end}</b> (환승할인)</h4><a href="${linkSection2}" target="_blank" class="step-link-btn">2구간 길찾기 ↗</a></div>
                        </div>
                    </div>`;
            }
        }
    </script>
</body>
</html>
"""

# HTML 컴포넌트를 브라우저 전체 높이로 렌더링
components.html(HTML_CODE, height=1350, scrolling=True)