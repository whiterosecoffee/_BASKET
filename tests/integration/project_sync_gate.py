"""Offline exact-source gate for the Project adapter and native Copier suites."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

PINNED_SOURCE = "743641f825dd7e5b7fe6b1e1958f634301cdcec4"
SUITES = {
    "adapter": ("orchestration/project_sync", 88),
    "copier": ("orchestration/bootstrap/tests", 6),
}
MARKERS = ("copier.yml", "orchestration/project_sync", "orchestration/bootstrap")


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def revision(value):
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("Expected a full lowercase 40-character commit SHA")
    return value


def select(root, requested=""):
    if requested:
        return {"sha": revision(requested), "mode": "explicit_exact_revision"}
    if any((root / marker).exists() or (root / marker).is_symlink() for marker in MARKERS):
        return {"sha": revision(git(root, "rev-parse", "HEAD")), "mode": "actual_head"}
    if git(root, "rev-parse", "--is-shallow-repository") != "false":
        raise ValueError("Complete history required before selecting an unmerged dependency")
    if git(root, "log", "-1", "--format=%H", "--", *MARKERS):
        raise ValueError("Previously present source was removed; refusing pinned fallback")
    return {"sha": PINNED_SOURCE, "mode": "unmerged_dependency_only"}


def fingerprint(root, expected):
    if git(root, "rev-parse", "HEAD") != revision(expected):
        raise ValueError("Checkout does not match expected revision")
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Checkout contains changed or untracked inputs")
    paths = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"]).decode().split("\0")
    result = {}
    for name in filter(None, paths):
        path = root / name
        payload = os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
        result[name] = hashlib.sha256(payload).hexdigest()
    return result


def strict_result(count, result, minimum):
    return (count >= minimum and result.testsRun == count and result.wasSuccessful()
            and not result.skipped and not result.expectedFailures)


def child(root, suite_name, result_path):
    directory, minimum = SUITES[suite_name]
    if not (root / directory).is_dir():
        raise ValueError("Required suite missing: " + directory)
    os.chdir(root)
    sys.path.insert(0, str(root))
    suite = unittest.TestLoader().discover(str(root / directory), pattern="test_*.py")
    count = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"suite": suite_name, "discovered": count, "run": result.testsRun,
              "minimum": minimum, "failures": len(result.failures), "errors": len(result.errors),
              "skipped": len(result.skipped), "expected_failures": len(result.expectedFailures),
              "unexpected_successes": len(result.unexpectedSuccesses),
              "passed": strict_result(count, result, minimum)}
    result_path.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["passed"] else 1


def run_gate(source, expected_source, acceptance, expected_acceptance, suite, mode, output, timeout=300):
    source, acceptance, output = source.resolve(), acceptance.resolve(), output.resolve()
    if output.is_relative_to(source) or output.is_relative_to(acceptance):
        raise ValueError("Evidence must be written outside both input checkouts")
    output.mkdir(parents=True, exist_ok=True)
    report = {"suite": suite, "source_sha": expected_source, "acceptance_sha": expected_acceptance,
              "source_mode": mode, "passed": False}
    try:
        before = fingerprint(source, expected_source)
        acceptance_before = fingerprint(acceptance, expected_acceptance)
        (output / "source-files.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
        report["source_manifest_sha256"] = hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            result_path = Path(temp) / "result.json"
            command = [sys.executable, str(Path(__file__).resolve()), "child", "--root", str(source),
                       "--suite", suite, "--result", str(result_path)]
            with (output / "suite.log").open("w") as log:
                completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=timeout)
            report["exit_code"] = completed.returncode
            if result_path.exists():
                report["result"] = json.loads(result_path.read_text())
            report["inputs_unchanged"] = (fingerprint(source, expected_source) == before
                                           and fingerprint(acceptance, expected_acceptance) == acceptance_before)
            report["passed"] = (completed.returncode == 0 and report.get("result", {}).get("passed") is True
                                and report["inputs_unchanged"])
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report["error"] = str(exc)
    (output / "evidence.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True, indent=2))
    if (output / "suite.log").exists():
        print((output / "suite.log").read_text())
    return 0 if report["passed"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("select")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--requested", default="")
    p = commands.add_parser("child")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--suite", choices=SUITES, required=True)
    p.add_argument("--result", type=Path, required=True)
    p = commands.add_parser("run")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--expected-source", required=True)
    p.add_argument("--acceptance", type=Path, required=True)
    p.add_argument("--expected-acceptance", required=True)
    p.add_argument("--suite", choices=SUITES, required=True)
    p.add_argument("--mode", choices=("actual_head", "unmerged_dependency_only", "explicit_exact_revision"), required=True)
    p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "select":
        for key, value in select(args.root.resolve(), args.requested).items():
            print(f"{key}={value}")
        return 0
    if args.command == "child":
        return child(args.root.resolve(), args.suite, args.result.resolve())
    return run_gate(args.source, args.expected_source, args.acceptance, args.expected_acceptance,
                    args.suite, args.mode, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
