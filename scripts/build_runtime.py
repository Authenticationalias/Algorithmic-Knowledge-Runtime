#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import sqlite3
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "runtime" / "akr.sqlite3"
SCHEMA_SQL = ROOT / "runtime" / "schema.sql"
REGISTRY = ROOT / "registry" / "registry.yaml"

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        raise ValueError(f"Missing YAML front matter: {path}")
    meta = yaml.safe_load(match.group(1)) or {}
    return meta, text


def markdown_sections(text: str) -> list[tuple[str, str]]:
    body = FRONT_MATTER.sub("", text, count=1)
    parts = re.split(r"(?m)^#\s+(.+?)\s*$", body)
    sections: list[tuple[str, str]] = []
    if parts[0].strip():
        sections.append(("", parts[0].strip()))
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        sections.append((heading, content))
    return sections or [("", body.strip())]


def iter_assets(registry: dict[str, Any]):
    for group, asset_type in [
        ("algorithms", "algorithm"),
        ("policies", "policy"),
        ("heuristics", "heuristic"),
    ]:
        for item in registry.get(group, []) or []:
            yield asset_type, item


def build(db_path: Path) -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))

        for asset_type, reg_item in iter_assets(registry):
            path = ROOT / reg_item["path"]
            meta, text = read_front_matter(path)

            asset_id = meta.get("id", reg_item["id"])
            name = meta.get("name", reg_item["name"])
            version = str(meta.get("version", reg_item.get("version", "0.0.0")))
            status = meta.get("status", reg_item.get("status", "draft"))

            conn.execute(
                """INSERT INTO assets
                   (id, asset_type, name, version, status, path, canonical_sha256)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    asset_id,
                    asset_type,
                    name,
                    version,
                    status,
                    reg_item["path"],
                    sha256_text(text),
                ),
            )

            for domain in reg_item.get("domain", meta.get("domain", [])) or []:
                conn.execute(
                    "INSERT OR IGNORE INTO domains(asset_id, domain) VALUES (?, ?)",
                    (asset_id, domain),
                )

            for trigger in reg_item.get("triggers", []) or []:
                conn.execute(
                    "INSERT INTO triggers(asset_id, trigger_text) VALUES (?, ?)",
                    (asset_id, trigger),
                )

            for required in reg_item.get("requires", meta.get("requires", [])) or []:
                # Dependency rows are inserted after all assets exist.
                pass

            for ordinal, (heading, body) in enumerate(markdown_sections(text), start=1):
                conn.execute(
                    "INSERT INTO sections(asset_id, ordinal, heading, body) VALUES (?, ?, ?, ?)",
                    (asset_id, ordinal, heading, body),
                )
                conn.execute(
                    "INSERT INTO sections_fts(asset_id, heading, body) VALUES (?, ?, ?)",
                    (asset_id, heading, body),
                )

        for asset_type, reg_item in iter_assets(registry):
            for required in reg_item.get("requires", []) or []:
                conn.execute(
                    "INSERT INTO dependencies(asset_id, required_asset_id) VALUES (?, ?)",
                    (reg_item["id"], required),
                )

        conn.execute(
            "INSERT INTO build_metadata(key, value) VALUES (?, ?)",
            ("registry_sha256", sha256_text(REGISTRY.read_text(encoding="utf-8"))),
        )
        conn.execute(
            "INSERT INTO build_metadata(key, value) VALUES (?, ?)",
            ("schema_version", str(registry.get("registry_version", "unknown"))),
        )
        conn.commit()
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_DB)
    args = parser.parse_args()
    build(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
