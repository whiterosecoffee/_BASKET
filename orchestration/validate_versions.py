#!/usr/bin/env python3
"""Validate BASKET project version declaration and release readiness metadata.

This script DOES NOT declare the core candidate released or assert live feed functionality.
Run from repository root: python orchestration/validate_versions.py
Stdlib only.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
REQUIRED_GATES = {"R0", "R1", "R2", "R3", "R4"}
REQUIRED_INSTRUCTIONS = (
    "Every new conversation",
    "issue",
    "branch",
    "handoff",
    "GitHub",
    "Time to Die",
    "USD",
    "ONE copyable block",
)


def semver(v):
    if not isinstance(v, str) or not SEMVER.fullmatch(v):
        raise ValueError(f"not a SemVer string: {v!r}")
    return tuple(int(x) for x in v.split("-")[0].split("+")[0].split("."))


def validate():
    issues = []
    manifest = json.loads((ROOT / "architecture/version-manifest.json").read_text(encoding="utf-8"))
    architecture = json.loads((ROOT / "architecture/basket.architecture.json").read_text(encoding="utf-8"))
    sparks = json.loads((ROOT / "orchestration/sparks.json").read_text(encoding="utf-8"))
    instructions = (ROOT / "orchestration/PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")
    policy = (ROOT / "architecture/VERSIONING.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    core = manifest["core"]
    catalog = manifest["orchestration"]
    for label, ver in [
        ("manifest", manifest["manifest_version"]),
        ("core", core["declared_architecture_version"]),
        ("candidate", core["next_candidate"]),
        ("catalog", catalog["catalog_version"]),
        ("spark_catalog", sparks["catalog_version"])
    ]:
        try:
            semver(ver)
        except ValueError as exc:
            issues.append(f"{label}: {exc}")
    if architecture["version"] != core["declared_architecture_version"]:
        issues.append("architecture declared version differs from baseline manifest")
    if sparks["catalog_version"] != catalog["catalog_version"]:
        issues.append("catalog version mismatch")
    if semver(core["next_candidate"]) <= semver(core["declared_architecture_version"]):
        issues.append("next candidate is not later than baseline")
    if core["candidate_status"] != "planned_unreleased":
        issues.append("core target should not claim release before gates pass")
    if core.get("release_tag_created") is not False:
        issues.append("tag status must stay false until verified tag is created")
    gates = manifest.get("candidate_gates", [])
    if {g["id"] for g in gates} != REQUIRED_GATES or len(gates) != len(REQUIRED_GATES):
        issues.append("release gate IDs must be R0..R4 without duplicates")
    if any(g["status"] == "complete" for g in gates):
        issues.append("candidate gate may not be marked complete without test/merge evidence")
    for item in manifest["schema_contracts"]:
        if not (ROOT / item["path"]).is_file():
            issues.append(f"missing declared schema path: {item['path']}")
    for text in REQUIRED_INSTRUCTIONS:
        if text not in instructions:
            issues.append(f"Project Instructions missing text: {text}")
    for reference in ("v0.5.0", "explicitly authorizes", "schema", "TTD"):
        if reference not in policy:
            issues.append(f"release policy missing: {reference}")
    if "Unreleased" not in changelog:
        issues.append("CHANGELOG must distinguish unreleased candidate")
    if not manifest["orchestration"]["instruction_path"] == "orchestration/PROJECT_INSTRUCTIONS.md":
        issues.append("manifest points to wrong instructions source")
    return issues, manifest, sparks


def main():
    try:
        issues, manifest, sparks = validate()
    except Exception as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1
    if issues:
        for issue in issues:
            print("ERROR: " + issue, file=sys.stderr)
        return 1
    print(json.dumps({
        "result": "pass",
        "core_declared": manifest["core"]["declared_architecture_version"],
        "next_candidate": manifest["core"]["next_candidate"],
        "core_release_status": manifest["core"]["candidate_status"],
        "catalog": sparks["catalog_version"],
        "spark_count": len(sparks["sparks"]),
        "schema_contracts": len(manifest["schema_contracts"]),
        "release_gates": [g["id"] for g in manifest["candidate_gates"]]
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
