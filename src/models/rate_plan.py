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


@dataclass(frozen=True)
class RatePlanSpec:
    """5G 저가 요금제 상세 스펙"""
    name: str
    monthly_fee_krw: int
    data_gb: float  # 기본 데이터 (GB)
    voice_minutes: int  # 음성 (분), -1 = 무제한
    sms_count: int  # 문자 (건), -1 = 무제한
    throttle_speed_kbps: int  # 소진 후 속도제한 (Kbps)
    target_segment: str  # "general" | "youth" | "senior"
    channel: str  # "online" | "offline" | "both"
    included_benefits: List[str]
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "monthly_fee_krw": self.monthly_fee_krw,
            "data_gb": self.data_gb,
            "voice_minutes": self.voice_minutes,
            "sms_count": self.sms_count,
            "throttle_speed_kbps": self.throttle_speed_kbps,
            "target_segment": self.target_segment,
            "channel": self.channel,
            "included_benefits": list(self.included_benefits),
            "notes": self.notes,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "RatePlanSpec":
        return RatePlanSpec(
            name=str(data["name"]),
            monthly_fee_krw=int(data["monthly_fee_krw"]),
            data_gb=float(data["data_gb"]),
            voice_minutes=int(data["voice_minutes"]),
            sms_count=int(data["sms_count"]),
            throttle_speed_kbps=int(data["throttle_speed_kbps"]),
            target_segment=str(data["target_segment"]),
            channel=str(data["channel"]),
            included_benefits=list(data.get("included_benefits", [])),
            notes=data.get("notes"),
        )
