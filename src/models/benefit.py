from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Benefit:
    manufacturer: str
    name: str
    free_months: int
    monthly_price_krw: int
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manufacturer": self.manufacturer,
            "name": self.name,
            "free_months": self.free_months,
            "monthly_price_krw": self.monthly_price_krw,
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Benefit":
        return Benefit(
            manufacturer=str(data["manufacturer"]),
            name=str(data["name"]),
            free_months=int(data["free_months"]),
            monthly_price_krw=int(data["monthly_price_krw"]),
            notes=data.get("notes"),
        )
