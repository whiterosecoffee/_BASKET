import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from jsonschema import ValidationError
from orchestration import component_conformance as cc
from orchestration.clean_templates import composition as c

META = dict(as_of="2026-11-12T00:00:00Z", code_sha="9ff7508308112da59f1fdeecc4a23136259a2f29")


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.request = c.read("composition.request.json")

    def run_example(self):
        receipt = c.compose(self.request, **META)
        return receipt, c.consume(receipt, expected_request=self.request)

    def test_success_through_serialized_ports(self):
        receipt, result = self.run_example()
        self.assertEqual(result["state"], "ready_for_local_probe")
        self.assertEqual(c.consume(json.loads(cc.canonical(receipt)), expected_request=self.request), result)
        self.assertEqual(receipt["result"]["quality"]["warnings"], [c.WARNING])

    def test_missing_capability_preserved(self):
        self.request["seed"]["requires"] = ["capability:worker.review"]
        receipt, result = self.run_example()
        self.assertEqual(result["state"], "blocked")
        self.assertEqual(result["missing_capabilities"], ["capability:worker.review"])
        # Successful execution of a readiness check is not a ready verdict.
        self.assertEqual(receipt["result"]["status"], "ok")

    def test_invalid_seed_preserved(self):
        self.request["seed"] = None
        self.assertEqual(self.run_example()[1]["state"], "invalid")

    def test_malformed_request_rejected(self):
        for request in [None, {}, {**self.request, "dispatch": True}]:
            with self.subTest(request=request), self.assertRaisesRegex(ValueError, "INVALID_REQUEST"):
                c.compose(request, **META)

    def test_determinism_and_no_input_mutation(self):
        before = copy.deepcopy(self.request)
        first, _ = self.run_example()
        second, _ = self.run_example()
        self.assertEqual(cc.canonical(first), cc.canonical(second))
        self.assertEqual(self.request, before)

    def test_only_fixed_local_files_no_archive_network_or_dispatch(self):
        self.request["seed"]["references"][0]["locator"] = "archive:/absent/implementation.py"
        original = Path.open
        allowed = {c.ROOT / name for name in ("component.json", "request.schema.json",
                   "readiness.schema.json", "seed.schema.json", "component.py", "validate.py")}
        def guarded(path, *args, **kwargs):
            self.assertIn(path, allowed)
            return original(path, *args, **kwargs)
        with patch.object(Path, "open", guarded), \
                patch("socket.socket", side_effect=AssertionError("network")), \
                patch("subprocess.run", side_effect=AssertionError("dispatch")):
            self.assertEqual(self.run_example()[1]["state"], "ready_for_local_probe")

    def test_tampered_bytes_rejected(self):
        receipt, _ = self.run_example()
        receipt["artifacts"]["example://readiness"] += " "
        with self.assertRaises(cc.ConformanceError):
            c.consume(receipt, expected_request=self.request)

    def test_invalid_readiness_rejected_even_with_updated_hash(self):
        receipt, _ = self.run_example()
        data = cc.canonical({"state": "authorized"})
        receipt["artifacts"]["example://readiness"] = data.decode()
        binding = receipt["result"]["outputs"]["readiness"]
        binding["artifact"]["sha256"] = cc.digest(data)
        with self.assertRaises(ValidationError):
            c.consume(receipt, expected_request=self.request)

    def test_unexpected_request_or_manifest_rejected(self):
        receipt, _ = self.run_example()
        changed = copy.deepcopy(self.request)
        changed["available_capabilities"] = ["capability:worker.review"]
        with self.assertRaises(cc.ConformanceError):
            c.consume(receipt, expected_request=changed)
        receipt["manifest"]["version"] = "9.0.0"
        with self.assertRaisesRegex(ValueError, "UNEXPECTED_MANIFEST"):
            c.consume(receipt, expected_request=self.request)

    def test_cli_repeat_is_json_and_consumable(self):
        command = [sys.executable, "-m", "orchestration.clean_templates.composition",
                   "--as-of", META["as_of"], "--code-sha", META["code_sha"]]
        first = subprocess.check_output(command, cwd=c.ROOT.parents[1])
        second = subprocess.check_output(command, cwd=c.ROOT.parents[1])
        self.assertEqual(first, second)
        self.assertEqual(c.consume(json.loads(first), expected_request=self.request)["state"],
                         "ready_for_local_probe")
