"""Offline declared-reference audit. No schema resolver, imports, or network I/O."""
import argparse
import hashlib
import json
import math
from pathlib import Path, PureWindowsPath
import re
import stat

MAX_BYTES = 1024 * 1024
MAX_FILES = 256
MAX_REFERENCES = 4096
MAX_DEPTH = 32


def digest(data):
    """Same exact-byte SHA-256 convention as component_conformance.digest."""
    return hashlib.sha256(data).hexdigest()


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key")
        result[key] = value
    return result


def _number(value):
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("nonfinite_number")
    return parsed


def _constant(value):
    raise ValueError("nonfinite_number")


def _json(data):
    return json.loads(data, object_pairs_hook=_object, parse_float=_number,
                      parse_constant=_constant)


def _locate(root, source, ref):
    # Do not reinterpret Windows, URI, fragment, percent-encoded or home paths.
    if not isinstance(ref, str) or not ref or any(ord(c) < 32 for c in ref):
        return None, "invalid_reference"
    if ref.startswith("/") or PureWindowsPath(ref).drive or ref.startswith("\\"):
        return None, "unsupported_absolute_path"
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", ref):
        return None, "unsupported_uri"
    if any(c in ref for c in "\\#?%") or ref.startswith("~"):
        return None, "unsupported_path_syntax"
    parts = list(Path(source).parent.parts) if source != "." else []
    for part in ref.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None, "outside_root"
            parts.pop()
        else:
            parts.append(part)
    if not parts:
        return None, "not_json_file"
    path = root.joinpath(*parts)
    relative = "/".join(parts)
    # Refuse every symlink (including in-root links). Never follow a link to
    # inspect its destination, even for informational references.
    current = root
    try:
        for part in parts:
            current = current / part
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode):
                return relative, "symlink_rejected"
        if not stat.S_ISREG(mode):
            return relative, "not_regular_file"
    except FileNotFoundError:
        return relative, "missing_reference"
    except OSError:
        return relative, "unreadable_reference"
    if path.suffix.lower() != ".json":
        return relative, "not_json_file"
    return relative, None


def audit(root, entry):
    """Audit top-level references arrays recursively from entry, inside root.

    Each declaration uses ref, optional sha256 and use (required by default;
    reference_only or archive are informational). This local audit profile is
    not a canonical component envelope. The caller supplies a static isolated
    root; concurrent hostile filesystem replacement is outside this contract.
    """
    report = {"ok": True, "files": [], "references": [], "findings": []}
    root = Path(root)

    def finding(source, pointer, code, severity="error"):
        report["findings"].append(dict(source=source, pointer=pointer,
                                       code=code, severity=severity))

    try:
        if not root.is_dir() or root.is_symlink():
            raise ValueError("invalid_root")
        root = root.resolve(strict=True)
    except (OSError, ValueError, RuntimeError):
        finding(".", "", "invalid_root")
        report["ok"] = False
        return report

    entry_path, error = _locate(root, ".", entry)
    if error:
        finding(".", "", error)
    else:
        pending = [(entry_path, 0)]
        seen = set()
        reference_count = 0
        while pending:
            source, depth = pending.pop()
            if source in seen:
                continue
            if len(seen) >= MAX_FILES or depth > MAX_DEPTH:
                finding(source, "", "audit_limit")
                continue
            seen.add(source)
            # Recheck before reading; errors contain no machine-specific paths.
            _, error = _locate(root, ".", source)
            if error:
                finding(source, "", error)
                continue
            try:
                with (root / source).open("rb") as stream:
                    raw = stream.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    finding(source, "", "file_size_limit")
                    continue
                report["files"].append(dict(path=source, sha256=digest(raw)))
                document = _json(raw)
            except (OSError, ValueError, UnicodeError, RecursionError):
                finding(source, "", "invalid_or_unreadable_json")
                continue
            if not isinstance(document, dict):
                finding(source, "", "document_not_object")
                continue
            references = document.get("references", [])
            if not isinstance(references, list):
                finding(source, "/references", "invalid_declarations")
                continue
            for index, declaration in enumerate(references):
                pointer = "/references/" + str(index)
                reference_count += 1
                if reference_count > MAX_REFERENCES:
                    finding(source, pointer, "audit_limit")
                    pending.clear()
                    break
                if not isinstance(declaration, dict) or set(declaration) - {"ref", "sha256", "use"}:
                    finding(source, pointer, "invalid_declaration")
                    continue
                use = declaration.get("use", "required")
                pin = declaration.get("sha256")
                if use not in ("required", "reference_only", "archive") or ("sha256" in declaration and
                        (not isinstance(pin, str) or not re.fullmatch(r"[a-f0-9]{64}", pin))):
                    finding(source, pointer, "invalid_declaration")
                    continue
                ref = declaration.get("ref")
                target, error = _locate(root, source, ref)
                item = dict(source=source, pointer=pointer, ref=ref, use=use,
                            target=target, expected_sha256=pin, sha256=None)
                report["references"].append(item)
                informational = use != "required"
                if error:
                    item["status"] = error
                    # Only absence is informational. Unsafe pointers still fail.
                    severity = "info" if informational and error == "missing_reference" else "error"
                    finding(source, pointer, error, severity)
                    continue
                if informational:
                    item["status"] = "reference_only_not_read"
                    continue
                try:
                    with (root / target).open("rb") as stream:
                        data = stream.read(MAX_BYTES + 1)
                    if len(data) > MAX_BYTES:
                        item["status"] = "file_size_limit"
                        finding(source, pointer, item["status"])
                        continue
                    item["sha256"] = digest(data)
                except OSError:
                    item["status"] = "unreadable_reference"
                    finding(source, pointer, item["status"])
                    continue
                if pin is not None and pin != item["sha256"]:
                    item["status"] = "hash_mismatch"
                    finding(source, pointer, item["status"])
                    continue
                item["status"] = "resolved"
                pending.append((target, depth + 1))
    report["files"].sort(key=lambda x: x["path"])
    report["references"].sort(key=lambda x: (x["source"], x["pointer"]))
    report["findings"].sort(key=lambda x: (x["source"], x["pointer"], x["code"]))
    report["ok"] = not any(x["severity"] == "error" for x in report["findings"])
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--entry", required=True, help="Root-relative JSON document")
    args = parser.parse_args(argv)
    result = audit(args.root, args.entry)
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
