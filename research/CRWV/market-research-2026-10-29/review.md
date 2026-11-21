# Review of the November19 update

The pre-release benchmark is resolved with Q3 issuer results, the November12 10-Q and the earnings-call transcript. Source timestamps and availability are retained where returned. Unknown retrieval/ingestion instants remain null.

Independent local checks read the saved JSON and CSV transport captures. They verify the current trade against its snapshot, all298 completed one-minute rows for ordering, numeric/OHLC validity and same exchange-local date, hash equality, cash/debt sums, Q4 guidance subtraction, scenario earnings formulas and null P/E for losses. Snapshot cumulative volume differs from the aggregate sum. The report uses the aggregate sum with eligibility/coverage limits. Thirteen vendor VWAP anomalies remain as supplied.

The first report draft was reviewed for inappropriate precision. Per-source observation times not provided by the tools were reset to null. Quote timestamps remain provider observations. Source declarations and explicit availability are distinct. The local pointer check first failed because the earlier November10 report existed only in the remote branch. Materializing its exact fetched bytes resolved that missing local input and the pointer check passed.

The previous summary's blanket pending-B02 wording was stale. Issue186 now contains B02 qualified historical byte acceptance, followed by explicit-input minute-consumer verification in PR197. Canonical routing and the B01 source gate remain external work. The report links the receiver evidence and pins the reviewed source SHA.

Useful outcome is the funding-sensitive earnings hurdle at a dated market price. Quarter-end balances and October30 shares are still dated inputs. Post-quarter cash, live bond spreads, actual billable MW, realized customer deposits, later equity issuance and fully diluted shares remain unresolved. The 2028 model inputs are assumptions. The monthly funding gap is unresolved.

Validate this update by reloading post-earnings-price-review-2026-11-19.json and checking the formulas in feature-design.md against its source fields. Reconcile next actual receipt/draw and billing evidence, then rerun the same sequence. Persist input hashes and final Git commit in the issue resolution. GitHub shared CI and independent financial/source acceptance have separate meanings.
