from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "rate_plans.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

mcp = FastMCP("storage-mcp")


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _migrate() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with _connect() as connection:
        connection.executescript(schema)
        connection.commit()


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
    design_id = str(design.get("design_id") or f"design_{int(datetime.now().timestamp())}")
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


if __name__ == "__main__":
    mcp.run()
