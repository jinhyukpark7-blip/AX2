let map, myPinMarker;
let isLocationLocked = false;
let resultMarkers = [];

// 초기 기준 좌표: 서울특별시청
const INITIAL_LAT = 37.5665;
const INITIAL_LNG = 126.9780;

document.addEventListener("DOMContentLoaded", () => {
    initMap();
});

function initMap() {
    map = L.map('map').setView([INITIAL_LAT, INITIAL_LNG], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
    }).addTo(map);

    myPinMarker = L.marker([INITIAL_LAT, INITIAL_LNG], { draggable: true }).addTo(map);

    map.on('click', (e) => {
        if (isLocationLocked) return;
        updateLocation(e.latlng.lat, e.latlng.lng, "선택한 지도 위치");
    });

    myPinMarker.on('dragend', () => {
        if (isLocationLocked) return;
        const pos = myPinMarker.getLatLng();
        updateLocation(pos.lat, pos.lng, "지정된 핀 위치");
    });

    updateLocation(INITIAL_LAT, INITIAL_LNG, "서울특별시청");
}

// 🔍 검색 이동
async function searchLocation(e) {
    e.preventDefault();
    if (isLocationLocked) {
        alert("위치가 고정되어 있습니다. [고정 해제]를 먼저 눌러주세요.");
        return;
    }

    const input = document.getElementById("search-keyword");
    const keyword = input.value.trim();
    if (!keyword) return;

    try {
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(keyword)}&countrycodes=kr&limit=1`;
        const res = await fetch(url);
        const data = await res.json();

        if (data && data.length > 0) {
            const lat = parseFloat(data[0].lat);
            const lon = parseFloat(data[0].lon);
            const name = data[0].display_name.split(",")[0];

            updateLocation(lat, lon, name);
            map.flyTo([lat, lon], 16, { animate: true, duration: 1.0 });
        } else {
            alert("검색 결과를 찾을 수 없습니다.");
        }
    } catch (err) {
        console.error("검색 에러:", err);
    }
}

// 🔒 위치 고정 토글
function toggleLocationLock() {
    isLocationLocked = !isLocationLocked;
    const btn = document.getElementById("lock-btn");
    const icon = document.getElementById("lock-icon");
    const text = document.getElementById("lock-text");
    const statusTag = document.getElementById("status-tag");
    const guideBadge = document.getElementById("guide-badge");

    if (isLocationLocked) {
        myPinMarker.dragging.disable();
        btn.classList.add("locked");
        icon.innerText = "🔒";
        text.innerText = "해제";
        statusTag.className = "status-tag locked";
        statusTag.innerText = "고정됨";
        guideBadge.innerHTML = "🔒 <b>위치가 고정되었습니다.</b>";
    } else {
        myPinMarker.dragging.enable();
        btn.classList.remove("locked");
        icon.innerText = "🔓";
        text.innerText = "고정";
        statusTag.className = "status-tag unlocked";
        statusTag.innerText = "수정 가능";
        guideBadge.innerHTML = "💡 클릭하여 핀 이동 후 [고정]을 누르세요.";
    }
}

function updateLocation(lat, lng, labelName) {
    myPinMarker.setLatLng([lat, lng]);
    document.getElementById("picked-location-name").innerText = labelName || "지정된 위치";
    clearResultMarkers();
    fetchNearbyFacilities(lat, lng);
}

// 편의시설 조회 (Overpass)
async function fetchNearbyFacilities(lat, lng) {
    const query = `
        [out:json][timeout:15];
        (
          node["railway"="station"](around:2000,${lat},${lng});
          node["highway"="bus_stop"](around:2000,${lat},${lng});
          node["shop"="convenience"](around:2000,${lat},${lng});
          node["amenity"="parcel_locker"](around:2000,${lat},${lng});
          node["amenity"="restaurant"](around:2000,${lat},${lng});
        );
        out body 30;
    `;
    try {
        const response = await fetch("https://overpass-api.de/api/interpreter", {
            method: "POST",
            body: query
        });
        const data = await response.json();
        renderFacilities(data.elements, lat, lng);
    } catch (e) {
        console.error(e);
    }
}

function renderFacilities(elements, originLat, originLng) {
    const list = elements.map(el => ({
        name: (el.tags && (el.tags.name || el.tags['name:ko'])) || "이름 정보 없음",
        lat: el.lat,
        lon: el.lon,
        tags: el.tags || {},
        dist: getDistanceMeters(originLat, originLng, el.lat, el.lon)
    })).sort((a, b) => a.dist - b.dist);

    bindCard('card-subway', list.find(el => el.tags.railway === 'station'), originLat, originLng);
    bindCard('card-bus', list.find(el => el.tags.highway === 'bus_stop'), originLat, originLng);
    bindCard('card-cs', list.find(el => el.tags.shop === 'convenience'), originLat, originLng);
    bindCard('card-locker', list.find(el => el.tags.amenity === 'parcel_locker'), originLat, originLng);
    bindCard('card-food-24', list.find(el => el.tags.amenity === 'restaurant' && (el.tags.opening_hours === '24/7' || (el.name && el.name.includes('24')))), originLat, originLng);
    bindCard('card-food', list.find(el => el.tags.amenity === 'restaurant'), originLat, originLng);
}

function bindCard(cardId, item, originLat, originLng) {
    const card = document.getElementById(cardId);
    const nameEl = card.querySelector('.name');
    const navBtn = card.querySelector('.mini-nav');

    if (item) {
        nameEl.innerText = `${item.name} (${item.dist}m)`;
        navBtn.href = `https://map.kakao.com/link/to/${encodeURIComponent(item.name)},${item.lat},${item.lon}`;
        navBtn.classList.remove('disabled');

        const marker = L.circleMarker([item.lat, item.lon], { radius: 5, fillColor: "#4f46e5", color: "#fff", weight: 2, fillOpacity: 0.9 }).addTo(map);
        resultMarkers.push(marker);
    } else {
        nameEl.innerText = "2km 내 없음";
        navBtn.classList.add('disabled');
    }
}

