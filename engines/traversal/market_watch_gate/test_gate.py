import unittest
from gate import qualify

BASE = {
    "event_id": "QQQ:2026-11-04:episode7:break",
    "confirmed": True, "material": True, "session": "regular",
    "source_verified": True, "data_conflict": False, "market_open": True,
    "event_at": "2026-11-04T15:59:00Z",
    "available_at": "2026-11-04T15:59:01Z",
    "evidence_ids": ["bar:1", "bar:2"],
    "requires_cross_asset": True, "cross_asset_synchronized": True,
}


def check(**overrides):
    return qualify({**BASE, **overrides}, prior_event_id=None,
                   cutoff="2026-11-04T16:00:00Z", max_lag_seconds=90)


class GateTests(unittest.TestCase):
    def test_confirmed_fresh_event(self):
        self.assertEqual(check()["reason_codes"], ["qualified"])
        self.assertTrue(check()["notify"])

    def test_duplicate(self):
        result = qualify(BASE, prior_event_id=BASE["event_id"],
                         cutoff="2026-11-04T16:00:00Z", max_lag_seconds=90)
        self.assertEqual(result["reason_codes"], ["duplicate_event"])

    def test_stale(self):
        self.assertIn("stale_event", check(event_at="2026-11-04T15:55:00Z",
                      available_at="2026-11-04T15:55:01Z")["reason_codes"])

    def test_rejects_unconfirmed_and_immaterial(self):
        self.assertEqual(check(confirmed=False, material=False)["reason_codes"],
                         ["unconfirmed", "immaterial"])

    def test_rejects_unsynchronized_multiasset(self):
        self.assertIn("unsynchronized_context",
                      check(cross_asset_synchronized=False)["reason_codes"])

    def test_rejects_conflicted_quote(self):
        self.assertIn("conflicted_or_unknown", check(data_conflict=True)["reason_codes"])

    def test_rejects_closed_market_noise(self):
        self.assertIn("closed_session",
                      check(session="after_hours", market_open=False,
                            material_after_hours=False)["reason_codes"])

    def test_rejects_afterhours_without_materiality_even_if_market_open(self):
        self.assertIn("no_material_after_hours", check(session="after_hours", market_open=True, material_after_hours=False)["reason_codes"])

    def test_rejects_closed_regular_market(self):
        self.assertIn("closed_session", check(market_open=False)["reason_codes"])

    def test_allows_qualified_material_afterhours(self):
        self.assertTrue(check(session="after_hours", market_open=False,
                              material_after_hours=True)["notify"])

    def test_rejects_future_availability(self):
        self.assertIn("invalid_temporal_order",
                      check(available_at="2026-11-04T16:00:01Z")["reason_codes"])

    def test_rejects_missing_tz(self):
        self.assertIn("missing_or_invalid_timestamp",
                      check(event_at="2026-11-04T15:59:00")["reason_codes"])

    def test_rejects_missing_evidence(self):
        self.assertIn("missing_evidence", check(evidence_ids=[])["reason_codes"])

    def test_rejects_invalid_ttl(self):
        result = qualify(BASE, prior_event_id=None, cutoff="2026-11-04T16:00:00Z",
                         max_lag_seconds=-1)
        self.assertIn("invalid_lag_policy", result["reason_codes"])

    def test_rejects_bad_event_input(self):
        self.assertFalse(qualify(None, prior_event_id=None,
                                cutoff="2026-11-04T16:00:00Z",
                                max_lag_seconds=90)["notify"])


if __name__ == "__main__":
    unittest.main()
