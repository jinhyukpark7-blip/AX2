# 🚢 Trade-Job-MBTI (무역 직무 맞춤형 성향 진단기)

Streamlit 기반의 인터랙티브 웹 애플리케이션으로, 사용자의 성향과 업무 스타일을 분석하여 6대 무역·물류 직무 중 가장 적합한 직무를 추천합니다.

---

## 📌 주요 특징
* **12문항 간이 진단:** 4개 차원(O/I, S/N, T/F, J/P)의 질문을 통해 중도 이탈 없이 3분 내 진단 완료
* **가중치 매핑 알고리즘:** 단순 단일 매칭이 아닌 직무별 역량 가중치 벡터 내적을 통한 1~3위 직무 추천
* **직무별 핵심 스킬 가이드:** 추천 직무에 필요한 핵심 실무 역량 및 업무 정의 제공

---

## 🧭 분석 축 (4 Dimensions)
| 차원 | 코드 (A / B) | 설명 |
|---|---|---|
| **소통 스타일** | `O` (Outward) vs `I` (Inward) | 대외 협상/네트워킹 vs 내부 서류/정밀 운영 |
| **접근 방식** | `S` (Structured) vs `N` (Navigational) | 규정/데이터 기반 vs 시장 트렌드/전략적 탐색 |
| **의사결정** | `T` (Task/Logic) vs `F` (Focus/People) | 수치/비용 효율 vs 파트너십/고객 신뢰 |
| **대응 스타일** | `J` (Judicious) vs `P` (Proactive) | 사전 계획/매뉴얼 vs 기민한 임기응변/이슈 대응 |

---

## 💼 진단 대상 직무 (6개)
1. **해외영업 (Overseas Sales)**: 글로벌 바이어 발굴 및 단가 협상
2. **포워딩 오퍼레이션 (Forwarding Ops)**: 해상/항공 스케줄링 및 운송 트러블슈팅
3. **무역사무 및 영업관리 (Trade Admin)**: 선적 서류(B/L, C/I, P/L) 작성 및 수발주 정산
4. **글로벌 SCM 및 물류기획 (Global SCM)**: 공급망 최적화 및 물류비 데이터 분석
5. **해외 소싱 및 구매 (Global Procurement)**: 원부자재 공급사 발굴 및 단가 네고
6. **관세 및 통관 컴플라이언스 (Customs)**: HS Code 분류, FTA 원산지 증명, 통관 규제 대응

---

## 🛠 설치 및 실행 방법

### 1. 레포지토리 클론
```bash
git clone [https://github.com/your-username/trade-job-mbti.git](https://github.com/your-username/trade-job-mbti.git)
cd trade-job-mbti