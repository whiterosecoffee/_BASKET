"""Explicit projections into audit.py's local profile; no source or network reads.

These functions do not validate the full source models or grant capability,
execution, acceptance, or integration authority.
"""
import argparse
import copy
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re


class ProjectionError(ValueError):
    pass


def _root_relative(path):
    if (not isinstance(path, str) or not path or path.startswith(("/", "~"))
            or PureWindowsPath(path).drive or any(c in path for c in "\\:#?%")
            or any(ord(c) < 32 for c in path)
            or any(part in ("", ".", "..") for part in path.split("/"))
            or PurePosixPath(path).suffix.lower() != ".json"):
        raise ProjectionError("selected source must have a portable root-relative JSON path")
    return path


def map_sources(document, selected):
    """Explicit selected source keys become required local files, at bundle root.

    Commit IDs remain provenance annotations, not independently verified Git
    identities. The audit verifies supplied file bytes against sha256 only.
    """
    if not isinstance(document, dict) or not isinstance(document.get("sources"), dict):
        raise ProjectionError("map sources must be an object")
    if (not isinstance(selected, list) or not selected
            or any(not isinstance(key, str) for key in selected)
            or len(set(selected)) != len(selected)):
        raise ProjectionError("select distinct explicit source keys")
    references, provenance = [], []
    for key in sorted(selected):
        source = document["sources"].get(key)
        if not isinstance(source, dict) or source.get("path") != key:
            raise ProjectionError("unknown source or key/path mismatch: " + key)
        path = _root_relative(source["path"])
        pin, commit = source.get("sha256"), source.get("commit")
        if not isinstance(pin, str) or not re.fullmatch(r"[a-f0-9]{64}", pin):
            raise ProjectionError("missing or invalid exact-byte sha256: " + key)
        if not isinstance(commit, str) or not re.fullmatch(r"[a-f0-9]{40}", commit):
            raise ProjectionError("missing or invalid commit provenance: " + key)
        references.append({"ref": path, "sha256": pin, "use": "required"})
        provenance.append({"source_key": key, "commit": commit})
    return {"references": references, "projection": {
        "profile": "map_selected_sources", "entry_location": "bundle_root",
        "selected_source_provenance": provenance,
        "commit_verification": "not_performed",
        "source_model_validation": "not_performed",
        "unselected_sources": "not_audited"}}


def seed_references(document):
    """Keep clean-seed reference_only locators as unread informational metadata.

    Seed requires describes capabilities, not required local files. It cannot be
    translated to file dependencies without a separate owner-approved binding.
    """
    if (not isinstance(document, dict) or document.get("schema") != "basket.clean_seed@1"
            or not isinstance(document.get("references"), list)
            or not isinstance(document.get("requires"), list)):
        raise ProjectionError("expected clean_seed@1 references and requires lists")
    notes = []
    for reference in document["references"]:
        if (not isinstance(reference, dict) or reference.get("use") != "reference_only"
                or not isinstance(reference.get("locator"), str) or not reference["locator"]
                or any(ord(c) < 32 for c in reference["locator"])):
            raise ProjectionError("only explicit reference_only seed locators can be projected")
        notes.append({"locator": reference["locator"], "use": "reference_only"})
    # Input comes from JSON. Reject unsupported Python objects/nonfinite values
    # for library callers too; never serialize capability objects as paths.
    try:
        json.dumps(document["requires"], allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ProjectionError("capabilities must be JSON data") from exc
    return {"references": [], "projection": {
        "profile": "clean_seed_reference_notes", "audit_scope": "informational_only",
        "reference_notes": notes, "required_capabilities": copy.deepcopy(document["requires"]),
        "capability_evaluation": "not_performed", "source_model_validation": "not_performed"}}


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProjectionError("duplicate JSON key")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("map", "seed"), required=True)
    parser.add_argument("--document", required=True)
    parser.add_argument("--select", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        document = json.loads(Path(args.document).read_text(), object_pairs_hook=_object)
        if args.profile == "seed" and args.select:
            raise ProjectionError("--select only applies to map sources")
        result = map_sources(document, args.select) if args.profile == "map" else seed_references(document)
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
        return 0
    except (OSError, UnicodeError, ValueError, RecursionError):
        print(json.dumps({"error": "invalid_projection_input"}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
