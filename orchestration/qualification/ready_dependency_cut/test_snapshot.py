"""Integrity checks for one immutable decision artifact, not a queue engine."""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent
SNAPSHOT = ROOT / "snapshot-2026-11-12.json"
SOURCE = ROOT / "canonical-l1-source.md"


def validate(s):
    errors = []
    actions = s["actions"]
    ids = [a["id"] for a in actions]
    if len(ids) != 25 or len(set(ids)) != 25:
        errors.append("action identity")
    known = set(ids)
    for a in actions:
        if not a["owner_sources"] or not a["acceptance_test"] or not a["input_revision"]:
            errors.append("missing provenance")
        if any(not x.startswith("https://github.com/whiterosecoffee/_BASKET/issues/") for x in a["owner_sources"]):
            errors.append("owner source")
        if a["authoritative_source"] != s["authority"]:
            errors.append("canonical authority")
        if any(d not in known or d == a["id"] for d in a["dependencies"]):
            errors.append("dangling dependency")
        if a["dependencies"] and (a["classification"] != "predecessor_acceptance_required" or not a["blocker_conditions"]):
            errors.append("lost acceptance gate")
        if a["complete"] or a["rank"] is not None:
            errors.append("unaccepted canonical promotion")
    visiting, visited = set(), set()
    graph = {a["id"]: a["dependencies"] for a in actions}
    def walk(node):
        if node in visiting:
            errors.append("dependency cycle")
            return
        if node in visited or node not in graph:
            return
        visiting.add(node)
        for child in graph[node]:
            walk(child)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        walk(node)
    lanes = s["cloud_lanes"]
    lane_ids = {c["id"] for c in lanes}
    if len(lane_ids) != len(lanes) or len({c["owner_issue"] for c in lanes}) != len(lanes):
        errors.append("duplicate assignment")
    ranked = [c for c in lanes if c["rank"] is not None]
    if len({c["rank"] for c in ranked}) != len(ranked):
        errors.append("duplicate rank")
    for c in ranked:
        if not c["authorized"] or not c["unblocked"] or c["blockers"]:
            errors.append("ineligible ranking")
        if not c["owner_source"] or not c["claim_source"] or not c["acceptance_tests"] or not c["branch"]:
            errors.append("unverified rank")
    for i, left in enumerate(lanes):
        for right in lanes[i+1:]:
            for p in left["write_paths"]:
                for q in right["write_paths"]:
                    a,b = p.removesuffix("/**"),q.removesuffix("/**")
                    if a == b or a.startswith(b+"/") or b.startswith(a+"/"):
                        errors.append("overlapping lanes")
    coverage = s["lane_coverage"]
    if coverage["observed"] != len(lanes) or coverage["unknown"] != coverage["requested"] - len(lanes):
        errors.append("coverage count")
    if coverage["complete"] != (coverage["unknown"] == 0):
        errors.append("invented lane coverage")
    for chosen in s["minimum_useful_cut"]["selected"]:
        if chosen not in lane_ids:
            errors.append("unknown cut member")
        elif not any(c["id"] == chosen and c["authorized"] and c["unblocked"] and not c["blockers"] for c in lanes):
            errors.append("blocked cut member")
    if s["ranking_policy"]["new_assignments"] != 0:
        errors.append("new assignment")
    if len(s["second_reuse_cases"]) < 2:
        errors.append("missing reuse case")
    for case in s["second_reuse_cases"]:
        if not all(case.get(k) for k in ("owner_sources","implementation","input_revision","contract_seam","acceptance_tests","test_owner","why_not_qualified")):
            errors.append("incomplete reuse seam")
        if case["executed_here"] or case["qualified"]:
            errors.append("fabricated reuse execution")
    required_classes = {"laptop_execution", "archive_reference_only", "approval", "required_source_input", "predecessor_acceptance", "existing_ownership"}
    if {c["id"] for c in s["dependency_classes"]} != required_classes:
        errors.append("collapsed blocker classes")
    for p in s["open_pr_inventories"]:
        if any(f.startswith("orchestration/qualification/ready_dependency_cut/") for f in p["files"]):
            errors.append("prior owner collision")
    return errors


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.s = json.loads(SNAPSHOT.read_text())

    def test_snapshot_integrity(self):
        self.assertEqual(validate(self.s), [])

    def test_exact_retained_canonical_acceptance(self):
        lines = [l for l in SOURCE.read_text().splitlines() if l.startswith("- [ ] **L1-")]
        self.assertEqual(len(lines), 25)
        for action,line in zip(self.s["actions"], lines):
            self.assertEqual(action["acceptance_test"], line.split("Exit: ")[1])
            self.assertIn(action["id"], line)

    def test_source_pins_and_capture(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), self.s["canonical_capture_sha256"])
        for pin in self.s["source_pins"]:
            self.assertEqual(hashlib.sha256((ROOT.parents[2]/pin["path"]).read_bytes()).hexdigest(), pin["sha256"])

    def test_ready_horizon_retained(self):
        self.assertEqual([a["id"] for a in self.s["actions"] if not a["dependencies"]],
                         ["L1-01","L1-02","L1-23"])

    def test_dangling_reference_rejected(self):
        self.s["actions"][2]["dependencies"] = ["L1-99"]
        self.assertIn("dangling dependency", validate(self.s))

    def test_dependency_cycle_rejected(self):
        self.s["actions"][0]["dependencies"] = ["L1-03"]
        self.assertIn("dependency cycle", validate(self.s))

    def test_blocked_or_unauthorized_rank_rejected(self):
        for key,value in (("blockers",["approval pending"]),("authorized",False),("unblocked",False)):
            with self.subTest(key=key):
                s=copy.deepcopy(self.s)
                s["cloud_lanes"][0][key]=value
                self.assertIn("ineligible ranking",validate(s))

    def test_overlapping_lane_rejected(self):
        self.s["cloud_lanes"][1]["write_paths"] = self.s["cloud_lanes"][0]["write_paths"]
        self.assertIn("overlapping lanes", validate(self.s))

    def test_duplicate_assignment_rejected(self):
        self.s["cloud_lanes"].append(copy.deepcopy(self.s["cloud_lanes"][0]))
        self.assertIn("duplicate assignment", validate(self.s))

    def test_missing_owner_and_acceptance_rejected(self):
        self.s["actions"][0]["owner_sources"]=[]
        self.s["actions"][0]["acceptance_test"]=None
        self.assertIn("missing provenance", validate(self.s))

    def test_no_open_pr_completion_inference(self):
        self.s["actions"][7]["complete"]=True
        self.assertIn("unaccepted canonical promotion", validate(self.s))

    def test_missing_lane_identity_not_invented(self):
        s=copy.deepcopy(self.s)
        s["lane_coverage"]["unknown"]=1
        s["lane_coverage"]["complete"]=True
        self.assertIn("invented lane coverage",validate(s))

    def test_reuse_execution_cannot_be_claimed(self):
        self.s["second_reuse_cases"][0]["qualified"]=True
        self.assertIn("fabricated reuse execution",validate(self.s))

    def test_immutable_replay(self):
        before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,SNAPSHOT)}
        self.assertEqual(validate(self.s),validate(copy.deepcopy(self.s)))
        self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in before})

    def test_claim_uses_existing_schema(self):
        from jsonschema import Draft202012Validator
        repo=ROOT.parents[2]
        Draft202012Validator(json.loads((repo/"schemas/worker-task.v1.json").read_text())).validate(
            json.loads((ROOT/"task.json").read_text()))


if __name__ == "__main__":
    unittest.main()
