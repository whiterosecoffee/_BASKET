# Exact-source daily-history acceptance and consumer composition

Parent method: ../../architecture/COMPONENT_QUICKSTART.md at state.json's main
revision. Existing pattern/specimen was inspected; this node is a small offline
composition, not a replacement framework, schema or data store.

## Purpose and boundary

Input: explicit immutable source commit and clean checkout containing PR122's
four retained input JSONL files and metadata. Output: JSON integrity evidence
with 22 reconstructed October partitions and three November daily snapshots.
`audit.run(root, expected_source)` defaults to the original frozen revision for
backward compatibility. CLI --expected-source allows deliberate review of a new
revision, still requiring a full40-character SHA, matching HEAD and clean bytes.
Old evidence.json is immutable historical output; evidence-current.json records
the refreshed candidate. No filename/date means 'live' or 'canonical accepted'.

The existing B10 splitter performs staging. This node independently verifies
row shape, ET date, hashes, counts, lineage, anomalies, byte reconstruction and
unchanged replay. It does not implement another splitter/writer. Dates here are
US equity local dates; no futures overnight-session generalization is assumed.
Unknown retrieval/first availability remains unknown; end-of-bar arithmetic is
not proof of publication. Original CSV unavailable: preserve that source limit.

## Child: existing minute-consumer probe

Input: successful source audit, exact reviewed main checkout and its existing
engines/traversal/metrics.py. Output: one metadata-only result per observed date,
listing input hash, regular-row count, available horizons and failure checks.
Uses the existing evaluate function and its5/15/60/390minute definitions; no
copied calculation or new read path. Every date is checked for deterministic
repeat, last-bar completion rejection and a missing interior minute returning
null. Source arrays stay private/local; only hashes/counts/booleans are emitted.

RTH selection09:30–16:00 ET is scoped to October1–November4 dates represented
here, not an exchange-calendar implementation. October30 has160regular rows:
5/15/60minute windows exist,390minute window is unavailable. November4 has390
regular rows but its extended session remains partial through17:43ET.

## Alternatives and limits

- Reuse main metrics: selected; directly accepts existing arrays and checks gaps.
- Modify old range.py CLI or resample into5m: unnecessary for explicit-input use;
  canonical discovery still needs its owner and approved routing.
- Copy source bars into this node: rejected; duplicates source/data ownership.
- Relax HEAD checks after source advancement: rejected; explicit pin plus clean
  bytes preserves exact-source identity. This solves repinning, not auto-approval.
- Extend existing B01 named domain gate: next owner action, not implemented here.
  Main gate currently lacks CRWV minute-history suite/path selection. Dispatching
  its other suites would not qualify this node.

Prior-art mechanisms: content-addressed manifests detect source changes; immutable
snapshots preserve revision history; explicit adapter composition reuses a tested
consumer; deterministic replay and negative probes expose gaps without inventing
observations. Hash integrity cannot establish vendor accuracy or availability.
