import unittest
from compare_funds import compare_funds
from test_compare_funds import fixture
from peer_report import render_peer_markdown

class TestReport(unittest.TestCase):
    def test_render_synthetic(self):
        x=render_peer_markdown(compare_funds(fixture()))
        self.assertIn('SYNTHETIC TEST DATA',x)
        self.assertIn('2027',x)
        self.assertIn('2028',x)
        self.assertIn('No risk-adjusted winner established',x)
    def test_missing_estimate_not_meaningful(self):
        d=fixture();del d['funds'][0]['holdings'][0]['estimates']['2028']
        self.assertIn('N/M',render_peer_markdown(compare_funds(d)))
    def test_wrong_result_contract(self):
        with self.assertRaises(ValueError):render_peer_markdown({'schema':'other'})

if __name__=='__main__':unittest.main()
