# Studionet E2E matrix

All scenarios must run on the exact PRE-DEPLOY-approved revision and have FINALIZED receipt, result, consensus evidence, authoritative readback and Explorer URL before E2E PASS.

| ID | Scenario | Expected state/result | Dependency / safe continuation |
|---|---|---|---|
| AGRCC-01 | File, lock, submit, deterministic read | RESPONSE_SUBMITTED; exact IDs/revision read back | Independent setup; run first |
| AGRCC-02 | Fully covered response assessment and close | assessment SUCCESS -> COVERED -> CLOSED; closure_ready true | Requires AGRCC-01 state |
| AGRCC-03 | Omitted ground counterexample | assessment SUCCESS -> GAPS_FOUND; closure_ready false; close ERROR and unchanged state | Requires clean independent case |
| AGRCC-04 | Correct response, reassess and close | CORRECTED -> reassessment SUCCESS -> COVERED -> CLOSED | Requires AGRCC-03; run on isolated case |
| AGRCC-05 | Unauthorized write and invalid transition | FINALIZED expected ERROR; state unchanged | Independent negative case |
| AGRCC-06 | Digest mismatch / unavailable evidence | FINALIZED expected ERROR; no accepted assessment | Independent negative case |

## RPC Quota Efficiency Plan

Run local lint/direct/validator checks before any transaction. Deploy once after dual PRE-DEPLOY approval. Use isolated appeal IDs so independent negative cases can continue after a failure. Use bounded polling with exponential backoff and stop at finality. Reuse read-only evidence from the same exact transaction where valid; do not repeat deploys, writes or readbacks. No scenario or required receipt is omitted to save quota.

## Failure harvesting

If an E2E failure occurs, freeze the deployed revision, record failure ID, tx/receipt/result/readback, continue only safe independent scenarios, mark dependent scenarios `BLOCKED BY <FAILURE ID>`, batch root causes, fix once, rerun local regression and dual PRE-DEPLOY, deploy once, then rerun the full matrix.
