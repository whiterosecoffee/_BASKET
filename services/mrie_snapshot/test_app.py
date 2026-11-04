import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from app import build_snapshot, make_server

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.entity = self.root / 'tickers/AAOI/entity.json'
        self.entity.parent.mkdir(parents=True)
        self.entity.write_text('{"id":"AAOI"}')
        self.token = 'a' * 40
        self.server = make_server(self.root, 'b' * 40, self.token, limit=3)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.tmp.cleanup()
    def get(self, path, authorized=True):
        c = http.client.HTTPConnection(*self.server.server_address)
        c.request('GET', path, headers={'Authorization': 'Bearer '+self.token} if authorized else {})
        r = c.getresponse()
        result = r.status, json.loads(r.read())
        c.close()
        return result
    def test_auth_and_health(self):
        self.assertEqual(self.get('/health', False)[0], 200)
        self.assertEqual(self.get('/tools', False)[0], 401)
        self.assertEqual(self.get('/tools')[1]['protocol'], 'REST-only')
    def test_immutable_provenance(self):
        before = self.get('/snapshot/AAOI')[1]
        self.entity.write_text('{"id":"AAOI","changed":true}')
        self.assertEqual(before, self.get('/snapshot/AAOI')[1])
        self.assertFalse(before['result']['live'])
        self.assertEqual(len(before['result']['input_sha256']), 64)
    def test_missing_and_traversal(self):
        self.assertEqual(self.get('/snapshot/MU')[1]['result']['status'], 'unavailable')
        self.assertEqual(self.get('/snapshot/../AAOI')[0], 400)
    def test_rate_limit(self):
        for _ in range(3):
            self.assertEqual(self.get('/tools')[0], 200)
        self.assertEqual(self.get('/tools')[0], 429)
    def test_manifest_determinism_and_identity(self):
        a = build_snapshot(self.root, 'b'*40)
        self.assertEqual(a, build_snapshot(self.root, 'b'*40))
        self.entity.write_text('{"id":"MU"}')
        with self.assertRaises(ValueError):
            build_snapshot(self.root, 'b'*40)
    def test_fail_closed_config(self):
        with self.assertRaises(ValueError):
            make_server(self.root, 'b'*40, '')
        with self.assertRaises(ValueError):
            build_snapshot(self.root, 'main')

if __name__ == '__main__':
    unittest.main()
