# SKT-5: 요금제 설계 시스템 - 제조사 혜택 연장 기능 (MVP: 삼성)

**Overall Progress:** `100%`

---

## TLDR
삼성/애플 플래그십폰 구매 시 제공되는 무료 혜택(Gemini, Apple Music 등)이 종료된 후, SKT 요금제 유지 고객에게 해당 혜택을 연장 제공하는 요금제 설계 시스템 구축. 4개의 MCP 서버로 기능 분리하여 재사용성 확보. 내부 기획자가 AI Agent로 자연어 질의하며 비용 절감 시뮬레이션 및 PDF 스펙 문서 생성.

---

## Critical Decisions

| 결정 | 선택 | 근거 |
|------|------|------|
| 아키텍처 | MCP 서버 4개 분리 | 재사용성, 독립 배포 가능 |
| 데이터 저장 | SQLite (로컬) | 단순성, 배포 용이, Phase 2에서 교체 가능 |
| 비용 비교 기준 | 선택약정 할인가 | 실제 고객 청구 금액 기준 |
| 약정 기간 | 24개월 기본 (12개월, 무약정 지원) | SKT 주력 상품 |
| Apple Music | 개인 10,900원/월 | 가족 단가는 결합 추가 혜택으로 분리 |
| PDF 라이브러리 | ReportLab 또는 WeasyPrint | Python 네이티브, 한글 지원 |

---

## Tasks

### Phase 1: 프로젝트 기반 구축

- [x] 🟩 **Step 1: 프로젝트 구조 및 환경 설정**
  - [x] 🟩 Python 프로젝트 초기화 (`pyproject.toml`, `uv` 또는 `poetry`)
  - [x] 🟩 디렉토리 구조 생성 (`src/`, `mcp_servers/`, `tests/`)
  - [x] 🟩 공통 의존성 설치 (`mcp`, `httpx`, `beautifulsoup4`, `sqlite3`, `reportlab`)

- [x] 🟩 **Step 2: 데이터 모델 정의**
  - [x] 🟩 `models/benefit.py` - 제조사 혜택 스키마
  - [x] 🟩 `models/rate_plan.py` - SKT 요금제 스키마
  - [x] 🟩 `models/design.py` - 설계된 요금제 스키마

---

### Phase 2: MCP 서버 구현

- [x] 🟩 **Step 3: scraper-mcp 서버**
  - [x] 🟩 MCP 서버 boilerplate 생성
  - [x] 🟩 `scrape_samsung_benefits()` - 삼성 사전예약 혜택 크롤링
  - [x] 🟩 `scrape_apple_benefits()` - 애플 사전예약 혜택 크롤링
  - [x] 🟩 `scrape_skt_plans()` - T-world 5GX 요금제 크롤링
  - [x] 🟩 `.mcp.json`에 서버 등록

- [x] 🟩 **Step 4: storage-mcp 서버**
  - [x] 🟩 SQLite 스키마 정의 및 마이그레이션
  - [x] 🟩 `save_design()` - 요금제 설계 저장
  - [x] 🟩 `list_designs()` - 설계 목록 조회
  - [x] 🟩 `get_design()` - 설계 상세 조회
  - [x] 🟩 `delete_design()` - 설계 삭제

- [x] 🟩 **Step 5: calculator-mcp 서버**
  - [x] 🟩 `calculate_extension_cost()` - 혜택 연장 비용 계산
  - [x] 🟩 `compare_with_existing()` - 기존 제휴 요금제 비교
  - [x] 🟩 `calculate_savings()` - 절감액 산출
  - [x] 🟩 약정 기간별 계산 (24개월/12개월/무약정)

- [x] 🟩 **Step 6: pdf-mcp 서버**
  - [x] 🟩 PDF 템플릿 설계 (한글 폰트 설정)
  - [x] 🟩 `generate_spec_document()` - 요금제 스펙 문서 생성
  - [x] 🟩 섹션: 기본정보, 기본료, 포함혜택, 연장혜택, 비용비교, 절감액, 가족결합

