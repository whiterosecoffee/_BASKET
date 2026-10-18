"""Independent B01 acceptance checks; missing research is a failure."""
import importlib.util
import math
import os
from pathlib import Path
import unittest


class OpenAIResearchGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ.get('BASKET_OPENAI_SOURCE', Path(__file__).resolve().parents[2]))
        spec = importlib.util.spec_from_file_location('b01_openai', root / 'research/OPENAI/ipo2027.py')
        cls.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.engine)

    def test_policy_normalization(self):
        e = self.engine
        p = e.read('ipo2027-policy.json')
        meta = e.verify(p, e.read('ipo2027-news.json'))
        self.assertEqual((meta['stages'], meta['regimes'], meta['factors']), (4, 4, 8))
        for stage in p['stages']:
            for regime in p['regime_adjustments']:
                w = e.weights(p, stage, regime)
                self.assertAlmostEqual(sum(w.values()), 100)
                self.assertTrue(all(math.isfinite(v) and v > 0 for v in w.values()))

    def test_missing_financials_and_conditional_regime(self):
        result = self.engine.run('2026-10-17', regime='credit_stress')
        self.assertEqual(result['evidence_quality']['status'], 'unrated')
        self.assertIsNone(result['conditional_EV_scenario'])
        self.assertIsNone(result['IPO_probability'])
        self.assertIsNone(result['net_SFTBY_NAV'])
        self.assertTrue(result['valuation_readiness'].startswith('blocked_'))
        self.assertEqual(result['regime_state'], 'conditional_user_selected_regime')

    def test_scenario_and_every_invalid_input(self):
        values = [100, 10, 10, 15, 5]
        result = self.engine.scenario(*values)
        self.assertEqual(result['implied_EV_usd_b'], 1000)
        self.assertEqual(result['implied_equity_usd_b'], 990)
        self.assertIn('not_fair_value', result['classification'])
        for index in range(5):
            for invalid in (None, -1, float('nan'), float('inf')):
                args = values.copy()
                args[index] = invalid
                with self.subTest(index=index, invalid=invalid), self.assertRaises(ValueError):
                    self.engine.scenario(*args)

    def test_stage_advancement_requires_proof(self):
        for stage in ('prospectus_public', 'bookbuilding', 'post_listing'):
            with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, 'stage blocked'):
                self.engine.run('2026-10-17', stage=stage)
