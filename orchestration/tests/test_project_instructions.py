"""Document regression checks, not proof of semantic acceptance or live execution."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
PROJECT = (ROOT / "orchestration/PROJECT_INSTRUCTIONS.md").read_text(encoding="utf-8")
PROTOCOL = (ROOT / "orchestration/WORKER_PROTOCOL.md").read_text(encoding="utf-8")
DOCUMENTS = {"AGENTS": AGENTS, "Project": PROJECT, "Protocol": PROTOCOL}


class ProjectInstructionTests(unittest.TestCase):
    def test_complete_project_text_fits_delivery_budget(self):
        self.assertLessEqual(len(PROJECT), 8000)
        self.assertTrue(PROJECT.endswith("\n"))
        for heading in range(1, 8):
            self.assertRegex(PROJECT, rf"(?m)^## {heading}\. ")
        self.assertIn("ONE copyable block", PROJECT)
        self.assertIn("complete downloadable file", PROJECT)

    def test_one_shared_routing_entrypoint(self):
        self.assertIn("## Work-routing policy", AGENTS)
        self.assertIn("shared work-routing policy in `AGENTS.md`", PROJECT)
        self.assertIn("../AGENTS.md#work-routing-policy", PROTOCOL)

    def test_read_and_capture_are_not_blanket_branch_triggers(self):
        self.assertIn("Read-only questions need no new issue, branch or worker", PROJECT)
        self.assertIn("existing authorized writer/storage contract without a branch", PROJECT)
        for text in DOCUMENTS.values():
            self.assertIn("ingestion-contract change", text)
            self.assertIn("before writing", text)

    def test_feature_continuity_and_explicit_transfer(self):
        for name, text in DOCUMENTS.items():
            with self.subTest(document=name):
                self.assertIn("canonical issue", text)
                self.assertIn("feature branch", text)
                self.assertRegex(text, r"controller-approved (?:owner )?transfer")
        self.assertIn("new chat alone needs no new issue or branch", PROJECT)
        self.assertRegex(PROJECT, r"(?:matching unclaimed|unclaimed matching) intake issue")
        self.assertIn("Separate unrelated problems", PROJECT)

    def test_historical_bootstrap_and_fixed_priorities_are_removed(self):
        for name, text in DOCUMENTS.items():
            with self.subTest(document=name):
                self.assertNotIn("work/1-conversation-sparks-orchestration", text)
                self.assertNotIn("after PR #2 merges", text)
                self.assertNotIn("First integration objective", text)
                self.assertNotIn("Prioritize strict SFTBY", text)
        self.assertIn("without a first-release prerequisite", PROJECT)

    def test_issues_queue_is_not_replaced_by_a_dashboard(self):
        for text in DOCUMENTS.values():
            self.assertIn("queue.json", text)
        self.assertIn("GitHub Issues are the working queue", PROJECT)
        self.assertIn("Projects is an optional view", PROJECT)
        self.assertIn("issues/136", PROJECT)

    def test_source_obligations_and_receiver_receipts_survive(self):
        for text in DOCUMENTS.values():
            self.assertIn("source obligations", text)
            self.assertIn("receiver claim", text)
            self.assertIn("independent assessment", text)
            self.assertIn("semantic completeness", text)
        self.assertIn("accepted intake is not completed implementation", PROJECT)

    def test_data_contracts_and_blocked_capture_are_explicit(self):
        for text in (AGENTS, PROJECT):
            self.assertIn("_DATA/<TICKER>/<YYYY-MM-DD>.1m.jsonl", text)
            self.assertIn("NVDA-only", text)
            self.assertIn("authorized storage", text)
            self.assertIn("provenance", text)
        self.assertIn("zero duplicates", PROJECT)
        self.assertIn("Do not create a replacement canonical store", PROJECT)
        self.assertIn("Time to Die", PROJECT)
        self.assertIn("USD", PROJECT)

    def test_gates_are_not_replaced_by_routing_convenience(self):
        for token in ("draft PR", "explicit authorization", "auto-merge", "deploy"):
            self.assertIn(token, PROJECT)
        for text in DOCUMENTS.values():
            self.assertIn("still-valid evidence", text)
            self.assertIn("baseline", text)
        self.assertIn("failed, skipped and not-run", PROJECT)
        self.assertIn("branch-published, main-merged or applied in ChatGPT Project settings", PROJECT)

    def test_referenced_main_documents_exist(self):
        paths = re.findall(r"`((?:architecture|orchestration|runtime)/[^`*<>]+\.(?:md|json))`", PROJECT)
        self.assertGreaterEqual(len(paths), 9)
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), path)
        for target in re.findall(r"\]\(([^)]+)\)", PROTOCOL):
            if "://" not in target:
                path = target.split("#", 1)[0]
                self.assertTrue((ROOT / "orchestration" / path).is_file(), target)


if __name__ == "__main__":
    unittest.main()
