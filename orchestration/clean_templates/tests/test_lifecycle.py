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

    def test_prior_fulfillment_does_not_satisfy_new_stale_demand(self):
        packet = lc.read("lifecycle.stale-demand.example.json")
        self.assertEqual(packet["evidence_status"], "source_inspected_risk_not_executed_FETCH_failure")
        result = lc.validate(packet["snapshot"], now=packet["evaluation_time"])
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"], packet["expected_errors"])

    def test_current_readback_can_reuse_generation_without_new_effect(self):
        demand = self.value["request"]["demand"]
        self.assertEqual(demand["persisted_generation_id"], demand["prior_fulfillment"]["persisted_generation_id"])
        self.assertNotEqual(demand["attempt_id"], demand["prior_fulfillment"]["attempt_id"])
        before = copy.deepcopy(self.value)
        self.assertTrue(self.check()["valid"])
        self.assertEqual(self.value, before)
        self.assertEqual(self.value["outcome"]["effect_state"], "none")

    def test_new_demand_cannot_reuse_prior_attempt_identity(self):
        demand = self.value["request"]["demand"]
        demand["attempt_id"] = demand["prior_fulfillment"]["attempt_id"]
        self.rebind()
        self.assertIn("NEW_DEMAND_MUST_NOT_REUSE_PRIOR_ATTEMPT", self.check()["errors"])

    def test_readback_must_match_generation_and_current_demand(self):
        readback = self.value["input"]["freshness_readback"]
        saved = readback["persisted_generation_id"]
        readback["persisted_generation_id"] = "another-generation"
        self.assertIn("GENERATION_READBACK_MISMATCH", self.check()["errors"])
        readback["persisted_generation_id"] = saved
        for stamp in ("2029-12-31T00:00:00Z", "2030-01-01T01:00:00Z"):
            readback["checked_at"] = stamp
            self.assertIn("CURRENT_DEMAND_NEEDS_FRESHNESS_READBACK", self.check()["errors"])

    def test_invocation_completion_independent_acceptance_and_usability_are_distinct(self):
        outcome = self.value["outcome"]
        outcome["invoked"] = False
        self.reject()
        outcome.update(invoked=True, consumer_usable=True)
        self.reject()
        outcome["independent_acceptance"] = "accepted"
        self.assertIn("INDEPENDENT_ACCEPTANCE_NEEDS_RECEIPT", self.check()["errors"])
        outcome["independent_receipt"] = self.acceptance("independent", "2")
        self.reject()  # Independent acceptance is not consumer acceptance.
        outcome["consumer_acceptance"] = "accepted"
        outcome["acceptance_receipt"] = self.acceptance("consumer", "3")
        self.assertTrue(self.check()["valid"])
        self.assertFalse(self.check()["execution_authorized"])

    def acceptance(self, role, digest):
        return {"role": role, "artifact": {"ref": "fixture://" + role, "sha256": digest * 64},
                "request_sha256": cc.digest(cc.canonical(self.value["request"])),
                "attempt_id": self.value["request"]["demand"]["attempt_id"],
                "persisted_generation_id": self.value["request"]["demand"]["persisted_generation_id"],
                "producer_artifact": copy.deepcopy(self.value["outcome"]["receipt"]["artifact"])}

    def test_public_branch_cannot_satisfy_private_destination(self):
        privacy = self.value["privacy"]
        privacy.update(input_class="private", publish_input=False,
                       requires_private_destination=True, destination_visibility="public")
        self.assertIn("PUBLIC_BRANCH_IS_NOT_PRIVATE_DESTINATION", self.check()["errors"])
        privacy["destination_visibility"] = "private"
        self.assertTrue(self.check()["valid"])

    def test_schedule_only_checkpoint_is_parked_not_consumer_usable(self):
        outcome = self.value["outcome"]
        outcome.update(state="parked", invoked=False, run_observed=False, consumer_usable=False)
        self.value["recovery"]["next_action"] = "park_and_route_to_owner"
        self.assertTrue(self.check()["valid"])
        outcome["consumer_usable"] = True
        self.reject()

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
