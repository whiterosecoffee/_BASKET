# CRWV reconciliation: usable facts before forecasts

B10 #91. Run from repository root, Python standard library:

```sh
python -m unittest discover -s research/CRWV/reconciliation/tests -v
python research/CRWV/reconciliation/audit.py --input research/CRWV/reconciliation/evidence/snapshot.json --as-of "$(cat research/CRWV/reconciliation/evidence/as-of.txt)" --output /tmp/crwv-reconciliation
```

The checked-in output was produced by this command with the recorded cutoff. Source
retrieval timestamps are conservative known-by bounds, not reconstructed original
publication times. The earlier November20 price/share reference is not refreshed
here. Use this as an audit packet, not current company fair value or live data.

## Resolved by evidence or arithmetic

- Historical independent CI blocker: PR90 f07763d now has successful run
  [40919835438](https://github.com/whiterosecoffee/_BASKET/actions/runs/40919835438).
  Logs show exact workflow f07763d, source7a33a6f, 39 tests, four demos. Neither
  PR90 nor PR87 is merged. This does not test this new reconciliation script.
- Q3 GAAP bridge: 207 - 846 + 13 - 83 = -709 (USD millions).
  Signed adjustments +160 SBC +12 acquired amortization -11 other +19 tax
  give -529 adjusted income. At559M weighted shares, calculated EPS is
  -1.268 GAAP versus -0.946 adjusted. Retain both branches; SBC stays in GAAP.
- Principal47.505B differs from carrying debt46.873B by0.632B discount/costs.
  Finance leases0.649B are separate; operating leases18.697B are a different EV
  convention. Restricted cash2.282B is not unrestricted parent cash.
- Reported total cash conservation:6.904 +1.975 -9.836 +7.361 =6.404B.
  Cash PPE purchases9.441B differ from total capex14.5B; do not substitute them.
- Operating cash1.975B includes2.127B deferred-revenue change. Removing only
  that change yields-0.152B as a mechanical sensitivity, not normalized cash flow.

## Corrected conclusions

The prior26.2x 2028 figure is only39.51 / a provider's1.51EPS. Its earnings basis
and matching forecast share denominator remain unverified. The audit returns a
null verified GAAP P/E while preserving this diagnostic division.
MarketScreener reports2028 EBIT9.220B and interest7.448B but EBT-0.5246B.
The unexplained difference is-2.2966B; 2027's difference is-1.823B. This may
reflect differing bases, other line items or provider inconsistency. It is not
evidence to assume those expenses away or to label one provider's forecast GAAP.

Expected9B deposits, available facility commitments and current cash are not
interchangeable. Current funding feasibility remains unknown until monthly uses,
eligible draws, deposit receipts, restrictions and covenants are supplied. No gap
amount is invented. The existing #86 synthetic unfunded fixture remains a test,
not the actual company's funding forecast.

Sources and exact numeric input identities are in evidence/snapshot.json. The
receiving main CRWV session should start with HANDOFF.md. Keep original estimates
and valuations as dated evidence; this packet qualifies their use rather than
silently rewriting historical conclusions.
