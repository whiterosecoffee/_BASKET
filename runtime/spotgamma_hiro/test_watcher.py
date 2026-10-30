import json
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path
from watcher import freshness,scan
BASE={"ticker":"AMD","hiro_usd":-69000000,"range_30d_low_usd":-734000000,"range_30d_high_usd":452000000}
class WatcherTests(unittest.TestCase):
    def test_unknown_time_fails_closed(self):
        self.assertEqual(freshness(BASE),"unknown_capture_time")
    def test_expiry_and_future(self):
        now=datetime(2026,10,30,13,0,tzinfo=timezone.utc)
        self.assertEqual(freshness({"observed_at":(now-timedelta(seconds=100)).isoformat()},now=now),"within_ttd")
        self.assertEqual(freshness({"observed_at":(now-timedelta(seconds=121)).isoformat()},now=now),"expired")
        self.assertEqual(freshness({"observed_at":(now+timedelta(seconds=11)).isoformat()},now=now),"future_capture_time")
    def test_restart_bad_input(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);box=root/"inbox";box.mkdir();out=root/"hiro.jsonl"
            (box/"a.jsonl").write_text(json.dumps(BASE)+"\n")
            (box/"bad.jsonl").write_text("not-json\n")
            first=scan(box,out)
            self.assertEqual(first["appended"],1)
            self.assertIn("bad.jsonl",first["errors"])
            self.assertEqual(first["symbols"]["AMD"]["freshness"],"unknown_capture_time")
            self.assertEqual(scan(box,out)["appended"],0)
            self.assertEqual(len(out.read_text().splitlines()),1)
if __name__=="__main__":unittest.main()
