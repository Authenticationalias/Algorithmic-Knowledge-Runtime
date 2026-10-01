"""Bounded AKR research fixtures. This is not an adopted AKR runtime."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent


def blob_sha(text):
    raw = text.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def header(text):
    # Deliberately limited to the fixed input headers, not a general YAML reader.
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("No fixed asset header")
    result = {"requires": []}
    field = None
    for line in parts[1].splitlines():
        if line and not line.startswith(" "):
            field, _, value = line.partition(":")
            if field in ("id", "version"):
                result[field] = value.strip().strip('"')
        elif field == "requires" and line.startswith("  - "):
            result["requires"].append(line[4:].strip())
    return result


def source_assets(snapshot):
    assets = {}
    for entry in snapshot["files"]:
        if entry["path"] == "registry/registry.yaml":
            continue
        assert blob_sha(entry["content"]) == entry["git_blob_sha"]
        info = header(entry["content"])
        assert info["id"] not in assets
        assets[info["id"]] = dict(entry, **info)
    return assets


def declared_closure(seed, assets):
    pending, seen = [seed], set()
    while pending:
        asset_id = pending.pop()
        if asset_id not in seen:
            seen.add(asset_id)
            pending.extend(assets[asset_id]["requires"])
    return seen


def git(root, *args, allow_failure=False):
    env = dict(os.environ)
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_AUTHOR_DATE": "2026-10-01T00:00:00+00:00",
                "GIT_COMMITTER_DATE": "2026-10-01T00:00:00+00:00"})
    proc = subprocess.run(["git", "-C", str(root), *args],
                          text=True, capture_output=True, env=env)
    if proc.returncode and not allow_failure:
        raise RuntimeError("git " + " ".join(args) + "\n" + proc.stderr)
    return proc


def commit(root, message):
    git(root, "add", ".")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD").stdout.strip()


def mutation_cases(snapshot):
    rows = []
    with tempfile.TemporaryDirectory(prefix="akr-git-pilot-", dir="/private/tmp") as tmp:
        root = Path(tmp)
        git(root, "init", "-q", "--initial-branch=main")
        git(root, "config", "user.name", "AKR Research Fixture")
        git(root, "config", "user.email", "akr-research@example.invalid")
        for f in snapshot["files"]:
            dest = root / f["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f["content"], encoding="utf-8")
        base = commit(root, "fixed research input")
        path = "algorithms/reasoning/blind-spot-expansion/algorithm.md"
        original = (root / path).read_text()
        a_text = original.replace("## Procedure\n", "## Procedure\n\nPILOT_A_INDEPENDENT_CHANGE\n", 1)
        b_text = original + "\nPILOT_B_INDEPENDENT_CHANGE\n"
        assert a_text != original and b_text != original
        git(root, "checkout", "-q", "-b", "writer-a", base)
        (root / path).write_text(a_text)
        a = commit(root, "synthetic A change")
        git(root, "checkout", "-q", "-b", "writer-b", base)
        (root / path).write_text(b_text)
        b = commit(root, "synthetic B change from old base")

        def observe(case, target, accepted, detail):
            text = git(root, "show", target + ":" + path).stdout
            tip = git(root, "rev-parse", target).stdout.strip()
            kept = {"A": "PILOT_A_INDEPENDENT_CHANGE" in text,
                    "B": "PILOT_B_INDEPENDENT_CHANGE" in text}
            preserved_on_rejection = None if accepted else (tip == a and text == a_text)
            rows.append({"case": case, "publication_accepted": accepted,
                         "markers_retained": kept,
                         "silent_lost_update": accepted and not all(kept.values()),
                         "previous_accepted_state_preserved_on_rejection": preserved_on_rejection,
                         "common_oracle_met": all(kept.values()) if accepted else preserved_on_rejection,
                         "detail": detail})

        git(root, "update-ref", "refs/heads/accepted-old", a)
        result = git(root, "push", ".", b + ":refs/heads/accepted-old", allow_failure=True)
        observe("old_parent_non_fast_forward", "accepted-old", result.returncode == 0,
                "actual local Git push; non-fast-forward rejection")
        assert result.returncode != 0

        git(root, "update-ref", "refs/heads/accepted-current", a)
        git(root, "checkout", "-q", "-b", "writer-current", a)
        (root / path).write_text(b_text)
        current = commit(root, "current parent with stale full payload")
        git(root, "push", ".", current + ":refs/heads/accepted-current")
        observe("current_parent_stale_full_payload", "accepted-current", True,
                "fast-forward accepted; parent freshness does not establish payload freshness")

        git(root, "update-ref", "refs/heads/accepted-merge", a)
        git(root, "checkout", "-q", "-b", "writer-merge", a)
        git(root, "merge", "-q", "--no-ff", "writer-b", "-m", "merge independent changes")
        merged = git(root, "rev-parse", "HEAD").stdout.strip()
        git(root, "push", ".", merged + ":refs/heads/accepted-merge")
        observe("three_way_merge_independent_edits", "accepted-merge", True,
                "actual Git merge; independent text changes only")

        git(root, "update-ref", "refs/heads/accepted-precondition", a)
        cas = git(root, "update-ref", "refs/heads/accepted-precondition", b, base,
                  allow_failure=True)
        observe("expected_base_precondition", "accepted-precondition", cas.returncode == 0,
                "actual Git ref old-value precondition; not a semantic transaction")
        assert cas.returncode != 0

        # A is internally consistent; B introduces a caller tied to the old ID.
        git(root, "checkout", "-q", "-b", "rename-a", base)
        for relative in ("registry/registry.yaml",
                         "algorithms/governance/actor-information-value/algorithm.md",
                         "algorithms/security/secure-information-suitability/algorithm.md"):
            p = root / relative
            p.write_text(p.read_text().replace("ALG-GOV-001", "ALG-GOV-PILOT-002"))
        renamed = commit(root, "synthetic consistent ID migration")
        git(root, "checkout", "-q", "-b", "caller-b", base)
        (root / "pilot-caller.json").write_text(json.dumps({"requires": ["ALG-GOV-001"]}))
        commit(root, "synthetic new caller tied to old ID")
        git(root, "checkout", "-q", "-b", "merged-reference", renamed)
        merge = git(root, "merge", "-q", "--no-ff", "caller-b", "-m", "textually clean merge",
                    allow_failure=True)
        ids = {header(p.read_text())["id"] for p in (root / "algorithms").glob("*/*/algorithm.md")}
        needed = set(json.loads((root / "pilot-caller.json").read_text())["requires"])
        missing = sorted(needed - ids)
        assert merge.returncode == 0 and missing == ["ALG-GOV-001"]
        rows.append({"case": "clean_merge_broken_reference", "git_merge_accepted": True,
                     "missing_references": missing, "reference_oracle_met": False,
                     "detail": "structural dependency counterexample; no general meaning checker"})
    return rows


def recover(bundle_path, cache_path):
    bundle = Path(bundle_path)
    manifest_path = bundle / "manifest.json"
    if not manifest_path.exists():
        return {"status": "UNKNOWN_INTAKE", "repair_source_entries_checked": 0,
                "reason": "saved payloads do not identify intended job scope and source revision"}
    manifest = json.loads(manifest_path.read_text())
    # The cache file is read in full; the counter below measures inspected repair entries, not I/O.
    cache = json.loads(Path(cache_path).read_text())
    upstream = {f["path"]: f for f in cache["files"]}
    checked_entries, repairs, unavailable = 0, [], []
    for entry in manifest["expected"]:
        target = bundle / (entry["id"] + ".md")
        reason = None
        if not target.exists():
            reason = "MISSING"
        else:
            body = target.read_text()
            info = header(body)
            if info["id"] != entry["id"] or info["version"] != entry["version"]:
                reason = "ID_OR_VERSION_MISMATCH"
            elif blob_sha(body) != entry["git_blob_sha"]:
                reason = "BYTE_MISMATCH"
        if reason is not None:
            repairs.append({"id": entry["id"], "reason": reason})
            source = upstream.get(entry["path"])
            if cache["ref"] != manifest["source_ref"] or source is None:
                unavailable.append(entry["id"])
                continue
            checked_entries += 1
            if blob_sha(source["content"]) != entry["git_blob_sha"]:
                unavailable.append(entry["id"])
                continue
            target.write_text(source["content"])
    if unavailable:
        return {"status": "INCOMPLETE", "repair_source_entries_checked": checked_entries,
                "detected": repairs, "unavailable": unavailable}
    actual = {header(p.read_text())["id"]: header(p.read_text()) for p in bundle.glob("*.md")}
    unresolved = sorted({dep for a in actual.values() for dep in a["requires"] if dep not in actual})
    result = {"status": "COMPLETE" if not unresolved else "INCOMPLETE", "repair_source_entries_checked": checked_entries,
              "detected": repairs, "unresolved_requires": unresolved,
              "complete_ids": sorted(actual)}
    # Receipt is written only after the completed-state checks, separate from intake.
    (bundle / "recovery-receipt.json").write_text(json.dumps(result, indent=2))
    return result


def context_cases(snapshot, oracle):
    assets = source_assets(snapshot)
    metadata_bytes = len(snapshot["files"][0]["content"].encode())
    all_ids = set(assets)
    rows = []
    for seed, manually_expected in oracle["expected_closures"].items():
        expected = set(manually_expected)
        assert declared_closure(seed, assets) == expected
        for strategy, loaded in (("selected_only", {seed}),
                                 ("declared_closure", declared_closure(seed, assets)),
                                 ("all_registered_assets", all_ids)):
            missing = sorted(expected - loaded)
            rows.append({"seed": seed, "strategy": strategy,
                         "loaded_ids": sorted(loaded), "missing_declared_ids": missing,
                         "extra_to_declared_closure": sorted(loaded - expected),
                         "payload_bytes": sum(len(assets[i]["content"].encode()) for i in loaded),
                         "registry_bytes_constant": metadata_bytes,
                         "declared_closure_oracle_met": not missing})
    recovery = []
    expected = [dict(a) for a in oracle["assets"]]
    cache_text = json.dumps(snapshot)
    specs = [("complete_checkpoint", 5, None), ("partial_checkpoint", 2, None),
             ("partial_without_intake", 2, "no_manifest"),
             ("same_id_other_version", 5, "version"),
             ("modified_bytes_same_header", 5, "bytes"),
             ("partial_source_unavailable", 2, "unavailable")]
    for name, count, fault in specs:
        with tempfile.TemporaryDirectory(prefix="akr-context-pilot-", dir="/private/tmp") as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            for entry in expected[:count]:
                (bundle / (entry["id"] + ".md")).write_text(assets[entry["id"]]["content"])
            if fault != "no_manifest":
                (bundle / "manifest.json").write_text(json.dumps({
                    "source_ref": snapshot["ref"], "seed": "ALG-SEC-001",
                    "stage": "materializing", "expected": expected}))
            changed = bundle / "POL-MOD-001.md"
            if fault == "version":
                changed.write_text(changed.read_text().replace("version: 0.1.0", "version: 0.2.0"))
            if fault == "bytes":
                changed.write_text(changed.read_text() + "\nPILOT_BYTE_MUTATION\n")
            source = root / "source-cache.json"
            if fault == "unavailable":
                partial = dict(snapshot, files=[f for f in snapshot["files"]
                                               if f["path"] != "policies/modality-preservation.md"])
                source.write_text(json.dumps(partial))
            else:
                source.write_text(cache_text)
            # A fresh process receives only saved files; no parent in-memory continuation.
            run = subprocess.run([sys.executable, str(__file__), "recover", str(bundle), str(source)],
                                 capture_output=True, text=True, check=True)
            result = json.loads(run.stdout)
            wanted = ("UNKNOWN_INTAKE" if fault == "no_manifest" else
                      "INCOMPLETE" if fault == "unavailable" else "COMPLETE")
            assert result["status"] == wanted
            if wanted == "COMPLETE":
                assert set(result["complete_ids"]) == set(oracle["expected_closures"]["ALG-SEC-001"])
                for entry in expected:
                    assert blob_sha((bundle / (entry["id"] + ".md")).read_text()) == entry["git_blob_sha"]
            recovery.append(dict(case=name, process="fresh child", expected_status=wanted,
                                 oracle_met=True, **result))
    return rows, recovery


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "recover":
        print(json.dumps(recover(sys.argv[2], sys.argv[3])))
        return
    snapshot = json.loads((HERE / "source-snapshot.json").read_text())
    oracle = json.loads((HERE / "oracle.json").read_text())
    assets = source_assets(snapshot)
    for expected in oracle["assets"]:
        actual = assets[expected["id"]]
        for key in ("version", "path", "git_blob_sha", "requires"):
            assert actual[key] == expected[key], (expected["id"], key)
    strategies, recovery = context_cases(snapshot, oracle)
    result = {"role": "bounded_research_observations", "source_ref": snapshot["ref"],
              "environment": {"python": sys.version.split()[0],
                              "git": subprocess.run(["git", "--version"], capture_output=True,
                                                    text=True, check=True).stdout.strip()},
              "mutation": mutation_cases(snapshot), "context": strategies, "recovery": recovery,
              "limits": oracle["limitations"]}
    (HERE / "results.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"mutation_cases": len(result["mutation"]),
                      "context_comparisons": len(strategies), "fresh_recovery_cases": len(recovery),
                      "results": str(HERE / "results.json")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
