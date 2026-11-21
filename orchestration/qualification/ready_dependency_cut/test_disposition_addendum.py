"""Integrity tests for the dated session-accounting addendum only."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
NAME = "disposition-addendum-2026-11-12-002.json"


def validate(record, baseline):
    errors = []
    sessions = record["sessions"]
    ids = [s["id"] for s in sessions]
    if len(sessions) != 10 or len(set(ids)) != 10:
        errors.append("ten distinct sessions required")
    published = [s for s in sessions if s["publication"]["status"] == "published"]
    unpublished = [s for s in sessions if s["publication"]["status"] == "unpublished"]
    if len(published) != 7 or len(unpublished) != 3:
        errors.append("publication partition")
    if record["counts"] != dict(identified_sessions=10, published_artifact_lanes=7,
                                unpublished_artifact_lanes=3, unidentified_sessions=0):
        errors.append("accounting counts")
    if {s["issue"] for s in published} != {245,246,247,248,249,250,252}:
        errors.append("published owner mapping")
    for s in sessions:
        if s["identity_status"] != "identified" or s["retry_denied_action"]:
            errors.append("identity or prohibited retry")
        if s["execution_acceptance"]["acceptance_status"] != "unknown":
            errors.append("unverified acceptance promotion")
        if s["execution_acceptance"]["independently_executed_in_this_addendum"]:
            errors.append("unverified execution promotion")
        p = s["publication"]
        if p["status"] == "published":
            if not p["pr"] or not p["head_sha"] or len(p["head_sha"]) != 40:
                errors.append("publication evidence missing")
        elif p["status"] == "unpublished":
            if p["pr"] is not None or p["head_sha"] is not None or p["reason"] != "publication_denied":
                errors.append("invented unpublished evidence")
    by_id = {s["id"]:s for s in sessions}
    for key in ("temporal-lineage-candidate","artifact-reproducibility-candidate"):
        if key not in by_id or by_id[key]["issue"] is not None or by_id[key]["branch"] is not None:
            errors.append("invented candidate claim")
    followups = record["followups"]
    if len(followups) != 1 or followups[0]["owner_issue"] != 246 or followups[0]["status"] != "pending_denied" or followups[0]["retry"]:
        errors.append("lost separate followup")
    expected = [{"id":a["id"],"owner_sources":a["owner_sources"],
                 "acceptance_test":a["acceptance_test"],
                 "authoritative_source":a["authoritative_source"],
                 "dependencies":a["dependencies"],"complete":False}
                for a in baseline["actions"]]
    if record["retained_actions"] != expected or len(expected) != 25:
        errors.append("changed obligation or acceptance")
    if record["ownership_check"]["new_assignments"] != 0:
        errors.append("assignment created")
    return errors


class DispositionTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT/NAME).read_text())
        self.baseline = json.loads((ROOT/"snapshot-2026-11-12.json").read_text())

    def test_complete_disposition(self):
        self.assertEqual(validate(self.record,self.baseline),[])

    def test_all_baseline_files_unchanged(self):
        for name, digest in self.record["baseline"]["preserved_files"].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
        self.assertEqual(self.record["baseline"]["sha256"],
                         hashlib.sha256((ROOT/"snapshot-2026-11-12.json").read_bytes()).hexdigest())

    def test_duplicate_identity_rejected(self):
        self.record["sessions"][-1]["id"]=self.record["sessions"][-2]["id"]
        self.assertIn("ten distinct sessions required",validate(self.record,self.baseline))

    def test_branch_does_not_imply_publication(self):
        lane=next(s for s in self.record["sessions"] if s["issue"] == 251)
        self.assertIsNotNone(lane["branch"])
        lane["publication"]["status"]="published"
        self.assertIn("publication partition",validate(self.record,self.baseline))
        self.assertIn("publication evidence missing",validate(self.record,self.baseline))

    def test_unpublished_candidates_do_not_get_fake_issues(self):
        self.record["sessions"][-1]["issue"]=999
        self.assertIn("invented candidate claim",validate(self.record,self.baseline))

    def test_followup_denial_separate_from_published_baseline(self):
        self.assertEqual(next(s for s in self.record["sessions"] if s["issue"]==246)["publication"]["status"],"published")
        self.record["followups"][0]["status"]="completed"
        self.assertIn("lost separate followup",validate(self.record,self.baseline))

    def test_denied_retry_rejected(self):
        self.record["sessions"][-1]["retry_denied_action"]=True
        self.assertIn("identity or prohibited retry",validate(self.record,self.baseline))

    def test_acceptance_and_execution_unknowns_preserved(self):
        for field,value,error in (
            ("acceptance_status","accepted","unverified acceptance promotion"),
            ("independently_executed_in_this_addendum",True,"unverified execution promotion")):
            with self.subTest(field=field):
                r=copy.deepcopy(self.record)
                r["sessions"][0]["execution_acceptance"][field]=value
                self.assertIn(error,validate(r,self.baseline))

    def test_retained_acceptance_not_weakened(self):
        self.record["retained_actions"][0]["acceptance_test"]="Exists"
        self.assertIn("changed obligation or acceptance",validate(self.record,self.baseline))

    def test_publication_count_not_session_count(self):
        self.record["counts"]["identified_sessions"]=7
        self.assertIn("accounting counts",validate(self.record,self.baseline))

    def test_no_private_identifiers_or_paths(self):
        text=(ROOT/NAME).read_text()
        import re
        self.assertFalse(re.search(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",text))
        for private_prefix in ("/workspace/","/home/","C:\\Users\\"):
            self.assertNotIn(private_prefix,text)


if __name__ == "__main__":
    unittest.main()
