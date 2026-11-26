import copy
import unittest
from coverage import project, RESOURCES


class CoverageTests(unittest.TestCase):
    def fixture(self):
        return {'schema': 'basket.scope_manifest@draft1', 'count': 4, 'records': [
            {'symbol': 'CRWV', 'instrument_type': 'equity_or_depositary_receipt'},
            {'symbol': 'FUND', 'instrument_type': 'fund_or_etp'},
            {'symbol': 'INDEX', 'instrument_type': 'index'},
            {'symbol': 'UNKNOWN', 'instrument_type': 'equity_or_depositary_receipt'}]}

    def test_complete_unique_and_no_mutation(self):
        manifest = self.fixture()
        before = copy.deepcopy(manifest)
        result = project(manifest)
        self.assertEqual(manifest, before)
        self.assertEqual(len(result['rows']), 4)
        self.assertEqual(set(r['scope_symbol_ref'] for r in result['rows']), {'CRWV', 'FUND', 'INDEX', 'UNKNOWN'})
        self.assertTrue(all(set(r['resources']) == set(RESOURCES) for r in result['rows']))

    def test_missingness_not_zero_or_current(self):
        for row in project(self.fixture())['rows']:
            self.assertIsNone(row['observed_premium_bps'])
            self.assertIsNone(row['justified_premium_bps'])
            self.assertIsNone(row['mispricing_residual_bps'])
            self.assertFalse(row['current_verified_pricing'])
        self.assertEqual(project(self.fixture())['resource_defaults']['entitlement'], 'unverified')

    def test_historical_draft_never_refreshes_quote(self):
        row = project(self.fixture())['rows'][0]
        self.assertTrue(row['resources']['maturities'].startswith('historical_draft'))
        self.assertTrue(row['resources']['bond_quotes'].startswith('unavailable'))
        self.assertIsNone(project(self.fixture())['resource_defaults']['observed_at'])

    def test_fund_not_assumed_no_debt(self):
        row = project(self.fixture())['rows'][1]
        self.assertIn('review_required', row['debt_applicability'])
        self.assertTrue(row['resources']['loan_terms'].startswith('unavailable'))

    def test_index_direct_credit_conditional_na_curve_missing(self):
        row = project(self.fixture())['rows'][2]
        self.assertTrue(row['resources']['loan_terms'].startswith('not_applicable'))
        self.assertTrue(row['resources']['treasury_curve'].startswith('unavailable'))

    def test_fail_closed_on_scope_changes(self):
        for field, value in [('count', 5), ('schema', 'unreviewed')]:
            fixture = self.fixture()
            fixture[field] = value
            with self.assertRaises(ValueError):
                project(fixture)
        fixture = self.fixture()
        fixture['records'][1]['symbol'] = 'CRWV'
        with self.assertRaises(ValueError):
            project(fixture)
        fixture = self.fixture()
        fixture['records'][1]['instrument_type'] = 'unknown'
        with self.assertRaises(ValueError):
            project(fixture)

    def test_order_independent(self):
        fixture = self.fixture()
        reversed_fixture = copy.deepcopy(fixture)
        reversed_fixture['records'].reverse()
        # Source hash preserves exact source ordering; row projection stays stable.
        self.assertEqual(project(fixture)['rows'], project(reversed_fixture)['rows'])


if __name__ == '__main__':
    unittest.main()
