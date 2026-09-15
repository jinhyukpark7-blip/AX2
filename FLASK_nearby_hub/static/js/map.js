let map, myPinMarker;
let isLocationLocked = false;
let resultMarkers = [];

// 오늘의 한끼 / 룰렛 데이터
let nearbyRestaurants = [];
let nearbyConveniences = [];
let isSpinning = false;
let currentRotation = 0;
let fetchTimeout = null;

// 기본 기준 좌표: 서울특별시청 (을지로 인근)
const INITIAL_LAT = 37.5665;
const INITIAL_LNG = 126.9780;

document.addEventListener("DOMContentLoaded", () => {
    initMap();
});

function initMap() {
    map = L.map('map').setView([INITIAL_LAT, INITIAL_LNG], 16);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
    }).addTo(map);

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

// 🔍 검색
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
        console.error("검색 오류:", err);
    }
}

// 🔒 위치 고정
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

    // 디바운스 적용 (연속 클릭 시 서버 과부하 방지)
    if (fetchTimeout) clearTimeout(fetchTimeout);
    setLoadingState();

    fetchTimeout = setTimeout(() => {
        fetchNearbyFacilities(lat, lng);
    }, 400);
}

// Flask 백엔드 프록시 호출
async function fetchNearbyFacilities(lat, lng) {
    try {
        const response = await fetch("/api/facilities", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lat: lat, lng: lng })
        });
        const data = await response.json();
        renderFacilities(data.elements || [], lat, lng);
    } catch (e) {
        console.error("데이터 통신 에러:", e);
        renderFacilities([], lat, lng);
    }
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
    }).filter(el => el.lat && el.lon)
      .sort((a, b) => a.dist - b.dist);

    // 1. 대표 카테고리 필터링
    const subway = list.find(el => (el.tags.railway === 'station' || el.tags.station === 'subway' || el.name.endsWith('역')) && !el.tags.highway);
    const bus = list.find(el => el.tags.highway === 'bus_stop' || el.tags.public_transport === 'platform');
    const cs = list.find(el => el.tags.shop === 'convenience');
    const locker = list.find(el => el.tags.amenity === 'parcel_locker' || el.tags.amenity === 'locker');
    const food24 = list.find(el => (el.tags.amenity === 'restaurant' || el.tags.amenity === 'fast_food') && (el.tags.opening_hours === '24/7' || (el.name && el.name.includes('24'))));
    const food = list.find(el => ['restaurant', 'fast_food', 'cafe', 'pub', 'bar'].includes(el.tags.amenity));

    bindCard('card-subway', subway, originLat, originLng, "지하철역");
    bindCard('card-bus', bus, originLat, originLng, "버스정류장");
    bindCard('card-cs', cs, originLat, originLng, "편의점");
    bindCard('card-locker', locker, originLat, originLng, "무인택배함");
    bindCard('card-food-24', food24, originLat, originLng, "24시 식당");
    bindCard('card-food', food, originLat, originLng, "식당");

    // 2. 오늘의 한끼 (도보 10분, 800m 내 모든 식당)
    nearbyRestaurants = list.filter(el => 
        ['restaurant', 'fast_food', 'cafe', 'pub', 'bar'].includes(el.tags.amenity) &&
        el.dist <= 800 && el.name.trim() !== ""
    );
    renderMealList(nearbyRestaurants);
    drawRoulette(nearbyRestaurants);

    // 3. 오늘의 편의점
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

        const marker = L.circleMarker([item.lat, item.lon], { 
            radius: 5, 
            fillColor: "#4f46e5", 
            color: "#fff", 
            weight: 2, 
            fillOpacity: 0.9 
        }).addTo(map);
        marker.bindPopup(`<b>${displayName}</b><br>거리: 약 ${item.dist}m`);
        resultMarkers.push(marker);
    } else {
        nameEl.innerText = "주변 정보 없음";
        navBtn.classList.add('disabled');
        navBtn.href = "#";
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
   오늘의 한끼 / 룰렛 / 편의점 탭
   ========================================================================= */

function switchFoodTab(tabId) {
    document.querySelectorAll('.tab-menu').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.food-tab-content').forEach(tab => tab.classList.add('hidden'));

    event.target.classList.add('active');
    document.getElementById(tabId).classList.remove('hidden');

    if (tabId === 'tab-roulette') {
        drawRoulette(nearbyRestaurants);
    }
}

function renderMealList(restaurants) {
    const container = document.getElementById('meal-list-container');
    const badge = document.getElementById('meal-count-badge');
    badge.innerText = `${restaurants.length}곳 발견`;

    if (restaurants.length === 0) {
        container.innerHTML = `<p class="empty-msg">도보 10분(800m) 내에 등록된 식당 정보가 없습니다.</p>`;
        return;
    }

    container.innerHTML = restaurants.map(r => `
        <div class="food-item-card">
            <div class="title-row">
                <h5>🍴 ${r.name}</h5>
                <span class="food-type-tag">${r.tags.cuisine || r.tags.amenity || '식당'}</span>
            </div>
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
    if (cvsList.length === 0) {
        container.innerHTML = `<p class="empty-msg">주변에 편의점 정보가 없습니다.</p>`;
        return;
    }

    container.innerHTML = cvsList.map(c => `
        <div class="food-item-card">
            <div class="title-row">
                <h5>🏪 ${c.name || '편의점'}</h5>
                <span class="food-type-tag">${c.tags.brand || '24시'}</span>
            </div>
            <p class="dist-text">도보 약 ${Math.ceil(c.dist / 80)}분 (${c.dist}m)</p>
            <div class="food-actions">
                <a href="https://map.kakao.com/link/to/${encodeURIComponent(c.name || '편의점')},${c.lat},${c.lon}" target="_blank" class="btn-route">길찾기</a>
                <a href="https://m.map.kakao.com/actions/searchView?q=${encodeURIComponent(c.name || '편의점')}" target="_blank" class="btn-review">좌석/정보 ↗</a>
            </div>
        </div>
    `).join('');
}

// 룰렛 로직
const colors = ["#6366f1", "#ec4899", "#f59e0b", "#10b981", "#3b82f6", "#8b5cf6", "#14b8a6", "#f97316"];

function drawRoulette(restaurants) {
    const canvas = document.getElementById("roulette-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const list = restaurants.slice(0, 8);

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (list.length === 0) {
        ctx.fillStyle = "#94a3b8";
        ctx.font = "14px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("주변 식당 탐색 후 표시됩니다", canvas.width / 2, canvas.height / 2);
        return;
    }

    const arc = (2 * Math.PI) / list.length;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = centerX - 10;

    ctx.save();
    ctx.translate(centerX, centerY);
    ctx.rotate(currentRotation);

    list.forEach((item, i) => {
        const angle = i * arc;
        ctx.beginPath();
        ctx.fillStyle = colors[i % colors.length];
        ctx.moveTo(0, 0);
        ctx.arc(0, 0, radius, angle, angle + arc);
        ctx.lineTo(0, 0);
        ctx.fill();

        ctx.save();
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 13px sans-serif";
        ctx.textAlign = "right";
        ctx.rotate(angle + arc / 2);
        ctx.fillText(item.name.substring(0, 7), radius - 20, 5);
        ctx.restore();
    });

    ctx.restore();
}

function spinRoulette() {
    if (isSpinning || nearbyRestaurants.length === 0) return;
    isSpinning = true;

    const list = nearbyRestaurants.slice(0, 8);
    const spinBtn = document.getElementById("roulette-spin-btn");
    spinBtn.disabled = true;

    const spinAngle = Math.floor(Math.random() * 360) + 1440;
    const duration = 3000;
    const start = performance.now();
    const initialRot = currentRotation;

    function animate(time) {
        const elapsed = time - start;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);

        currentRotation = initialRot + (spinAngle * Math.PI / 180) * easeOut;
        drawRoulette(list);

        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            isSpinning = false;
            spinBtn.disabled = false;
            selectWinner(list);
        }
    }
    requestAnimationFrame(animate);
}

function selectWinner(list) {
    const arc = (2 * Math.PI) / list.length;
    const normalizedRotation = (currentRotation % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
    let winningIndex = Math.floor(((3 * Math.PI / 2) - normalizedRotation + 2 * Math.PI) % (2 * Math.PI) / arc);
    winningIndex = winningIndex % list.length;

    const winner = list[winningIndex];
    const container = document.getElementById("roulette-winner-card");

    container.innerHTML = `
        <div class="winner-name">🏆 ${winner.name}</div>
        <p style="font-size:0.85rem; color:#64748b; margin-bottom:8px;">도보 약 ${Math.ceil(winner.dist / 80)}분 (${winner.dist}m)</p>
        <a href="https://map.kakao.com/link/to/${encodeURIComponent(winner.name)},${winner.lat},${winner.lon}" target="_blank" class="step-link-btn">식당으로 길찾기 ↗</a>
    `;
}

/* =========================================================================
   대중교통 경유지 경로 연산
   ========================================================================= */

function toggleOptionView() {
    const selectedOption = document.querySelector('input[name="route-option"]:checked').value;
    const detailBox = document.getElementById("cheapest-detail-box");
    if (selectedOption === "cheapest") {
        detailBox.classList.remove("hidden");
    } else {
        detailBox.classList.add("hidden");
    }
}

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

    const linkSection1 = `https://map.kakao.com/?sName=${encodeURIComponent(start)}&eName=${encodeURIComponent(via)}`;
    const linkSection2 = `https://map.kakao.com/?sName=${encodeURIComponent(via)}&eName=${encodeURIComponent(end)}`;

    if (option === "fastest") {
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