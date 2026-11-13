"""Rate-limit/provenance controls with fake transport and no real waits."""
import io
import json
import tempfile
import unittest
from datetime import datetime,timedelta
from email.utils import format_datetime
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from runtime.massive_maintainer import maintain as m

class TransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.key=self.root/'key';self.key.write_text('FAKE_SECRET_123')
        self.enterContext(patch('time.sleep'))
    def error(self,value,**headers):
        return HTTPError('https://api.massive.com/fixture',429,'rate limit',dict({'Retry-After':value},**headers),io.BytesIO(b''))
    def test_long_wait_durably_defers_and_restart_does_not_retry(self):
        with patch('urllib.request.urlopen',side_effect=self.error('120')) as network:
            with self.assertRaises(m.RetryDeferred):m.Massive(self.root,self.key).get('/fixture')
            self.assertEqual(network.call_count,1)
            receipt=m.read(self.root/'retry-after.json');self.assertEqual(receipt['minimum_wait_seconds'],120)
            with self.assertRaises(m.RetryDeferred):m.Massive(self.root,self.key).get('/fixture')
            self.assertEqual(network.call_count,1)
    def test_short_wait_retries_with_pacing(self):
        with patch('urllib.request.urlopen',side_effect=[self.error('3'),io.BytesIO(b'{"ok":true}')]) as network, patch('time.sleep') as sleep:
            body,ev=m.Massive(self.root,self.key).get('/fixture')
            self.assertTrue(body['ok']);self.assertEqual(network.call_count,2)
            self.assertTrue(any(c.args[0]>=3 for c in sleep.call_args_list))
    def test_http_date_uses_server_date_against_clock_skew(self):
        server=datetime(2026,11,13,tzinfo=m.UTC)
        with patch.object(m,'now',return_value=(server+timedelta(hours=1)).isoformat()):
            with patch('urllib.request.urlopen',side_effect=self.error(format_datetime(server+timedelta(seconds=120)),Date=format_datetime(server))) as network:
                with self.assertRaises(m.RetryDeferred):m.Massive(self.root,self.key).get('/fixture')
                self.assertEqual(network.call_count,1)
        self.assertGreaterEqual(m.read(self.root/'retry-after.json')['minimum_wait_seconds'],120)
    def test_malformed_header_requires_review(self):
        for header in ('garbage','-1','NaN','Infinity'):
            with self.subTest(header=header):
                (self.root/'retry-after.json').unlink(missing_ok=True)
                with patch('urllib.request.urlopen',side_effect=self.error(header)) as network:
                    with self.assertRaises(m.RetryDeferred):m.Massive(self.root,self.key).get('/fixture')
                    self.assertEqual(network.call_count,1)
                self.assertEqual(m.read(self.root/'retry-after.json')['status'],'retry_header_review_required')
    def test_query_provenance_and_secret_removal(self):
        evs=[]
        with patch('urllib.request.urlopen',side_effect=lambda *a,**kw:io.BytesIO(b'{"ok":true}')) as network:
            for adjusted in ('true','false'):
                body,ev=m.Massive(self.root,self.key).get('/fixture?adjusted='+adjusted+'&limit=1&limit=2&apiKey=FAKE_SECRET_123')
                evs.append(ev)
            self.assertNotIn('apiKey',network.call_args.args[0].full_url)
        self.assertNotEqual(evs[0]['request_params'],evs[1]['request_params'])
        self.assertEqual(evs[0]['request_params'],[['adjusted','true'],['limit','1'],['limit','2']])
        self.assertTrue(list((self.root/'raw-receipts').glob('*.json')))
        for p in (self.root/'raw-receipts').glob('*.json'):
            self.assertNotIn(b'FAKE_SECRET_123',p.read_bytes())
    def test_unknown_secret_query_rejected_before_network(self):
        with patch('urllib.request.urlopen') as network:
            with self.assertRaises(ValueError):m.Massive(self.root,self.key).get('/fixture?access_token=another-secret')
            network.assert_not_called()
    def test_backward_clock_preserves_deferral(self):
        instant=datetime.now(m.UTC)
        with patch.object(m,'now',return_value=instant.isoformat()),patch('urllib.request.urlopen',side_effect=self.error('120')):
            with self.assertRaises(m.RetryDeferred):m.Massive(self.root,self.key).get('/fixture')
        with patch.object(m,'now',return_value=(instant-timedelta(hours=1)).isoformat()),patch('urllib.request.urlopen') as network:
            with self.assertRaises(m.RetryDeferred):m.Massive(self.root,self.key).get('/fixture')
            network.assert_not_called()

    def test_forward_wall_clock_same_client_cannot_bypass_monotonic(self):
        instant=datetime.now(m.UTC);client=m.Massive(self.root,self.key)
        with patch.object(m,'now',return_value=instant.isoformat()),patch('urllib.request.urlopen',side_effect=self.error('120')):
            with self.assertRaises(m.RetryDeferred):client.get('/fixture')
        with patch.object(m,'now',return_value=(instant+timedelta(hours=1)).isoformat()),patch('urllib.request.urlopen') as network:
            with self.assertRaises(m.RetryDeferred):client.get('/fixture')
            network.assert_not_called()
    def test_exhaustion_is_bounded_and_durable(self):
        with patch('urllib.request.urlopen',side_effect=self.error('0')) as network:
            with self.assertRaises(m.RetryDeferred):m.Massive(self.root,self.key).get('/fixture')
            self.assertEqual(network.call_count,4)
        self.assertEqual(m.read(self.root/'retry-after.json')['status'],'retry_deferred')
    def test_http_date_without_server_date_and_past_date(self):
        instant=datetime(2026,11,13,tzinfo=m.UTC)
        self.assertEqual(m.retry_minimum({'Retry-After':format_datetime(instant+timedelta(seconds=120))},instant),120)
        self.assertEqual(m.retry_minimum({'Retry-After':format_datetime(instant-timedelta(seconds=120))},instant),0)
    def test_response_parse_failure_still_has_raw_provenance(self):
        with patch('urllib.request.urlopen',return_value=io.BytesIO(b'not json')):
            with self.assertRaises(ValueError):m.Massive(self.root,self.key).get('/fixture?limit=2')
        receipt=json.loads(next((self.root/'raw-receipts').glob('*.json')).read_bytes())
        self.assertEqual(receipt['request_params'],[['limit','2']])
        self.assertEqual((self.root/receipt['path']).read_bytes(),b'not json')
