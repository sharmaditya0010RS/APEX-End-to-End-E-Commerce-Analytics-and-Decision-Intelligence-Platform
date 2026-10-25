CREATE TABLE IF NOT EXISTS audit.source_loads (
    source_file TEXT PRIMARY KEY,
    source_sha256 TEXT NOT NULL,
    expected_rows BIGINT NOT NULL,
    loaded_rows BIGINT NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
