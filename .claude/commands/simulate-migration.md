# 가입자 이동 시뮬레이션

신규 저가 요금제에 대한 가입자 이동 시뮬레이션을 실행합니다. 보수/기준/낙관 3개 시나리오를 생성하고 ARPU 영향도를 분석합니다.

## 워크플로우

1. **데이터 입력**: Excel 파일 경로 또는 가정값 입력
2. **현재 요금제 파싱**: `parse_excel()` 또는 가정값 사용
3. **이동 확률 추정**: `estimate_migration_rates()` → 사용자 확인/조정
4. **Win-back 계산**: `calculate_winback()` 실행
5. **3개 시나리오 생성**: 보수/기준/낙관 시나리오 각각 생성
6. **시뮬레이션 실행**: `run_simulation()` 각 시나리오별 실행
7. **저장**: `save_scenario()` 각 시나리오 저장
8. **고가 요금제 옵션**: 사용자 확인 후 포함 여부 결정

## 사용 가능한 MCP 도구

### simulation-mcp
- `parse_excel(file_path)`: Excel 파일 파싱
- `estimate_migration_rates(current_plans, new_plan, scenario_type)`: 이동 확률 추정
- `calculate_winback(new_plan, mvno_benchmark)`: Win-back 효과 계산
- `run_simulation(scenario, current_plans, total_subscribers, avg_arpu)`: 시뮬레이션 실행

### storage-mcp
- `save_scenario(scenario)`: 시나리오 저장
- `list_scenarios()`: 저장된 시나리오 목록 조회

## 시나리오 타입

- **conservative (보수적)**: 이동 확률 0.7배, 낮은 Win-back
- **base (기준)**: 기본 추정값 사용
- **optimistic (낙관적)**: 이동 확률 1.3배, 높은 Win-back

## 입력 데이터 형식

### Excel 파일 (선택)
```
| 요금제명 | 월정액 | 데이터구간 | 가입자수 | ARPU | 주요앱 |
```

### 가정값 (Excel 없을 경우)
- 전체 가입자 수: 1,000,000명 (기본값)
- 평균 ARPU: 50,000원 (기본값)
- 현재 요금제 리스트: 사용자 입력 또는 기본값

## 시뮬레이션 결과

각 시나리오별로 다음 결과 산출:
- ARPU 변화율 (%)
- 연간 매출 영향 (원)
- 신규 가입자 수
- 다운그레이드 가입자 수
- Win-back 가입자 수

## 응답 형식

```
시뮬레이션 완료: 3개 시나리오 생성

[보수적 시나리오]
- ARPU 변화: -X.XX%
- 연간 매출 영향: -XXX,XXX,XXX원
- 신규 가입자: XX,XXX명
- 다운그레이드: XX,XXX명
- Win-back: X,XXX명

[기준 시나리오]
...

[낙관적 시나리오]
...

다음 단계: /export-simulation-report로 리포트 생성
```

## 인자

$ARGUMENTS: 
- Excel 파일 경로 (선택): "data/sample_subscribers.xlsx"
- 신규 요금제 스펙 (필수): RatePlanSpec dict 또는 design_id
- 전체 가입자 수 (선택): 기본값 1,000,000
- 평균 ARPU (선택): 기본값 50,000원
