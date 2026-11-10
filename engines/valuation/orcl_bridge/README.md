# ORCL valuation bridge

Executable B04-owned calculation component, scoped by B00 in #75 and linked to
#76/#80. It implements calculations and a tracker publisher; it does not claim that
consensus feeds, ORCL data-plane ingestion or deployment already exist.

## Outputs

- Annual forward EPS and operating margin; modeled unlevered FCFF and equity free
  cash flow before net borrowing; enterprise value and net financial obligations.
- Separate P/E, EV/EBITDA, EV/sales, price/equity FCF and EV/FCFF peer comparisons,
  weighted medians/means, coverage and exclusions. No blend of unlike raw ratios.
- Each fully covered comparable metric's implied USD price and difference from
  the input quote. These are current forward-multiple indications, not dated targets.
- Reverse checks: EPS and EBITDA margin required at peer reference multiples,
  with gaps versus the input forecast.
- Bear/base/bull scenarios: explicit revenue, margin, D&A, capex, working-capital,
  interest and dilution changes; separate implied prices for each declared method.
- A mechanical +/-50/100bp rate grid on declared floating, refinancing and new-debt exposure; fixed debt remains unchanged.
- Exact EPS change attribution: earnings change at old shares plus dilution impact.
- Input hash, engine version, timestamps, provenance IDs, missing-data reasons,
  scenario rationale and falsifiers. No invented probability, rank or confidence score.

## Run

```sh
python -m engines.valuation.orcl_bridge.engine /data/valuation-input.json --as-of 2026-10-26T14:00:00Z
python -m orchestration.ticker_trackers.publish_valuation --db /durable/data/orcl.sqlite
python -m orchestration.ticker_trackers.tracker --db /durable/data/orcl.sqlite html > /data/orcl.html
python -m unittest engines.valuation.orcl_bridge.test_engine orchestration.ticker_trackers.test_tracker orchestration.ticker_trackers.test_valuation -v
```

`example.fixture(as_of)` produces a fully synthetic, deliberately small model for
replay/testing. The names ORCL/IBM/MSFT in that fixture do not make any of its numbers
real. Synthetic outputs always have `eligible=false`; the dashboard explicitly
marks them SYNTHETIC and keeps the production valuation refresh item open.

## Input contract

`basket.valuation_input@1`: `data_mode` (`synthetic` or `source_backed`), `target`,
`peer_weights` (positive, sum exactly to 1 within numeric tolerance), `companies`,
`scenarios` (bear/base/bull). `example.py` is the complete executable shape example.
Source-backed status is an upstream assertion: this engine checks timestamps,
source presence and math, not the contents of an issuer/consensus website.

Each company has ticker, USD currency, and quote/forecast/balance evidence records.
Each record supplies source_id, HTTPS sources, effective_at, observed_at,
available_at, ingested_at, expires_at, verification, classification and data.
No input may be first available or ingested after the analysis timestamp. Expired
or unverified target input blocks all target valuations; invalid peers are excluded
with original weight disclosed. Quotes have a five-minute age cap on observation
AND effective trade time. Forecast/balance review caps are one day; their historical
period is retained separately. Source adapters must not reset review times without
checking for intervening filings/estimate revisions.

Forecast data: horizon_start/end, earnings_basis (GAAP or normalized), explicit
reconciliation for normalized inputs, lease_basis (`included_consistent`), revenue,
EBIT, D&A (`da`), capex, delta_nwc, cash_interest, tax_rate, diluted_shares. All USD
figures are dollars, share counts are individual shares, and rates are fractions.
A horizon starts on the as-of UTC date and spans roughly one year (350–380 days);
all peers must have **identical** endpoints and earnings/lease bases. The daily
horizon requirement intentionally forces source refresh rather than relabeling a
fixed fiscal year as NTM. Quarterly interpolation/seasonality estimation belongs to
upstream forecast producers. This engine does not annualize one reported quarter.

Balance data: debt, cash, leases, preferred, minority. Quote data: price. Shares are
forward diluted shares; consequently market cap/EV here are *forward diluted*
valuation measures rather than quoted basic-share market capitalization.

