"""Negative tests for B19 whole-basket structural role mappings."""
import copy
import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("whole_map",Path(__file__).with_name("check_whole_map.py"))
check=importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

def sample():
    row={"symbol":"NVDA","instrument_type":"equity_or_depositary_receipt","tracked_status":"watchlist","pool_ids":["semiconductors"],"cross_cutting_roles":[],"source_supported_revenue_usd":None,"captured_share":None,"production_capacity":None,"contract_edges":[],"evidence_refs":[],"canonical_entity_id":None,"venue_status":"unverified"}
    mapping={"schema":"basket.b19-whole-basket-role-map@research1","authoritative_scope":{"count":1,"head_sha":"a"*40},"pool_reference":{"pool_count":1,"head_sha":"b"*40},"rows":[row],"coverage":{"all_tracked_instruments":1,"classified_to_at_least_one_pool":1,"nonissuer_instruments":0,"provisional_issuer_roles":1,"unclassified_operating_issuers":0,"unclassified_or_nonissuer":0,"operating_equity_with_pool_or_crosscutting_role":1,"pool_participant_counts":{"semiconductors":1}}}
    manifest={"source_head_sha":"a"*40,"records":[{"symbol":"NVDA","instrument_type":"equity_or_depositary_receipt","tracking_status":"watchlist"}]}
    pools={"source_head_sha":"b"*40,"pools":[{"id":"semiconductors"}]}
    return mapping,manifest,pools,"a"*40,"b"*40

class WholeMapChecks(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(check.verify(*sample())["all"],1)
    def test_missing_symbol(self):
        a,b,c,ma,po=sample(); b["records"][0]["symbol"]="AMD"
        with self.assertRaises(check.MapError):check.verify(a,b,c,ma,po)
    def test_duplicate_symbol(self):
        a,b,c=sample(); a["rows"].append(copy.deepcopy(a["rows"][0]))
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_unknown_pool(self):
        a,b,c=sample(); a["rows"][0]["pool_ids"]=["invented"]
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_nonissuer_as_operating_company(self):
        a,b,c=sample(); a["rows"][0]["instrument_type"]=b["records"][0]["instrument_type"]="fund_or_etp"
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_proposed_contract_not_verified(self):
        a,b,c=sample(); a["rows"][0]["contract_edges"]=[{"supplier":"TSM"}]
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_financial_claim(self):
        a,b,c=sample(); a["rows"][0]["source_supported_revenue_usd"]=123
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_stale_counts(self):
        a,b,c=sample(); a["coverage"]["all_tracked_instruments"]=2
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_source_head_mismatch(self):
        a,b,c=sample(); ma="c"*40
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_duplicate_pool(self):
        a,b,c=sample(); c["pools"].append({"id":"semiconductors"})
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_identity_promotion(self):
        a,b,c=sample(); a["rows"][0]["canonical_entity_id"]="NVDA"
        with self.assertRaises(check.MapError):check.verify(a,b,c)
    def test_unclassified_issuer(self):
        a,b,c=sample(); a["rows"][0]["pool_ids"]=[]
        with self.assertRaises(check.MapError):check.verify(a,b,c)

if __name__=="__main__":
    unittest.main()
