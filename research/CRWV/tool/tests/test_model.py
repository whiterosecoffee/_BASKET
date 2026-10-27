import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from model import evaluate, analyze, lifecycle, reverse_valuation, digest
from history import append_record, bridge
from market import turnover, accept_attribution

ROOT=Path(__file__).resolve().parents[1]
ASOF='2026-10-27T14:30:00Z'

class EconomicsTests(unittest.TestCase):
    def setUp(self):
        self.s=json.loads((ROOT/'fixtures/snapshot.json').read_text())
        self.c=json.loads((ROOT/'fixtures/base.json').read_text())
    def run_model(self):
        return evaluate(self.s,self.c,ASOF)
    def test_hand_calculated_first_month(self):
        r=self.run_model()['operating_forecast'][0]
        self.assertEqual(r['revenue'],8_000_000)
        self.assertEqual(r['depreciation'],60_000_000/72)
        self.assertAlmostEqual(r['cash_interest'],130_000)
        ni=(8_000_000-2_800_000-1_000_000-100_000-60_000_000/72-130_000)*.79
        self.assertAlmostEqual(r['net_income'],ni)
        self.assertAlmostEqual(r['eps'],ni/10_005_000)
    def test_conservation_all_months(self):
        for r in self.run_model()['operating_forecast']:
            self.assertAlmostEqual(r['cash_conservation_error'],0,places=5)
            self.assertAlmostEqual(r['debt_conservation_error'],0,places=5)
            self.assertAlmostEqual(sum(x['revenue'] for x in r['cohorts']),r['revenue'])
    def test_no_debt_double_subtraction(self):
        r=self.run_model()
        rows=r['operating_forecast']
        end=rows[-1]
        expected=(end['closing_cash']+end['restricted_cash']-end['closing_debt'])/end['diluted_shares']/(1.12)**10
        self.assertAlmostEqual(r['valuation_curve'][0]['conditional_value_per_share'],expected)
    def test_negative_eps_suppresses_pe(self):
        self.s['costs']['corporate_monthly']=100_000_000
        r=self.run_model()
        self.assertLess(r['valuation_curve'][0]['forward_12m_eps'],0)
        self.assertIsNone(r['valuation_curve'][0]['pe_value_per_share'])
    def test_early_disposal_charges_remaining_book_once(self):
        self.s['cohorts'][0]['earning_months_remaining']=24
        self.s['costs']['tax_rate']=0
        rows=self.run_model()['operating_forecast']
        self.assertGreater(rows[24]['disposal_loss'],0)
        self.assertEqual(rows[25]['disposal_loss'],0)
        self.assertAlmostEqual(rows[24]['operating_cash'],rows[24]['net_income']+rows[24]['depreciation']+rows[24]['disposal_loss']+rows[24]['sbc'])
    def test_missing_balance(self):
        self.s['opening']['cash']=None
        with self.assertRaisesRegex(ValueError,'cash'):
            self.run_model()
    def test_missing_source(self):
        self.s['cohorts'][0]['source_ids']=[]
        with self.assertRaises(ValueError): self.run_model()
    def test_unknown_publication(self):
        self.s['sources'][0]['available_at']=None
        with self.assertRaisesRegex(ValueError,'unavailable'): self.run_model()
    def test_no_lookahead(self):
        self.s['sources'][0]['available_at']='2026-10-28T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'unavailable'): self.run_model()
    def test_expiry_preserves_replay_not_current(self):
        self.s['sources'][0]['expires_at']='2026-10-26T00:00:00Z'
        r=self.run_model()
        self.assertEqual(r['freshness']['stale_source_ids'],['SYNTHETIC'])
        self.assertFalse(r['freshness']['current_claim_allowed'])
        self.assertEqual(len(r['operating_forecast']),120)
    def test_acceptance_delay_moves_capex_and_billing(self):
        base=self.run_model()['operating_forecast']
        self.c['acceptance_delay_months']=3
        delay=self.run_model()['operating_forecast']
        self.assertEqual(base[1]['growth_capex'],60_000_000)
        self.assertEqual(delay[1]['growth_capex'],0)
        self.assertEqual(delay[4]['growth_capex'],60_000_000)
        self.assertEqual(delay[3]['revenue'],8_000_000)
        self.assertEqual(base[3]['revenue'],18_000_000)
    def test_fixed_coupon_does_not_follow_market_yield(self):
        base=self.run_model()['operating_forecast'][0]
        self.c['traded_yield_shock']=.50
        shock=self.run_model()['operating_forecast'][0]
        self.assertEqual(base['instruments'],shock['instruments'])
    def test_floating_only_unhedged_fraction(self):
        base=self.run_model()['operating_forecast'][0]
        self.c['benchmark_shock']=.02
        shock=self.run_model()['operating_forecast'][0]
        self.assertEqual(base['instruments'][0]['cash_interest'],shock['instruments'][0]['cash_interest'])
        self.assertAlmostEqual(shock['cash_interest']-base['cash_interest'],12_000_000*.5*.02/12)
    def test_unfunded_not_equity_plug(self):
        self.s['opening']['cash']=0
        for f in self.s['facilities']: f['conditions_met']=False
        r=self.run_model()
        self.assertEqual(r['funding_waterfall']['earliest_gap_month'],1)
        self.assertLess(r['operating_forecast'][1]['closing_cash'],0)
        self.assertTrue(all(p['conditional_value_per_share'] is None for p in r['valuation_curve']))
        self.assertTrue(all(x['equity_shares']==0 for x in r['operating_forecast']))
    def test_explicit_equity_fees_and_dilution(self):
        self.c['equity_issues']=[dict(month=0,amount=10_000_000,price=10,fee_fraction=.02,approved=True)]
        r=self.run_model()['operating_forecast'][0]
        self.assertEqual(r['equity_shares'],1_000_000)
        self.assertEqual(r['equity_net'],9_800_000)
        self.assertEqual(r['diluted_shares'],11_010_000)
    def test_unapproved_equity_not_available(self):
        self.c['equity_issues']=[dict(month=0,amount=10_000_000,price=10,fee_fraction=.02,approved=False)]
        self.assertEqual(self.run_model()['operating_forecast'][0]['equity_net'],0)
    def test_prospective_depreciation_no_pretax_cash_creation(self):
        self.s['costs']['tax_rate']=0
        base=self.run_model()['operating_forecast'][0]
        self.c['depreciation_life_multiplier']=1.5
        longer=self.run_model()['operating_forecast'][0]
        self.assertGreater(longer['net_income'],base['net_income'])
        self.assertAlmostEqual(longer['operating_cash'],base['operating_cash'])
        self.assertLess(longer['depreciation'],base['depreciation'])
    def test_earning_life_creates_distinct_cash(self):
        base=self.run_model()['operating_forecast']
        self.c['earning_life_multiplier']=7/9
        shorter=self.run_model()['operating_forecast']
        self.assertGreater(sum(x['cash_collections'] for x in base[84:108]),sum(x['cash_collections'] for x in shorter[84:108]))
    def test_contract_rpo_not_double_counted(self):
        self.s['contracts'][0]['rpo_remaining']=10_000_000
        rows=self.run_model()['operating_forecast']
        self.assertEqual(sum(x['cohorts'][0]['revenue'] for x in rows),10_000_000)
    def test_restricted_cash_cannot_pay_general_debt(self):
        self.s['opening']['cash']=0
        self.s['opening']['restricted_cash']=100_000_000
        self.s['facilities'][0]['maturity_month']=0
        self.s['facilities'][0]['balance']=100_000_000
        self.s['facilities'][0]['commitment']=100_000_000
        self.s['facilities'][0]['eligible_undrawn']=0
        r=self.run_model()['operating_forecast'][0]
        self.assertGreater(r['funding_gap'],0)
        self.assertEqual(r['restricted_cash'],100_000_000)
    def test_eligibility_limits_draw(self):
        self.s['facilities'][0]['eligible_undrawn']=1_000_000
        self.assertEqual(self.run_model()['operating_forecast'][1]['instruments'][0]['draw'],1_000_000)
    def test_principal_does_not_reduce_eps(self):
        a=self.run_model()['operating_forecast'][0]
        self.s['facilities'][0]['principal']={'0':1_000_000}
        b=self.run_model()['operating_forecast'][0]
        self.assertEqual(a['net_income'],b['net_income'])
        self.assertAlmostEqual(a['closing_cash']-b['closing_cash'],1_000_000)
    def test_fees_counted_once_in_cash(self):
        base=self.run_model()['operating_forecast']
        for f in self.s['facilities']: f['fee_fraction']=0
        nofees=self.run_model()['operating_forecast']
        # Cash fee 200K offset by 42K tax benefit; no duplicated cash fee.
        self.assertAlmostEqual(nofees[1]['closing_cash']-base[1]['closing_cash'],200_000*.79)
    def test_capitalized_interest_deferred_then_amortized(self):
        for f in self.s['facilities']: f['capitalized_fraction']=1
        rows=self.run_model()['operating_forecast']
        self.assertEqual(rows[0]['expensed_interest'],0)
        self.assertAlmostEqual(rows[0]['capitalized_interest_asset'],rows[0]['cash_interest'])
        self.assertGreater(rows[1]['depreciation'],rows[0]['depreciation'])
    def test_cash_lag_does_not_change_revenue(self):
        base=self.run_model()['operating_forecast'][0]
        self.s['contracts'][0]['cash_lag_months']=2
        lag=self.run_model()['operating_forecast'][0]
        self.assertEqual(lag['revenue'],base['revenue'])
        self.assertEqual(lag['cash_collections'],0)
        self.assertAlmostEqual(base['closing_cash']-lag['closing_cash'],8_000_000)
    def test_tradein_exclusive(self):
        r=lifecycle([100]*12,.1,100,1000,200,[200]*12,2)
        self.assertEqual(r['old_fleet_earnings_in_upgrade'],0)
        self.assertAlmostEqual(r['incremental_upgrade_npv'],r['upgrade_npv']-r['keep_npv'])
        with self.assertRaises(ValueError): lifecycle([], .1, 0, 100, 200, [])
    def test_reverse_roundtrip(self):
        row=self.run_model()['operating_forecast'][0]
        quote=row['net_income']*12/row['diluted_shares']*15
        r=reverse_valuation(row,quote,15,.21,12_000_000)
        self.assertAlmostEqual(r['required_revenue'],row['revenue']*12)
        self.assertAlmostEqual(r['maximum_diluted_shares'],row['diluted_shares'])
    def test_future_quote_excluded(self):
        self.s['quote']['available_at']='2026-10-28T00:00:00Z'
        self.assertIsNone(self.run_model()['reverse_valuation'])
    def test_weights_not_calibrated(self):
        self.c['weight_class']='calibrated'
        with self.assertRaises(ValueError): self.run_model()
    def test_invalid_power_basis_and_nan(self):
        self.s['cohorts'][0]['power_basis']='facility_MW'
        with self.assertRaises(ValueError): self.run_model()
        self.setUp()
        self.s['opening']['cash']=math.nan
        with self.assertRaises(ValueError): self.run_model()
    def test_hash_determinism_and_input_purity(self):
        before=copy.deepcopy((self.s,self.c))
        a=self.run_model()
        self.assertEqual(a,self.run_model())
        self.assertEqual(before,(self.s,self.c))
    def test_append_only_history(self):
        r=self.run_model()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'history.jsonl'
            a=append_record(path,r,self.s,self.c,'first')
            prefix=path.read_bytes()
            b=append_record(path,r,self.s,self.c,'correction',actuals=[dict(revenue=1)])
            self.assertTrue(path.read_bytes().startswith(prefix))
            self.assertEqual(b['supersedes'],a['record_id'])
    def test_revision_bridge_reconciles(self):
        new=copy.deepcopy(self.c)
        new['price_multiplier']=1.1
        b=bridge(self.s,self.c,self.s,new,ASOF)
        self.assertAlmostEqual(b['reconciliation_error'],0)
        self.assertGreater(b['revised_value'],b['original_value'])
    def test_declared_unsupported_features_fail_closed(self):
        self.s['unsupported_features']=['convertible conversion']
        with self.assertRaisesRegex(ValueError,'Unsupported'): self.run_model()

