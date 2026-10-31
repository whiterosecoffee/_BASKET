"""B00 negative and deterministic tests; execute with unittest discovery."""
import datetime as dt
import tempfile
import unittest
from pathlib import Path
from orchestration.agentic.manager import (
    GuardError, evaluate, event_check, append_event, load_events, path_matches,
    collisions, validate_queue, run_safe_checks,
)
from orchestration.agentic.github_adapter import collect, pages

NOW=dt.datetime(2026,10,17,21,0,tzinfo=dt.timezone.utc)
SHA="a"*40
OTHER="b"*40

def task(id, mode, issue=None, pr=None, scope=None, deps=None):
    return {"id":id,"spark_id":"B00","mode":mode,"issue_number":issue,
            "pr_number":pr,"priority":"P0","impact":4,"effort":2,
            "write_scope":scope if scope is not None else ["services/**"],
            "depends_on":deps or [],"acceptance":["source", "test"]}

def queue():
    return {"queue_version":"unit", "active_worker_limit":2, "tasks":[
        task("T-001","orchestrator_review",1,10,[]),
        task("T-002","resume_existing_worker",2,11,["research/events/**"]),
        task("T-003","launch_new_worker",deps=[{"task_id":"T-001","gate":"merged"}])]}

def ev():
    return {"schema":"basket.github_evidence@1","capture_mode":"live_connector",
            "repository":"whiterosecoffee/_BASKET","observed_at":NOW.isoformat(),
            "main_commit":OTHER,
            "issues":[{"number":1,"state":"open"},{"number":2,"state":"open"}],
            "pull_requests":[
                {"number":10,"head_sha":SHA,"changed_paths":["orchestration/config.json"],
                 "state":"closed","merged":True},
                {"number":11,"head_sha":"c"*40,"changed_paths":["research/events/a.json"],
                 "state":"open","merged":False}],
            "workflow_runs":[{"head_sha":SHA,"name":"Validate BASKET data","conclusion":"success"}]}

def event(id, type, task_id="T-001", seconds=0, **kwargs):
    return {"schema":"basket.agentic_event@1","event_id":id,"type":type,
            "task_id":task_id,"at":(NOW+dt.timedelta(seconds=seconds)).isoformat(),**kwargs}

