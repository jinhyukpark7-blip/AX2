let map, myPinMarker;
let isLocationLocked = false;
let resultMarkers = [];

// 기본 좌표: 서울특별시청
const INITIAL_LAT = 37.5665;
const INITIAL_LNG = 126.9780;

document.addEventListener("DOMContentLoaded", () => {
    initMap();
});

function initMap() {
    // 1. Leaflet 지도 생성
    map = L.map('map').setView([INITIAL_LAT, INITIAL_LNG], 15);

    // 2. OpenStreetMap 무료 타일 레이어
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // 3. 이동 가능한 기준 핀 생성
    myPinMarker = L.marker([INITIAL_LAT, INITIAL_LNG], {
        draggable: true
    }).addTo(map);

    // 4. 지도 클릭 시 핀 이동
    map.on('click', (e) => {
        if (isLocationLocked) return;
        updateLocation(e.latlng.lat, e.latlng.lng, "선택한 지도 위치");
    });

    // 5. 핀 드래그 종료 시 이동
    myPinMarker.on('dragend', () => {
        if (isLocationLocked) return;
        const pos = myPinMarker.getLatLng();
        updateLocation(pos.lat, pos.lng, "지정된 핀 위치");
    });

    // 초기 1회 실행
    updateLocation(INITIAL_LAT, INITIAL_LNG, "서울특별시청");
}

