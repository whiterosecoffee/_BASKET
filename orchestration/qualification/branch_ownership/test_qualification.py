"""Independent corpus assertions against unchanged published functions."""
import copy
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("branch_ownership_replay", HERE / "replay.py")
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
CORPUS = replay.load("cases.json")


class OwnershipCases(unittest.TestCase):
    def test_required_coverage_and_sources(self):
        cases = CORPUS["cases"]
        self.assertEqual(len(cases), 17)
        self.assertEqual(len({c["id"] for c in cases}), len(cases))
        self.assertEqual({c["category"] for c in cases}, {
            "success", "branch_conflict", "path_conflict", "stale_evidence",
            "uncertain_outcome", "archived_reference", "pending_approval"})
        sources = replay.load("sources.json")
        for case in cases:
            self.assertIn(case["policy_source"], sources["policy_sources"])
            self.assertTrue(case["expected_disposition"])
        replay.verify_sources()

    def test_complete_replay_is_deterministic_and_unchanged(self):
        original = copy.deepcopy(CORPUS)
        paths = [HERE / "cases.json", HERE / "sources.json"]
        before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in paths}
        first = replay.replay(CORPUS)
        second = replay.replay(CORPUS)
        self.assertEqual(first, second)
        self.assertEqual(first["observation_mismatches"], 0)
        self.assertEqual(first["explicit_gaps"], 7)
        self.assertTrue(first["unchanged_sources_and_inputs"])
        self.assertEqual(CORPUS, original)
        self.assertEqual(before, {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in paths})

    def test_saved_observations_match_actual_replay(self):
        self.assertEqual(replay.load("observed.json"), replay.replay())

    def test_incorrect_source_pin_fails_closed(self):
        manifest = replay.load("sources.json")
        manifest["sha256"]["orchestration/agentic/manager.py"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Pinned source mismatch"):
            replay.verify_sources(manifest)

    def test_fixture_corruption_is_not_silently_accepted(self):
        case = copy.deepcopy(CORPUS["cases"][0])
        case["arguments"]["task"]["write_paths"] = []
        with self.assertRaisesRegex(ValueError, "Invalid qualification fixture"):
            replay.observe(case)


def case_test(case):
    def test(self):
        before = copy.deepcopy(case)
        self.assertEqual(replay.observe(case), case["expected_observation"])
        self.assertEqual(case, before)
    return test


for case in CORPUS["cases"]:
    setattr(OwnershipCases, "test_case_" + case["id"], case_test(case))

if __name__ == "__main__":
    unittest.main()
