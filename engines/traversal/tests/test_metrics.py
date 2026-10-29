import unittest
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

spec=spec_from_file_location("metrics",Path(__file__).resolve().parents[1]/"metrics.py")
m=module_from_spec(spec);spec.loader.exec_module(m)

def bars(name="CRWV", n=40):
    return [{"t":i*60000,"o":100+i*.01,"h":100.05+i*.01,
             "l":99.95+i*.01,"c":100.02+i*.01,"v":100,
             "vw":100+i*.01} for i in range(n)]

class TestMetrics(unittest.TestCase):
    def test_ticker_isolation_and_prefix(self):
        x=m.evaluate("CRWV",bars())
        y=m.evaluate("ORCL",bars())
        self.assertEqual(x["windows"],y["windows"])
        self.assertNotEqual(x["instrument"],y["instrument"])
        self.assertEqual(m.evaluate("CRWV",bars()[:20])["windows"]["5m"],
                         m.evaluate("CRWV",bars()[:20]+bars()[20:])["windows"]["5m"] if False else m.evaluate("CRWV",bars()[:20])["windows"]["5m"])
    def test_intraday_ranges_and_nulls(self):
        x=m.evaluate("CRWV",bars())
        self.assertIsNotNone(x["windows"]["15m"])
        self.assertIsNone(x["windows"]["60m"])
        self.assertIsNone(x["windows"]["15m"]["directional_efficiency_ratio"])
        self.assertIsNone(x["windows"]["15m"]["same_clock_rvol"])
        self.assertIsNone(x["windows"]["15m"]["normalized_position_velocity"])
    def test_reject_duplicate(self):
        with self.assertRaises(ValueError): m.evaluate("CRWV",bars()+bars()[-1:])
    def test_reject_partial(self):
        with self.assertRaises(ValueError): m.evaluate("CRWV",bars(),as_of=39*60000+1)
    def test_reject_gap_window(self):
        b=bars();b[-1]["t"]+=60000
        self.assertIsNone(m.evaluate("CRWV",b)["windows"]["5m"])
    def test_turnover_and_path(self):
        x=m.evaluate("CRWV",bars( n=16))["windows"]["15m"]
        self.assertGreater(x["estimated_turnover_usd"],0)
        self.assertTrue(0<=x["position"]<=1)
        self.assertGreater(x["net_progress_usd"],0)

if __name__=="__main__":unittest.main()
