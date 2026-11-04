import json
import tempfile
import unittest
from pathlib import Path
from prepare_daily_shards import prepare


class DailyShardTests(unittest.TestCase):
    def test_actual_october_lossless_and_replay(self):
        source = Path(__file__).resolve().parents[3] / 'tickers/CRWV/intraday/2026-10.1m.jsonl'
        with tempfile.TemporaryDirectory() as folder:
            first = prepare(source, folder)
            self.assertEqual(first['records'], 19186)
            self.assertEqual(first['day_count'], 22)
            self.assertEqual(first['vwap_outside_ohlc'], 2374)
            self.assertEqual(first['source_sha256'], '9249539642e10805bcb1a6dfabb53de0bd53f4e5adbea454092f44ecfc55b1ac')
            self.assertEqual(b''.join(p.read_bytes() for p in sorted(Path(folder).glob('*.jsonl'))), source.read_bytes())
            self.assertEqual(prepare(source, folder)['added_files'], 0)

    def test_invalid_inputs_do_not_write(self):
        row = [1790868600000, 10, 11, 9, 10, 100, 10, 2]
        cases = [b'', b'[]', (json.dumps(row)+'\n') .encode()*2,
                 (json.dumps([row[0], 10, 8, 9, 10, 100, 10, 2])+'\n').encode(),
                 (json.dumps([row[0], 10, 11, 9, 10, float('nan'), 10, 2])+'\n').encode()]
        for data in cases:
            with self.subTest(data=data), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); source = root/'source'/'capture.jsonl'
                source.parent.mkdir(); source.write_bytes(data)
                with self.assertRaises(ValueError):
                    prepare(source, root/'staging')
                self.assertFalse((root/'staging').exists())

    def test_conflict_and_canonical_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'source'/'capture.jsonl'
            source.parent.mkdir()
            source.write_text('[1790868600000,10,11,9,10,100,10,2]\n')
            with self.assertRaises(ValueError):
                prepare(source, source.parent)
            result = prepare(source, root/'staging')
            shard = root/'staging'/result['shards'][0]['name']
            shard.write_text('conflict\n')
            with self.assertRaises(ValueError):
                prepare(source, root/'staging')
            self.assertEqual(shard.read_text(), 'conflict\n')


if __name__ == '__main__':
    unittest.main()
