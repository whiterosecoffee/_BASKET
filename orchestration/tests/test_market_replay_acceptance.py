"""Run existing B02 acceptance tests through required orchestration discovery.

B00 discovery only: domain assertions remain owned by B02. No provider calls,
data writes, duplicated test fixtures or B01 workflow changes.
"""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    ("tests/test_ttd.py", "basket_b02_ttd_acceptance", {
        "TTDTests.test_expiration",
        "TTDTests.test_dependency_expires_first",
        "TTDTests.test_missing",
        "TTDTests.test_future_invalid",
    }),
    ("runtime/test_observations.py", "basket_b02_observation_acceptance", {
        "ObservationTests.test_revision_replay_and_deterministic_checkpoint",
        "ObservationTests.test_unsafe_correction_rejected",
        "ObservationTests.test_lock_fails_closed",
        "ObservationTests.test_cross_feed_expiration",
        "ObservationTests.test_ambiguous_revision_is_conflict",
        "ObservationTests.test_no_live_claim_without_worker_and_entitlement",
    }),
)


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def load_tests(loader, tests, pattern):
    accepted = unittest.TestSuite()
    for relative_path, module_name, required in SOURCES:
        spec = importlib.util.spec_from_file_location(module_name, ROOT / relative_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite = loader.loadTestsFromModule(module)
        discovered = list(cases(suite))
        identities = {
            type(case).__name__ + "." + case._testMethodName
            for case in discovered
        }
        if not required <= identities:
            missing = ", ".join(sorted(required - identities))
            raise RuntimeError(relative_path + ": missing acceptance cases: " + missing)
        if len(identities) != len(discovered):
            raise RuntimeError(relative_path + ": duplicate acceptance cases")
        for case in discovered:
            method = getattr(case, case._testMethodName)
            if any(
                getattr(target, flag, False)
                for target in (type(case), method)
                for flag in ("__unittest_skip__", "__unittest_expecting_failure__")
            ):
                raise RuntimeError(relative_path + ": skipped/expected-failure acceptance")
        accepted.addTests(suite)
    return accepted
