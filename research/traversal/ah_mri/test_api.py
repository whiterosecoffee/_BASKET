import copy
import unittest
from api import analyze_eod
from test_core import SAMPLE

class InvocationTests(unittest.TestCase):
    def test_success_is_provisional(self):
        result = analyze_eod(copy.deepcopy(SAMPLE))
        self.assertEqual(result["status"], "research_provisional")
        self.assertEqual(result["transport"], "in_process_offline")
        self.assertFalse(result["production_ready"])
        self.assertFalse(result["source_certified"])
        self.assertIn("# AH-MRI", result["markdown"])
        self.assertEqual(result["input_manifest_hash"], result["report"]["input_manifest_hash"])

    def test_missing_fields(self):
        for bad in ({}, {"as_of": SAMPLE["as_of"]}, {"as_of": SAMPLE["as_of"], "session": SAMPLE["session"]}):
            with self.subTest(bad=bad):
                out = analyze_eod(bad)
                self.assertEqual(out["status"], "invalid_request")
                self.assertIsNone(out["report"])

    def test_wrong_shapes(self):
        for bad in (None, [], "sample", {"as_of": "now", "session": [], "instruments": []}):
            with self.subTest(bad=bad):
                self.assertEqual(analyze_eod(bad)["status"], "invalid_request")

    def test_invalid_instrument_does_not_throw(self):
        b = copy.deepcopy(SAMPLE)
        b["instruments"][0]["levels"][0]["lower_usd"] = -5
        out = analyze_eod(b)
        self.assertEqual(out["status"], "invalid_observations")
        self.assertIsNone(out["markdown"])

    def test_no_historical_support_upgrade(self):
        b = copy.deepcopy(SAMPLE)
        b["instruments"][0]["levels"][0].update({
            "kind": "observed",
            "evidence_ids": ["unverified-claim"],
            "calculation": "claim",
            "sample_window": "claim",
        })
        out = analyze_eod(b)
        self.assertEqual(out["status"], "research_provisional")
        self.assertEqual(out["report"]["instruments"][0]["levels"][0]["kind"], "reference")

    def test_repeat_same_input_byte_stable(self):
        a = analyze_eod(SAMPLE)
        b = analyze_eod(copy.deepcopy(SAMPLE))
        self.assertEqual(a, b)

if __name__ == "__main__":
    unittest.main()