---

### Phase 3: 통합 및 테스트

- [x] 🟩 **Step 7: MCP 서버 통합**
  - [x] 🟩 `.mcp.json` 전체 서버 설정
  - [x] 🟩 Python 3.11 가상환경 설정 (`.venv/`)
  - [x] 🟩 MCP SDK v1.26.0 설치
  - [x] 🟩 서버 간 데이터 흐름 검증

- [x] 🟩 **Step 8: End-to-End 테스트**
  - [x] 🟩 삼성 갤럭시 + Gemini 시나리오 테스트 (522,000원/18개월)
  - [x] 🟩 애플 아이폰 + Apple Music 시나리오 테스트 (196,200원/18개월)
  - [x] 🟩 PDF 출력 검증 (`data/e2e_test_spec.pdf`)
  - [x] 🟩 Scraper 에러 핸들링 검증 (redirect 처리 확인)

---

### Phase 4: 문서화 및 마무리

- [x] 🟩 **Step 9: Linear 이슈 업데이트 및 문서화**
  - [x] 🟩 SKT-5 이슈 상태 업데이트 (In Progress)
  - [x] 🟩 사용법 가이드 작성 (`docs/USAGE.md`)

---

## 파일 구조 (예상)

```
skt-ai-adoption-plan/
├── src/
│   └── models/
│       ├── benefit.py
│       ├── rate_plan.py
│       └── design.py
├── mcp_servers/
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── server.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── schema.sql
│   ├── calculator/
│   │   ├── __init__.py
│   │   └── server.py
│   └── pdf/
│       ├── __init__.py
│       ├── server.py
│       └── templates/
├── data/
│   └── rate_plans.db
├── tests/
├── pyproject.toml
└── .mcp.json
```

---

## 데이터 참조

### 제조사 혜택 (MVP)

| 제조사 | 혜택 | 무료 기간 | 월 단가 |
|--------|------|----------|---------|
| 삼성 | Google One AI Premium (Gemini Advanced + 2TB) | 6개월 | 29,000원 |
| 애플 | Apple Music (개인) | 6개월 | 10,900원 |
| 애플 | Apple Music (가족) - 결합 추가 혜택 | 6개월 | 16,900원 |

### SKT 5GX 요금제 (선택약정 기준)

| 요금제 | 월정액 (선택약정) | 포함 혜택 |
|--------|------------------|----------|
| 5GX 플래티넘(넷플릭스) | 93,750원 | Netflix Premium |
| 5GX 프라임플러스(넷플릭스) | - | Netflix Standard |
| 5GX 프라임(넷플릭스) | - | Netflix Standard |
| 5GX 프리미엄(넷플릭스) | - | Netflix Premium |

### 비용 계산 예시

**삼성 갤럭시 + Gemini (24개월 선택약정):**
```
제조사 무료 기간: 6개월
SKT 연장 기간: 18개월 (24 - 6)
연장 비용: 29,000원 × 18개월 = 522,000원
```

**애플 아이폰 + Apple Music (24개월 선택약정):**
```
제조사 무료 기간: 6개월
SKT 연장 기간: 18개월 (24 - 6)
연장 비용: 10,900원 × 18개월 = 196,200원
```

---

## 관련 링크

- [Linear Issue: SKT-5](https://linear.app/skt-ai-adoption/issue/SKT-5)
- [Samsung 사전예약 혜택](https://www.samsungsvc.co.kr/solution/3195073)
- [T-world 5GX 플래티넘(넷플릭스)](https://www.tworld.co.kr/web/product/callplan/NA00008719)
- [Google One AI Premium](https://one.google.com/about/google-ai-plans/)
- [Apple Music Offers](https://offers.applemusic.apple/six-month-offer-devices)