## Equations and economic assumptions

```text
pretax = EBIT - cash interest
net income = pretax - max(pretax, 0) * tax rate
EPS = net income / diluted shares
EBITDA = EBIT + D&A
FCFF = EBIT - max(EBIT, 0) * tax rate + D&A - capex - change in NWC
equity FCF before net borrowing = net income + D&A - capex - change in NWC
net obligations = debt + leases + preferred + minority - cash
EV = price * diluted shares + net obligations
peer EV-derived price = max(0, peer multiple * forward denominator - net obligations) / shares
```

This is a simplified normalized model: no automatic tax refund on losses, other
income, preferred dividend or minority earnings adjustment. Producers must reconcile
those into appropriate common-equity EBIT/interest inputs or flag the model unsuitable.
Debt/lease treatment must be disjoint and consistent with lease-adjusted earnings;
adding lease liabilities while leaving lease costs in an incompatible EBITDA is invalid.
A label alone does not independently verify an accounting reconciliation.

Negative income/FCF or nonpositive EV gives an unavailable corresponding multiple,
never an attractive negative P/E. Negative cash flow remains visible. A partial peer
median is displayed as provisional; its implied price is suppressed. Missing weight
is never silently redistributed. Peer/target quotes must be within 120 seconds.
Cash flows must be compared with matched equity or enterprise values. No PEG or
sales/growth blend is used. No growth capex is silently removed to improve FCF.

## Financing and dilution scenarios

Every scenario supplies rationale, falsifiers, revenue_change (fraction),
margin_change (absolute margin fraction), capex_change/delta_nwc_change/da_change
(USD), new_debt, new_debt_rate, new_debt_year_fraction, equity_raise, issue_price,
additional_shares, retained_funding_cash, repricing tranches and five multiples
(each positive or explicitly null).

A repricing tranche has a unique tranche_id, kind (fixed/floating/refinancing),
principal, old_rate, new_rate and year_fraction. All existing-debt tranches must be
disjoint; aggregate principal cannot exceed balance-sheet debt. Fixed debt cannot
change coupon unless classified as refinancing. New-debt interest is incremental;
all scenario changes must be **absent from the baseline forecast**, or they would
be double counted. Fraction-of-year interest reflects the expected exposure period.

New equity shares = equity_raise / issue_price. Additional shares are incremental
SBC/other dilution. Share additions are treated as present for the entire forward
period; mid-period issuance timing requires a richer upstream weighted-share model.
Retained funding cash cannot exceed new debt plus equity proceeds. It reduces net
obligations, while new debt increases them; shares separately dilute equity value.
Do not add retained funding to FCF. Future cash-burn/FCF accumulation is not rolled
into the balance automatically: this is a static forward-multiple bridge, not a DCF.

## Tracker connection

The publisher reads eligible market, fundamentals and financing revisions from the
existing SQLite ledger. Market data supplies `last_usd`; financing supplies `balance`
as described above. Fundamentals supplies `forecast`, `peers` (full company evidence
records), `peer_weights`, `scenarios`, `data_mode`. Source envelopes are transformed
into valuation evidence with original timestamps and IDs. The publisher cannot reset
the upstream clock. It records every consumed top-level revision as a dependency.

The valuation panel is always conditional. It is never moved into `current_data` as
an observed quote. Fresh conditional results appear under `conditional_data`; expired,
superseded or disputed dependencies hide them. Synthetic and incomplete runs remain
on the refresh queue. Input corrections require recalculation. Publisher replays of
identical still-valid inputs reuse the existing revision, rather than adding noise.
The earliest input deadline also caps the valuation, including nested peer evidence.

## Remaining real-data work

The engine is functional with validated inputs, and its ledger/dashboard connection
is tested. Production population still needs ORCL and comparable-peer NTM estimates,
reconciled accounting/lease bases, current prices and debt terms from the domain
producers in #76. A reported FY27 EPS guidance number is not itself an NTM consensus
forecast. Existing ORCL research specifications in #83–#85 remain untouched.