class ManagerTest(unittest.TestCase):
    def test_initial_unreconciled_worker_capacity(self):
        r=evaluate(queue(),ev(),[],NOW)
        self.assertIsNone(r["active_workers"])
        self.assertEqual(next(t for t in r["decisions"] if t["task_id"]=="T-003")["next_action"],
                         "reconcile_worker_capacity")

    def test_historical_fixture_rejected(self):
        x=ev();x["capture_mode"]="fixture"
        with self.assertRaises(GuardError): evaluate(queue(),x,[],NOW)

    def test_future_source_rejected(self):
        x=ev();x["observed_at"]=(NOW+dt.timedelta(hours=1)).isoformat()
        with self.assertRaises(GuardError): evaluate(queue(),x,[],NOW)

    def test_old_source_rejected(self):
        x=ev();x["observed_at"]=(NOW-dt.timedelta(hours=1)).isoformat()
        with self.assertRaises(GuardError): evaluate(queue(),x,[],NOW)

    def test_missing_changed_files_rejected(self):
        x=ev();x["pull_requests"][1].pop("changed_paths")
        with self.assertRaises(GuardError): evaluate(queue(),x,[],NOW)

    def test_duplicate_task_id_rejected(self):
        q=queue();q["tasks"].append(q["tasks"][0])
        with self.assertRaises(GuardError):validate_queue(q)

    def test_dependency_cycle_rejected(self):
        q=queue();q["tasks"][0]["depends_on"]=[{"task_id":"T-003","gate":"merged"}]
        with self.assertRaises(GuardError):validate_queue(q)

    def test_pr_merge_not_equal_to_completion(self):
        r=evaluate(queue(),ev(),[],NOW)
        t=next(t for t in r["decisions"] if t["task_id"]=="T-001")
        self.assertEqual(t["state"],"merged_unverified")
        self.assertFalse(t["acceptance"]["integrated"])

    def test_independent_acceptance_requires_same_sha(self):
        events=[event("a1","acceptance_verified",criterion_id="A1",
                      source_url="https://github.com/evidence",independent_reviewer="B01",
                      head_sha="d"*40)]
        r=evaluate(queue(),ev(),events,NOW)
        t=next(t for t in r["decisions"] if t["task_id"]=="T-001")
        self.assertEqual(t["acceptance"]["verified"],0)

    def test_same_sha_acceptance_recomputed(self):
        events=[event("a1","acceptance_verified",criterion_id="A1",source_url="https://github.com/a",
                      independent_reviewer="B01",head_sha=SHA),
                event("a2","acceptance_verified",criterion_id="A2",source_url="https://github.com/b",
                      independent_reviewer="B01",head_sha=SHA)]
        r=evaluate(queue(),ev(),events,NOW)
        t=next(t for t in r["decisions"] if t["task_id"]=="T-001")
        self.assertEqual(t["acceptance"]["verified"],2)
        self.assertTrue(t["acceptance"]["component_verified"])
        self.assertFalse(t["acceptance"]["integrated"])

    def test_duplicate_event_is_invalid(self):
        event1=event("x","attempt_started",attempt_id="ATT-x",step_id="fetch")
        with self.assertRaises(GuardError):event_check([event1,event1],NOW)

    def test_deliverable_append_and_supersession(self):
        a=event("d1","deliverable_registered",deliverable_id="D-unit",
                artifact_path="orchestration/check.json",
                source_url="https://github.com/evidence",head_sha=SHA)
        b=event("d2","deliverable_superseded",deliverable_id="D-unit")
        r=evaluate(queue(),ev(),[a,b],NOW)
        t=next(t for t in r["decisions"] if t["task_id"]=="T-001")
        self.assertTrue(t["deliverables"]["D-unit"]["superseded"])

    def test_journal_append_is_durable_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"events.jsonl"
            e=event("e1","attempt_started",attempt_id="ATT-e1",step_id="fetch")
            append_event(path,e,NOW)
            self.assertEqual(load_events(path),[e])
            with self.assertRaises(GuardError):append_event(path,e,NOW)

    def test_path_wildcard_respects_directories(self):
        self.assertTrue(path_matches("research/*/README.md","research/CRWV/README.md"))
        self.assertFalse(path_matches("research/*/README.md","research/CRWV/a/README.md"))

    def test_active_pr_write_collision(self):
        x=ev()
        x["pull_requests"].append({"number":52,"head_sha":"d"*40,
            "changed_paths":["services/api.py"],"state":"open","merged":False})
        r=evaluate(queue(),x,[],NOW)
        t=next(t for t in r["decisions"] if t["task_id"]=="T-003")
        self.assertEqual(t["state"],"blocked")
        self.assertEqual(t["scope_collisions"][0]["pr"],52)

    def test_active_worker_lease_blocks_double_resume(self):
        lease=event("l","lease_granted",task_id="T-002",issue=2,branch="work/2-unique",
                   expires_at=(NOW+dt.timedelta(hours=1)).isoformat())
        cap=event("c","capacity_reconciled",task_id="__controller__",
                  verified_active_task_ids=["T-002"],verified_by="auditor",
                  source_url="https://github.com/audit")
        r=evaluate(queue(),ev(),[lease,cap],NOW)
        t=next(t for t in r["decisions"] if t["task_id"]=="T-002")
        self.assertEqual(t["next_action"],"verify_heartbeat")
        self.assertEqual(r["active_workers"],1)

    def test_expired_worker_lease_is_not_released_automatically(self):
        lease=event("l","lease_granted",task_id="T-002",issue=2,branch="work/2-unique",
                   expires_at=(NOW+dt.timedelta(seconds=30)).isoformat())
        cap=event("c","capacity_reconciled",task_id="__controller__",
                  verified_active_task_ids=["T-002"],verified_by="auditor",
                  source_url="https://github.com/audit")
        r=evaluate(queue(),ev(),[lease,cap],NOW+dt.timedelta(seconds=35))
        self.assertIsNone(r["active_workers"])
        self.assertEqual(r["expired_unverified_leases"],["T-002"])

    def test_safe_checks_do_not_execute_task_shell(self):
        with self.assertRaises(GuardError):run_safe_checks("/",["rm -rf /"])

    def test_missing_validator_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            r=run_safe_checks(d,["planner"])
            self.assertEqual(r[0]["status"],"unavailable")

    def test_failed_attempt_requeues_original_step(self):
        events=[event("a1","attempt_started",task_id="T-002",attempt_id="ATT-one",step_id="validate"),
                event("a2","attempt_failed",task_id="T-002",attempt_id="ATT-one",step_id="validate",
                      result_url="https://github.com/failed-ci")]
        result=evaluate(queue(),ev(),events,NOW)
        task=next(t for t in result["decisions"] if t["task_id"]=="T-002")
        self.assertEqual(task["next_action"],"retry_original_step")
        self.assertEqual(task["attempt_history"]["failures"],1)
        unrelated=next(t for t in result["decisions"] if t["task_id"]=="T-001")
        self.assertEqual(unrelated["attempt_history"]["attempts"],0)

    def test_retry_must_preserve_failed_step(self):
        events=[event("a1","attempt_started",attempt_id="ATT-one",step_id="validate"),
                event("a2","attempt_failed",attempt_id="ATT-one",step_id="validate",
                      result_url="https://github.com/failed-ci"),
                event("a3","attempt_started",attempt_id="ATT-two",step_id="other",
                      retry_of="ATT-one")]
        with self.assertRaises(GuardError):
            evaluate(queue(),ev(),events,NOW)

    def test_retry_with_proof_clears_failure_blocker_but_retains_history(self):
        events=[event("a1","attempt_started",task_id="T-002",
                      attempt_id="ATT-one",step_id="validate"),
                event("a2","attempt_failed",task_id="T-002",
                      attempt_id="ATT-one",step_id="validate",
                      result_url="https://github.com/failed-ci"),
                event("a3","attempt_started",task_id="T-002",
                      attempt_id="ATT-two",step_id="validate",retry_of="ATT-one"),
                event("a4","attempt_passed",task_id="T-002",
                      attempt_id="ATT-two",step_id="validate",
                      result_url="https://github.com/passing-ci")]
        result=evaluate(queue(),ev(),events,NOW)
        worker=next(t for t in result["decisions"] if t["task_id"]=="T-002")
        self.assertEqual(worker["attempt_history"]["failures"],1)
        self.assertEqual(worker["attempt_history"]["last_result"],"attempt_passed")
        self.assertNotEqual(worker["next_action"],"retry_original_step")

    def test_full_open_pr_inventory_used(self):
        def fetch(path):
            if path.endswith("/branches/main"):
                return {"commit":{"sha":OTHER}}
            if "/pulls?state=open" in path:
                return [{"number":52,"html_url":"https://test/52","state":"open","draft":True,
                         "merged_at":None,"head":{"sha":"d"*40,"ref":"work/52-x"},
                         "base":{"ref":"main"}}]
            if "/pulls/52/files" in path:
                return [{"filename":"services/api.py"}]
            if "/pulls/10/files" in path or "/pulls/11/files" in path:
                return []
            if "/pulls/10" in path or "/pulls/11" in path:
                n=10 if "/pulls/10" in path else 11
                return {"number":n,"html_url":"https://test/pr","state":"closed","draft":False,
                        "merged_at":"2026-10-15" if n==10 else None,
                        "head":{"sha":SHA,"ref":"work/1-x"},"base":{"ref":"main"}}
            if "/issues?state=open" in path:
                return [{"number":1,"state":"open","html_url":"https://test/issue/1"},
                        {"number":2,"state":"open","html_url":"https://test/issue/2"}]
            if "/actions/runs" in path:
                return {"workflow_runs":[]}
            raise AssertionError(path)
        snapshot=collect(queue(),fetch,NOW)
        self.assertIn(52,[p["number"] for p in snapshot["pull_requests"]])
        self.assertTrue(collisions(["services/**"],snapshot))

if __name__=="__main__":
    unittest.main()
