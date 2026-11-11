"""Offline adapter unit tests. Doubles here are never execution evidence."""
import copy
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from orchestration.worker_bridge.bridge import (
    Blocked, ROOT, UTC, assert_fence, claims_from_issue, digest,
    load_controller, match_profile, run_codex, own_pr_exemption,
    owned_output_directory, publication_inputs_unchanged, assert_attempt,
)


class BridgeGuardTests(unittest.TestCase):
    def setUp(self):
        self.library = json.loads((ROOT / "orchestration/planner/worker-library.json").read_text())

    def test_profile_reuses_library_and_is_order_stable(self):
        before = copy.deepcopy(self.library)
        expected = match_profile(self.library, ["implementation", "contract_governance"])
        changed = copy.deepcopy(self.library)
        changed["profiles"].reverse()
        self.assertEqual(expected, match_profile(changed, ["contract_governance", "implementation"]))
        self.assertEqual(expected["id"], "contract_engineer")
        self.assertEqual(self.library, before)

    def test_second_existing_profile(self):
        self.assertEqual(match_profile(self.library, ["github_evidence", "adversarial_validation"])["id"], "qa_reviewer")

    def test_missing_capability_or_ineligible_profile_blocks(self):
        for required, requested in [([], None), (["invented"], None), (["implementation"], "qa_reviewer")]:
            with self.subTest(required=required, requested=requested), self.assertRaises(Blocked):
                match_profile(self.library, required, requested)

    def test_parse_claim_is_exact_and_malformed_fence_is_not_authority(self):
        claim = {"schema": "basket.worker_task@1", "task_id": "B00-136"}
        issue = {"body": "```json\ninvalid\n```", "comments_data": [{"body": "```json\n" + json.dumps(claim) + "\n```"}]}
        self.assertEqual(claims_from_issue(issue), [claim])

    def test_digest_is_stable_and_source_change_invalidates_it(self):
        self.assertEqual(digest({"a": 1, "b": 2}), digest({"b": 2, "a": 1}))
        self.assertNotEqual(digest({"sha": "old"}), digest({"sha": "new"}))

    def test_fence_binding_uses_owner_controller_result(self):
        controller = Mock()
        controller.lease_state.return_value = ({"T-136": {"event_id": "new"}}, [], False)
        now = dt.datetime.now(UTC)
        with self.assertRaisesRegex(Blocked, "stale_fence"):
            assert_fence(controller, [], "T-136", "old", now)
        self.assertEqual(assert_fence(controller, [], "T-136", "new", now)["event_id"], "new")
        controller.event_check.assert_called()

    def test_missing_or_expired_lease_is_not_reassigned(self):
        controller = Mock()
        controller.lease_state.return_value = ({}, ["T-136"], False)
        with self.assertRaisesRegex(Blocked, "lease_expired"):
            assert_fence(controller, [], "T-136", "unknown", dt.datetime.now(UTC))

    def test_controller_revision_drift_blocks_loading(self):
        with patch("orchestration.worker_bridge.bridge.git", return_value="b" * 40):
            with self.assertRaisesRegex(Blocked, "controller_revision"):
                load_controller(ROOT, {"controller_commit": "a" * 40})

    def test_output_outside_owned_evidence_is_blocked_before_model_call(self):
        controller = Mock()
        controller.lease_state.return_value = ({"T-136": {"event_id": "lease"}}, [], False)
        prepared = {"assignment": {"source_issue": 136, "execution": {"lease_id": "lease"}},
                    "profile": {"capabilities": ["implementation"]}}
        with tempfile.TemporaryDirectory() as directory, patch("subprocess.run") as call:
            with self.assertRaisesRegex(Blocked, "log_scope"):
                run_codex(ROOT, prepared, "test fixture", directory, controller, [], dt.datetime.now(UTC))
            call.assert_not_called()

    def test_read_only_profile_cannot_select_write_sandbox(self):
        prepared = {"assignment": {"source_issue": 136, "execution": {"lease_id": "lease"}},
                    "profile": {"id": "qa_reviewer", "capabilities": ["github_evidence", "adversarial_validation"]}}
        with patch("subprocess.run") as call, self.assertRaisesRegex(Blocked, "execution_permission"):
            run_codex(ROOT, prepared, "test fixture", ROOT / "orchestration/worker_bridge/evidence/unused",
                      Mock(), [], dt.datetime.now(UTC), read_only=False)
        call.assert_not_called()

    def test_unrelated_pr_cannot_be_exempted_from_collision_checks(self):
        task = {"branch": {"name": "work/136-worker-execution-bridge"}}
        pr = {"number": 99, "state": "open", "merged": False, "head_branch": "work/99-other",
              "base_branch": "main", "head_sha": "a" * 40, "head_repository": "whiterosecoffee/_BASKET"}
        with self.assertRaisesRegex(Blocked, "pr_identity"):
            own_pr_exemption(task, {"pull_requests": [pr]}, 99, "a" * 40)
        pr["head_branch"] = task["branch"]["name"]
        self.assertEqual(own_pr_exemption(task, {"pull_requests": [pr]}, 99, "a" * 40), 99)
        for key, value in [("head_repository", "other/fork"), ("head_sha", "b" * 40), ("base_branch", "other")]:
            changed = {**pr, key: value}
            with self.subTest(key=key), self.assertRaisesRegex(Blocked, "pr_identity"):
                own_pr_exemption(task, {"pull_requests": [changed]}, 99, "a" * 40)

    def test_unbound_or_ambiguous_same_branch_pr_is_blocked(self):
        task = {"branch": {"name": "work/136-bridge"}}
        pr = {"number": 99, "state": "open", "head_branch": "work/136-bridge"}
        with self.assertRaisesRegex(Blocked, "pr_association_required"):
            own_pr_exemption(task, {"pull_requests": [pr]}, None, "a" * 40)
        with self.assertRaisesRegex(Blocked, "pr_ambiguous"):
            own_pr_exemption(task, {"pull_requests": [pr, {**pr, "number": 100}]}, 99, "a" * 40)

    def test_stable_source_drift_invalidates_publication(self):
        keys = ("task", "library", "catalog", "profile", "required_capabilities", "controller_lock", "policy", "checkout_head")
        before = {"assignment": {"base_commit_sha": "a" * 40, "execution": {"attempt_id": "ATT-one"},
                                  "input_manifest": {k: "same" for k in keys}}}
        publication_inputs_unchanged(before, copy.deepcopy(before))
        for key in keys:
            after = copy.deepcopy(before)
            after["assignment"]["input_manifest"][key] = "changed"
            with self.subTest(key=key), self.assertRaisesRegex(Blocked, "source_drift"):
                publication_inputs_unchanged(before, after)

    def test_unregistered_resolved_or_replayed_attempt_is_blocked(self):
        controller = Mock()
        controller.attempts.return_value = {"last_attempt": "ATT-new", "pending": ["ATT-new"]}
        self.assertEqual(assert_attempt(controller, [], "T-136", "ATT-new")["last_attempt"], "ATT-new")
        for aid in (None, "ATT-old", "ATT-unregistered"):
            with self.subTest(aid=aid), self.assertRaisesRegex(Blocked, "attempt_unregistered"):
                assert_attempt(controller, [], "T-136", aid)
        controller.attempts.return_value["pending"] = []
        with self.assertRaisesRegex(Blocked, "attempt_unregistered"):
            assert_attempt(controller, [], "T-136", "ATT-new")

    def test_symlinked_evidence_base_cannot_escape_owned_checkout(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            base = root / "orchestration/worker_bridge"
            base.mkdir(parents=True)
            (base / "evidence").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(Blocked, "log_scope"):
                owned_output_directory(root, base / "evidence/ATT-one")


if __name__ == "__main__":
    unittest.main()
