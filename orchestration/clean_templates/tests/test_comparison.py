import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from orchestration import component_conformance as cc
from orchestration.clean_templates import composition as c
from orchestration.clean_templates import comparison as consumer

META = dict(as_of="2026-11-12T00:00:00Z", code_sha="6f5e39cd8590a6431bec56cd62af086bb28d6326")


class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate_fixture = [
            {"candidate_id": identity, "request": c.read(filename)}
            for identity, filename in [("basic-intake", "comparison.ready.request.json"),
                                       ("review-required", "comparison.blocked.request.json")]]
        cls.receipt_fixture = [dict(candidate_id=item["candidate_id"],
                                   receipt=c.compose(item["request"], **META))
                               for item in cls.candidate_fixture]

    def setUp(self):
        self.candidates = copy.deepcopy(self.candidate_fixture)
        self.receipts = copy.deepcopy(self.receipt_fixture)

    def compare(self):
        return consumer.compare(self.candidates, self.receipts)

    def test_two_candidates_preserve_ready_and_blocked(self):
        report = self.compare()
        self.assertEqual([row["declared_readiness"]["state"] for row in report["candidates"]],
                         ["ready_for_local_probe", "blocked"])
        self.assertFalse(report["execution_authorized"])
        self.assertEqual(report, c.read("comparison.report.example.json"))

    def test_invalid_is_never_reported_ready(self):
        self.candidates[0]["request"]["seed"] = None
        report = consumer.compose_comparison(self.candidates, **META)
        self.assertEqual(report["candidates"][0]["declared_readiness"]["state"], "invalid")
        self.assertEqual(report["candidates"][1]["declared_readiness"]["state"], "blocked")

    def test_swapped_receipts_rejected(self):
        self.receipts[0]["receipt"], self.receipts[1]["receipt"] = (
            self.receipts[1]["receipt"], self.receipts[0]["receipt"])
        with self.assertRaises(cc.ConformanceError):
            self.compare()

    def test_swapped_requests_rejected(self):
        self.candidates[0]["request"], self.candidates[1]["request"] = (
            self.candidates[1]["request"], self.candidates[0]["request"])
        with self.assertRaises(cc.ConformanceError):
            self.compare()

    def test_duplicate_ids_rejected_for_both_ports(self):
        for attr in ("candidates", "receipts"):
            with self.subTest(port=attr):
                values = getattr(self, attr)
                saved = values[1]["candidate_id"]
                values[1]["candidate_id"] = values[0]["candidate_id"]
                with self.assertRaisesRegex(ValueError, "DUPLICATE_CANDIDATE_ID"):
                    self.compare()
                values[1]["candidate_id"] = saved

    def test_duplicate_requests_with_distinct_labels_rejected(self):
        self.candidates[1]["request"] = copy.deepcopy(self.candidates[0]["request"])
        with self.assertRaisesRegex(ValueError, "DUPLICATE_REQUEST"):
            self.compare()

    def test_missing_or_wrong_candidate_set_rejected(self):
        with self.assertRaisesRegex(ValueError, "EXPECTED_TWO_CANDIDATES"):
            consumer.compare(self.candidates[:1], self.receipts)
        self.receipts[0]["candidate_id"] = "unrelated"
        with self.assertRaisesRegex(ValueError, "CANDIDATE_SET_MISMATCH"):
            self.compare()

    def test_missing_artifact_rejected(self):
        del self.receipts[1]["receipt"]["artifacts"]["example://readiness"]
        with self.assertRaises(cc.ConformanceError):
            self.compare()

    def test_tampered_artifact_rejected(self):
        self.receipts[0]["receipt"]["artifacts"]["example://readiness"] += " "
        with self.assertRaises(cc.ConformanceError):
            self.compare()

    def test_order_and_repeat_are_deterministic(self):
        expected = cc.canonical(self.compare())
        self.candidates.reverse()
        self.receipts.reverse()
        self.assertEqual(expected, cc.canonical(self.compare()))
        self.assertEqual(expected, cc.canonical(consumer.compose_comparison(self.candidates, **META)))

    def test_requests_and_receipts_are_not_mutated(self):
        before = copy.deepcopy((self.candidates, self.receipts))
        self.compare()
        consumer.compose_comparison(self.candidates, **META)
        self.assertEqual(before, (self.candidates, self.receipts))

    def test_no_archive_network_dispatch_or_output_writes(self):
        self.candidates[0]["request"]["seed"]["references"][0]["locator"] = "archive:/absent.py"
        original = Path.open
        allowed = {c.ROOT / name for name in ("component.json", "request.schema.json",
                   "readiness.schema.json", "seed.schema.json", "component.py", "validate.py")}
        def guarded(path, mode="r", *args, **kwargs):
            self.assertIn(path, allowed)
            self.assertIn(mode, ("r", "rb"))
            return original(path, mode, *args, **kwargs)
        with patch.object(Path, "open", guarded), \
                patch("socket.socket", side_effect=AssertionError("network")), \
                patch("subprocess.run", side_effect=AssertionError("dispatch")):
            consumer.compose_comparison(self.candidates, **META)

    def test_rehashed_false_declaration_does_not_confer_authority(self):
        # Existing integrity-only boundary deliberately does not authenticate truth.
        receipt = self.receipts[1]["receipt"]
        data = cc.canonical(dict(state="ready_for_local_probe", errors=[], missing_capabilities=[]))
        receipt["artifacts"]["example://readiness"] = data.decode()
        binding = receipt["result"]["outputs"]["readiness"]
        binding["artifact"]["sha256"] = cc.digest(data)
        report = self.compare()
        self.assertFalse(report["execution_authorized"])
        self.assertEqual(report["evidence_class"], "offline_integrity_checked_declarations")
        self.assertIn("not authenticated", report["limitation"])

    def test_cli_matches_example_and_repeat(self):
        command = [sys.executable, "-B", "-m", "orchestration.clean_templates.comparison"]
        first = subprocess.check_output(command, cwd=c.ROOT.parents[1])
        second = subprocess.check_output(command, cwd=c.ROOT.parents[1])
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), c.read("comparison.report.example.json"))
