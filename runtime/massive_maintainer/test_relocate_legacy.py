"""Safe placement tests use only small disposable files."""
import contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from runtime.massive_maintainer import relocate_legacy as r

class PlacementTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.source=self.root/'original';self.source.mkdir();self.staging=self.root/'staging';self.staging.mkdir();self.target=self.root/'_TICKERS';self.journal=self.root/'journal';self.authority=self.root/'authority'
        self.raw=b'{"ticker":"NVDA","t":1}\n';(self.source/'NVDA.jsonl').write_bytes(self.raw);(self.staging/'NVDA.jsonl').write_bytes(self.raw)
        self.manifest=self.root/'input.json';self.manifest.write_text(json.dumps({'discovered':1,'complete':True,'files':[{'ticker':'NVDA','source':str(self.source/'NVDA.jsonl'),'destination':str(self.staging/'NVDA.jsonl'),'bytes':len(self.raw),'sha256':None}]}))
    def run_placement(self):
        with contextlib.redirect_stdout(io.StringIO()):return r.execute(self.manifest,self.source,self.staging,self.target,self.authority,self.journal)
    def test_complete_and_idempotent_lookup_preserves_original(self):
        self.run_placement();self.assertEqual((self.source/'NVDA.jsonl').read_bytes(),self.raw);self.assertFalse((self.staging/'NVDA.jsonl').exists())
        result=r.resolve_archive(self.target/'_FETCH-placement.json','NVDA');self.assertEqual(Path(result['path']).read_bytes(),self.raw);self.assertEqual(result['status'],'archive_available_not_qualified')
        self.run_placement();self.assertEqual((self.source/'NVDA.jsonl').read_bytes(),self.raw)
    def test_collision_never_overwrites_or_retires_staging(self):
        path=self.target/'NVDA/NVDA.jsonl';path.parent.mkdir(parents=True);path.write_bytes(b'different')
        with self.assertRaises(FileExistsError):self.run_placement()
        self.assertEqual(path.read_bytes(),b'different');self.assertEqual((self.staging/'NVDA.jsonl').read_bytes(),self.raw)
    def test_differing_staging_refuses(self):
        (self.staging/'NVDA.jsonl').write_bytes(b'bad')
        with self.assertRaises(ValueError):self.run_placement()
        self.assertEqual((self.source/'NVDA.jsonl').read_bytes(),self.raw)
        self.assertFalse((self.target/'NVDA/NVDA.jsonl').exists())
    def test_failure_before_retirement_preserves_recovery(self):
        original=r.append
        def crash(path,record):
            if record.get('event')=='published_verified':raise RuntimeError('synthetic crash')
            return original(path,record)
        with patch.object(r,'append',side_effect=crash):
            with self.assertRaises(RuntimeError):self.run_placement()
        self.assertEqual((self.staging/'NVDA.jsonl').read_bytes(),self.raw)
        self.assertEqual((self.target/'NVDA/NVDA.jsonl').read_bytes(),self.raw)
        self.run_placement();self.assertFalse((self.staging/'NVDA.jsonl').exists())
    def test_escaped_path_refused(self):
        obj=json.loads(self.manifest.read_bytes());obj['files'][0]['source']=str(self.root/'outside.jsonl');self.manifest.write_text(json.dumps(obj))
        with self.assertRaises(ValueError):self.run_placement()
    def test_competing_writer_refused(self):
        with r.writer(self.authority):
            with self.assertRaises(FileExistsError):self.run_placement()
