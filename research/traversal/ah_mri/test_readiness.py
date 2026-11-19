import unittest
from readiness import evaluate, GATES

class ReadinessTests(unittest.TestCase):
    def test_no_evidence_fails_closed(self):
        out = evaluate()
        self.assertFalse(out["production_ready"])
        self.assertEqual(out["independently_verified_gates"], 0)
        self.assertEqual(out["attested_gates"], 0)
        self.assertEqual(len(out["blockers"]), len(GATES))

    def test_forged_pass_is_not_independent(self):
        claims = {name: {"status": "pass", "evidence_ref": "example://not-verified"}
                  for name, _, _ in GATES}
        out = evaluate(claims)
        self.assertEqual(out["attested_gates"], len(GATES))
        self.assertEqual(out["independently_verified_gates"], 0)
        self.assertFalse(out["production_ready"])
        self.assertFalse(out["release_authorized"])

    def test_malformed_claims_fail_closed(self):
        out = evaluate({"source_snapshot": {"status": "pass", "evidence_ref": ""}, 
                        "historical_replay": True})
        self.assertEqual(out["attested_gates"], 0)
        self.assertEqual(out["gates"][0]["status"], "invalid")
        self.assertEqual(out["gates"][4]["status"], "invalid")

    def test_wrong_evidence_type_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(["not", "a", "mapping"])

if __name__ == "__main__":
    unittest.main()
