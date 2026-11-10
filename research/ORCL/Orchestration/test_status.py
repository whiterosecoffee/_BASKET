import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import status  # noqa: E402

VSET = {
    "id": "T",
    "title": "T",
    "issue": 1,
    "branch": "work/1-t",
    "folder": "research/ORCL/T",
    "write_paths": ["research/ORCL/T/**"],
    "files": ["README.md", "A.md"],
}
TREE_OK = {"research/ORCL/T/README.md", "research/ORCL/T/A.md"}
BRANCH = {"commit": {"sha": "abc"}}
CLEAN = {"ahead_by": 1, "behind_by": 0, "files": [{"filename": "research/ORCL/T/A.md"}]}
PR = [{"number": 5, "state": "open"}]


def flags(**kw):
    args = dict(ownership_status="ratified", branch_info=BRANCH, compare=CLEAN, prs=PR,
                tree_paths=TREE_OK, tree_truncated=False, other_pr_files={})
    args.update(kw)
    return status.vector_flags(VSET, args["ownership_status"], args["branch_info"], args["compare"],
                               args["prs"], args["tree_paths"], args["tree_truncated"], args["other_pr_files"])


class PathMatching(unittest.TestCase):
    def test_prefix_pattern(self):
        self.assertTrue(status.matches("a/b/**", "a/b/c.md"))
        self.assertTrue(status.matches("a/b/**", "a/b/c/d.md"))
        self.assertFalse(status.matches("a/b/**", "a/bc/d.md"))
        self.assertFalse(status.matches("a/b/**", "a/b"))

    def test_exact_pattern(self):
        self.assertTrue(status.matches("a/b.md", "a/b.md"))
        self.assertFalse(status.matches("a/b.md", "a/b.md2"))


class Flags(unittest.TestCase):
    def test_clean_ratified_branch_has_only_unmerged(self):
        self.assertEqual(flags(), ["UNMERGED"])

    def test_unratified_flag(self):
        self.assertIn("UNRATIFIED", flags(ownership_status="unratified"))

    def test_missing_branch_is_hard(self):
        self.assertEqual(flags(branch_info=None, compare=None), ["BRANCH_MISSING"])

    def test_no_pr(self):
        self.assertIn("NO_PR", flags(prs=[]))

    def test_drift(self):
        self.assertIn("DRIFT", flags(compare={**CLEAN, "behind_by": 3}))

    def test_scope_violation(self):
        bad = {**CLEAN, "files": [{"filename": "orchestration/sparks.json"}]}
        self.assertIn("SCOPE_VIOLATION", flags(compare=bad))

    def test_missing_file(self):
        self.assertIn("MISSING_FILE", flags(tree_paths={"research/ORCL/T/README.md"}))

    def test_tree_truncated_never_claims_missing(self):
        got = flags(tree_paths=set(), tree_truncated=True)
        self.assertIn("TREE_TRUNCATED", got)
        self.assertNotIn("MISSING_FILE", got)

    def test_collision_names_the_pr(self):
        self.assertIn("COLLISION:#9", flags(other_pr_files={9: ["research/ORCL/T/A.md"], 10: ["x.md"]}))
        self.assertFalse([f for f in flags(other_pr_files={10: ["x.md"]}) if f.startswith("COLLISION")])

    def test_files_truncated(self):
        many = {**CLEAN, "files": [{"filename": f"research/ORCL/T/{i}.md"} for i in range(300)]}
        self.assertIn("FILES_TRUNCATED", flags(compare=many))


class FailClosed(unittest.TestCase):
    def test_unapproved_path_rejected(self):
        with self.assertRaises(status.EvidenceUnavailable):
            status.fetch("/user/repos")
        with self.assertRaises(status.EvidenceUnavailable):
            status.fetch("/repos/someone/else/issues")


class RegistryIntegrity(unittest.TestCase):
    def setUp(self):
        self.reg = status.load_registry()

    def test_ids_unique_and_dependencies_exist(self):
        ids = [v["id"] for s in self.reg["vector_sets"] for v in s["vectors"]]
        self.assertEqual(len(ids), len(set(ids)))
        for s in self.reg["vector_sets"]:
            for v in s["vectors"]:
                for dep in v["depends_on"] + v.get("optional_inputs", []):
                    self.assertIn(dep, ids, f"{v['id']} depends on unknown {dep}")

    def test_no_dependency_cycles(self):
        graph = {v["id"]: v["depends_on"] for s in self.reg["vector_sets"] for v in s["vectors"]}
        state = {}

        def visit(node):
            if state.get(node) == 1:
                self.fail(f"cycle at {node}")
            if state.get(node) == 2:
                return
            state[node] = 1
            for d in graph[node]:
                visit(d)
            state[node] = 2

        for node in graph:
            visit(node)

    def test_files_live_inside_write_paths_and_sets_are_disjoint(self):
        sets = self.reg["vector_sets"]
        for s in sets:
            for name in s["files"]:
                self.assertTrue(status.any_match(s["write_paths"], f"{s['folder']}/{name}"))
        for i, a in enumerate(sets):
            for b in sets[i + 1:]:
                for name in a["files"]:
                    self.assertFalse(status.any_match(b["write_paths"], f"{a['folder']}/{name}"))

    def test_every_vector_file_is_listed(self):
        for s in self.reg["vector_sets"]:
            for v in s["vectors"]:
                self.assertIn(v["file"], s["files"])

    def test_assignments_match_registry_and_are_unclaimed(self):
        by_issue = {s["issue"]: s for s in self.reg["vector_sets"]}
        for path in sorted((HERE / "assignments").glob("*.json")):
            a = json.loads(path.read_text())
            self.assertEqual(a["schema"], "basket.agent_assignment@1")
            s = by_issue[a["source_issue"]]
            self.assertEqual(a["branch"], s["branch"])
            self.assertEqual(a["exclusive_write_paths"], s["write_paths"])
            self.assertIsNone(a["base_commit_sha"])
            self.assertIsNone(a["execution"]["lease_id"])
            self.assertFalse(a["execution"]["may_merge"])


if __name__ == "__main__":
    unittest.main()
