import copy
import unittest
from pathlib import Path
from unittest.mock import patch

from orchestration.clean_templates import lifecycle as lc
from orchestration import component_conformance as cc


class LifecycleTemplateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = lc.read("lifecycle.examples.json")
        self.now = self.fixture["evaluation_time"]
        self.value = self.fixture["examples"]["market-readonly"]

    def check(self):
        return lc.validate(self.value, now=self.now)

    def reject(self):
        result = self.check()
        self.assertFalse(result["valid"])
        self.assertFalse(result["execution_authorized"])

    def test_three_contrasting_synthetic_examples_pass(self):
        for name, value in self.fixture["examples"].items():
            with self.subTest(name=name):
                result = lc.validate(value, now=self.now)
                self.assertTrue(result["valid"], result["errors"])
                self.assertFalse(result["execution_authorized"])

    def test_wrong_host_and_disconnected_executor_fail(self):
        for key, value in [("observed_host", "CLOUD"), ("connected", False),
                           ("executor_verified", False), ("worktree_isolated", False)]:
            with self.subTest(key=key):
                saved = self.value["session"][key]
                self.value["session"][key] = value
                self.reject()
                self.value["session"][key] = saved

    def test_duplicate_owner_fails_even_same_session(self):
        self.value["ownership"]["active_writers"] *= 2
        self.reject()

    def test_missing_or_stale_qualified_input_fails(self):
        original = copy.deepcopy(self.value)
        del self.value["input"]
        self.reject()
        self.value = copy.deepcopy(original)
        self.value["input"]["qualification"] = "unknown"
        self.reject()
        self.value = original
        self.value["input"]["qualified_until"] = self.now
        self.reject()

    def test_direct_analyst_fetch_or_data_write_fails(self):
        self.value["request"]["operation"] = "refresh"
        # Rebind to isolate the role rule from the request fingerprint rule.
        self.rebind()
        self.reject()
        self.value["request"]["operation"] = "consume"
        self.rebind()
        self.value["input"]["access"] = "owner_managed"
        self.reject()

    def test_acquisition_repair_persistence_refresh_stay_with_fetch(self):
        for key in ("acquisition_owner", "persistence_owner", "repair_owner", "refresh_owner"):
            with self.subTest(key=key):
                self.value["input"][key] = "analyst"
                self.reject()
                self.value["input"][key] = "_FETCH"

    def test_missing_receipt_or_ack_fails(self):
        self.value["outcome"]["receipt"] = None
        self.reject()
        self.value = copy.deepcopy(self.fixture["examples"]["clean-comparison"])
        del self.value["acknowledgment"]
        self.reject()

    def test_uncertain_effect_fails_until_reconciled(self):
        self.value["outcome"]["effect_state"] = "uncertain"
        self.reject()
        self.value["outcome"]["effect_state"] = "reconciled_no_change"
        self.value["recovery"]["prior_failures"] = ["synthetic uncertain write inspected; no effect found"]
        self.value["recovery"]["next_action"] = "resume_after_reconciliation"
        self.assertTrue(self.check()["valid"])
        self.assertFalse(self.check()["execution_authorized"])

    def test_schedule_is_not_run_or_consumer_acceptance(self):
        self.value["schedule"]["configured"] = True
        self.value["outcome"]["run_observed"] = False
        self.reject()
        self.value["outcome"]["run_observed"] = True
        self.value["outcome"]["consumer_acceptance"] = "accepted"
        self.reject()

    def test_failed_and_parked_outcomes_preserve_evidence(self):
        for state in ("failed", "parked"):
            self.value["outcome"].update(state=state, run_observed=False)
            self.value["recovery"]["prior_failures"] = ["synthetic unavailable dependency"]
            self.value["recovery"]["next_action"] = "park_and_route_to_owner"
            self.assertTrue(self.check()["valid"])

    def test_repeat_is_deterministic_without_mutation_or_effects(self):
        before = copy.deepcopy(self.value)
        self.assertEqual(cc.canonical(self.check()), cc.canonical(self.check()))
        self.assertEqual(before, self.value)
        self.assertFalse(self.check()["execution_authorized"])

    def test_request_identity_revision_and_deadline_are_bound(self):
        for key, value in [("request_id", "different"), ("idempotency_key", "different"),
                           ("input_revision", "0" * 64), ("deadline", self.now)]:
            with self.subTest(key=key):
                saved = self.value["request"][key]
                self.value["request"][key] = value
                self.reject()
                self.value["request"][key] = saved

    def rebind(self):
        fingerprint = cc.digest(cc.canonical(self.value["request"]))
        self.value["acknowledgment"]["request_sha256"] = fingerprint
        self.value["outcome"]["receipt"]["request_sha256"] = fingerprint

    def test_owned_paths_reuse_protocol_guard(self):
        for path in ("runtime/forbidden.py", "orchestration/clean_templates/../../runtime/x.py"):
            self.value["request"]["planned_writes"] = [path]
            self.rebind()
            self.reject()

    def test_method_is_proposal_with_existing_owner_adoption_matrix(self):
        method = lc.read("lifecycle.method.json")
        self.assertFalse(method["execution_authorized"])
        self.assertEqual(method["status"], "local_proposal_not_enforced")
        self.assertEqual(len(method["stages"]), 9)
        self.assertEqual(len(method["adoption_matrix"]), 8)
        for rule in method["adoption_matrix"]:
            self.assertTrue(rule["governing_owner"])
            self.assertTrue(rule["reference"].startswith("https://github.com/whiterosecoffee/_BASKET/"))

    def test_private_inputs_cannot_be_published(self):
        self.value["privacy"].update(input_class="private", publish_input=True)
        self.reject()

    def test_existing_open_conversation_and_both_channels_required(self):
        for key in ("conversation_open", "nathan_can_communicate", "dot_can_communicate"):
            self.value["session"][key] = False
            self.reject()
            self.value["session"][key] = True

    def test_lint_reads_only_fixed_schemas_and_has_no_external_effects(self):
        original = Path.open
        allowed = {lc.ROOT / "lifecycle.schema.json",
                   lc.ROOT.parents[1] / "schemas/worker-task.v1.json"}
        def guarded(path, mode="r", *args, **kwargs):
            self.assertIn(path, allowed)
            self.assertEqual(mode, "r")
            return original(path, mode, *args, **kwargs)
        with patch.object(Path, "open", guarded), \
                patch("socket.socket", side_effect=AssertionError("network")), \
                patch("subprocess.run", side_effect=AssertionError("dispatch")):
            self.assertTrue(self.check()["valid"])
