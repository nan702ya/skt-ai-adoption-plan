from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from mcp.server.fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "rate_plans.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

mcp = FastMCP("storage-mcp")

# P2 Fix: 마이그레이션 플래그
_MIGRATED = False


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _migrate() -> None:
    global _MIGRATED
    if _MIGRATED:
        return
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with _connect() as connection:
        connection.executescript(schema)
        connection.commit()
    _MIGRATED = True


def _generate_id(prefix: str) -> str:
    """P2 Fix: UUID 기반 고유 ID 생성"""
    return f"{prefix}_{uuid4().hex[:12]}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_design(design: Dict[str, Any]) -> None:
    """Validate required fields in design dict."""
    required = ["manufacturer", "rate_plan", "benefit", "term_months"]
    missing = [k for k in required if k not in design]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    if not isinstance(design.get("rate_plan"), dict):
        raise ValueError("rate_plan must be a dict")
    if not isinstance(design.get("benefit"), dict):
        raise ValueError("benefit must be a dict")


@mcp.tool()
def save_design(design: Dict[str, Any]) -> Dict[str, Any]:
    """요금제 설계 저장.

    Required fields: manufacturer, rate_plan (dict), benefit (dict), term_months
    Optional fields: design_id, discount_type, created_at, memo
    """
    _validate_design(design)
    _migrate()
    design_id = str(design.get("design_id") or _generate_id("design"))
    payload = {
        "design_id": design_id,
        "manufacturer": str(design["manufacturer"]),
        "rate_plan_json": json.dumps(design["rate_plan"], ensure_ascii=False),
        "benefit_json": json.dumps(design["benefit"], ensure_ascii=False),
        "term_months": int(design["term_months"]),
        "discount_type": design.get("discount_type", "선택약정"),
        "created_at": design.get("created_at", _now_iso()),
        "memo": design.get("memo"),
    }

    with _connect() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO plan_designs
              (design_id, manufacturer, rate_plan_json, benefit_json,
               term_months, discount_type, created_at, memo)
            VALUES
              (:design_id, :manufacturer, :rate_plan_json, :benefit_json,
               :term_months, :discount_type, :created_at, :memo)
            """,
            payload,
        )
        connection.commit()

    return {"design_id": design_id}


@mcp.tool()
def list_designs() -> List[Dict[str, Any]]:
    """설계 목록 조회."""
    _migrate()
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT design_id, manufacturer, term_months, discount_type, created_at, memo
            FROM plan_designs
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


@mcp.tool()
def get_design(design_id: str) -> Optional[Dict[str, Any]]:
    """설계 상세 조회."""
    _migrate()
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM plan_designs
            WHERE design_id = ?
            """,
            (design_id,),
        ).fetchone()

    if row is None:
        return None

    return {
        "design_id": row["design_id"],
        "manufacturer": row["manufacturer"],
        "rate_plan": json.loads(row["rate_plan_json"]),
        "benefit": json.loads(row["benefit_json"]),
        "term_months": row["term_months"],
        "discount_type": row["discount_type"],
        "created_at": row["created_at"],
        "memo": row["memo"],
    }


@mcp.tool()
def delete_design(design_id: str) -> Dict[str, Any]:
    """설계 삭제."""
    _migrate()
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM plan_designs WHERE design_id = ?",
            (design_id,),
        )
        connection.commit()

    return {"deleted": cursor.rowcount > 0}


def _validate_scenario(scenario: Dict[str, Any]) -> None:
    """Validate required fields in scenario dict."""
    required = ["scenario_type", "new_plan", "migration_rates", "winback_rate", "results"]
    missing = [k for k in required if k not in scenario]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    if not isinstance(scenario.get("new_plan"), dict):
        raise ValueError("new_plan must be a dict")
    if not isinstance(scenario.get("migration_rates"), dict):
        raise ValueError("migration_rates must be a dict")
    if not isinstance(scenario.get("results"), dict):
        raise ValueError("results must be a dict")


@mcp.tool()
def save_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """시뮬레이션 시나리오 저장.

    Required fields: scenario_type, new_plan (dict), migration_rates (dict),
                     winback_rate, results (dict)
    Optional fields: scenario_id, premium_plan (dict), created_at
    """
    _validate_scenario(scenario)
    _migrate()
    scenario_id = str(scenario.get("scenario_id") or _generate_id("scenario"))
    payload = {
        "scenario_id": scenario_id,
        "scenario_type": str(scenario["scenario_type"]),
        "new_plan_json": json.dumps(scenario["new_plan"], ensure_ascii=False),
        "premium_plan_json": json.dumps(scenario["premium_plan"], ensure_ascii=False) if scenario.get("premium_plan") else None,
        "migration_rates_json": json.dumps(scenario["migration_rates"], ensure_ascii=False),
        "winback_rate": float(scenario["winback_rate"]),
        "results_json": json.dumps(scenario["results"], ensure_ascii=False),
        "created_at": scenario.get("created_at", _now_iso()),
    }

    with _connect() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO simulation_scenarios
              (scenario_id, scenario_type, new_plan_json, premium_plan_json,
               migration_rates_json, winback_rate, results_json, created_at)
            VALUES
              (:scenario_id, :scenario_type, :new_plan_json, :premium_plan_json,
               :migration_rates_json, :winback_rate, :results_json, :created_at)
            """,
            payload,
        )
        connection.commit()

    return {"scenario_id": scenario_id}


@mcp.tool()
def list_scenarios() -> List[Dict[str, Any]]:
    """시나리오 목록 조회."""
    _migrate()
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT scenario_id, scenario_type, winback_rate, created_at
            FROM simulation_scenarios
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


@mcp.tool()
def get_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
    """시나리오 상세 조회."""
    _migrate()
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM simulation_scenarios
            WHERE scenario_id = ?
            """,
            (scenario_id,),
        ).fetchone()

    if row is None:
        return None

    result = {
        "scenario_id": row["scenario_id"],
        "scenario_type": row["scenario_type"],
        "new_plan": json.loads(row["new_plan_json"]),
        "migration_rates": json.loads(row["migration_rates_json"]),
        "winback_rate": row["winback_rate"],
        "results": json.loads(row["results_json"]),
        "created_at": row["created_at"],
    }
    if row["premium_plan_json"]:
        result["premium_plan"] = json.loads(row["premium_plan_json"])
    return result


@mcp.tool()
def delete_scenario(scenario_id: str) -> Dict[str, Any]:
    """시나리오 삭제."""
    _migrate()
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM simulation_scenarios WHERE scenario_id = ?",
            (scenario_id,),
        )
        connection.commit()

    return {"deleted": cursor.rowcount > 0}


if __name__ == "__main__":
    mcp.run()
