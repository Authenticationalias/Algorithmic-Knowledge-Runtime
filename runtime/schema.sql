-- AKR derived runtime schema.
-- Canonical authority remains Markdown/YAML in the repository.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  asset_type TEXT NOT NULL CHECK(asset_type IN ('algorithm','policy','heuristic')),
  name TEXT NOT NULL,
  version TEXT NOT NULL,
  status TEXT NOT NULL,
  path TEXT NOT NULL UNIQUE,
  canonical_sha256 TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS domains (
  asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  domain TEXT NOT NULL,
  PRIMARY KEY(asset_id, domain)
);

CREATE TABLE IF NOT EXISTS triggers (
  asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  trigger_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dependencies (
  asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  required_asset_id TEXT NOT NULL REFERENCES assets(id),
  PRIMARY KEY(asset_id, required_asset_id)
);

CREATE TABLE IF NOT EXISTS sections (
  asset_id TEXT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  ordinal INTEGER NOT NULL,
  heading TEXT,
  body TEXT NOT NULL,
  PRIMARY KEY(asset_id, ordinal)
);

CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
  asset_id UNINDEXED,
  heading,
  body
);

CREATE TABLE IF NOT EXISTS build_metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
