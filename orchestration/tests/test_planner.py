#!/usr/bin/env python3
"""Deterministic B00 planner and recombinable-role regression tests (offline).

Run from repository root:
python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
"""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("basket_planner", ROOT / "orchestration/planner.py")
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)


class PlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = planner.load(ROOT / "orchestration/planner/queue.json")
        cls.library = planner.load(ROOT / "orchestration/planner/worker-library.json")
        cls.catalog = planner.load(ROOT / "orchestration/sparks.json")
        cls.evidence = planner.load(ROOT / "orchestration/examples/github-evidence-2026-10-16.json")

    def plan(self, queue=None, library=None, evidence=None, active=()):
        return planner.run_plan(queue or self.queue, library or self.library,
                                self.catalog, evidence or self.evidence, active)

    def entries(self, **kwargs):
        return {x["id"]: x for x in self.plan(**kwargs)["ordered_tasks"]}

    def test_library_and_queue_have_valid_references(self):
        self.assertEqual(planner.validate_plan(self.queue, self.library, self.catalog), [])
        self.assertEqual(len(self.queue["tasks"]), 11)
        self.assertEqual(self.queue["active_worker_limit"], 3)

    def test_task_queue_is_not_a_live_status_claim(self):
        out = self.plan()
        self.assertFalse(out["continuous_background_monitoring"] )
        self.assertTrue(out["no_automatic_merge"])
        self.assertTrue(out["no_automatic_issue_or_branch_creation"])
        self.assertEqual(out["source_evidence_observed_at"],
                         self.evidence["observed_at"])

    def test_dependency_and_first_wave_states(self):
        e = self.entries()
        self.assertEqual(e["T-001"]["state"], "review_ready_ci_green")
        self.assertEqual(e["T-002"]["state"], "blocked_upstream")
        self.assertEqual(e["T-003"]["state"], "blocked_upstream")
        self.assertEqual(e["T-004"]["state"], "resume_incomplete")
        self.assertEqual(e["T-005"]["state"], "resume_incomplete")
        self.assertEqual(e["T-006"]["state"], "ready_new_worker")
        self.assertEqual(e["T-007"]["state"], "blocked_upstream")
        self.assertEqual(e["T-008"]["state"], "blocked_upstream")
        self.assertEqual(e["T-009"]["state"], "blocked_upstream")
        self.assertEqual(e["T-010"]["state"], "evidence_unavailable")
        self.assertEqual(e["T-011"]["state"], "blocked_upstream")

    def test_active_worker_limit_blocks_extra_new_chats(self):
        p = self.plan(active=("T-004", "T-005"))
        self.assertEqual(p["worker_slots_remaining"], 1)
        self.assertEqual(p["next_new_worker"], "T-006")
        self.assertIsNone(self.plan(active=("T-004", "T-005", "T-006"))["next_new_worker"])

    def test_reviews_do_not_count_as_parallel_code_workers(self):
        p = self.plan(active=("T-004", "T-005"))
        self.assertEqual(p["next_orchestrator_action"], "T-001")
        with self.assertRaises(ValueError):
            self.plan(active=("T-001",))

    def test_composed_profiles_cover_all_required_recipe_skills(self):
        assert not planner.validate_plan(self.queue, self.library, self.catalog)
        altered = copy.deepcopy(self.queue)
        t = next(x for x in altered["tasks"] if x["id"] == "T-007")
        t["profiles"] = ["inference_analyst"]
        failures = planner.validate_plan(altered, self.library, self.catalog)
        self.assertTrue(any("capability not provided" in x for x in failures))

    def test_cross_domain_writes_fail_closed(self):
        altered = copy.deepcopy(self.queue)
        t = next(x for x in altered["tasks"] if x["id"] == "T-004")
        t["write_scope"].append("schemas/worker-resolution.v1.json")
        failures = planner.validate_plan(altered, self.library, self.catalog)
        self.assertTrue(any("claims other domain" in x for x in failures))

    def test_new_worker_cannot_preassign_legacy_issue(self):
        altered = copy.deepcopy(self.queue)
        t = next(x for x in altered["tasks"] if x["id"] == "T-006")
        t["issue_number"] = 11
        self.assertTrue(any("cannot preassign" in x
                            for x in planner.validate_plan(altered, self.library, self.catalog)))

    def test_cycle_detection_is_strict(self):
        altered = copy.deepcopy(self.queue)
        t = next(x for x in altered["tasks"] if x["id"] == "T-001")
        t["depends_on"].append({"task_id": "T-002", "gate": "merged"})
        self.assertTrue(any("cycle" in x for x in
                            planner.validate_plan(altered, self.library, self.catalog)))

    def test_old_branch_ci_not_valid_on_changed_head(self):
        altered = copy.deepcopy(self.evidence)
        pr = next(x for x in altered["pull_requests"] if x["number"] == 10)
        pr["head_sha"] = "0" * 40
        e = self.entries(evidence=altered)
        self.assertEqual(e["T-001"]["state"], "review_required_checks_pending")
        self.assertFalse(e["T-001"]["branch_ci_pass"])

    def test_merge_does_not_imply_main_ci(self):
        altered = copy.deepcopy(self.evidence)
        pr = next(x for x in altered["pull_requests"] if x["number"] == 10)
        pr.update({"merged": True, "draft": False, "state": "closed"})
        e = self.entries(evidence=altered)
        self.assertEqual(e["T-001"]["state"], "integrated_main_ci_unverified")
        self.assertTrue(e["T-002"]["ready_for_action"])
        self.assertEqual(e["T-003"]["state"], "blocked_upstream")

    def test_reusable_dispatch_prompt_does_not_claim_actions(self):
        prompt = planner.render_next_worker(self.queue, "T-006")
        self.assertIn("Create ONE NEW issue", prompt)
        self.assertIn("ONE UNIQUE", prompt)
        self.assertIn("B21", prompt)
        self.assertIn("Never merge", prompt)
        self.assertNotIn("Your branch has been created", prompt)

    def test_path_matching_with_globs_is_domain_limited(self):
        self.assertTrue(planner.path_matches("tickers/*/events.json", "tickers/SFTBY/events.json"))
        self.assertFalse(planner.path_matches("tickers/*/events.json", "tickers/SFTBY/subdir/events.json"))
        self.assertTrue(planner.scope_subset("research/events/SFTBY/**", ["research/events/**"]))
        self.assertFalse(planner.scope_subset("schemas/**", ["research/events/**"]))



    def test_post_merge_simulation_prioritizes_new_b01_qc(self):
        # Simulated completed integration. Not a substitute for live GitHub evidence.
        evidence = copy.deepcopy(self.evidence)
        for p in evidence["pull_requests"]:
            if p["number"] in (2, 10, 13):
                p.update({"merged": True, "draft": False, "state": "closed"})
        evidence["main_commit"] = "5bf7fc14e2577e479279efdedfeae4b90bf85820"
        evidence["workflow_runs"].append({
            "id": 38990763024, "url": "https://github.com/whiterosecoffee/_BASKET/actions/runs/38990763024",
            "head_sha": evidence["main_commit"], "conclusion": "success",
            "name": "Validate BASKET data"})
        out = self.plan(evidence=evidence, active=("T-004", "T-005"))
        entries = {x["id"]: x for x in out["ordered_tasks"]}
        self.assertEqual(entries["T-001"]["state"], "integrated_main_ci_verified")
        self.assertEqual(entries["T-003"]["state"], "integrated_main_ci_verified")
        self.assertEqual(entries["T-009"]["state"], "ready_new_worker")
        self.assertEqual(out["next_new_worker"], "T-009")

if __name__ == "__main__":
    unittest.main()
