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
