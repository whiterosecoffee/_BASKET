import copy
import unittest
from datetime import datetime, timezone, timedelta
from inventory import build, cache_matches


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.e = dict(repository='a/b', observed_at='2026-10-29T17:00:00Z', main_sha='a'*40,
            tree_truncated=False, open_prs_complete=True, open_issues_complete=True,
            branches_complete=True, main_tree=[], main_ci=[], pull_requests=[dict(number=1,
            title='[B02] replay', body='Receives #7', branch='work/1-replay', head_sha='b'*40,
            files_complete=True, files=[dict(path='runtime/replay.py', blob_sha='c'*40)],
            ci=[dict(sha='d'*40, name='stale green', conclusion='success')])])

    def test_stale_green_excluded_and_no_operation_inferred(self):
        c = build(self.e)['capabilities'][0]
        self.assertEqual(c['exact_head_ci'], [])
        self.assertIsNone(c['operational_evidence'])
        self.assertEqual(c['dependency_issues'], [7])

    def test_head_and_main_change_invalidate(self):
        before = build(self.e)
        for key in ('main_sha', 'head_sha'):
            changed = copy.deepcopy(self.e)
            if key == 'main_sha':
                changed[key] = 'e'*40
            else:
                changed['pull_requests'][0][key] = 'e'*40
            self.assertEqual(build(changed, before)['invalidated_records'], ['pr-1'])

    def test_collision_reported(self):
        other = copy.deepcopy(self.e['pull_requests'][0])
        other['number'] = 2
        self.e['pull_requests'].append(other)
        self.assertEqual(build(self.e)['exact_path_collisions'][0]['prs'], [1, 2])

    def test_partial_snapshots_fail_closed(self):
        for flag in ('open_prs_complete', 'open_issues_complete', 'branches_complete'):
            e = copy.deepcopy(self.e)
            e[flag] = False
            with self.assertRaises(ValueError):
                build(e)

    def test_duplicate_and_unsafe_paths_fail(self):
        self.e['pull_requests'][0]['files'].append(dict(path='../secret', blob_sha='f'*40))
        with self.assertRaises(ValueError):
            build(self.e)

    def test_missing_record_is_refresh_not_deletion(self):
        before = build(self.e)
        self.e['pull_requests'] = []
        after = build(self.e, before)
        self.assertEqual(after['absent_since_previous'], ['pr-1'])
        self.assertIn('never infer', after['absence_policy'])

    def test_cache_requires_digest_time_and_head(self):
        report = build(self.e)
        now = datetime(2026, 10, 29, 17, 1, tzinfo=timezone.utc)
        self.assertTrue(cache_matches(report, self.e, now=now))
        self.assertFalse(cache_matches(report, self.e, now=now + timedelta(hours=1)))
        self.assertFalse(cache_matches(report, self.e, now=now - timedelta(hours=1)))
        changed = copy.deepcopy(self.e)
        changed['main_sha'] = 'e'*40
        self.assertFalse(cache_matches(report, changed, now=now))

    def test_missing_schema_never_invented(self):
        c = build(self.e)['capabilities'][0]
        self.assertIsNone(c['input_schema_version'])
        self.assertIsNone(c['invocation'])


if __name__ == '__main__':
    unittest.main()
