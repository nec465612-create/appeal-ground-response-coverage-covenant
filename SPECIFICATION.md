# Appeal Ground Response Coverage Covenant

## Purpose

This standalone GenLayer Intelligent Contract records whether one locked set of appeal grounds is materially addressed by one final institutional response. It is a coverage receipt, not a legal merits decision, a finding that a response is lawful, or a guarantee of truth.

## Locked model

An appellant files one bounded public-safe original decision and grounds set. The appellant locks the grounds. The responding authority submits a bounded public response revision. `assess_coverage` performs exactly one consensus execution. The contract stores only the accepted normalized decision and derives `closure_ready` deterministically. An incomplete response can be corrected and reassessed. Only a reassessed `COVERED` response can close.

## Lifecycle and permissions

`FILED -> GROUNDS_LOCKED -> RESPONSE_SUBMITTED -> COVERED | GAPS_FOUND | UNRESOLVED -> CORRECTED -> RESPONSE_SUBMITTED -> ...`; `COVERED -> CLOSED`. The appellant owns filing/locking/closing; the responding authority submits/corrects; the downstream reader has no write authority. `CLOSED` is terminal.

## Evidence and consensus binding

Original decision, grounds, and response are HTTPS text bounded to 8,000 characters and bound by SHA-256. Their URLs, hashes and revision are copied to memory before nondeterministic execution. Response revisions are append-only in `revision_history`; correction updates the current pointer only after preserving the prior revision. The leader and each validator independently fetch all three bodies, evaluate every ground, and compare the exact normalized vector: aggregate booleans, omitted IDs, per-ground results, revision and evidence digest. Storage mutation occurs only after accepted consensus. No raw page body is stored.

Evidence is untrusted data. The fixed prompt delimits each evidence block and explicitly rejects instructions inside evidence. Silence is not coverage. Malformed JSON, extra keys, invalid IDs, changed digests, retrieval failure or validator disagreement fails closed.

## Consequence

`closure_ready` is true only when all three aggregate fields are true and `omitted_ground_ids` is empty. The aggregate fields are required to be true for every ground, and the validator-bound per-ground vector is persisted for audit. Explanatory reason and references are bounded and non-authoritative.

## Limitations

The contract cannot determine legal adequacy, truth, fairness or enforce a real-world appeal outcome. Public evidence must remain available and hash-stable. Semantic consensus can fail closed. Downstream systems must consume `read_case` and treat `closure_ready` as a fail-closed workflow signal only.
