"""Independent assertions for real-function bridge rejection probes."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ownership_bridge_probe', HERE / 'bridge_probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
CORPUS = json.loads((HERE / 'bridge-cases.json').read_text())


class BridgeProbeTests(unittest.TestCase):
    def test_coverage_and_source_symbols(self):
        self.assertEqual({c['id'] for c in CORPUS['cases']}, {
            'readonly_write', 'outside_output', 'stale_token', 'expired_lease',
            'missing_lease', 'missing_attempt', 'wrong_attempt', 'resolved_attempt'})
        from orchestration.worker_bridge import bridge
        for case in CORPUS['cases']:
            self.assertTrue(callable(getattr(bridge, case['source_symbol'])))
        probe.pins()

    def test_deterministic_saved_report(self):
        first = probe.run()
        self.assertEqual(first, probe.run())
        self.assertEqual(first, json.loads((HERE / 'bridge-observed.json').read_text()))
        self.assertEqual((first['passed'], first['failed']), (8, 0))
        self.assertTrue(first['unchanged_sources'])

    def test_tripwire_control_reaches_first_effect(self):
        result = probe.observe('tripwire_control')
        self.assertEqual(result['observed_code'], 'effect_attempt:os.mkdir')
        self.assertEqual(result['effect_attempts'], ['os.mkdir'])
        self.assertTrue(result['output_absent'])
        self.assertTrue(result['inputs_unchanged'])

    def test_hook_recognizes_write_process_and_network_events(self):
        # Synthetic audit events verify detection without invoking these operations.
        for event, args in [('open', ('unused', 'w', 0)),
                            ('subprocess.Popen', ('unused', [], None, None)),
                            ('socket.connect', (None, ('example.invalid', 0)))]:
            with self.subTest(event=event):
                probe.ATTEMPTS.clear()
                probe.ACTIVE = True
                try:
                    with self.assertRaises(probe.EffectAttempt):
                        sys.audit(event, *args)
                finally:
                    probe.ACTIVE = False
                self.assertEqual(probe.ATTEMPTS, [event])


def negative_case(case):
    def test(self):
        result = probe.observe(case['id'])
        self.assertEqual(result['observed_code'], case['expected_code'])
        self.assertEqual(result['effect_attempts'], [])
        self.assertTrue(result['inputs_unchanged'])
        self.assertTrue(result['output_absent'])
    return test


for case in CORPUS['cases']:
    setattr(BridgeProbeTests, 'test_reject_' + case['id'], negative_case(case))

if __name__ == '__main__':
    unittest.main()
