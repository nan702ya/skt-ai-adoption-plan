# Changelog

All notable changes to the SKT AI Adoption Plan project.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **simulation-mcp**: New MCP server for subscriber migration analysis
  - `parse_excel()` - Excel 파일 파싱 (한글/영문 컬럼 지원)
  - `estimate_migration_rates()` - 이동 확률 추정 (가격차이, 사용량 적합도 기반)
  - `calculate_winback()` - Win-back 효과 계산 (고객 체감 효익 기반)
  - `run_simulation()` - 시뮬레이션 실행 (보수/기준/낙관 시나리오)

- **storage-mcp 확장**: 시나리오 저장/조회 기능
  - `save_scenario()`, `list_scenarios()`, `get_scenario()`, `delete_scenario()`
  - `simulation_scenarios` 테이블 추가

- **pdf-mcp 확장**: 시뮬레이션 리포트 생성
  - `generate_simulation_report()` - 시나리오별 색상 구분 포함

- **데이터 모델**
  - `RatePlanSpec` - 5G 요금제 상세 스펙 (data_gb, voice, sms, throttle, segment, channel)
  - `SimulationScenario`, `SimulationResult` - 시뮬레이션 시나리오/결과

- **Claude Skills**
  - `/design-low-cost-plan` - 3만원대 5G 저가 요금제 설계
  - `/simulate-migration` - 가입자 이동 시뮬레이션
  - `/export-simulation-report` - 시뮬레이션 리포트 PDF 출력
  - `/peer-review` - 피어 코드 리뷰 검증

- **테스트**
  - `tests/test_simulation_e2e.py` - E2E 시뮬레이션 워크플로우 테스트

- **의존성**
  - `pandas`, `openpyxl` 추가 (Excel 파싱용)

### Changed
- `storage-mcp`: ID 생성 방식 변경 (timestamp → UUID)
- `storage-mcp`: `_migrate()` 최적화 (프로세스당 1회 실행)
- `pyproject.toml`: Python 3.11+ 명시, 의존성 업데이트

### Fixed
- `run_simulation()`: 가입자 수 over-allocation 버그 수정
- `parse_excel()`: IndexError 방어 (컬럼 탐색 시 mask.any() 체크)
- `parse_excel()`: 필수 컬럼 누락 시 명시적 에러
- `schema_down.sql`: `simulation_scenarios` DROP 누락 수정
- `USAGE.md`: `calculate_winback()` 반환 타입 문서 수정 (dict → float)

---

## [0.1.0] - 2026-02-05

### Added
- 초기 요금제 설계 시스템 구현 (SKT-5)
- 4개 MCP 서버: scraper, storage, calculator, pdf
- 제조사 혜택 연장 비용 계산 기능
- Claude Skills: `/design-benefit`, `/list-designs`, `/export-pdf`, `/calculate-cost`
- 한글 폰트 자동 탐지 (macOS/Linux/Windows)
