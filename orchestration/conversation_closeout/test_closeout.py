import unittest
from orchestration.conversation_closeout.__main__ import assess, render

BASE = {"objective": "Review conversation", "local_required_remaining": False,
        "decision_required": False, "external_required_remaining": False}

class CloseoutTests(unittest.TestCase):
    def test_ready(self):
        self.assertEqual(assess(BASE)["disposition"], "Ready to Archive")

    def test_local_first(self):
        self.assertEqual(assess(dict(BASE, local_required_remaining=True, decision_required=True))["disposition"], "Continue here")

    def test_decision(self):
        self.assertEqual(assess(dict(BASE, decision_required=True))["disposition"], "Decision needed")

    def test_transfer_requires_prompt(self):
        with self.assertRaisesRegex(ValueError, "handoff required"):
            assess(dict(BASE, external_required_remaining=True))

    def test_transfer_prompt(self):
        handoff = dict(owner="B00", destination="Issue #1", objective="Finish tool",
                       completed="Prototype", remaining="Tests", write_paths="orchestration/**",
                       prohibited="Other files", validation="Run tests", next_action="Test")
        data = dict(BASE, external_required_remaining=True, handoff=handoff)
        report = render(data, assess(data))
        self.assertIn("Next executable action: Test", report)
        self.assertTrue(report.endswith("Hand off before archiving\n"))

    def test_scoring_na(self):
        result = assess(dict(BASE, scores={"reuse": 4, "verification_integrity": None}))
        self.assertEqual((result["execution_score"], result["scored_dimensions"]), (80.0, 1))

    def test_invalid_score(self):
        with self.assertRaises(ValueError):
            assess(dict(BASE, scores={"reuse": 6}))

    def test_invalid_insight(self):
        with self.assertRaises(ValueError):
            assess(dict(BASE, insights=[{"principle": "x", "disposition": "unknown"}]))

    def test_verified_claim_requires_revision(self):
        data = dict(BASE, claims=[{"id": "C1", "type": "repository_verified", "text": "CI passed"}])
        with self.assertRaisesRegex(ValueError, "requires source_ref and revision"):
            assess(data)

    def test_duplicate_claim_id_rejected(self):
        claim = {"id": "C1", "type": "proposal", "text": "Proposed contract"}
        with self.assertRaisesRegex(ValueError, "duplicated"):
            assess(dict(BASE, claims=[claim, claim]))

    def test_insight_claim_reference(self):
        data = dict(BASE, insights=[{"principle": "Verify claims", "disposition": "propose",
                                     "claim_ids": ["missing"]}])
        with self.assertRaisesRegex(ValueError, "unknown claim"):
            assess(data)

    def test_preserve_structured_knowledge(self):
        claim = {"id": "C1", "type": "independent_test", "text": "Tests passed",
                 "source_ref": "actions/123", "revision": "abc123"}
        insight = {"principle": "Execute tests", "disposition": "transfer", "priority": 23,
                   "pattern": "Fail closed", "application": "CRWV", "limitations": "Synthetic",
                   "rationale": "Avoid false success", "claim_ids": ["C1"]}
        data = dict(BASE, claims=[claim], insights=[insight])
        report = render(data, assess(data))
        self.assertIn("Fail closed", report)
        self.assertIn("Synthetic", report)
        self.assertIn("actions/123 @ abc123", report)

if __name__ == "__main__":
    unittest.main()
