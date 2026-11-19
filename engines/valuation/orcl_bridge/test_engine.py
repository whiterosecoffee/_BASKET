import copy
import unittest
from engines.valuation.orcl_bridge.engine import evaluate, scenario, company, timestamp
from engines.valuation.orcl_bridge.example import fixture

NOW='2026-10-26T14:00:00Z'


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.bundle=fixture(NOW)

    def run_model(self):
        return evaluate(self.bundle,NOW)

    def test_hand_calculated_earnings_cashflows_ev_and_reverse(self):
        report=self.run_model(); s=report['target']['stats']
        self.assertAlmostEqual(s['eps'],2.24)
        self.assertEqual(s['enterprise_value'],5_160_000_000)
        self.assertEqual(s['fcff'],170_000_000)
        self.assertEqual(s['equity_fcf_before_net_borrowing'],154_000_000)
        self.assertAlmostEqual(report['comparisons']['pe']['implied_price_usd'],60)
        self.assertAlmostEqual(report['reverse']['required_eps_at_peer_pe'],1.8666666666666667)
        self.assertFalse(report['eligible']) # Synthetic never operational

    def test_no_silent_peer_reweighting(self):
        del self.bundle['companies']['IBM']
        result=self.run_model()['comparisons']['pe']
        self.assertEqual(result['peer_weight_coverage'],0.5)
        self.assertEqual(result['status'],'partial_non_actionable')
        self.assertIsNone(result['implied_price_usd'])

    def test_negative_cashflow_kept_visible_without_fake_multiple(self):
        self.bundle['companies']['ORCL']['forecast']['data']['capex']=500_000_000
        report=self.run_model()
        self.assertLess(report['target']['stats']['fcff'],0)
        self.assertIsNone(report['comparisons']['ev_fcff']['implied_price_usd'])
        self.assertIsNotNone(report['comparisons']['pe']['implied_price_usd'])

    def test_fiscal_and_normalized_basis_cannot_mix(self):
        f=self.bundle['companies']['IBM']['forecast']['data']
        f.update(earnings_basis='normalized',reconciliation='Synthetic SBC reconciliation')
        report=self.run_model()
        self.assertEqual(report['comparisons']['pe']['excluded'][0]['reason'],'incomparable_horizon_or_basis')
        self.assertIsNone(report['comparisons']['pe']['implied_price_usd'])

    def test_future_stale_unverified_backfilled_target_blocked(self):
        original=copy.deepcopy(self.bundle)
        for key,value in [('available_at','2026-10-27T00:00:00Z'),('ingested_at','2026-10-27T00:00:00Z'),
                          ('expires_at',NOW),('verification','unverified'),('effective_at','2026-10-25T14:00:00Z')]:
            self.bundle=copy.deepcopy(original)
            self.bundle['companies']['ORCL']['quote'][key]=value
            with self.subTest(key=key):
                report=self.run_model(); self.assertIsNone(report['target']); self.assertFalse(report['eligible'])

    def test_annual_guidance_is_not_automatically_ntm(self):
        self.bundle['companies']['ORCL']['forecast']['data']['horizon_start']='2026-06-01T00:00:00Z'
        self.bundle['companies']['ORCL']['forecast']['data']['horizon_end']='2027-06-01T00:00:00Z'
        self.assertIsNone(self.run_model()['target'])

    def test_financing_and_dilution_reconcile(self):
        case=self.bundle['scenarios']['base']
        case.update(new_debt=100_000_000,new_debt_rate=.06,equity_raise=50_000_000,
                    additional_shares=2_000_000,retained_funding_cash=150_000_000)
        case['repricing']=[{'tranche_id':'floating-1','kind':'floating','principal':50_000_000,'old_rate':.06,'new_rate':.05,'year_fraction':1}]
        out=self.run_model()['scenarios']['base']
        self.assertAlmostEqual(out['interest_change_usd'],5_500_000)
        self.assertEqual(out['diluted_shares'],103_000_000)
        self.assertEqual(out['net_obligations'],110_000_000)
        self.assertAlmostEqual(out['eps'],219_600_000/103_000_000)
        self.assertAlmostEqual(out['eps_change'],out['earnings_eps_change']+out['dilution_eps_change'])

    def test_fixed_debt_does_not_reprice(self):
        self.bundle['scenarios']['base']['repricing']=[{'tranche_id':'fixed-1','kind':'fixed','principal':50_000_000,'old_rate':.06,'new_rate':.05,'year_fraction':1}]
        self.assertEqual(self.run_model()['scenarios']['base']['status'],'blocked')

    def test_losses_have_no_assumed_tax_refund_or_pe(self):
        self.bundle['companies']['ORCL']['forecast']['data']['ebit']=-10_000_000
        out=self.run_model()
        self.assertEqual(out['target']['stats']['net_income'],-30_000_000)
        self.assertIsNone(out['target']['stats']['pe'])

    def test_duplicate_tranches_and_overstated_cash_rejected(self):
        case=self.bundle['scenarios']['base']
        tranche={'tranche_id':'same','kind':'floating','principal':20_000_000,'old_rate':.06,'new_rate':.05,'year_fraction':1}
        case['repricing']=[tranche,tranche]
        self.assertEqual(self.run_model()['scenarios']['base']['status'],'blocked')
        case['repricing']=[];case['retained_funding_cash']=1
        self.assertEqual(self.run_model()['scenarios']['base']['status'],'blocked')

    def test_misaligned_quotes_block_peer_price(self):
        self.bundle['companies']['IBM']['quote']['effective_at']='2026-10-26T13:57:00Z'
        self.assertIsNone(self.run_model()['comparisons']['pe']['implied_price_usd'])

    def test_inputs_not_mutated_and_output_reproducible(self):
        before=copy.deepcopy(self.bundle)
        self.assertEqual(self.run_model(),self.run_model())
        self.assertEqual(self.bundle,before)

    def test_rate_grid_is_mechanical_and_excludes_fixed_debt(self):
        base=self.bundle['scenarios']['base']
        base['repricing']=[{'tranche_id':'float','kind':'floating','principal':50_000_000,'old_rate':.06,'new_rate':.06,'year_fraction':1},
                           {'tranche_id':'fixed','kind':'fixed','principal':100_000_000,'old_rate':.05,'new_rate':.05,'year_fraction':1}]
        out=self.run_model()['rate_sensitivity']
        self.assertEqual(out['annualized_exposure_usd'],50_000_000)
        self.assertAlmostEqual(out['rows'][-1]['incremental_interest_usd'],500_000)
        self.assertAlmostEqual(out['rows'][-1]['eps_delta_vs_base'],-.004)
        self.assertAlmostEqual(out['rows'][0]['eps_delta_vs_base'],.004)

    def test_bad_weights_and_nonfinite_rejected(self):
        self.bundle['peer_weights']['IBM']=.3
        with self.assertRaises(ValueError):self.run_model()
        self.bundle=fixture();self.bundle['companies']['ORCL']['quote']['data']['price']=float('nan')
        with self.assertRaises(ValueError):self.run_model()


if __name__=='__main__':unittest.main()
