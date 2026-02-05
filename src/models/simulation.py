from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from .rate_plan import RatePlanSpec


@dataclass(frozen=True)
class SimulationResult:
    """시뮬레이션 결과"""
    arpu_change_pct: float  # ARPU 변화율 (%)
    annual_revenue_impact_krw: int  # 연간 매출 영향 (원)
    new_subscribers: int  # 신규 가입자 수
    downgrade_subscribers: int  # 다운그레이드 가입자 수
    winback_subscribers: int  # Win-back 가입자 수

    def to_dict(self) -> Dict[str, Any]:
        return {
            "arpu_change_pct": self.arpu_change_pct,
            "annual_revenue_impact_krw": self.annual_revenue_impact_krw,
            "new_subscribers": self.new_subscribers,
            "downgrade_subscribers": self.downgrade_subscribers,
            "winback_subscribers": self.winback_subscribers,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SimulationResult":
        return SimulationResult(
            arpu_change_pct=float(data["arpu_change_pct"]),
            annual_revenue_impact_krw=int(data["annual_revenue_impact_krw"]),
            new_subscribers=int(data["new_subscribers"]),
            downgrade_subscribers=int(data["downgrade_subscribers"]),
            winback_subscribers=int(data["winback_subscribers"]),
        )


@dataclass(frozen=True)
class SimulationScenario:
    """시뮬레이션 시나리오"""
    scenario_id: str
    scenario_type: str  # "conservative" | "base" | "optimistic"
    new_plan: RatePlanSpec
    premium_plan: Optional[RatePlanSpec]  # 고가 요금제 옵션
    migration_rates: Dict[str, float]  # 요금제별 이동 확률
    winback_rate: float
    results: SimulationResult
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_type": self.scenario_type,
            "new_plan": self.new_plan.to_dict(),
            "premium_plan": self.premium_plan.to_dict() if self.premium_plan else None,
            "migration_rates": self.migration_rates,
            "winback_rate": self.winback_rate,
            "results": self.results.to_dict(),
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SimulationScenario":
        return SimulationScenario(
            scenario_id=str(data["scenario_id"]),
            scenario_type=str(data["scenario_type"]),
            new_plan=RatePlanSpec.from_dict(data["new_plan"]),
            premium_plan=RatePlanSpec.from_dict(data["premium_plan"]) if data.get("premium_plan") else None,
            migration_rates=dict(data["migration_rates"]),
            winback_rate=float(data["winback_rate"]),
            results=SimulationResult.from_dict(data["results"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
        )
