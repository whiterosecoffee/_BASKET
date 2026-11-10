import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("source_gate_check", HERE / "check.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
assess = MODULE.assess


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.record = dict(
            source_head="a" * 40, gate_head="b" * 40, run_head="b" * 40,
            executed_source="a" * 40, conclusion="success",
            source_binding="immutable_dependency",
            run_url="https://github.com/whiterosecoffee/_BASKET/actions/runs/1")

    def test_component_does_not_mean_integrated(self):
        result = assess(self.record)
        self.assertTrue(result["component_evidence_matches"])
        self.assertFalse(result["reviewed_source_exercised"])
        self.assertFalse(result["integration_verified"])

    def test_reviewed_checkout(self):
        self.record.update(source_binding="reviewed_checkout", source_head="b" * 40, executed_source="b" * 40)
        self.assertTrue(assess(self.record)["reviewed_source_exercised"])
        self.assertFalse(assess(self.record)["integration_verified"])

    def test_stale_source_and_gate(self):
        for field, reason in (("source_head", "stale_source_execution"), ("gate_head", "stale_gate_run")):
            record = dict(self.record, **{field: "c" * 40})
            self.assertIn(reason, assess(record)["blockers"])

    def test_non_success_conclusions(self):
        for state in ("failure", "cancelled", "skipped", "pending"):
            self.assertFalse(assess(dict(self.record, conclusion=state))["component_evidence_matches"])

    def test_false_checkout_claim(self):
        record = dict(self.record, source_binding="reviewed_checkout")
        self.assertIn("checkout_not_run_revision", assess(record)["blockers"])

    def test_missing_extra_and_invalid_fields(self):
        for key in self.record:
            record = dict(self.record)
            record.pop(key)
            with self.assertRaises(ValueError):
                assess(record)
        for patch in (dict(extra=True), dict(source_head="main"), dict(executed_source=None),
                      dict(run_url=None), dict(conclusion=True), dict(source_binding="unknown")):
            with self.assertRaises(ValueError):
                assess(dict(self.record, **patch))

    def test_wrong_repository_url(self):
        with self.assertRaises(ValueError):
            assess(dict(self.record, run_url="https://github.com/other/repo/actions/runs/1"))

    def test_stable_fingerprint_without_mutation(self):
        original = copy.deepcopy(self.record)
        first = assess(self.record)
        self.assertEqual(first, assess(dict(reversed(list(self.record.items())))))
        self.assertEqual(original, self.record)
        self.assertNotEqual(first["dependency_fingerprint"], assess(dict(self.record, source_head="c" * 40))["dependency_fingerprint"])

    def test_historical_fixture_is_component_only(self):
        result = assess(json.loads((HERE / "historical-component.json").read_text()))
        self.assertTrue(result["component_evidence_matches"])
        self.assertFalse(result["integration_verified"])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            for record, expected in ((self.record, 0), (dict(self.record, conclusion="skipped"), 1), ({}, 2)):
                path.write_text(json.dumps(record))
                run = subprocess.run([sys.executable, str(HERE / "check.py"), str(path)], capture_output=True)
                self.assertEqual(run.returncode, expected, run.stderr)


if __name__ == "__main__":
    unittest.main()
