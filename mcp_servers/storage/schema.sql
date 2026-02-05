-- Schema for plan_designs table
-- Note: DOWN migration (DROP TABLE) moved to schema_down.sql for manual execution

CREATE TABLE IF NOT EXISTS plan_designs (
  design_id TEXT PRIMARY KEY,
  manufacturer TEXT NOT NULL,
  rate_plan_json TEXT NOT NULL,
  benefit_json TEXT NOT NULL,
  term_months INTEGER NOT NULL,
  discount_type TEXT NOT NULL,
  created_at TEXT NOT NULL,
  memo TEXT
);

CREATE INDEX IF NOT EXISTS idx_plan_designs_created_at
  ON plan_designs (created_at);
