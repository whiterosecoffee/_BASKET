"""Offline deterministic regression suite for B02 observation journal."""
import datetime as dt
import pathlib
import tempfile
import unittest

try:
    from runtime import observations as o
except ModuleNotFoundError:
    import observations as o


def sample(value=100, available="2026-10-15T21:00:00Z", supersedes=None):
    r = {
        "entity_id": "SFTBY", "kind": "daily_close", "source": "offline-fixture",
        "source_record_id": "SFTBY-2026-10-15", "observed_at": "2026-10-15T20:00:00Z",
        "available_at": available, "ingested_at": available, "currency": "USD",
        "value": value, "ttd_seconds": 3600, "venue": "OTC", "adjustment_basis": "split_adjusted",
    }
    if supersedes:
        r["supersedes"] = supersedes
    return r


class ObservationTests(unittest.TestCase):
    def test_revision_replay_and_deterministic_checkpoint(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "history.jsonl"
            old = o.append(p, sample())
            old_asof = "2026-10-15T21:30:00Z"
            before = o.snapshot(o.read_journal(p), old_asof)
            self.assertEqual(before, o.snapshot(o.read_journal(p), old_asof))
            correction = o.append(p, sample(102, "2026-10-16T12:00:00Z", old["record_id"]))
            rows = o.read_journal(p)
            self.assertEqual(len(rows), 2)
            self.assertEqual(o.replay(rows, old_asof)[0]["record_id"], old["record_id"])
            newer = o.replay(rows, "2026-10-16T13:00:00Z")
            self.assertEqual(newer[0]["record_id"], correction["record_id"])
            self.assertNotEqual(before["snapshot_sha256"],
                                o.snapshot(rows, "2026-10-16T13:00:00Z")["snapshot_sha256"])
            self.assertEqual(before, o.snapshot(rows, old_asof))
            with self.assertRaises(ValueError):
                o.append(p, sample())

    def test_unsafe_correction_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "journal"
            first = o.append(p, sample())
            with self.assertRaises(ValueError):
                o.append(p, sample(101, "2026-10-14T21:00:00Z", first["record_id"]))
            self.assertEqual(len(o.read_journal(p)), 1)

    def test_lock_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "journal"
            lock = pathlib.Path(str(p) + ".lock")
            lock.touch()
            with self.assertRaises(FileExistsError):
                o.append(p, sample())
            self.assertTrue(lock.exists())
            self.assertFalse(p.exists())

    def test_cross_feed_expiration(self):
        record = sample()
        record["record_id"] = o.digest(record)
        dep = {"expires_at": "2026-10-15T20:40:00Z"}
        self.assertEqual(o.state(record, "2026-10-15T20:30:00Z", [dep]), "unavailable")
        # Availability becomes true at 21:00; an expired FX dependency invalidates it.
        self.assertEqual(o.state(record, "2026-10-15T21:01:00Z", [dep]), "stale")
        self.assertEqual(o.state(record, "2026-10-15T21:01:00Z",
                                 [{"state": "conflicted", **dep}]), "conflicted")
        self.assertEqual(o.state(None, "2026-10-15T21:01:00Z"), "unavailable")

    def test_ambiguous_revision_is_conflict(self):
        a = sample()
        b = sample(101)
        a["record_id"] = o.digest(a)
        b["record_id"] = o.digest(b)
        with self.assertRaises(ValueError):
            o.replay([a, b], "2026-10-16T00:00:00Z")

    def test_no_live_claim_without_worker_and_entitlement(self):
        self.assertEqual(o.adapter_access(), "unavailable")
        self.assertEqual(o.adapter_access(entitled=True), "unavailable")


if __name__ == "__main__":
    unittest.main()
