import json
import tempfile
import unittest
from pathlib import Path
from hiro import normalize,ingest

BASE={"ticker":"AMD","hiro_usd":-69000000,"range_30d_low_usd":-734000000,
"range_30d_high_usd":452000000,"hedge_wall":560,"key_gamma_strike":550,
"key_delta_strike":5,"call_wall":600,"put_wall":500}
class HTest(unittest.TestCase):
    def test_missing_timestamp_never_live(self):
        row=normalize(BASE)
        self.assertIsNone(row["observed_at"])
        self.assertFalse(row["actionable"])
    def test_repeat_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"input.jsonl"; q=Path(tmp)/"out.jsonl"
            p.write_text(json.dumps(BASE)+"\n")
            self.assertEqual(ingest(p,q),1)
            self.assertEqual(ingest(p,q),0)
            self.assertEqual(len(q.read_text().splitlines()),1)
    def test_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            normalize({**BASE,"hiro_usd":1000000000})
    def test_naive_datetime_rejected(self):
        with self.assertRaises(ValueError):
            normalize({**BASE,"observed_at":"2026-10-30T09:00:00"})
if __name__=="__main__": unittest.main()
