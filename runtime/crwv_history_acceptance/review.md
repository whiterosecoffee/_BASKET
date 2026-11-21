# Resumed review — current evidence in state.json

Observed failure: previous audit assumed PR122 would remain at827dd1e; current
head c575f0f adds an earnings report, with original20files unchanged. Its default
failure was intentional pin protection but made the receiver instructions stale.
Minimal correction: allow an explicitly reviewed full source SHA, retain original
default/evidence and dirty-source guard. Test malformed pins and wrong checkout.

Another stale finding was 'existing tools require reader integration'. Main now
includes metrics.py/run_metrics.py accepting explicit1m arrays. A25-date probe
proves descriptive compatibility while leaving canonical discovery unverified.
The first probe attempt used the wrong output key 'horizons' and failed with
KeyError; inspected actual return contract, corrected to 'windows', reran all25
cases successfully. No failed run was counted as passing.

Current scope:8audit tests +6original source tests pass. Source audit reports21844
records,22October shard hashes,3November files,2563retained anomalies,zero replay
changes.25consumer cases each repeat identically, reject incomplete last bars
and return null on an intentionally missing last-window minute. October30's
390minute window remains unavailable. These are local execution results.

Unfinished: B00 canonical target/path allocation; B01 independent minute-domain
CI; original CSV retrieval and historical availability; canonical adoption and
operational/restart qualification. No receiving worker or DOT receipt verified.
The prior #6 handoff targeted a completed generic CI issue. Reuse the current
B01 named source-gate owner #214 rather than pretend that comment dispatched work.

Next decision is concrete: B00 must identify one approved CRWV data target and
PR122 path-update owner; B01 adds this exact-source composition to its existing
gate after reviewing inputs. No need to create another queue, engine or history.


## 2026-11-21 transport recovery

Recovered the existing private capture archive through its published binding.
Both original transport CSV hashes match that binding; October also matches
PR122 capture metadata. Existing backfill code reproduced all25daily JSONL
partitions (21,844rows) exactly, with zero duplicate rows and unchanged replay.
All2,563vendor VWAP anomalies remain. No private source bytes were published.
The older audit's unavailable-CSV limitation is resolved by this separate proof;
unknown original retrieval/first availability and provider truth remain unknown.

PR122 source reviewed at4151d3f75570f7ab5828c6ccd60bb9994c891bb1.
Consumer evidence remains pinned to main74d913; it is not a claim about newer main.
Existing FETCH writer authority and _MASSIVE adoption were inspected: no bound
request route or confirmed connected host was supplied. Canonical target and
independent B01 exact-head acceptance remain blockers; no merge performed.