class PartialTests(unittest.TestCase):
    setUp=EconomicsTests.setUp
    run_model=EconomicsTests.run_model
    def test_partial_market_survives_missing_finance(self):
        self.s['opening']['cash']=None
        self.s['market_observations']={'bars':[]}
        r=analyze(self.s,self.c,ASOF)
        self.assertIsNone(r['valuation_curve'])
        self.assertIsNotNone(r['traversal'])
        self.assertIn('cash',r['coverage']['reason'])
    def test_horizon_must_cover_equipment_life(self):
        self.c['months']=36
        with self.assertRaisesRegex(ValueError,'earning life'): self.run_model()

class MarketTests(unittest.TestCase):
    def test_factor_no_lookahead_and_reconciliation(self):
        r=dict(schema='crwv.factor-research@1',models={'market_ai':dict(history=[dict(date='2026-10-23',trained_through='2026-10-22',intercept=.01,contributions={'QQQ':.02,'NVDA':-.01},residual=.01,actual_return=.03)])})
        self.assertEqual(accept_attribution(r,ASOF)['status'],'historical_ex_post_diagnostic')
        r['models']['market_ai']['history'][0]['trained_through']='2026-10-23'
        with self.assertRaises(ValueError): accept_attribution(r,ASOF)
    def test_turnover_units_and_sessions(self):
        bars=[dict(date='2026-10-07',session='regular',available_at='2026-10-08T00:00:00Z',completed=True,volume=10,vwap=11,open=10,close=12,high=13,low=9),dict(date='2026-10-07',session='premarket',available_at='2026-10-08T00:00:00Z',completed=True,volume=100,vwap=100,open=100,close=100,high=101,low=99)]
        r=turnover(bars,ASOF)
        self.assertEqual(r['anchored']['dollar_turnover'],110)
        self.assertEqual(r['anchored']['anchored_vwap'],11)
        self.assertEqual(r['windows']['60']['status'],'missing')
        self.assertIsNone(r['transition_probabilities'])
        self.assertIsNone(r['anchored']['unique_holder_replacement'])
    def test_turnover_future_availability_excluded(self):
        b=dict(date='2026-10-07',session='regular',available_at='2027-01-01T00:00:00Z',completed=True,volume=10,vwap=11,open=10,close=12,high=13,low=9)
        self.assertEqual(turnover([b],ASOF)['anchored']['status'],'missing_anchor')

if __name__=='__main__': unittest.main()
