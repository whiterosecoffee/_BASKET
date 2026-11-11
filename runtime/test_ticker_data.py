"""NVDA-only acceptance: persistence, concurrency, replay and input failures."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    from . import ticker_data as data
except ImportError:
    import ticker_data as data


def bar():
    # Controlled synthetic values, not actual NVDA market observations.
    return data.massive_bar({'ticker':'NVDA','status':'OK','adjusted':False,
        'results':[{'t':1793367000000,'o':100,'h':102,'l':99,'c':101,'v':1000}]}, 0,
        interval='1m', adjustment_basis='unadjusted', available_at='2026-10-30T13:31:00Z',
        ingested_at='2026-11-01T02:00:00Z')


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = data.TickerStore(self.tmp.name)

    def write(self):
        r = self.store.put(bar())
        self.assertEqual(r['status'],'created',r['errors'])
        return r['records'][0]

    def test_create_restart_duplicate(self):
        first = self.write()
        row = bar(); row['ingested_at']='2026-11-01T03:00:00Z'
        self.assertEqual(self.store.put(row)['status'],'unchanged')
        fresh=data.TickerStore(self.tmp.name).read('2026-11-02T00:00:00Z')
        self.assertEqual(fresh['records'],[first])
        self.assertEqual(len(self.store.path.read_text().splitlines()),1)

    def test_revision_asof_and_retry(self):
        first=self.write(); row=bar()
        row['value']['close']=102; row['supersedes']=first['record_id']
        row['available_at']='2026-11-01T04:00:00Z'; row['ingested_at']='2026-11-01T04:01:00Z'
        revised=self.store.put(row,first['record_id'])
        self.assertEqual(revised['status'],'revised',revised)
        self.assertEqual(self.store.read('2026-11-01T03:00:00Z')['records'],[first])
        self.assertEqual(self.store.put(row,first['record_id'])['status'],'unchanged')
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z')['records'][0]['value']['close'],102)

    def test_changed_without_expected_head_conflicts(self):
        self.write(); row=bar(); row['value']['close']=102
        self.assertEqual(self.store.put(row)['status'],'conflict')

    def test_stale_head_conflicts(self):
        self.write(); row=bar(); row['value']['close']=102; row['supersedes']='a'*64
        self.assertEqual(self.store.put(row,'a'*64)['status'],'conflict')

    def test_retract_preserves_history(self):
        first=self.write(); row=bar(); row.update(value=None,retracted=True,supersedes=first['record_id'])
        row['ingested_at']='2026-11-01T04:00:00Z'
        self.assertEqual(self.store.put(row,first['record_id'])['status'],'retracted')
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z')['status'],'no_data')
        self.assertEqual(self.store.read('2026-11-01T03:00:00Z')['records'],[first])
        self.assertEqual(len(self.store.read('2026-11-02T00:00:00Z',include_retracted=True)['records']),1)

    def test_asof_excludes_later_ingestion(self):
        self.write()
        self.assertEqual(self.store.read('2026-10-31T00:00:00Z')['status'],'no_data')

    def test_empty_is_not_complete_coverage(self):
        r=self.store.read('2026-11-01T00:00:00Z')
        self.assertEqual(r['status'],'no_data')
        self.assertNotIn('coverage_complete',r)

    def test_other_tickers_rejected(self):
        r=bar(); r['entity_id']='MU'
        self.assertEqual(self.store.put(r)['status'],'rejected')
        self.assertFalse(self.store.path.exists())

    def test_invalid_ohlc(self):
        r=bar(); r['value']['close']=200
        self.assertEqual(self.store.put(r)['errors'][0]['code'],'INVALID_OHLC')

    def test_negative_volume_and_nan(self):
        for value in (-1,float('nan')):
            r=bar(); r['value']['volume']=value
            self.assertEqual(self.store.put(r)['status'],'rejected')

    def test_invalid_time(self):
        r=bar(); r['ingested_at']='2020-01-01T00:00:00Z'
        self.assertEqual(self.store.put(r)['status'],'rejected')

    def test_lock_fails_closed(self):
        self.store.path.parent.mkdir(parents=True)
        lock=self.store.path.with_suffix('.lock'); lock.write_text('busy')
        self.assertEqual(self.store.put(bar())['errors'][0]['code'],'LOCKED')
        self.assertTrue(lock.exists())

    def test_interrupted_replace_preserves_previous_file(self):
        first=self.write(); before=self.store.path.read_bytes()
        r=bar(); r['source_record_id']='second'
        with patch.object(data.os,'replace',side_effect=OSError('interrupted')):
            self.assertEqual(self.store.put(r)['status'],'rejected')
        self.assertEqual(self.store.path.read_bytes(),before)
        self.assertFalse(self.store.path.with_suffix('.lock').exists())
        self.assertEqual(self.store.put(r)['status'],'created')

    def test_corruption_not_reported_as_empty(self):
        self.write(); self.store.path.write_text('{truncated')
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z')['status'],'rejected')
        self.assertEqual(self.store.put(bar())['status'],'rejected')

    def test_hash_tampering_detected(self):
        r=self.write(); r['value']['volume']=10
        self.store.path.write_text(json.dumps(r)+'\n')
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z')['errors'][0]['code'],'CORRUPT_JOURNAL')

    def test_snapshot_deterministic(self):
        self.write()
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z'),self.store.read('2026-11-02T00:00:00Z'))

    def test_input_unchanged(self):
        r=bar(); old=copy.deepcopy(r); self.store.put(r); self.assertEqual(r,old)

    def test_query_validation(self):
        self.assertEqual(self.store.read('invalid')['status'],'rejected')
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z',kind='anything')['status'],'rejected')

    def test_filter_range(self):
        self.write()
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z',kind='financial_fact')['status'],'no_data')
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z',end='2026-10-01T00:00:00Z')['status'],'no_data')

    def test_source_failure_and_incomplete_pages(self):
        for response in ({'ticker':'NVDA','status':'ERROR'}, {'ticker':'NVDA','status':'OK','next_url':'more'}):
            with self.assertRaises(data.StoreError):
                data.massive_bar(response,0,interval='1m',adjustment_basis='unadjusted',available_at='',ingested_at='')

    def test_legacy_preserves_format_and_uncertainty(self):
        p=Path(self.tmp.name)/'history.jsonl'; row=[1,100,102,99,101,1000,None,None]
        p.write_text(json.dumps(row)+'\n')
        r=data.legacy_bars(p,{'schema':'market.daily@1','entity_id':'NVDA'})
        self.assertEqual(r['records'],[row]); self.assertFalse(r['point_in_time_verified'])

    def test_result_contract(self):
        schema={'$ref':'#/$defs/result','$defs':data.SCHEMA['$defs']}
        validator=data.Draft202012Validator(schema,format_checker=data.FormatChecker())
        for r in [self.store.put(bar()),self.store.put(bar()),self.store.read('2026-11-02T00:00:00Z'),self.store.read('bad')]:
            validator.validate(r)

    def test_batch_invalid_member_is_atomic(self):
        first=self.write(); before=self.store.path.read_bytes()
        a=bar(); a['source_record_id']='another'
        b=bar(); b['value']['volume']=-1
        self.assertEqual(self.store.put_many([a,b])['status'],'rejected')
        self.assertEqual(before,self.store.path.read_bytes())

    def test_retrieval_metadata_is_not_new_economic_event(self):
        self.write(); r=bar(); r['available_at']='2026-11-01T03:00:00Z'; r['ingested_at']='2026-11-01T03:00:00Z'
        r['source_fingerprint']='a'*64
        self.assertEqual(self.store.put(r)['status'],'unchanged')

    def test_csv_adapter(self):
        text='v,vw,o,c,h,l,t,n\n1000,101,100,101,102,99,1793367000000,10\n'
        rows=data.massive_csv_observations(text,adjustment_basis='unadjusted',retrieved_at='2026-11-01T02:00:00Z')
        self.assertEqual(self.store.put_many(rows)['status'],'created')
        self.assertEqual(self.store.put_many(rows)['status'],'unchanged')
        self.assertEqual(len(rows[0]['source_fingerprint']),64)

    def test_csv_failure(self):
        for text in ('status,error','v,vw,o,c,h,l,t,n\n','v,vw,o,c,h,l,t,n\n1,2\n'):
            with self.assertRaises((ValueError,TypeError)):
                data.massive_csv_observations(text,adjustment_basis='unadjusted',retrieved_at='2026-11-01T02:00:00Z')

    def test_json_array_is_corruption(self):
        self.store.path.parent.mkdir(parents=True);self.store.path.write_text('[]\n')
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z')['status'],'rejected')

    def test_source_backed_revenue_fixture(self):
        p=Path(__file__).parent/'fixtures/nvda/revenue.json'
        r=json.loads(p.read_text())
        self.assertEqual(r['value']['amount'],35082000000)
        self.assertEqual(self.store.put(r)['status'],'created')
        self.assertEqual(self.store.read('2026-11-02T00:00:00Z',kind='financial_fact')['records'][0]['value']['basis'],'reported')


if __name__=='__main__': unittest.main()
