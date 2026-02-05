from __future__ import annotations

from typing import Any, Dict

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("calculator-mcp")


def _extension_months(term_months: int, free_months: int) -> int:
    return max(0, term_months - free_months)


@mcp.tool()
def calculate_extension_cost(
    monthly_price_krw: int,
    free_months: int,
    term_months: int,
) -> Dict[str, Any]:
    """혜택 연장 비용 계산."""
    extension_months = _extension_months(term_months, free_months)
    total_cost = int(monthly_price_krw) * extension_months
    return {
        "extension_months": extension_months,
        "total_cost_krw": total_cost,
    }


@mcp.tool()
def compare_with_existing(
    extension_total_cost_krw: int,
    existing_total_cost_krw: int,
) -> Dict[str, Any]:
    """기존 제휴 요금제 대비 비용 비교."""
    difference = int(extension_total_cost_krw) - int(existing_total_cost_krw)
    if difference < 0:
        result = "extension_cheaper"
    elif difference > 0:
        result = "existing_cheaper"
    else:
        result = "same_cost"

    return {
        "difference_krw": difference,
        "result": result,
    }


@mcp.tool()
def calculate_savings(
    existing_total_cost_krw: int,
    proposed_total_cost_krw: int,
) -> Dict[str, Any]:
    """절감액 산출."""
    savings = int(existing_total_cost_krw) - int(proposed_total_cost_krw)
    return {
        "savings_krw": savings,
        "is_saving": savings > 0,
    }


if __name__ == "__main__":
    mcp.run()
