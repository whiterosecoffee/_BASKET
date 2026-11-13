"""Regressions from independent review of 8b9c88b; no external owner execution."""
import copy
import unittest

from orchestration import component_conformance as cc
from orchestration.clean_templates import lifecycle as lc


class LifecycleReviewRegressionTests(unittest.TestCase):
    def setUp(self):
        fixture = lc.read("lifecycle.examples.json")
        self.value = fixture["examples"]["market-readonly"]
        self.now = fixture["evaluation_time"]

    def check(self):
        result = lc.validate(self.value, now=self.now)
        self.assertFalse(result["execution_authorized"])
        return result

    def legacy_acceptances(self):
        outcome = self.value["outcome"]
        outcome.update(independent_acceptance="accepted", consumer_acceptance="accepted")
        outcome["independent_receipt"] = copy.deepcopy(outcome["receipt"]["artifact"])
        outcome["acceptance_receipt"] = copy.deepcopy(outcome["receipt"]["artifact"])

    def rebind_producer(self):
        digest = cc.digest(cc.canonical(self.value["request"]))
        self.value["acknowledgment"]["request_sha256"] = digest
        self.value["outcome"]["receipt"]["request_sha256"] = digest

    def test_f1_malformed_nested_task_returns_structured_rejection(self):
        saved = copy.deepcopy(self.value["task"])
        no_branch = copy.deepcopy(saved)
        del no_branch["branch"]
        for value in ({}, no_branch, {**saved, "branch": {}}, [], None):
            with self.subTest(task=value):
                self.value["task"] = value
                self.assertFalse(self.check()["valid"])

    def test_f2_schema_accepted_lowercase_timestamps_parse_consistently(self):
        self.now = self.now.lower()
        self.value["request"]["deadline"] = self.value["request"]["deadline"].lower()
        self.value["request"]["demand"]["requested_at"] = self.now
        self.value["request"]["demand"]["prior_fulfillment"]["completed_at"] = "2029-12-31t00:00:00z"
        self.value["input"]["qualified_until"] = "2030-01-02t00:00:00z"
        self.value["input"]["freshness_readback"]["checked_at"] = self.now
        self.rebind_producer()
        self.assertTrue(self.check()["valid"])

    def test_f3_producer_artifact_cannot_fill_both_acceptance_slots(self):
        self.legacy_acceptances()
        self.assertFalse(self.check()["valid"])

    def test_f3_old_acceptances_do_not_survive_rebound_new_request(self):
        self.legacy_acceptances()
        self.value["request"]["request_id"] += "-new"
        self.value["request"]["idempotency_key"] += "-new"
        self.rebind_producer()
        self.assertFalse(self.check()["valid"])

    def test_f4_failed_checkpoint_cannot_retain_accepted_labels(self):
        self.legacy_acceptances()
        self.value["outcome"].update(state="failed", consumer_usable=False)
        self.assertFalse(self.check()["valid"])

    def bound_acceptances(self):
        outcome = self.value["outcome"]
        demand = self.value["request"]["demand"]
        for role, slot, status, digit in (
                ("independent", "independent_receipt", "independent_acceptance", "2"),
                ("consumer", "acceptance_receipt", "consumer_acceptance", "3")):
            outcome[status] = "accepted"
            outcome[slot] = {
                "role": role, "artifact": {"ref": "fixture://" + role, "sha256": digit * 64},
                "request_sha256": cc.digest(cc.canonical(self.value["request"])),
                "attempt_id": demand["attempt_id"],
                "persisted_generation_id": demand["persisted_generation_id"],
                "producer_artifact": copy.deepcopy(outcome["receipt"]["artifact"])}
        outcome["consumer_usable"] = True

    def test_bound_acceptances_repeat_without_mutation_or_authority(self):
        self.bound_acceptances()
        before = copy.deepcopy(self.value)
        first = self.check()
        self.assertTrue(first["valid"], first["errors"])
        self.assertEqual(first, self.check())
        self.assertEqual(before, self.value)

    def test_bound_acceptances_reject_rebound_request(self):
        self.bound_acceptances()
        self.value["request"]["request_id"] += "-new"
        self.rebind_producer()
        self.assertIn("ACCEPTANCE_BINDING_MISMATCH", self.check()["errors"])

    def test_acceptance_role_attempt_generation_and_producer_are_bound(self):
        self.bound_acceptances()
        original = copy.deepcopy(self.value)
        for slot in ("independent_receipt", "acceptance_receipt"):
            for key, value in (("role", "wrong"), ("attempt_id", "wrong"),
                               ("persisted_generation_id", "wrong"),
                               ("request_sha256", "0" * 64),
                               ("producer_artifact", {"ref": "fixture://wrong", "sha256": "0" * 64})):
                with self.subTest(slot=slot, key=key):
                    self.value = copy.deepcopy(original)
                    self.value["outcome"][slot][key] = value
                    self.assertFalse(self.check()["valid"])

    def test_acceptance_artifact_aliases_reject_by_ref_or_digest(self):
        self.bound_acceptances()
        original = copy.deepcopy(self.value)
        for source in ("receipt", "independent_receipt"):
            for key in ("ref", "sha256"):
                with self.subTest(source=source, key=key):
                    self.value = copy.deepcopy(original)
                    outcome = self.value["outcome"]
                    outcome["acceptance_receipt"]["artifact"][key] = outcome[source]["artifact"][key]
                    self.assertIn("ACCEPTANCE_EVIDENCE_MUST_BE_DISTINCT", self.check()["errors"])

    def test_bound_acceptance_rejects_failed_and_parked_results(self):
        self.bound_acceptances()
        for state in ("failed", "parked"):
            self.value["outcome"].update(state=state, consumer_usable=False)
            self.assertIn("ACCEPTANCE_REQUIRES_SUCCESSFUL_RESULT", self.check()["errors"])

    def test_pending_or_rejected_status_cannot_keep_acceptance_receipt(self):
        self.bound_acceptances()
        for status in ("pending", "rejected"):
            self.value["outcome"].update(consumer_acceptance=status, consumer_usable=False)
            self.assertIn("ACCEPTANCE_RECEIPT_REQUIRES_ACCEPTED_STATUS", self.check()["errors"])
