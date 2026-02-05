from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("simulation-mcp")

# MVNO 벤치마크 데이터 (MVP 하드코딩)
MVNO_BENCHMARK = {
    "price_krw": 30000,  # 평균 MVNO 요금
    "data_gb": 50.0,
    "quality_premium": 0.15,  # MNO 망품질/AS 프리미엄
}


@mcp.tool()
def parse_excel(file_path: str) -> List[Dict[str, Any]]:
    """Excel 파일에서 요금제 데이터 파싱.

    예상 구조:
    | 요금제명 | 월정액 | 데이터구간 | 가입자수 | ARPU | 주요앱 |
    """
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    try:
        df = pd.read_excel(file_path)
        # 컬럼명 정규화 (대소문자 무시, 공백 제거)
        df.columns = df.columns.str.strip().str.lower()

        # 필수 컬럼 확인 및 매핑
        col_mapping = {
            "요금제명": None,
            "월정액": None,
        }
        en_mapping = {"요금제명": "plan_name", "월정액": "monthly_fee"}

        for key in col_mapping:
            if key in df.columns:
                col_mapping[key] = key
            elif en_mapping[key] in df.columns:
                col_mapping[key] = en_mapping[key]

        # P1 Fix: 필수 컬럼 누락 시 명시적 에러
        missing = [k for k, v in col_mapping.items() if v is None]
        if missing:
            raise ValueError(f"필수 컬럼 누락: {missing}. 예상 컬럼: 요금제명/plan_name, 월정액/monthly_fee")

        plans = []
        for _, row in df.iterrows():
            plan = {
                "name": str(row.get(col_mapping["요금제명"], "")),
                "monthly_fee_krw": int(row.get(col_mapping["월정액"], 0)),
            }

            # P0 Fix: 선택적 필드 - 안전한 컬럼 탐색
            # 가입자수
            subscriber_mask = df.columns.str.contains("가입자|subscriber", case=False)
            if subscriber_mask.any():
                plan["subscribers"] = int(row.get(df.columns[subscriber_mask][0], 0))

            # ARPU
            arpu_mask = df.columns.str.lower() == "arpu"
            if arpu_mask.any():
                plan["arpu"] = float(row.get(df.columns[arpu_mask][0], 0))

            # 데이터
            data_mask = df.columns.str.contains("데이터|data", case=False)
            if data_mask.any():
                plan["data_gb"] = float(row.get(df.columns[data_mask][0], 0))

            plans.append(plan)

        return plans
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Excel: {str(e)}")


@mcp.tool()
def estimate_migration_rates(
    current_plans: List[Dict[str, Any]],
    new_plan: Dict[str, Any],
    scenario_type: str = "base",
) -> Dict[str, float]:
    """현재 요금제에서 신규 요금제로의 이동 확률 추정.

    Args:
        current_plans: 현재 요금제 리스트 (name, monthly_fee_krw, data_gb 등 포함)
        new_plan: 신규 요금제 스펙 (monthly_fee_krw, data_gb, target_segment 등)
        scenario_type: "conservative" | "base" | "optimistic"

    Returns:
        요금제명 -> 이동 확률 매핑
    """
    new_price = float(new_plan["monthly_fee_krw"])
    new_data_gb = float(new_plan.get("data_gb", 0))
    target_segment = new_plan.get("target_segment", "general")

    # 시나리오별 가중치
    scenario_multipliers = {
        "conservative": 0.7,
        "base": 1.0,
        "optimistic": 1.3,
    }
    multiplier = scenario_multipliers.get(scenario_type, 1.0)

    # 세그먼트별 가중치
    segment_multipliers = {
        "youth": 1.2,  # 청년층은 이동률 높음
        "general": 1.0,
        "senior": 0.8,  # 시니어층은 이동률 낮음
    }
    segment_mult = segment_multipliers.get(target_segment, 1.0)

    migration_rates = {}
    base_rate = 0.05  # 기본 이동률 5%

    for plan in current_plans:
        plan_name = str(plan["name"])
        old_price = float(plan.get("monthly_fee_krw", 0))
        avg_usage = float(plan.get("data_gb", 0))

        if old_price <= 0:
            migration_rates[plan_name] = 0.0
            continue

        # 가격 차이 기반 추정
        price_factor = (old_price - new_price) / old_price if old_price > 0 else 0
        price_factor = max(0, min(1, price_factor))  # 0~1 범위로 제한

        # 사용량 적합도 (신규 요금제 데이터량이 충분한지)
        usage_fit = 1.0 if avg_usage <= new_data_gb else 0.5

        # 이동 확률 계산
        migration_rate = base_rate * (1 + price_factor * 2) * usage_fit * multiplier * segment_mult
        migration_rate = max(0, min(1, migration_rate))  # 0~1 범위로 제한

        migration_rates[plan_name] = round(migration_rate, 4)

    return migration_rates


