import datetime as dt, importlib.util, json, pathlib, tempfile, unittest
PATH=pathlib.Path(__file__).resolve().parents[1]/"runtime"/"ttd.py"
spec=importlib.util.spec_from_file_location("ttd",PATH);ttd=importlib.util.module_from_spec(spec);spec.loader.exec_module(ttd)
class TTDTests(unittest.TestCase):
 def test_expiration(self):
  now=dt.datetime(2026,10,16,15,0,tzinfo=dt.timezone.utc)
  obs={"observed_at":"2026-10-16T14:59:00Z","ttd_seconds":90,"state":"valid"}
  self.assertEqual(ttd.status(obs,now),"alive")
  self.assertEqual(ttd.status(obs,now+dt.timedelta(seconds=31)),"dead")
 def test_dependency_expires_first(self):
  obs={"observed_at":"2026-10-16T14:59:00Z","ttd_seconds":300,"dependency_expires_at":["2026-10-16T14:59:30Z"],"state":"valid"}
  self.assertEqual(ttd.expiry(obs),ttd.parse("2026-10-16T14:59:30Z"))
 def test_missing(self):self.assertEqual(ttd.status(None),"unavailable")
 def test_future_invalid(self):
  obs={"observed_at":"2999-01-01T00:00:00Z","ttd_seconds":90}
  self.assertEqual(ttd.status(obs),"invalidated")
if __name__=="__main__":unittest.main()

# B02 journal regression: test discovery uses this module.
journal_path = pathlib.Path(__file__).resolve().parents[1] / "runtime" / "observations.py"
journal_spec = importlib.util.spec_from_file_location("basket_observations", journal_path)
observations = importlib.util.module_from_spec(journal_spec)
journal_spec.loader.exec_module(observations)

class JournalReplayTests(unittest.TestCase):
 def fixture(self, value, available, supersedes=None):
  row={"entity_id":"SFTBY","kind":"daily_close","source":"fixture",
       "source_record_id":"2026-10-15","observed_at":"2026-10-15T20:00:00Z",
       "available_at":available,"ingested_at":available,"currency":"USD",
       "value":value,"ttd_seconds":3600}
  if supersedes: row["supersedes"]=supersedes
  return row
 def test_revision_snapshot_and_replay(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/"feed.jsonl"
   first=observations.append(path,self.fixture(1,"2026-10-15T21:00:00Z"))
   checkpoint=observations.snapshot(observations.read_journal(path),"2026-10-15T22:00:00Z")
   second=observations.append(path,self.fixture(2,"2026-10-16T12:00:00Z",first["record_id"]))
   rows=observations.read_journal(path)
   self.assertEqual(len(rows),2)
   self.assertEqual(observations.replay(rows,"2026-10-15T22:00:00Z")[0]["record_id"],first["record_id"])
   self.assertEqual(observations.replay(rows,"2026-10-16T13:00:00Z")[0]["record_id"],second["record_id"])
   self.assertEqual(checkpoint,observations.snapshot(rows,"2026-10-15T22:00:00Z"))
   self.assertNotEqual(checkpoint["snapshot_sha256"],observations.snapshot(rows,"2026-10-16T13:00:00Z")["snapshot_sha256"])
 def test_lock_conflict_and_dependency_expiry(self):
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/"feed.jsonl"
   pathlib.Path(str(path)+".lock").touch()
   with self.assertRaises(FileExistsError):
    observations.append(path,self.fixture(1,"2026-10-15T21:00:00Z"))
  row=self.fixture(1,"2026-10-15T21:00:00Z")
  self.assertEqual(observations.state(row,"2026-10-15T21:01:00Z",[{"expires_at":"2026-10-15T20:40:00Z"}]),"stale")
  self.assertEqual(observations.adapter_access(entitled=True,worker_running=False),"unavailable")
