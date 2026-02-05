A different team lead within the company has reviewed the current code/implementation and provided findings below. Important context:

- **They have less context than you** on this project's history and decisions
- **You are the team lead** - don't accept findings at face value
- Your job is to critically evaluate each finding

Findings from peer review:

[PASTE FEEDBACK FROM OTHER MODEL]
✅ Looks Good
simulation-mcp의 estimate_migration_rates / calculate_winback / run_simulation 로직이 주석과 함께 잘 정리되어 있고, 파라미터·리턴 구조가 명확함.
storage-mcp의 설계/시나리오용 _validate_* 함수로 기본 입력 검증을 분리한 점이 유지보수에 유리함.
pdf-mcp에서 한글 폰트 자동 탐지 + 공통 섹션 렌더링 헬퍼(_section, _scenario_table)로 재사용 가능하게 구성된 점이 좋음.
SimulationResult/SimulationScenario 모델이 to_dict/from_dict 쌍으로 직렬화 책임을 잘 캡슐화하고 있어, MCP payload와의 경계가 명확함.
⚠️ Issues Found
[MEDIUM] mcp_servers/simulation/server.py:20-68 – parse_excel의 컬럼 탐색 로직이 다소 취약
문제:
"가입자수"/"subscribers" 판별 시 df.columns.str.contains("가입자|subscriber", case=False)[0]를 바로 인덱싱해 사용하고 있어, 매칭되는 컬럼이 하나도 없을 경우 IndexError 가능성이 있음.
"arpu" 체크도 if "arpu" in df.columns.str.lower()처럼 쓰고 있어 가독성이 떨어지고(동일 로직이 여러 번 등장), 잘못된 컬럼명/복수 컬럼이 있을 때 어떤 컬럼을 쓰는지 명확하지 않음.
Fix:
contains 결과를 변수로 받아 길이를 먼저 체크한 뒤, 0번째를 사용하는 패턴으로 통일하는 편이 안전함. 예를 들어:
    mask = df.columns.str.contains("가입자|subscriber", case=False)    if mask.any():        col = df.columns[mask][0]        plan["subscribers"] = int(row.get(col, 0))
"arpu", "데이터" 등도 동일한 패턴으로 정리하고, 필수/선택 컬럼 리스트를 상수로 빼서 재사용하면 유지보수성이 높아짐.
[MEDIUM] mcp_servers/simulation/server.py:243-252 – compare_scenarios가 사실상 더미 구현
문제: 현재는 단순 메시지 반환만 하고 있어, 이름(compare_scenarios)이 암시하는 기능(실제 지표 비교)과 구현이 괴리됨. 나중에 호출 측에서 “비교 결과”를 기대하고 사용할 경우 혼란을 줄 수 있음.
Fix:
최소한 함수 docstring에 “comparison logic is not implemented, client must fetch scenarios and compare manually”와 같은 경고를 좀 더 강하게 적거나, 함수명을 describe_comparison_inputs 등으로 바꾸는 것을 고려.
또는 storage-mcp의 get_scenario를 호출하는 비교 로직을 간단하게라도 구현해 두는 것이 좋음.
[LOW] mcp_servers/storage/server.py:25-31 – 모든 호출에서 _migrate()를 매번 수행
문제: 현재 규모에서는 큰 이슈는 아니지만, 트래픽이 늘면 매 호출마다 schema 스크립트를 실행하는 것은 낭비일 수 있음.
Fix:
간단히 “마이그레이션 완료 플래그”를 모듈 전역에 두고 한 프로세스 생명주기 동안 한 번만 실행되도록 변경을 검토할 수 있음 (예: _MIGRATED = False 플래그 체크).
[LOW] mcp_servers/simulation/server.py:171-240 – 시뮬레이션 로직의 가정값이 하드코딩되어 있음
문제: total_subscribers 기본값(100만), avg_arpu 기본값(50,000원), Win-back에서 “전체의 10%가 MVNO에서 복귀 가능” 등 비즈니스적으로 민감한 상수들이 코드에 직접 박혀 있어, 운영 중 튜닝/실험이 어려움.
Fix:
최소한 이 값들을 모듈 상단 상수로 끌어올리고, docstring에 “MVP 가정값”임을 명시.
가능하다면 추후 환경 변수나 설정 파일(예: config.py 또는 SQLite 테이블)을 통해 주입받을 수 있도록 확장 여지를 남겨두는 것이 좋음.
📊 Summary
Files reviewed: 4 (simulation/server.py, storage/server.py, pdf/server.py, src/models/simulation.py)
Critical issues: 0
Warnings: 4 (MEDIUM 2, LOW 2)


Findings (ordered by severity)

High: run_simulation() can over‑allocate subscribers when only some plans have explicit subscriber counts. For plans missing subscribers, it assigns total_subscribers // len(current_plans) per plan, which inflates totals if other plans already have non‑zero subscribers. This distorts migration, revenue, and ARPU impact. File: server.py.
Medium: calculate_winback() returns a float, but the docs claim it returns a dict like {"winback_rate": 0.15}. That breaks consumer expectations. Either return the dict or update the docs. File: server.py, USAGE.md.
Medium: schema_down.sql only drops plan_designs but not simulation_scenarios. If this is meant to be a down migration, it’s incomplete and potentially confusing. File: schema_down.sql.
Medium: save_design() and save_scenario() IDs are based on int(datetime.now().timestamp()), which is only second‑precision and can collide under concurrent writes, leading to silent overwrite via INSERT OR REPLACE. File: server.py.
Low: parse_excel() silently proceeds even if required columns are missing after English mapping. That can produce empty name/monthly_fee_krw values with no error. Consider explicit validation and a clear exception. File: server.py.
Low: Scraper MCP outputs are hardcoded; you do include fetch_status and data_source, which is good, but this still risks stale data being treated as current by downstream tools. Worth a clear warning in docs or return shape to force acknowledgment. File: server.py.
Open questions / assumptions

For run_simulation(), should we treat missing subscribers as “unknown” and only distribute remaining subscribers rather than the full total?
Do you want calculate_winback() to return a float or a structured dict for consistency with other tools?

---

For EACH finding above:

1. **Verify it exists** - Actually check the code. Does this issue/bug really exist?
2. **If it doesn't exist** - Explain clearly why (maybe it's already handled, or they misunderstood the architecture)
3. **If it does exist** - Assess severity and add to your fix plan

After analysis, provide:
- Summary of valid findings (confirmed issues)
- Summary of invalid findings (with explanations)
- Prioritized action plan for confirmed issues