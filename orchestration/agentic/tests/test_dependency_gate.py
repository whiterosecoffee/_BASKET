"""PIT, contract, idempotency and invalidation negative tests."""
import copy
import hashlib
import unittest
from orchestration.agentic.dependency_gate import DependencyError, snapshot, recompute_decision

H = hashlib.sha256(b"source-v1").hexdigest()
CONFIG = hashlib.sha256(b"config-v1").hexdigest()
A = "2026-10-17T12:00:00Z"
B = "2026-10-17T13:00:00Z"
KEY = "B03/issuer.events@1/SFTBY-earnings-2026q2"

def row():
    return {"producer": "B03", "contract": "issuer.events@1", "record_id": "SFTBY-earnings-2026q2",
            "revision_id": "rev1", "source_sha256": H, "effective_at": A,
            "available_at": A, "ingested_at": A, "valid_until": "2026-11-17T00:00:00Z"}

def decide(prev, cur, required=None):
    return recompute_decision(previous=prev, current=cur, model_version="mrie@0.1.0",
                              config_sha256=CONFIG, required_ids=[KEY] if required is None else required)

class GateTests(unittest.TestCase):
    def test_source_added_requires_recompute(self):
        d = decide(None,snapshot([row()],as_of=B)); self.assertEqual(d["state"],"recompute_required")
    def test_same_source_does_not_rerun_on_new_poll(self):
        s=snapshot([row()],as_of=B); d=decide(s,s); self.assertEqual(d["state"],"unchanged")
    def test_order_independent(self):
        a=row();b=dict(a,producer="B02",contract="prices@1",record_id="NVDA")
        self.assertEqual(snapshot([a,b],as_of=B)["fingerprint"],snapshot([b,a],as_of=B)["fingerprint"])
    def test_revision_triggers_downstream_invalidation(self):
        old=snapshot([row()],as_of=B);r=row();r["revision_id"]="rev2"
        new=snapshot([r],as_of=B);d=decide(old,new)
        self.assertEqual(d["state"],"recompute_required");self.assertEqual(d["changed_ids"],[KEY])
    def test_source_digest_change_triggers(self):
        old=snapshot([row()],as_of=B);r=row();r["source_sha256"]=CONFIG
        self.assertEqual(decide(old,snapshot([r],as_of=B))["state"],"recompute_required")
    def test_missing_required_blocks(self):
        self.assertEqual(decide(None,snapshot([],as_of=B))["state"],"blocked")
    def test_expired_required_blocks(self):
        r=row();r["valid_until"]="2026-10-17T12:30:00Z"
        self.assertEqual(decide(None,snapshot([r],as_of=B))["state"],"blocked")
    def test_unrelated_expired_does_not_block(self):
        r=row();r["valid_until"]="2026-10-17T12:30:00Z"
        d=decide(None,snapshot([r],as_of=B),required=[])
        self.assertEqual(d["state"],"recompute_required")
    def test_future_available_blocked_even_if_effective_old(self):
        r=row();r["available_at"]="2026-10-18T00:00:00Z";r["ingested_at"]="2026-10-18T01:00:00Z"
        with self.assertRaises(DependencyError):snapshot([r],as_of=B)
    def test_ingested_before_available_fails(self):
        r=row();r["ingested_at"]="2026-10-17T11:00:00Z"
        with self.assertRaises(DependencyError):snapshot([r],as_of=B)
    def test_duplicate_records_fails(self):
        with self.assertRaises(DependencyError):snapshot([row(),row()],as_of=B)
    def test_no_naked_timestamp(self):
        r=row();r["available_at"]="2026-10-17"
        with self.assertRaises(DependencyError):snapshot([r],as_of=B)
    def test_tamper_fails(self):
        x=snapshot([row()],as_of=B);x["fingerprint"]="f"*64
        with self.assertRaises(DependencyError):decide(None,x)
    def test_config_change_changes_idempotency_key(self):
        s=snapshot([row()],as_of=B)
        a=decide(None,s)
        b=recompute_decision(previous=None,current=s,model_version="mrie@0.1.1",config_sha256=CONFIG,required_ids=[KEY])
        self.assertNotEqual(a["idempotency_key"],b["idempotency_key"])
    def test_clock_regress_fails(self):
        with self.assertRaises(DependencyError):decide(snapshot([row()],as_of=B),snapshot([row()],as_of=A))
    def test_replay_is_deterministic(self):
        x=snapshot([row()],as_of=B);self.assertEqual(decide(None,x),decide(None,x))

if __name__=="__main__":unittest.main()