# Review
Read parent protocol rather than copying it. Verify:
1. Source clock, expiry universe, metric, units and model settings match.
2. Expiry removal reconciles; unexplained residual stays unexplained.
3. Net exposure is not called volume/OI; OI growth is not called bullish flow.
4. No expired historical observation is used for current guidance.
5. Auction separation, matched-clock volume baseline and trade-condition gaps remain explicit.
6. Private data stays outside Git; use existing owner/resolver and no duplicate store.
7. Record actual checks and exact SHA; branch tests are not independent acceptance or deployment.

Observed execution lesson: recognizing the before/after expiry pair should precede generic cautions. The first response missed that relationship; later responses corrected it. Earlier raw minute pulls were not durably retained by this conversation. Do not call the original full objective complete until source retention and comparison acceptance are verified.
