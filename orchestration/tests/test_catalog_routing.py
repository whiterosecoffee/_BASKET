"""Catalog routing regressions; not semantic approval or operational evidence."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "orchestration"))
from validate_sparks import validate as validate_sparks


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def routing_errors(catalog):
    """Check explicit routing safeguards, including every reusable prompt."""
    errors = []
    reference = "AGENTS.md#work-routing-policy"
    if catalog.get("policy_reference") != reference:
        errors.append("shared policy reference missing")
    notice = catalog.get("historical_routing_notice", "")
    for token in ("first_task", "priority", "launch_sequence", "handoffs", "#136"):
        if token not in notice:
            errors.append("historical context missing: " + token)
    active = [catalog.get("bootstrap_policy", ""), *catalog["global_rules"].values(),
              *catalog["worker_protocol"]["constraints"]]
    forbidden = ("work/1-conversation-sparks-orchestration", "after PR #2 merges",
                 "Until PR #2 is merged", "for THIS conversation", "unique branch per chat",
                 "one new worker issue/branch per new conversation")
    for value in active:
        if isinstance(value, str) and any(token in value for token in forbidden):
            errors.append("obsolete active routing")
    for key, token in (("bootstrap_if_unmerged", reference), ("ci_repair_first", "#136"),
                       ("reusable_workers", reference), ("merge_readiness", reference)):
        if token not in catalog["global_rules"].get(key, ""):
            errors.append("current policy missing: " + key)
    for spark in catalog["sparks"]:
        prompt = spark.get("launch_prompt", "")
        required = (
            reference, "AGENTS.md#small-reusable-blocks-and-complete-handoffs",
            "live GitHub issue #136", "canonical issue and feature branch",
            "knowledgeable branch worker", "controller-approved transfer", "exact head",
            "exclusive writer", "Read-only work and authorized routine capture",
            "Create a NEW GitHub issue only for a genuinely new problem with no matching unclaimed intake issue",
            "work/<issue-number>-<objective-slug>", "task claim before repository-content writes",
            "only for that new engineering problem, create one work/",
            "When repository content changes, run applicable checks",
            "new writer or ingestion-contract change enters scoped engineering before writing",
            "existing receiver issue/intake", "create a linked issue only if no suitable record exists",
            "source obligations", "No direct edits outside the recorded exclusive scope or to main",
            "draft PR", "No merge, auto-merge, tag, release or deployment without explicit authorization",
        )
        if any(token not in prompt for token in required):
            errors.append(spark["id"] + ": routing safeguard missing")
        if any(token in prompt for token in forbidden):
            errors.append(spark["id"] + ": obsolete prompt routing")
    return errors


def version_errors(catalog, manifest, scopes):
    expected = catalog["catalog_version"]
    return [] if (manifest["orchestration"]["catalog_version"] == expected and
                  scopes["source_spark_catalog_version"] == expected) else ["catalog version mismatch"]


class CatalogRoutingTests(unittest.TestCase):
    def setUp(self):
        self.catalog = read("orchestration/sparks.json")

    def test_shared_policy_and_every_prompt_pass(self):
        self.assertEqual(routing_errors(self.catalog), [])
        self.assertIn("## Work-routing policy", (ROOT / "AGENTS.md").read_text())

    def test_original_registry_validator_still_passes(self):
        self.assertEqual(validate_sparks(self.catalog), [])

    def test_prompt_scope_and_domain_contract_follow_catalog(self):
        for spark in self.catalog["sparks"]:
            with self.subTest(spark=spark["id"]):
                prompt = spark["launch_prompt"]
                for token in (spark["id"], spark["title"], spark["objective"], spark["acceptance"],
                              *spark["write_paths"], *spark["read_paths"]):
                    self.assertIn(token, prompt)
                self.assertIn("Dependencies: " + (", ".join(spark["dependencies"]) or "none") + ".", prompt)

    def test_historical_tasks_are_retained_but_not_reissued(self):
        self.assertTrue(self.catalog["launch_sequence"])
        self.assertTrue(self.catalog["handoffs"])
        for spark in self.catalog["sparks"]:
            with self.subTest(spark=spark["id"]):
                self.assertTrue(spark["first_task"])
                self.assertNotIn("First task: " + spark["first_task"], spark["launch_prompt"])
                self.assertIn("context, not the current assignment", spark["launch_prompt"])

    def test_catalog_versions_remain_coherent(self):
        manifest = read("architecture/version-manifest.json")
        scopes = read("orchestration/planner/worker-scopes.json")
        self.assertEqual(version_errors(self.catalog, manifest, scopes), [])

    def test_existing_readiness_and_evidence_contracts_are_preserved(self):
        rules = self.catalog["global_rules"]
        self.assertTrue(rules["no_cross_domain_writes"])
        self.assertEqual(rules["reporting_currency"], "USD")
        self.assertIn("basket.worker_resolution@1", rules["worker_resolution"])
        self.assertIn("explicit authorization", rules["non_merge"])
        self.assertIn("main CI verification", rules["readiness"])
        self.assertIn("not proof of operation", rules["dependency_semantics"])

    def test_negative_one_stale_prompt_fails(self):
        self.catalog["sparks"][-1]["launch_prompt"] += " Read bootstrap after PR #2 merges."
        self.assertIn("B21: obsolete prompt routing", routing_errors(self.catalog))

    def test_negative_unconditional_new_issue_fails(self):
        p = self.catalog["sparks"][0]
        p["launch_prompt"] = p["launch_prompt"].replace(
            "Create a NEW GitHub issue only for a genuinely new problem with no matching unclaimed intake issue",
            "Create a NEW GitHub issue")
        # Original validator still sees an issue guard; the new check rejects
        # removal of its conditional routing rather than weakening that guard.
        self.assertEqual(validate_sparks(self.catalog), [])
        self.assertIn("B00: routing safeguard missing", routing_errors(self.catalog))

    def test_negative_unconditional_branch_creation_fails(self):
        spark = self.catalog["sparks"][0]
        spark["launch_prompt"] = spark["launch_prompt"].replace(
            "only for that new engineering problem, create one work/", "create one work/")
        self.assertIn("B00: routing safeguard missing", routing_errors(self.catalog))

    def test_negative_unconditional_draft_pr_fails(self):
        spark = self.catalog["sparks"][0]
        spark["launch_prompt"] = spark["launch_prompt"].replace(
            "When repository content changes, run applicable checks", "Run applicable checks")
        self.assertIn("B00: routing safeguard missing", routing_errors(self.catalog))

    def test_negative_lost_owner_transfer_fails(self):
        self.catalog["sparks"][0]["launch_prompt"] = self.catalog["sparks"][0]["launch_prompt"].replace("exclusive writer", "a writer")
        self.assertTrue(routing_errors(self.catalog))

    def test_negative_unscoped_ingestion_change_fails(self):
        self.catalog["sparks"][0]["launch_prompt"] = self.catalog["sparks"][0]["launch_prompt"].replace("ingestion-contract change", "data read")
        self.assertTrue(routing_errors(self.catalog))

    def test_negative_historical_context_without_notice_fails(self):
        self.catalog.pop("historical_routing_notice")
        self.assertTrue(routing_errors(self.catalog))

    def test_negative_old_global_rule_fails(self):
        self.catalog["global_rules"]["reusable_workers"] = "one new worker issue/branch per new conversation"
        self.assertIn("obsolete active routing", routing_errors(self.catalog))

    def test_negative_fixed_historical_priority_fails(self):
        self.catalog["global_rules"]["ci_repair_first"] = "First fix the historical SFTBY relationships failure."
        self.assertIn("current policy missing: ci_repair_first", routing_errors(self.catalog))

    def test_negative_version_drift_fails(self):
        manifest = read("architecture/version-manifest.json")
        scopes = read("orchestration/planner/worker-scopes.json")
        scopes["source_spark_catalog_version"] = "0.0.0"
        self.assertEqual(version_errors(self.catalog, manifest, scopes), ["catalog version mismatch"])

    def test_negative_cross_domain_overlap_still_rejected(self):
        self.catalog["sparks"][1]["write_paths"].append("runtime/**")
        self.assertTrue(any("overlapping write ownership" in e for e in validate_sparks(self.catalog)))


if __name__ == "__main__":
    unittest.main()
