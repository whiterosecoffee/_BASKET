"""Offline regression fixtures for GitHub Project control-plane reducer."""
import unittest
from reconcile import reconcile, _scope_overlap


class ReconcileTests(unittest.TestCase):
    def test_scope_collision(self):
        self.assertTrue(_scope_overlap("orchestration/**", "orchestration/planner/queue.json"))
        self.assertTrue(_scope_overlap("research/*/entity.json", "research/CRWV/entity.json"))
        self.assertFalse(_scope_overlap("runtime/**", "research/CRWV/**"))

    def test_head_sha_gate(self):
        s = {"as_of": "2026-10-30T20:00:00Z", "issues": [
            {"number": 10, "state": "OPEN", "task": {"branch": "work/10-a", "worker": "agent",
             "write_paths": ["research/AAOI/**"]}}],
             "pull_requests": [{"number": 11, "headRefName": "work/10-a",
              "headRefOid": "new", "isDraft": True, "changedFiles": ["research/AAOI/a.json"],
              "checks": [{"head_sha": "old", "conclusion": "SUCCESS"}]}]}
        result = reconcile(s)
        self.assertEqual(result["items"][0]["validation"], "unverified")
        self.assertEqual(result["items"][0]["status"], "Draft PR")
        s["pull_requests"][0]["checks"][0]["head_sha"] = "new"
        self.assertEqual(reconcile(s)["items"][0]["validation"], "head_passed_not_integrated")

    def test_duplicate_claim_and_unverified_project(self):
        s = {"issues": [
             {"number": 1, "state": "OPEN", "task": {"branch": "a", "write_paths": ["orchestration/**"]}},
             {"number": 2, "state": "OPEN", "task": {"branch": "b", "write_paths": ["orchestration/x.py"]}}],
             "pull_requests": []}
        r = reconcile(s)
        self.assertEqual(r["summary"]["collision_flags"], 1)
        self.assertEqual(r["project_state"], "unverified")

    def test_open_issue_without_claim_not_active(self):
        r = reconcile({"issues": [{"number": 1, "state": "OPEN"}], "pull_requests": []})
        self.assertEqual(r["items"][0]["status"], "Backlog")


if __name__ == "__main__":
    unittest.main()
