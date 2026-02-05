from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RatePlan:
    name: str
    monthly_fee_krw: int
    included_benefits: List[str]
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "monthly_fee_krw": self.monthly_fee_krw,
            "included_benefits": list(self.included_benefits),
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "RatePlan":
        return RatePlan(
            name=str(data["name"]),
            monthly_fee_krw=int(data["monthly_fee_krw"]),
            included_benefits=list(data.get("included_benefits", [])),
            notes=data.get("notes"),
        )
