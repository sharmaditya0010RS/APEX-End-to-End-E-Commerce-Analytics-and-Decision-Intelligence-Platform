CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    rows_processed BIGINT,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_name_started
ON audit.pipeline_runs (pipeline_name, started_at DESC);
