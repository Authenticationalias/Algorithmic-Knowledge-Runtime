#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "registry.yaml"
SCHEMA = ROOT / "schemas" / "algorithm.schema.json"
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def front_matter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        raise ValueError(f"Missing YAML front matter: {path}")
    return yaml.safe_load(match.group(1)) or {}


def main() -> None:
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    ids: set[str] = set()
    paths: set[str] = set()
    errors: list[str] = []

    groups = [
        ("algorithms", "algorithm"),
        ("policies", "policy"),
        ("heuristics", "heuristic"),
    ]

    entries: dict[str, dict[str, Any]] = {}

    for group, expected_type in groups:
        for item in registry.get(group, []) or []:
            aid = item["id"]
            rel = item["path"]
            path = ROOT / rel

            if aid in ids:
                errors.append(f"Duplicate ID: {aid}")
            ids.add(aid)

            if rel in paths:
                errors.append(f"Duplicate path: {rel}")
            paths.add(rel)

            if not path.exists():
                errors.append(f"Missing canonical file: {rel}")
                continue

            try:
                meta = front_matter(path)
            except Exception as exc:
                errors.append(str(exc))
                continue

            entries[aid] = item
            if meta.get("id") != aid:
                errors.append(f"ID mismatch {aid}: front matter={meta.get('id')}")
            if meta.get("asset_type") != expected_type:
                errors.append(
                    f"Asset type mismatch {aid}: expected {expected_type}, "
                    f"got {meta.get('asset_type')}"
                )

            if expected_type == "algorithm":
                for err in validator.iter_errors(meta):
                    location = ".".join(str(x) for x in err.absolute_path)
                    errors.append(f"{aid} schema {location}: {err.message}")

    for aid, item in entries.items():
        for dep in item.get("requires", []) or []:
            if dep not in ids:
                errors.append(f"Unknown dependency: {aid} -> {dep}")

    # Dependency cycle check.
    graph = {aid: (entries.get(aid, {}).get("requires", []) or []) for aid in ids}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, stack: list[str]) -> None:
        if node in visiting:
            errors.append("Dependency cycle: " + " -> ".join(stack + [node]))
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep in graph:
                visit(dep, stack + [node])
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node, [])

    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors))
        raise SystemExit(1)

    print(f"OK: validated {len(ids)} registered assets")


if __name__ == "__main__":
    main()
