import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("reference_portability_audit", HERE / "audit.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
audit = module.audit


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "root"
        shutil.copytree(HERE / "fixtures", self.root)

    def put(self, value, name="entry.json"):
        (self.root / name).write_text(json.dumps(value))
        return name

    def codes(self, result):
        return {x["code"] for x in result["findings"]}

    def fingerprint(self):
        return {p.relative_to(self.root).as_posix():
                (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file() and not p.is_symlink()}

    def test_valid_nested_reference(self):
        result = audit(self.root, "nested-case.json")
        self.assertTrue(result["ok"])
        self.assertEqual([x["path"] for x in result["files"]],
                         ["nested-case.json", "nested/worker.json", "shared/payload.json"])
        self.assertEqual(result["references"][1]["target"], "shared/payload.json")

    def test_second_case_reuses_exact_bytes(self):
        one = audit(self.root, "nested-case.json")
        two = audit(self.root, "reuse-case.json")
        self.assertTrue(two["ok"])
        self.assertEqual(one["files"][-1], two["files"][-1])
        self.assertEqual(len(two["findings"]), 2)
        self.assertEqual({x["severity"] for x in two["findings"]}, {"info"})

    def test_present_archive_never_read_or_followed(self):
        (self.root / "archive.json").write_text("not json, never parsed")
        entry = self.put({"references":[{"ref":"archive.json", "use":"archive", "sha256":"0"*64}]})
        original = Path.open
        def guarded(path, *args, **kwargs):
            self.assertNotEqual(path.name, "archive.json")
            return original(path, *args, **kwargs)
        with patch.object(Path, "open", guarded):
            result = audit(self.root, entry)
        self.assertTrue(result["ok"])
        self.assertEqual(result["references"][0]["status"], "reference_only_not_read")
        self.assertIsNone(result["references"][0]["sha256"])

    def test_symlink_escape(self):
        outside = Path(self.temp.name) / "outside.json"
        outside.write_text("{}")
        (self.root / "link.json").symlink_to(outside)
        result = audit(self.root, self.put({"references":[{"ref":"link.json"}]}))
        self.assertFalse(result["ok"])
        self.assertIn("symlink_rejected", self.codes(result))
        self.assertEqual(outside.read_text(), "{}")

    def test_symlink_directory_escape(self):
        (self.root / "link").symlink_to(Path(self.temp.name), target_is_directory=True)
        result = audit(self.root, self.put({"references":[{"ref":"link/outside.json"}]}))
        self.assertIn("symlink_rejected", self.codes(result))

    def test_broken_symlink_rejects_even_archive(self):
        (self.root / "link.json").symlink_to("absent.json")
        result = audit(self.root, self.put({"references":[{"ref":"link.json","use":"archive"}]}))
        self.assertFalse(result["ok"])

    def test_in_root_symlink_is_explicitly_unsupported(self):
        (self.root / "link.json").symlink_to("shared/payload.json")
        self.assertIn("symlink_rejected", self.codes(audit(self.root, "link.json")))

    def test_deterministic_replay_and_unchanged_inputs(self):
        before = self.fingerprint()
        one = json.dumps(audit(self.root, "nested-case.json"), sort_keys=True)
        two = json.dumps(audit(self.root, "nested-case.json"), sort_keys=True)
        self.assertEqual(one, two)
        self.assertEqual(before, self.fingerprint())

    def test_relocated_root_same_report(self):
        second = Path(self.temp.name) / "relocated"
        shutil.copytree(self.root, second)
        self.assertEqual(audit(self.root, "nested-case.json"), audit(second, "nested-case.json"))

    def test_exact_byte_hash_not_canonical_json(self):
        path = self.root / "shared/payload.json"
        path.write_bytes(path.read_bytes() + b" ")
        self.assertIn("hash_mismatch", self.codes(audit(self.root, "reuse-case.json")))

    def test_cycle_terminates(self):
        entry = self.put({"references":[{"ref":"entry.json"}]})
        result = audit(self.root, entry)
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["files"]), 1)

    def test_invalid_nested_json_fails(self):
        (self.root / "bad.json").write_text('{"a":1,"a":2}')
        entry = self.put({"references":[{"ref":"bad.json"}]})
        self.assertIn("invalid_or_unreadable_json", self.codes(audit(self.root, entry)))

    def test_nonfinite_json_rejects(self):
        for value in ('NaN', 'Infinity', '1e999'):
            with self.subTest(value=value):
                (self.root / "bad.json").write_text('{"x":'+value+'}')
                self.assertFalse(audit(self.root, "bad.json")["ok"])

    def test_declarations_are_explicit_not_schema_resolution(self):
        entry = self.put({"$ref":"https://example.invalid/schema", "data":{"ref":"absent.json"}})
        result = audit(self.root, entry)
        self.assertTrue(result["ok"])
        self.assertEqual(result["references"], [])

    def test_malformed_declarations_fail_closed(self):
        for value in ([], {"references":{}}, {"references":[None]}, {"references":[{}]}):
            with self.subTest(value=value):
                self.assertFalse(audit(self.root, self.put(value))["ok"])

    def test_no_network_or_referenced_code_execution(self):
        sentinel = self.root / "executed"
        (self.root / "code.py").write_text("raise RuntimeError('must never execute')")
        entry = self.put({"references":[{"ref":"code.py"},{"ref":"https://example.invalid/a.json"}]})
        with patch.object(socket, "create_connection", side_effect=AssertionError("network")), \
             patch.object(subprocess, "run", side_effect=AssertionError("execute")):
            result = audit(self.root, entry)
        self.assertEqual(self.codes(result), {"not_json_file","unsupported_uri"})
        self.assertFalse(sentinel.exists())

    def test_directory_not_regular_file(self):
        (self.root / "directory.json").mkdir()
        self.assertIn("not_regular_file", self.codes(audit(self.root, "directory.json")))

    def test_size_limit(self):
        with patch.object(module, "MAX_BYTES", 1):
            self.assertIn("file_size_limit", self.codes(audit(self.root, "nested-case.json")))

    def test_file_and_depth_limits(self):
        for key in ("MAX_FILES", "MAX_DEPTH"):
            with self.subTest(limit=key), patch.object(module, key, 0):
                self.assertIn("audit_limit", self.codes(audit(self.root, "nested-case.json")))

    def test_reference_limit(self):
        with patch.object(module, "MAX_REFERENCES", 0):
            self.assertIn("audit_limit", self.codes(audit(self.root, "nested-case.json")))

    def test_invalid_root_and_entry(self):
        self.assertFalse(audit(self.root / "missing", "entry.json")["ok"])
        self.assertFalse(audit(self.root, "../entry.json")["ok"])

    def test_cli_success_failure_and_json_stdout(self):
        command = [sys.executable, "-B", str(HERE / "audit.py"), "--root", str(self.root), "--entry"]
        for entry, code in (("nested-case.json", 0), ("reuse-case.json", 0), ("absent.json", 1)):
            result = subprocess.run(command + [entry], capture_output=True, text=True)
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertEqual(json.loads(result.stdout)["ok"], code == 0)
            self.assertEqual(result.stderr, "")


def add_negative(case):
    def test(self):
        document = copy.deepcopy(case["document"])
        entry = self.put(document)
        before = self.fingerprint()
        result = audit(self.root, entry)
        self.assertFalse(result["ok"])
        self.assertIn(case["expected"], self.codes(result))
        self.assertEqual(document, case["document"])
        self.assertEqual(before, self.fingerprint())
    setattr(PortabilityTests, "test_fixture_" + case["name"].replace("-", "_"), test)


for case in json.loads((HERE / "fixtures/negative-cases.json").read_text()):
    add_negative(case)

if __name__ == "__main__":
    unittest.main()
