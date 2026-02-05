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

-- Schema for simulation_scenarios table
CREATE TABLE IF NOT EXISTS simulation_scenarios (
  scenario_id TEXT PRIMARY KEY,
  scenario_type TEXT NOT NULL,
  new_plan_json TEXT NOT NULL,
  premium_plan_json TEXT,
  migration_rates_json TEXT NOT NULL,
  winback_rate REAL NOT NULL,
  results_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_simulation_scenarios_created_at
  ON simulation_scenarios (created_at);

CREATE INDEX IF NOT EXISTS idx_simulation_scenarios_type
  ON simulation_scenarios (scenario_type);
