"""Profile matching tests authored by the bounded B00-136 engineer worker.

These are offline unit tests of existing registered profiles, not evidence that
an external agent or persistent runtime has executed.
"""
import copy
import json
from pathlib import Path
import unittest

from orchestration.worker_bridge.bridge import Blocked, match_profile


ROOT = Path(__file__).resolve().parents[2]


class AgentProfileMatchingTests(unittest.TestCase):
    def setUp(self):
        self.library = json.loads(
            (ROOT / "orchestration/planner/worker-library.json").read_text()
        )

    def test_contract_engineer_covers_contract_implementation(self):
        result = match_profile(
            self.library, ["contract_governance", "implementation"]
        )
        self.assertEqual(result["id"], "contract_engineer")
        self.assertTrue(
            {"contract_governance", "implementation"}
            <= set(result["capabilities"])
        )

    def test_second_profile_is_registered_qa_reviewer(self):
        result = match_profile(
            self.library, ["adversarial_validation", "github_evidence"]
        )
        self.assertEqual(result["id"], "qa_reviewer")
        self.assertIn(result, self.library["profiles"])

    def test_explicit_eligible_profile_is_honored(self):
        result = match_profile(
            self.library, ["implementation"], requested="contract_engineer"
        )
        self.assertEqual(result["id"], "contract_engineer")

    def test_requested_profile_cannot_gain_missing_capability(self):
        with self.assertRaises(Blocked) as caught:
            match_profile(
                self.library, ["implementation"], requested="qa_reviewer"
            )
        self.assertEqual(caught.exception.code, "profile_ineligible")

    def test_unknown_requested_profile_is_rejected(self):
        with self.assertRaises(Blocked) as caught:
            match_profile(
                self.library, ["implementation"], requested="unregistered"
            )
        self.assertEqual(caught.exception.code, "profile_ineligible")

    def test_unknown_or_empty_capability_request_is_rejected(self):
        for required in ([], ["unregistered_capability"],
                         ["implementation", "unregistered_capability"]):
            with self.subTest(required=required):
                with self.assertRaises(Blocked) as caught:
                    match_profile(self.library, required)
                self.assertEqual(caught.exception.code, "capability_unknown")

    def test_known_but_uncovered_capability_combination_is_rejected(self):
        with self.assertRaises(Blocked) as caught:
            match_profile(self.library, ["contract_governance", "github_evidence"])
        self.assertEqual(caught.exception.code, "profile_ineligible")

    def test_least_excess_capabilities_wins(self):
        result = match_profile(self.library, ["implementation"])
        self.assertEqual(result["id"], "data_engineer")

    def test_tie_break_and_order_are_deterministic(self):
        reversed_library = copy.deepcopy(self.library)
        reversed_library["profiles"].reverse()
        reversed_library["capabilities"].reverse()
        # Both existing profiles have one excess capability; identifier breaks tie.
        expected = match_profile(self.library, ["github_evidence"])
        self.assertEqual(expected["id"], "integration_steward")
        self.assertEqual(
            expected, match_profile(reversed_library, ["github_evidence"])
        )
        self.assertEqual(
            match_profile(self.library, ["implementation", "contract_governance"]),
            match_profile(reversed_library, ["contract_governance", "implementation"]),
        )

    def test_success_and_failure_leave_library_and_requests_unchanged(self):
        before = copy.deepcopy(self.library)
        required = ["implementation", "contract_governance"]
        requested_before = required.copy()
        match_profile(self.library, required)
        with self.assertRaises(Blocked):
            match_profile(self.library, ["unregistered_capability"])
        self.assertEqual(self.library, before)
        self.assertEqual(required, requested_before)


if __name__ == "__main__":
    unittest.main()