@mcp.tool()
def calculate_winback(
    new_plan: Dict[str, Any],
    mvno_benchmark: Optional[Dict[str, Any]] = None,
) -> float:
    """Win-back 효과 계산.

    Args:
        new_plan: 신규 요금제 스펙
        mvno_benchmark: MVNO 벤치마크 데이터 (없으면 기본값 사용)

    Returns:
        Win-back 확률 (0~1)
    """
    if mvno_benchmark is None:
        mvno_benchmark = MVNO_BENCHMARK

    new_price = float(new_plan["monthly_fee_krw"])
    mvno_price = float(mvno_benchmark.get("price_krw", 30000))
    quality_premium = float(mvno_benchmark.get("quality_premium", 0.15))

    if mvno_price <= 0:
        return 0.0

    # 가격 효익
    price_benefit = (mvno_price - new_price) / mvno_price
    price_benefit = max(0, min(1, price_benefit))  # 0~1 범위로 제한

    # Win-back 확률 = (가격 효익 + 품질 프리미엄) * 변환율
    winback_rate = (price_benefit + quality_premium) * 0.3
    winback_rate = max(0, min(1, winback_rate))  # 0~1 범위로 제한

    return round(winback_rate, 4)


@mcp.tool()
def run_simulation(
    scenario: Dict[str, Any],
    current_plans: List[Dict[str, Any]],
    total_subscribers: int = 1000000,
    avg_arpu: float = 50000.0,
) -> Dict[str, Any]:
    """시뮬레이션 실행.

    Args:
        scenario: 시나리오 데이터 (scenario_type, new_plan, migration_rates, winback_rate)
        current_plans: 현재 요금제 리스트
        total_subscribers: 전체 가입자 수 (기본값: 100만)
        avg_arpu: 평균 ARPU (기본값: 50,000원)

    Returns:
        시뮬레이션 결과 (arpu_change_pct, annual_revenue_impact_krw, 등)
    """
    new_plan = scenario["new_plan"]
    migration_rates = scenario["migration_rates"]
    winback_rate = scenario.get("winback_rate", 0.0)

    new_price = float(new_plan["monthly_fee_krw"])

    # 가입자 이동 계산
    new_subscribers = 0
    downgrade_subscribers = 0
    revenue_loss = 0.0
    revenue_gain = 0.0

    # P0 Fix: 명시적 가입자 수가 있는 플랜의 합계를 먼저 계산
    explicit_subscribers = sum(
        int(p.get("subscribers", 0)) for p in current_plans if int(p.get("subscribers", 0)) > 0
    )
    plans_without_subscribers = [p for p in current_plans if int(p.get("subscribers", 0)) <= 0]
    remaining_subscribers = max(0, total_subscribers - explicit_subscribers)

    for plan in current_plans:
        plan_name = str(plan["name"])
        old_price = float(plan.get("monthly_fee_krw", 0))
        subscribers = int(plan.get("subscribers", 0))
        migration_rate = migration_rates.get(plan_name, 0.0)

        if subscribers <= 0:
            # 가입자 수가 없으면 남은 가입자 수를 해당 플랜들로 균등 배분
            subscribers = remaining_subscribers // len(plans_without_subscribers) if plans_without_subscribers else 0

        migrating = int(subscribers * migration_rate)
        new_subscribers += migrating

        if old_price > new_price:
            # 다운그레이드
            downgrade_subscribers += migrating
            revenue_loss += migrating * (old_price - new_price)
        else:
            # 업그레이드 (드물지만)
            revenue_gain += migrating * (new_price - old_price)

    # Win-back 가입자
    winback_subscribers = int(total_subscribers * winback_rate * 0.1)  # 전체의 10%가 MVNO에서 복귀 가능
    new_subscribers += winback_subscribers
    revenue_gain += winback_subscribers * new_price

    # ARPU 변화 계산
    total_revenue_change = revenue_gain - revenue_loss
    current_total_revenue = total_subscribers * avg_arpu
    arpu_change_pct = (total_revenue_change / current_total_revenue) * 100 if current_total_revenue > 0 else 0

    # 연간 매출 영향
    annual_revenue_impact_krw = int(total_revenue_change * 12)

    return {
        "arpu_change_pct": round(arpu_change_pct, 2),
        "annual_revenue_impact_krw": annual_revenue_impact_krw,
        "new_subscribers": new_subscribers,
        "downgrade_subscribers": downgrade_subscribers,
        "winback_subscribers": winback_subscribers,
    }


@mcp.tool()
def compare_scenarios(scenario_ids: List[str]) -> Dict[str, Any]:
    """여러 시나리오 비교.

    Note: 실제 구현은 storage-mcp의 get_scenario를 호출해야 함.
    이 함수는 비교 로직만 제공합니다.
    """
    return {
        "message": "Use storage-mcp's get_scenario to fetch scenarios, then compare results",
        "scenario_ids": scenario_ids,
    }


if __name__ == "__main__":
    mcp.run()
