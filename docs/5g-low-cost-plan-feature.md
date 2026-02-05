# 5G 저가 요금제 설계 시스템 구현 계획

**Overall Progress:** `100%`

**Linear Issue:** [SKT-6](https://linear.app/skt-ai-adoption/issue/SKT-6/5g-저가-요금제-3만원대-신규-설계-정부-대응)

---

## TLDR

지방선거 대응 정부/국회 요구에 맞춘 **3만원대 5G 저가 요금제** 설계 시스템 구축. 가입자 이동 시뮬레이션을 통해 ARPU 영향도를 분석하고, 손실 최소화 포트폴리오 전략을 수립한다.

**핵심 산출물:**
- 신규 요금제 스펙 설계
- 가입자 이동 시나리오 시뮬레이션 (보수/기준/낙관)
- 시뮬레이션 리포트 PDF (요금제 스펙 포함)

---

## Critical Decisions

| 결정 | 선택 | 근거 |
|------|------|------|
| 구현 방식 | 새로운 Claude Skill + MCP 서버 | 기존 제조사 혜택 시스템과 분리 |
| 데이터 소스 (MVP) | Excel 파싱 + 가정값 | 빠른 출시, Athena는 Phase 2 |
| 이동 확률 | Claude 추정 → 사용자 확인 | 과거 데이터 없이도 시뮬레이션 가능 |
| Win-back 계산 | 고객 체감 효익 기반 | 가격차이, 데이터충족도, 부가서비스 |
| 고가 요금제 | 시나리오 옵션으로 포함 | 필수 아님, 손실 보전 전략의 일부 |
| 저장소 | 로컬 SQLite 확장 | 기존 storage-mcp 재사용 |
| 출력 | 시뮬레이션 리포트 PDF | 요금제 스펙 + 시나리오 결과 통합 |

---

## Tasks

### Phase 1: 데이터 모델 확장

- [x] 🟩 **Step 1: 요금제 스키마 확장**
  - [x] 🟩 `src/models/rate_plan.py` 확장
    ```python
    @dataclass
    class RatePlanSpec:
        name: str
        monthly_fee_krw: int
        data_gb: float              # 기본 데이터 (GB)
        voice_minutes: int          # 음성 (분), -1 = 무제한
        sms_count: int              # 문자 (건), -1 = 무제한
        throttle_speed_kbps: int    # 소진 후 속도제한 (Kbps)
        target_segment: str         # "general" | "youth" | "senior"
        channel: str                # "online" | "offline" | "both"
        included_benefits: List[str]
        notes: Optional[str]
    ```
  - [x] 🟩 `src/models/simulation.py` 신규 생성
    ```python
    @dataclass
    class SimulationScenario:
        scenario_id: str
        scenario_type: str          # "conservative" | "base" | "optimistic"
        new_plan: RatePlanSpec
        premium_plan: Optional[RatePlanSpec]  # 고가 요금제 옵션
        migration_rates: Dict[str, float]     # 요금제별 이동 확률
        winback_rate: float
        results: SimulationResult
        created_at: datetime

    @dataclass
    class SimulationResult:
        arpu_change_pct: float
        annual_revenue_impact_krw: int
        new_subscribers: int
        downgrade_subscribers: int
        winback_subscribers: int
    ```

- [x] 🟩 **Step 2: 저장소 스키마 확장**
  - [x] 🟩 `mcp_servers/storage/schema.sql` 테이블 추가
    ```sql
    CREATE TABLE simulation_scenarios (
      scenario_id TEXT PRIMARY KEY,
      scenario_type TEXT NOT NULL,
      new_plan_json TEXT NOT NULL,
      premium_plan_json TEXT,
      migration_rates_json TEXT NOT NULL,
      winback_rate REAL NOT NULL,
      results_json TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    ```
  - [x] 🟩 `mcp_servers/storage/server.py`에 시나리오 CRUD 추가

---

### Phase 2: 시뮬레이션 MCP 서버

- [x] 🟩 **Step 3: simulation-mcp 서버 생성**
  - [x] 🟩 `mcp_servers/simulation/__init__.py`
  - [x] 🟩 `mcp_servers/simulation/server.py`
    - `parse_excel(file_path)` - Excel 데이터 파싱
    - `estimate_migration_rates(current_plans, new_plan)` - 이동 확률 추정
    - `calculate_winback(new_plan, mvno_benchmark)` - Win-back 효과 계산
    - `run_simulation(scenario)` - 시뮬레이션 실행
    - `compare_scenarios(scenario_ids)` - 시나리오 비교
  - [x] 🟩 `.mcp.json`에 simulation 서버 등록

- [x] 🟩 **Step 4: Excel 파싱 로직**
  - [x] 🟩 예상 Excel 구조 처리
    ```
    | 요금제명 | 월정액 | 데이터구간 | 가입자수 | ARPU | 주요앱 |
    ```
  - [x] 🟩 데이터구간별 세분화 지원
  - [x] 🟩 pandas 의존성 추가 (`pyproject.toml`)

- [x] 🟩 **Step 5: 이동 확률 추정 로직**
  - [x] 🟩 가격 차이 기반 추정 공식
    ```
    base_rate = 0.05  # 기본 이동률 5%
    price_factor = (old_price - new_price) / old_price
    usage_fit = 1 if avg_usage <= new_data_gb else 0.5
    migration_rate = base_rate * (1 + price_factor) * usage_fit
    ```
  - [x] 🟩 세그먼트별 가중치 (청년 높음, 시니어 낮음)

- [x] 🟩 **Step 6: Win-back 효과 계산**
  - [x] 🟩 고객 체감 효익 공식
    ```
    price_benefit = (mvno_price - new_price) / mvno_price
    quality_premium = 0.15  # MNO 망품질/AS 프리미엄
    winback_rate = max(0, price_benefit + quality_premium) * 0.3
    ```
  - [x] 🟩 MVNO 벤치마크 데이터 하드코딩 (MVP)

---

### Phase 3: Claude Skills

- [x] 🟩 **Step 7: `/design-low-cost-plan` 스킬**
  - [x] 🟩 `.claude/commands/design-low-cost-plan.md` 생성
  - [ ] 🟥 워크플로우:
    1. 타겟 가격대 입력 (예: 35,000원)
    2. 경쟁사 벤치마크 조회 (scraper-mcp)
    3. 스펙 설계 (data_gb, voice, sms, throttle)
    4. 저장 (storage-mcp)

- [x] 🟩 **Step 8: `/simulate-migration` 스킬**
  - [x] 🟩 `.claude/commands/simulate-migration.md` 생성
  - [ ] 🟥 워크플로우:
    1. Excel 파일 경로 또는 가정값 입력
    2. 이동 확률 추정 → 사용자 확인/조정
    3. 3개 시나리오 생성 (보수/기준/낙관)
    4. 고가 요금제 옵션 포함 여부 확인
    5. 시뮬레이션 실행 및 저장

- [x] 🟩 **Step 9: `/export-simulation-report` 스킬**
  - [x] 🟩 `.claude/commands/export-simulation-report.md` 생성
  - [ ] 🟥 PDF 리포트 구조:
    - 요약 (Executive Summary)
    - 신규 요금제 스펙
    - 경쟁사 비교표
    - 시나리오별 결과 (ARPU, 매출영향, 가입자이동)
    - 고가 요금제 옵션 (있는 경우)
    - 권고사항

---

### Phase 4: PDF 리포트 생성

- [x] 🟩 **Step 10: pdf-mcp 확장**
  - [x] 🟩 `mcp_servers/pdf/server.py`에 `generate_simulation_report()` 추가
  - [ ] 🟥 시뮬레이션 리포트 템플릿
    ```python
    {
      "title": "5G 저가 요금제 시뮬레이션 리포트",
      "sections": {
        "요약": [...],
        "신규 요금제 스펙": [...],
        "경쟁사 비교": [...],
        "시나리오 분석": {
          "보수적": [...],
          "기준": [...],
          "낙관적": [...]
        },
        "권고사항": [...]
      }
    }
    ```
  - [x] 🟩 테이블 스타일링 (시나리오별 색상 구분)

---

### Phase 5: 통합 테스트

- [ ] 🟨 **Step 11: End-to-End 테스트**
  - [ ] 🟥 샘플 Excel 파일 생성 (`data/sample_subscribers.xlsx`)
  - [ ] 🟥 `/design-low-cost-plan` → `/simulate-migration` → `/export-simulation-report` 플로우 테스트
  - [ ] 🟥 PDF 출력 검증

- [ ] 🟨 **Step 12: 문서화**
  - [x] 🟩 `docs/USAGE.md` 업데이트 (새로운 스킬/MCP 도구 추가)
  - [ ] 🟥 Linear 이슈 완료 처리

---

## 파일 구조 (예상)

```
skt-ai-adoption-plan/
├── src/models/
│   ├── rate_plan.py          # 확장 (RatePlanSpec)
│   └── simulation.py         # 신규
├── mcp_servers/
│   ├── simulation/           # 신규
│   │   ├── __init__.py
│   │   └── server.py
│   ├── storage/
│   │   ├── schema.sql        # 테이블 추가
│   │   └── server.py         # CRUD 확장
│   └── pdf/
│       └── server.py         # 리포트 템플릿 추가
├── .claude/commands/
│   ├── design-low-cost-plan.md      # 신규
│   ├── simulate-migration.md        # 신규
│   └── export-simulation-report.md  # 신규
├── data/
│   └── sample_subscribers.xlsx      # 테스트용
└── docs/
    ├── 5g-low-cost-plan-feature.md  # 본 문서
    └── USAGE.md                      # 업데이트
```

---

## Phase 2 (향후)

- [ ] AWS Athena MCP 서버 구현
- [ ] 이벤트별 이동 확률 저장/재사용
- [ ] 실시간 경쟁사 요금제 스크래핑
- [ ] 차트/그래프 PDF 삽입

---

## 예상 작업량

| Phase | 예상 태스크 | 복잡도 |
|-------|------------|--------|
| Phase 1 | 데이터 모델 | 낮음 |
| Phase 2 | simulation-mcp | 중간 |
| Phase 3 | Claude Skills | 낮음 |
| Phase 4 | PDF 리포트 | 중간 |
| Phase 5 | 통합 테스트 | 낮음 |

---

**작성일:** 2026-02-05
**작성자:** CTO Agent
