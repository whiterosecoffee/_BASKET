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
        m.atomic(self.pointer,m.encode({'root':str(self.root)}))

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

if __name__=='__main__': unittest.main()
