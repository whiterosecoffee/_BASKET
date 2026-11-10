# 01 Peer set and weights

Vector: who TARGET is compared against, and how much each peer counts. Runs first; every later vector reads its output.

## Inputs
- TARGET revenue mix by segment (B04 / issuer filings via Quartr). TTD: until the next filing.
- Candidate peers: Quartr related companies and GICS neighbors.
- Tickers: confirm each resolves in the iPhone Stocks app; flag any that do not (for example a foreign-exchange-only listing with no US ADR) and use the US-listed line.

## Default for ORCL (v0, uncalibrated)
Core peers, weighted median:
- IBM 25%: hybrid cloud, software, consulting, mainframe base; the named comparison.
- MSFT 25%: Azure, SQL and database, Dynamics, AI infrastructure.
- SAP 20%: ERP and applications, direct overlap with Fusion and NetSuite.
- AMZN 15%: AWS infrastructure and managed databases.
- GOOGL 15%: Google Cloud and AI infrastructure.

Overlay, shown separately and never in the median:
- CRWV: GPU neocloud; AI-infrastructure comp with a noisy multiple (evidence in `research/CRWV/**`, B10).

Optional swap-in:
- NOW: use only for the software-seat-shift thesis (incumbents converting to usage-based seats).

Not peers: NVDA is a supplier and sentiment benchmark (used in Range_Traversal divergence), not a valuation peer.

## Method for any new TARGET
1. Score each candidate by revenue-segment overlap with TARGET. Overlap score = sum over segments of (TARGET segment share x candidate segment share).
2. Take the top five as core peers. Weight proportional to overlap score, cap any single name at 30%, then renormalize.
3. Any candidate with negative NTM EPS, a pending merger, or an unstable multiple goes to overlay.
4. Print the weights and one line of reason per name.
5. Rebalance rule: recompute after each peer's earnings or when a segment share moves materially; record the date and reason.

## Output
- Peer list with weights summing to 100%, overlay list, rationale line per name, ticker resolution flags, data ages.

## Failure modes
- Weights set by familiarity, not overlap: require the overlap score to be shown.
- A peer with a different fiscal year: handled in vector 02 by calendarizing, not here.

## Open parameters
- Overlap segment taxonomy (database, applications, cloud infrastructure, AI compute, hybrid and consulting).
- Whether MSFT's OpenAI exposure and ORCL's OpenAI exposure should be flagged as a shared factor in vector 05.