// 🔍 무료 Nominatim 검색 API로 장소 검색하여 이동
async function searchLocation(e) {
    e.preventDefault();
    if (isLocationLocked) {
        alert("현재 위치가 고정되어 있습니다. 상단의 [고정 해제]를 먼저 눌러주세요.");
        return;
    }

    const input = document.getElementById("search-keyword");
    const keyword = input.value.trim();
    if (!keyword) return;

    const btn = document.getElementById("search-btn");
    btn.innerText = "검색중";
    btn.disabled = true;

    try {
        // 대한민국 기준 검색 (countrycodes=kr)
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(keyword)}&countrycodes=kr&limit=1`;
        const res = await fetch(url);
        const data = await res.json();

        if (data && data.length > 0) {
            const place = data[0];
            const lat = parseFloat(place.lat);
            const lon = parseFloat(place.lon);
            const displayName = place.display_name.split(",")[0];

            updateLocation(lat, lon, displayName);
            map.flyTo([lat, lon], 16, { animate: true, duration: 1.2 });
        } else {
            alert("검색 결과를 찾을 수 없습니다. 지하철역 이름이나 동 명칭을 정확히 입력해보세요.");
        }
    } catch (err) {
        console.error("검색 중 오류:", err);
        alert("검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
        btn.innerText = "검색";
        btn.disabled = false;
    }
}

// 위치 고정 토글
function toggleLocationLock() {
    isLocationLocked = !isLocationLocked;

    const lockBtn = document.getElementById("lock-btn");
    const lockIcon = document.getElementById("lock-icon");
    const lockText = document.getElementById("lock-text");
    const guideBadge = document.getElementById("guide-badge");
    const statusTag = document.getElementById("status-tag");
    const searchInput = document.getElementById("search-keyword");
    const searchBtn = document.getElementById("search-btn");

    if (isLocationLocked) {
        myPinMarker.dragging.disable();
        lockBtn.classList.add("locked");
        lockIcon.innerText = "🔒";
        lockText.innerText = "고정 해제";

        guideBadge.classList.add("locked");
        guideBadge.innerHTML = "🔒 <b>위치가 고정되었습니다.</b> 클릭하거나 검색해도 핀이 유지됩니다.";

        statusTag.classList.remove("unlocked");
        statusTag.classList.add("locked");
        statusTag.innerText = "위치 고정됨";

        searchInput.disabled = true;
        searchBtn.disabled = true;
    } else {
        myPinMarker.dragging.enable();
        lockBtn.classList.remove("locked");
        lockIcon.innerText = "🔓";
        lockText.innerText = "위치 고정";

        guideBadge.classList.remove("locked");
        guideBadge.innerHTML = "💡 장소를 검색하거나 지도를 클릭하여 핀을 놓은 뒤 <b>[위치 고정]</b>을 누르세요.";

        statusTag.classList.remove("locked");
        statusTag.classList.add("unlocked");
        statusTag.innerText = "수정 가능";

        searchInput.disabled = false;
        searchBtn.disabled = false;
    }
}

// 핀 위치 업데이트 및 주변 탐색
function updateLocation(lat, lng, labelName) {
    myPinMarker.setLatLng([lat, lng]);

    document.getElementById("picked-location-name").innerText = labelName || "선택 위치";
    document.getElementById("picked-coords").innerText = `좌표: 위도 ${lat.toFixed(5)}, 경도 ${lng.toFixed(5)}`;

    clearResultMarkers();
    fetchNearbyFacilities(lat, lng);
}

// 두 좌표 간 직선거리 계산 (m)
function getDistanceMeters(lat1, lon1, lat2, lon2) {
    const R = 6371e3;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return Math.round(R * c);
}

// Overpass API 호출 (반경 2000m)
async function fetchNearbyFacilities(lat, lng) {
    setLoadingState();

    const query = `
        [out:json][timeout:15];
        (
          node["railway"="station"](around:2000,${lat},${lng});
          node["highway"="bus_stop"](around:2000,${lat},${lng});
          node["shop"="convenience"](around:2000,${lat},${lng});
          node["amenity"="parcel_locker"](around:2000,${lat},${lng});
          node["amenity"="restaurant"](around:2000,${lat},${lng});
        );
        out body 40;
    `;

    try {
        const response = await fetch("https://overpass-api.de/api/interpreter", {
            method: "POST",
            body: query
        });
        const data = await response.json();
        processOverpassResults(data.elements, lat, lng);
    } catch (error) {
        console.error("데이터 조회 실패:", error);
    }
}

function setLoadingState() {
    ['card-subway', 'card-bus', 'card-cs', 'card-locker', 'card-food-24', 'card-food'].forEach(id => {
        const card = document.getElementById(id);
        card.querySelector('.facility-name').innerText = "탐색 중...";
        card.querySelector('.facility-dist').innerText = "-";
        const btn = card.querySelector('.nav-btn');
        btn.classList.add('disabled');
        btn.href = "#";
    });
}

function processOverpassResults(elements, originLat, originLng) {
    const list = elements.map(el => ({
        name: (el.tags && (el.tags.name || el.tags['name:ko'])) || "이름 정보 없음",
        lat: el.lat,
        lon: el.lon,
        tags: el.tags || {},
        dist: getDistanceMeters(originLat, originLng, el.lat, el.lon)
    }));

    list.sort((a, b) => a.dist - b.dist);

    const subway = list.find(el => el.tags.railway === 'station');
    const bus = list.find(el => el.tags.highway === 'bus_stop');
    const cs = list.find(el => el.tags.shop === 'convenience');
    const locker = list.find(el => el.tags.amenity === 'parcel_locker');
    const food24 = list.find(el => el.tags.amenity === 'restaurant' && (el.tags.opening_hours === '24/7' || (el.name && el.name.includes('24'))));
    const food = list.find(el => el.tags.amenity === 'restaurant');

    bindCard('card-subway', subway, originLat, originLng);
    bindCard('card-bus', bus, originLat, originLng);
    bindCard('card-cs', cs, originLat, originLng);
    bindCard('card-locker', locker, originLat, originLng);
    bindCard('card-food-24', food24, originLat, originLng);
    bindCard('card-food', food, originLat, originLng);
}

function bindCard(cardId, item, originLat, originLng) {
    const card = document.getElementById(cardId);
    const nameEl = card.querySelector('.facility-name');
    const distEl = card.querySelector('.facility-dist');
    const navBtn = card.querySelector('.nav-btn');

    if (item) {
        nameEl.innerText = item.name;
        distEl.innerText = `거리: 약 ${item.dist}m`;
        
        // 길찾기 링크 연결 (도보 기준)
        navBtn.href = `https://www.google.com/maps/dir/?api=1&origin=${originLat},${originLng}&destination=${item.lat},${item.lon}&travelmode=walking`;
        navBtn.classList.remove('disabled');

        // 지도상에 결과 마커 표기
        const marker = L.circleMarker([item.lat, item.lon], {
            radius: 6,
            fillColor: "#4f46e5",
            color: "#ffffff",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
        }).addTo(map);
        marker.bindPopup(`<b>${item.name}</b><br>거리: 약 ${item.dist}m`);
        resultMarkers.push(marker);
    } else {
        nameEl.innerText = "반경 2km 내 데이터 없음";
        distEl.innerText = "-";
        navBtn.href = "#";
        navBtn.classList.add('disabled');
    }
}

function clearResultMarkers() {
    resultMarkers.forEach(m => map.removeLayer(m));
    resultMarkers = [];
}