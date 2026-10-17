#!/usr/bin/env python3
"""B00 mocked tests: live GitHub evidence collector never writes to GitHub.

Run: python -m unittest discover -s orchestration/tests -p 'test_*.py' -v
"""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "basket_snapshot", ROOT / "orchestration/github_snapshot.py")
provider = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provider)


class GitHubSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue = provider.json.loads(
            (ROOT / "orchestration/planner/queue.json").read_text())

    def fake(self, endpoint):
        if endpoint.endswith("/branches/main"):
            return {"commit": {"sha": "a" * 40}}
        if "/issues/" in endpoint:
            num = int(endpoint.split("/issues/")[1])
            return {"number": num, "html_url":
                    "https://github.com/whiterosecoffee/_BASKET/issues/%d" % num,
                    "state": "open", "title": "Issue %d" % num}
        if "/pulls/" in endpoint and "/files" in endpoint:
            return [{"filename": "orchestration/examples/example.json"}]
        if "/pulls/" in endpoint:
            num = int(endpoint.split("/pulls/")[1])
            return {"html_url":
                    "https://github.com/whiterosecoffee/_BASKET/pull/%d" % num,
                    "head": {"ref": "work/%d-fixture" % num, "sha": "%040d" % num},
                    "base": {"ref": "main"}, "state": "open", "draft": True,
                    "merged_at": None}
        if "/actions/runs?" in endpoint:
            return {"workflow_runs": [{
                "id": 12345, "html_url":
                "https://github.com/whiterosecoffee/_BASKET/actions/runs/12345",
                "head_sha": "%040d" % 10, "conclusion": "success",
                "name": "Validate BASKET data"}]}
        raise AssertionError("Unexpected endpoint " + endpoint)

    def test_collect_read_only_snapshot(self):
        out = provider.collect(self.queue, self.fake)
        self.assertEqual(out["schema"], "basket.github_evidence@1")
        self.assertEqual(out["capture_mode"], "live_connector")
        self.assertEqual(out["main_commit"], "a" * 40)
        self.assertTrue(out["observed_at"])
        self.assertEqual(len(out["pull_requests"]), 5)
        self.assertEqual(out["workflow_runs"][0]["id"], 12345)
        self.assertIn(16, {x["number"] for x in out["issues"]})

    def test_missing_workflow_payload_fails_closed(self):
        def bad(endpoint):
            if "/actions/runs?" in endpoint:
                return {}
            return self.fake(endpoint)
        with self.assertRaises(provider.EvidenceUnavailable):
            provider.collect(self.queue, bad)

    def test_wrong_issue_identity_fails_closed(self):
        def bad(endpoint):
            row = self.fake(endpoint)
            if endpoint.endswith("/issues/8"):
                row["number"] = 999
            return row
        with self.assertRaises(provider.EvidenceUnavailable):
            provider.collect(self.queue, bad)

    def test_incomplete_pagination_is_error(self):
        with self.assertRaises(provider.EvidenceUnavailable):
            provider.paged(lambda _: [{"filename": "file"}] * 100,
                           "/repos/whiterosecoffee/_BASKET/pulls/10/files",
                           max_pages=2)

    def test_approved_public_api_path_required(self):
        with self.assertRaises(provider.EvidenceUnavailable):
            provider.fetch_json("/users/someone")


if __name__ == "__main__":
    unittest.main()
