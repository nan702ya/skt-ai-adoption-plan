from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from .benefit import Benefit
from .rate_plan import RatePlan


@dataclass(frozen=True)
class PlanDesign:
    design_id: str
    manufacturer: str
    rate_plan: RatePlan
    benefit: Benefit
    term_months: int
    discount_type: str
    created_at: datetime
    memo: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "design_id": self.design_id,
            "manufacturer": self.manufacturer,
            "rate_plan": self.rate_plan.to_dict(),
            "benefit": self.benefit.to_dict(),
            "term_months": self.term_months,
            "discount_type": self.discount_type,
            "created_at": self.created_at.isoformat(),
            "memo": self.memo,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PlanDesign":
        return PlanDesign(
            design_id=str(data["design_id"]),
            manufacturer=str(data["manufacturer"]),
            rate_plan=RatePlan.from_dict(data["rate_plan"]),
            benefit=Benefit.from_dict(data["benefit"]),
            term_months=int(data["term_months"]),
            discount_type=str(data["discount_type"]),
            created_at=datetime.fromisoformat(str(data["created_at"])),
            memo=data.get("memo"),
        )