function clearResultMarkers() {
    resultMarkers.forEach(m => map.removeLayer(m));
    resultMarkers = [];
}

function getDistanceMeters(lat1, lon1, lat2, lon2) {
    const R = 6371e3;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
    return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
}

/* =========================================================================
   대중교통 경유지 경로 프로그램 로직
   ========================================================================= */

// 옵션 탭 전환 시 화면 노출 여부
function toggleOptionView() {
    const selectedOption = document.querySelector('input[name="route-option"]:checked').value;
    const detailBox = document.getElementById("cheapest-detail-box");
    if (selectedOption === "cheapest") {
        detailBox.classList.remove("hidden");
    } else {
        detailBox.classList.add("hidden");
    }
}

// 대중교통 경로 연산 및 렌더링
function calculateTransitRoute() {
    const start = document.getElementById("route-start").value.trim();
    const via = document.getElementById("route-via").value.trim();
    const end = document.getElementById("route-end").value.trim();
    const option = document.querySelector('input[name="route-option"]:checked').value;

    if (!start || !via || !end) {
        alert("출발지, 경유지, 최종 목적지를 모두 입력해주세요!");
        return;
    }

    const resultContainer = document.getElementById("route-result-container");
    const resultContent = document.getElementById("result-content");
    resultContainer.classList.remove("hidden");

    // 카카오맵/네이버 대중교통 길찾기 다이렉트 링크 생성
    const linkSection1 = `https://map.kakao.com/?sName=${encodeURIComponent(start)}&eName=${encodeURIComponent(via)}`;
    const linkSection2 = `https://map.kakao.com/?sName=${encodeURIComponent(via)}&eName=${encodeURIComponent(end)}`;

    if (option === "fastest") {
        // [옵션 1 : 최단시간 모드]
        resultContent.innerHTML = `
            <div class="result-header">
                <h3>⚡ [최단시간] ${start} ➔ (경유: ${via}) ➔ ${end}</h3>
                <p style="color:#64748b; font-size:0.88rem; margin-top:4px;">
                    대중교통 배차 간격 및 경유지 도착 후 환승 시간을 고려하여 2개 구간으로 최적 분할 안내합니다.
                </p>
            </div>
            <div class="route-step-box">
                <div class="step-item">
                    <div class="step-header">
                        <h4>1단계 구간: <b>${start}</b> ➔ <b>${via}</b></h4>
                        <a href="${linkSection1}" target="_blank" class="step-link-btn">대중교통 실시간 경로 보기 ↗</a>
                    </div>
                    <p style="font-size:0.85rem; color:#475569;">출발지에서 경유지까지 가장 빠른 지하철/급행 버스 노선을 확인하고 이동하세요.</p>
                </div>

                <div class="step-item">
                    <div class="step-header">
                        <h4>2단계 구간: <b>${via}</b> ➔ <b>${end}</b></h4>
                        <a href="${linkSection2}" target="_blank" class="step-link-btn">대중교통 실시간 경로 보기 ↗</a>
                    </div>
                    <p style="font-size:0.85rem; color:#475569;">경유지에서 볼일을 마친 시점의 실시간 도착 버스/열차를 확인하여 최종 목적지로 이동합니다.</p>
                </div>
            </div>
        `;
    } else {
        // [옵션 2 : 최소 비용 30분 환승할인 극대화 모드]
        const transportType = document.getElementById("prev-transport-type").value;
        const transportNum = document.getElementById("prev-transport-num").value.trim() || "이용 노선";

        let transferGuideText = "";
        if (transportType === "subway") {
            transferGuideText = `
                <li>⚠️ <b>지하철 재탑승 불가</b>: 지하철에서 하차 후 다시 지하철을 타면 기본요금이 다시 부과됩니다.</li>
                <li>✅ <b>추천 환승</b>: <b>시내버스, 지선버스, 마을버스</b>로 갈아타시면 <b>0원 환승(기본요금 면제)</b>이 적용됩니다.</li>
            `;
        } else {
            transferGuideText = `
                <li>⚠️ <b>동일 버스 재탑승 불가</b>: 방금 타신 <b>${transportNum}</b>과 같은 번호의 버스를 타면 환승이 인정되지 않습니다.</li>
                <li>✅ <b>추천 환승</b>: <b>지하철</b> 또는 <b>다른 번호의 버스</b>로 갈아타시면 <b>0원 환승(기본요금 면제)</b>이 적용됩니다.</li>
            `;
        }

        resultContent.innerHTML = `
            <div class="result-header">
                <h3>💰 [최소 비용 30분 환승 공략] ${start} ➔ ${via} ➔ ${end}</h3>
                <p style="color:#64748b; font-size:0.88rem; margin-top:4px;">
                    경유지(B)에서 30분 이내에 환승할 수 있는 최적의 교통 조합 가이드입니다.
                </p>
            </div>
            <div class="route-step-box">
                <div class="step-item transfer-guide">
                    <div class="step-header">
                        <h4 style="color:#065f46;">⏱️ 30분 환승 골든타임 공략법</h4>
                    </div>
                    <ul style="font-size:0.85rem; color:#1e293b; padding-left:18px; line-height:1.6;">
                        <li>경유지(${via}) 버스/지하철 단말기 하차 태그 시점부터 <b>30분 이내</b>에 다음 교통수단에 승차 태그를 해야 합니다.</li>
                        ${transferGuideText}
                    </ul>
                </div>

                <div class="step-item">
                    <div class="step-header">
                        <h4>1단계 이동: <b>${start}</b> ➔ <b>${via}</b> (${transportNum})</h4>
                        <a href="${linkSection1}" target="_blank" class="step-link-btn">1구간 길찾기 ↗</a>
                    </div>
                </div>

                <div class="step-item">
                    <div class="step-header">
                        <h4>2단계 환승: <b>${via}</b> ➔ <b>${end}</b> (환승할인 적용)</h4>
                        <a href="${linkSection2}" target="_blank" class="step-link-btn">2구간 길찾기 ↗</a>
                    </div>
                </div>
            </div>
        `;
    }
}