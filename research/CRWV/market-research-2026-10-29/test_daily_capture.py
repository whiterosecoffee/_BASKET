import csv
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from backfill_minutes import capture
from prepare_daily_shards import ET


class CaptureTests(unittest.TestCase):
    def write_csv(self, path, rows):
        with path.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ticker', 'v', 'vw', 'o', 'c', 'h', 'l', 't', 'n'])
            writer.writerows(rows)

    def row(self, dt):
        return ['CRWV', 100, 10, 10, 10, 11, 9, int(dt.timestamp() * 1000), 2]

    def test_dst_midnight_and_replay(self):
        times = [datetime(2026, 11, 1, 1, 59, tzinfo=ET, fold=0),
                 datetime(2026, 11, 1, 1, 0, tzinfo=ET, fold=1),
                 datetime(2026, 11, 1, 23, 59, tzinfo=ET),
                 datetime(2026, 11, 2, 0, 0, tzinfo=ET)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root/'input.csv'; out = root/'stage'
            rows = [self.row(t) for t in times]
            self.write_csv(source, rows + [rows[0]])
            result = capture(source, out, '2026-11')
            self.assertEqual(result['records'], 4)
            self.assertEqual(result['day_count'], 2)
            self.assertEqual(result['duplicate_source_rows'], 1)
            metadata = json.loads((out/'2026-11-01.1m.meta.json').read_text())
            self.assertTrue(metadata['start'].endswith('-04:00'))
            self.assertTrue(metadata['as_of_last_bar'].endswith('-05:00'))
            before = {p.name: p.read_bytes() for p in out.iterdir()}
            self.assertEqual(capture(source, out, '2026-11')['added_files'], 0)
            self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
            fold_source = root/'fold.csv'
            self.write_csv(fold_source, rows[:1])
            capture(fold_source, root/'fold', '2026-11')
            fold_metadata = json.loads((root/'fold/2026-11-01.1m.meta.json').read_text())
            self.assertEqual(fold_metadata['as_of_last_bar'], '2026-11-01T01:00:00-05:00')
            self.write_csv(source, rows[:-1])
            with self.assertRaisesRegex(ValueError, 'new staging generation'):
                capture(source, out, '2026-11')
            self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})

    def test_source_conflict_and_wrong_month_leave_no_outputs(self):
        row = self.row(datetime(2026, 10, 1, 9, 30, tzinfo=ET))
        changed = row.copy(); changed[4] = 10.5
        for rows, month in [([row, changed], '2026-10'), ([row], '2026-11')]:
            with self.subTest(month=month), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); source = root/'input.csv'; out = root/'stage'
                self.write_csv(source, rows)
                with self.assertRaises(ValueError):
                    capture(source, out, month)
                self.assertFalse(out.exists())

    def test_reject_repo_output(self):
        with self.assertRaisesRegex(ValueError, 'External staging'):
            capture('not-read.csv', Path(__file__).parent/'forbidden-stage', '2026-10')


if __name__ == '__main__':
    unittest.main()
