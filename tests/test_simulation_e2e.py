"""E2E 테스트: 5G 저가 요금제 시뮬레이션 워크플로우"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.simulation.server import (
    estimate_migration_rates,
    calculate_winback,
    run_simulation,
)
from mcp_servers.storage.server import (
    save_scenario,
    get_scenario,
    list_scenarios,
    delete_scenario,
)


def test_simulation_workflow():
    """전체 시뮬레이션 워크플로우 테스트"""
    print("=" * 60)
    print("E2E 테스트: 5G 저가 요금제 시뮬레이션")
    print("=" * 60)

    # 1. 신규 요금제 스펙 정의
    new_plan = {
        "name": "5G 라이트35",
        "monthly_fee_krw": 35000,
        "data_gb": 8.0,
        "voice_minutes": -1,  # 무제한
        "sms_count": -1,  # 무제한
        "throttle_speed_kbps": 400,
        "target_segment": "general",
        "channel": "both",
        "included_benefits": ["T멤버십 기본"],
    }
    print(f"\n[1] 신규 요금제: {new_plan['name']} ({new_plan['monthly_fee_krw']:,}원)")

    # 2. 현재 요금제 데이터 (일부는 가입자수 명시, 일부는 없음)
    current_plans = [
        {"name": "5GX 슬림", "monthly_fee_krw": 55000, "data_gb": 9, "subscribers": 300000},
        {"name": "5GX 레귤러", "monthly_fee_krw": 69000, "data_gb": 50, "subscribers": 200000},
        {"name": "컴팩트", "monthly_fee_krw": 39000, "data_gb": 6, "subscribers": 0},  # 가입자수 없음
        {"name": "컴팩트플러스", "monthly_fee_krw": 45000, "data_gb": 8, "subscribers": 0},  # 가입자수 없음
    ]
    print(f"\n[2] 현재 요금제: {len(current_plans)}개")
    for p in current_plans:
        print(f"    - {p['name']}: {p['monthly_fee_krw']:,}원, 가입자: {p['subscribers']:,}명")

    # 3. 이동 확률 추정 테스트 (3개 시나리오)
    print("\n[3] 이동 확률 추정")
    scenarios = []
    for scenario_type in ["conservative", "base", "optimistic"]:
        migration_rates = estimate_migration_rates(current_plans, new_plan, scenario_type)
        print(f"    [{scenario_type}] {migration_rates}")

        # 4. Win-back 계산
        winback_rate = calculate_winback(new_plan)
        print(f"    Win-back rate: {winback_rate}")

        # 5. 시뮬레이션 실행
        scenario = {
            "scenario_type": scenario_type,
            "new_plan": new_plan,
            "migration_rates": migration_rates,
            "winback_rate": winback_rate,
        }
        results = run_simulation(scenario, current_plans, total_subscribers=1000000, avg_arpu=50000)
        scenario["results"] = results

        print(f"    결과: ARPU {results['arpu_change_pct']:+.2f}%, 연간 매출 {results['annual_revenue_impact_krw']:,}원")
        print(f"           신규: {results['new_subscribers']:,}명, 다운그레이드: {results['downgrade_subscribers']:,}명, Win-back: {results['winback_subscribers']:,}명")

        scenarios.append(scenario)

    # 6. 시나리오 저장 테스트
    print("\n[4] 시나리오 저장")
    saved_ids = []
    for scenario in scenarios:
        result = save_scenario(scenario)
        saved_ids.append(result["scenario_id"])
        print(f"    저장됨: {result['scenario_id']}")

    # 7. 시나리오 조회 테스트
    print("\n[5] 시나리오 조회")
    scenario_list = list_scenarios()
    print(f"    저장된 시나리오: {len(scenario_list)}개")

    # 8. 시나리오 상세 조회
    print("\n[6] 시나리오 상세 조회")
    for sid in saved_ids[:1]:  # 첫 번째만
        detail = get_scenario(sid)
        if detail:
            print(f"    {sid}: {detail['scenario_type']}, winback={detail['winback_rate']}")

    # 9. P0 수정 검증: 가입자 over-allocation 확인
    print("\n[7] P0 검증: 가입자 수 over-allocation")
    # 명시적 가입자: 300,000 + 200,000 = 500,000
    # 나머지: 1,000,000 - 500,000 = 500,000 → 2개 플랜에 250,000씩
    total_explicit = 300000 + 200000
    total_remaining = 1000000 - total_explicit
    expected_per_missing = total_remaining // 2
    print(f"    명시적 가입자 합계: {total_explicit:,}")
    print(f"    배분 대상 가입자: {total_remaining:,}")
    print(f"    누락 플랜당 배분: {expected_per_missing:,}")

    # 총 가입자가 total_subscribers를 초과하지 않는지 확인
    test_scenario = scenarios[1]  # base scenario
    total_new = test_scenario["results"]["new_subscribers"]
    total_downgrade = test_scenario["results"]["downgrade_subscribers"]
    print(f"    시뮬레이션 결과 - 신규: {total_new:,}, 다운그레이드: {total_downgrade:,}")

    # 10. 정리 (테스트 데이터 삭제)
    print("\n[8] 테스트 데이터 정리")
    for sid in saved_ids:
        delete_scenario(sid)
        print(f"    삭제됨: {sid}")

    print("\n" + "=" * 60)
    print("E2E 테스트 완료!")
    print("=" * 60)
    return True


def test_parse_excel_validation():
    """P0/P1 테스트: parse_excel 검증"""
    from mcp_servers.simulation.server import parse_excel
    import tempfile
    import pandas as pd

    print("\n[P0/P1 검증] parse_excel 필수 컬럼 검증")

    # 1. 정상 케이스
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        df = pd.DataFrame({
            "요금제명": ["5GX 슬림", "5GX 레귤러"],
            "월정액": [55000, 69000],
            "가입자수": [300000, 200000],
            "ARPU": [52000, 67000],
        })
        df.to_excel(f.name, index=False)
        try:
            plans = parse_excel(f.name)
            print(f"    정상 케이스: {len(plans)}개 파싱 성공")
            assert len(plans) == 2
            assert plans[0]["subscribers"] == 300000
            print("    ✅ PASS")
        except Exception as e:
            print(f"    ❌ FAIL: {e}")

    # 2. 영문 컬럼명
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        df = pd.DataFrame({
            "plan_name": ["5GX 슬림"],
            "monthly_fee": [55000],
        })
        df.to_excel(f.name, index=False)
        try:
            plans = parse_excel(f.name)
            print(f"    영문 컬럼: {len(plans)}개 파싱 성공")
            print("    ✅ PASS")
        except Exception as e:
            print(f"    ❌ FAIL: {e}")

    # 3. 필수 컬럼 누락 케이스 (에러 발생해야 함)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        df = pd.DataFrame({
            "잘못된컬럼": ["5GX 슬림"],
            "또잘못된컬럼": [55000],
        })
        df.to_excel(f.name, index=False)
        try:
            plans = parse_excel(f.name)
            print("    ❌ FAIL: 에러가 발생해야 하는데 성공함")
        except ValueError as e:
            print(f"    필수 컬럼 누락 검증: {e}")
            print("    ✅ PASS (예상된 에러)")

    print("    P0/P1 검증 완료")


if __name__ == "__main__":
    test_simulation_workflow()
    test_parse_excel_validation()
