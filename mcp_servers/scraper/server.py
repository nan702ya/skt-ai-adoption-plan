from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP


SAMSUNG_BENEFITS_URL = "https://www.samsungsvc.co.kr/solution/3195073"
APPLE_BENEFITS_URL = "https://offers.applemusic.apple/six-month-offer-devices"
T_WORLD_PLANS_URL = "https://www.tworld.co.kr/web/product/callplan/NA00008719"

mcp = FastMCP("scraper-mcp")


def _fetch_html(url: str) -> tuple[Optional[str], str]:
    """Fetch HTML from URL. Returns (html, status)."""
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text, "ok"
    except httpx.TimeoutException:
        return None, "timeout"
    except httpx.HTTPStatusError as e:
        return None, f"http_{e.response.status_code}"
    except Exception as e:
        return None, f"error_{type(e).__name__}"


def _page_title(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    return title


@mcp.tool()
def scrape_samsung_benefits() -> List[Dict[str, Any]]:
    """삼성 사전예약 혜택을 가져와 표준 스키마로 반환.

    NOTE: MVP stub implementation. Benefit data is hardcoded based on
    Galaxy S25 pre-order (2025.01). Real parsing to be implemented in Phase 2.
    """
    html, fetch_status = _fetch_html(SAMSUNG_BENEFITS_URL)
    title = _page_title(html) if html else None
    return [
        {
            "manufacturer": "Samsung",
            "name": "Google One AI Premium",
            "free_months": 6,
            "monthly_price_krw": 29000,
            "notes": "Gemini Advanced + 2TB 포함",
            "source_url": SAMSUNG_BENEFITS_URL,
            "source_title": title,
            "fetch_status": fetch_status,
            "data_source": "hardcoded_mvp",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    ]


@mcp.tool()
def scrape_apple_benefits() -> List[Dict[str, Any]]:
    """애플 사전예약 혜택을 가져와 표준 스키마로 반환.

    NOTE: MVP stub implementation. Benefit data is hardcoded based on
    iPhone 16 pre-order (2024.09). Real parsing to be implemented in Phase 2.
    """
    html, fetch_status = _fetch_html(APPLE_BENEFITS_URL)
    title = _page_title(html) if html else None
    return [
        {
            "manufacturer": "Apple",
            "name": "Apple Music (Personal)",
            "free_months": 6,
            "monthly_price_krw": 10900,
            "notes": "개인 요금제 기준",
            "source_url": APPLE_BENEFITS_URL,
            "source_title": title,
            "fetch_status": fetch_status,
            "data_source": "hardcoded_mvp",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
        {
            "manufacturer": "Apple",
            "name": "Apple Music (Family)",
            "free_months": 6,
            "monthly_price_krw": 16900,
            "notes": "가족 결합 추가 혜택",
            "source_url": APPLE_BENEFITS_URL,
            "source_title": title,
            "fetch_status": fetch_status,
            "data_source": "hardcoded_mvp",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    ]


@mcp.tool()
def scrape_skt_plans() -> List[Dict[str, Any]]:
    """T-world 5GX 요금제 정보를 가져와 표준 스키마로 반환.

    NOTE: MVP stub implementation. Plan data is hardcoded based on
    T-world (2025.02). Real parsing to be implemented in Phase 2.
    """
    html, fetch_status = _fetch_html(T_WORLD_PLANS_URL)
    title = _page_title(html) if html else None
    base_data = {
        "source_url": T_WORLD_PLANS_URL,
        "source_title": title,
        "fetch_status": fetch_status,
        "data_source": "hardcoded_mvp",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    return [
        {
            "name": "5GX 플래티넘(넷플릭스)",
            "monthly_fee_krw": 93750,
            "included_benefits": ["Netflix Premium"],
            "notes": "선택약정 기준",
            **base_data,
        },
        {
            "name": "5GX 프라임플러스(넷플릭스)",
            "monthly_fee_krw": 0,
            "included_benefits": ["Netflix Standard"],
            "notes": "월정액 미정",
            **base_data,
        },
        {
            "name": "5GX 프라임(넷플릭스)",
            "monthly_fee_krw": 0,
            "included_benefits": ["Netflix Standard"],
            "notes": "월정액 미정",
            **base_data,
        },
        {
            "name": "5GX 프리미엄(넷플릭스)",
            "monthly_fee_krw": 0,
            "included_benefits": ["Netflix Premium"],
            "notes": "월정액 미정",
            **base_data,
        },
    ]


if __name__ == "__main__":
    mcp.run()
