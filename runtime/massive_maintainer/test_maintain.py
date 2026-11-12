import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from decimal import Decimal
from datetime import datetime, timezone
from runtime.massive_maintainer import maintain as m

class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.day='2026-11-11'
        self.t=int(datetime(2026,11,11,15,tzinfo=timezone.utc).timestamp())*1000
        self.row={'t':self.t,'o':Decimal('1.000000000000000001'),'h':2,'l':1,'c':1,'v':3,'n':1}
        self.ev=[{'fetched_at':m.now(),'sha256':'fixture'}]
        self.pointer=self.root/'pointer.json'
        m.atomic(self.pointer,m.encode({'root':str(self.root),'schema':m.SCHEMA}))

    def publish(self,rows=None):
        return m.promote(self.root,'NVDA',self.day,rows or [self.row],self.ev,{})

    def test_decimal_and_repeat(self):
        a=self.publish(); b=self.publish()
        self.assertEqual(a['sha256'],b['sha256'])
        self.assertEqual(b['outcome'],'unchanged')
        row=json.loads((self.root/a['path']).read_text())
        self.assertEqual(row['o'],'1.000000000000000001')

    def test_conflict_rejects_without_publication(self):
        bad=dict(self.row,c=2)
        with self.assertRaises(ValueError): self.publish([self.row,bad])
        self.assertFalse((self.root/'index.json').exists())

    def test_mixed_date_rejects(self):
        with self.assertRaises(ValueError): self.publish([dict(self.row,t=self.t+86400000)])

    def test_midnight_and_dst(self):
        for iso,day in [('2026-11-02T00:30:00+00:00','2026-11-01'),('2026-03-09T03:30:00+00:00','2026-03-08')]:
            self.assertEqual(m.date_of(int(datetime.fromisoformat(iso).timestamp())*1000),day)

    def test_network_free_consumer_and_stale_request(self):
        self.publish()
        with patch('urllib.request.urlopen',side_effect=AssertionError('consumer network call')) as network:
            self.assertEqual(m.resolve(self.pointer,'NVDA',self.day)['status'],'qualified_historical')
            self.assertEqual(m.resolve(self.pointer,'NVDA',self.day,self.t+60000)['status'],'refresh_required')
            network.assert_not_called()

    def test_checksum_tamper_rejected(self):
        r=self.publish(); (self.root/r['path']).write_text('{}')
        with self.assertRaises(ValueError): m.resolve(self.pointer,'NVDA',self.day)

    def test_revision_retains_previous(self):
        a=self.publish(); b=self.publish([dict(self.row,c=2)])
        self.assertEqual(b['supersedes'],a['sha256'])
        self.assertTrue((self.root/a['path']).exists())

    def test_lock(self):
        with m.writer(self.root):
            with self.assertRaises(FileExistsError):
                with m.writer(self.root): pass

    def test_archive_and_quarantine(self):
        legacy=self.root/'legacy'; legacy.mkdir()
        raw=m.encode(dict(self.row,ticker='NVDA',grain='1min',src='unverified'))+b'invalid\n'
        (legacy/'NVDA.jsonl').write_bytes(raw)
        record=m.inventory(self.root,legacy)[0]; result=m.audit(self.root,record)
        self.assertEqual(Path(result['archive']).read_bytes(),raw)
        self.assertEqual(result['invalid'],1)
        self.assertEqual(result['confirmed_ranges'],[])

    def test_float_and_empty_rejected(self):
        with self.assertRaises(ValueError): m.normalize(dict(self.row,c=1.1),'NVDA',self.day)
        with self.assertRaises(ValueError): m.promote(self.root,'NVDA',self.day,[],self.ev,{})

    def test_no_credential_to_foreign_host(self):
        c=m.Massive(self.root,self.root/'nonexistent-key')
        with self.assertRaises(ValueError): c.get('https://evil.example/path')

    def rewrite_index(self, change):
        index=m.read(self.root/'index.json')
        change(index)
        m.atomic(self.root/'index.json',m.encode(index))

    def test_resolver_rejects_relabelled_ticker(self):
        self.publish()
        def relabel(index):
            entry=index['partitions'].pop('NVDA/'+self.day)
            entry['source_confirmed_query']['ticker']='AAOI'
            index['partitions']['AAOI/'+self.day]=entry
        self.rewrite_index(relabel)
        with self.assertRaises(ValueError): m.resolve(self.pointer,'AAOI',self.day)

    def test_resolver_rejects_relabelled_date(self):
        self.publish()
        day='2026-11-10'
        def relabel(index):
            entry=index['partitions'].pop('NVDA/'+self.day)
            entry['source_confirmed_query']['date']=day
            index['partitions']['NVDA/'+day]=entry
        self.rewrite_index(relabel)
        with self.assertRaises(ValueError): m.resolve(self.pointer,'NVDA',day)

    def test_resolver_rejects_incompatible_index_schema(self):
        self.publish()
        self.rewrite_index(lambda index: index.update(schema='incompatible@99'))
        with self.assertRaises(ValueError): m.resolve(self.pointer,'NVDA',self.day)

    def test_resolver_rejects_false_row_count(self):
        start=int(datetime(2026,11,11,9,tzinfo=timezone.utc).timestamp())*1000
        self.publish([dict(self.row,t=start+i*60000) for i in range(960)])
        self.rewrite_index(lambda index: index['partitions']['NVDA/'+self.day].update(rows=1))
        with self.assertRaises(ValueError): m.resolve(self.pointer,'NVDA',self.day)

    def test_resolver_rejects_checksum_valid_row_metadata_corruption(self):
        for field,value in [('schema','other@1'),('source','other'),('grain','1d'),
                            ('currency','EUR'),('adjustment','unadjusted'),
                            ('timezone','UTC'),('session_date','2026-11-10'),
                            ('ticker','AAOI'),('t',self.t+86400000)]:
            with self.subTest(field=field):
                result=self.publish()
                data_path=self.root/result['path']
                original=data_path.read_bytes()
                try:
                    row=json.loads(original); row[field]=value
                    data=m.encode(row); data_path.write_bytes(data)
                    self.rewrite_index(lambda index: index['partitions']['NVDA/'+self.day].update(sha256=m.digest(data)))
                    with self.assertRaises(ValueError): m.resolve(self.pointer,'NVDA',self.day)
                finally:
                    data_path.write_bytes(original)

    def test_resolver_rejects_manifest_metadata_corruption(self):
        for field,value in [('rows',True),('first_t',self.t-60000),('last_t',self.t+60000),
                            ('source_confirmed_query',{'ticker':'AAOI','date':self.day,'grain':'1m','adjusted':True})]:
            with self.subTest(field=field):
                self.publish()
                self.rewrite_index(lambda index: index['partitions']['NVDA/'+self.day].update({field:value}))
                with self.assertRaises(ValueError): m.resolve(self.pointer,'NVDA',self.day)

    def test_resolver_rejects_incompatible_pointer_schema(self):
        self.publish()
        for cfg in ({'root':str(self.root),'schema':'incompatible@99'},
                    {'root':str(self.root)}, [], None):
            with self.subTest(pointer=cfg):
                m.atomic(self.pointer,m.encode(cfg))
                with self.assertRaisesRegex(ValueError,'incompatible resolver pointer'):
                    m.resolve(self.pointer,'NVDA',self.day)
        m.atomic(self.pointer,m.encode({'root':str(self.root),'schema':m.SCHEMA}))
        self.assertEqual(m.resolve(self.pointer,'NVDA',self.day)['status'],'qualified_historical')

    def test_resolver_root_contract_before_data_access(self):
        configs=[{'schema':m.SCHEMA}]+[
            {'schema':m.SCHEMA,'root':value}
            for value in (None,42,True,[],{},'', '   ', 'bad\x00root', 'relative-root')]
        for cfg in configs:
            with self.subTest(pointer=cfg):
                with patch.object(m,'read',side_effect=[cfg,AssertionError('data-root read before validation')]) as reader:
                    with patch.object(Path,'open',side_effect=AssertionError('unexpected data access')):
                        with patch.object(Path,'mkdir',side_effect=AssertionError('unexpected data write')):
                            with self.assertRaisesRegex(ValueError,'^invalid resolver root: expected an absolute non-empty path string$'):
                                m.resolve(self.pointer,'NVDA',self.day)
                    self.assertEqual(reader.call_count,1)
        self.publish()
        self.assertEqual(m.resolve(self.pointer,'NVDA',self.day)['status'],'qualified_historical')

if __name__=='__main__': unittest.main()
