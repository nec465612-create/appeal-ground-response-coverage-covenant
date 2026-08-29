# Appeal Ground Response Coverage Covenant

Standalone GenLayer Intelligent Contract for a revision-bound, consensus-validated coverage receipt over a locked appeal-ground set. It answers only whether the submitted final response materially addresses every locked ground; it does not decide legal merits or legal compliance.

## API

Writes: `file_appeal`, `lock_grounds`, `submit_response`, `assess_coverage`, `correct_response`, `close_case`.

Deterministic view: `read_case` exposes lifecycle, actors, ground IDs, current response revision, append-only revision history, normalized decision fields, omitted grounds, bounded explanation/references, evidence digest and `closure_ready`.

## Consensus engineering

One `run_nondet_unsafe` execution per assessment. Leader and validators independently fetch the same three digest-bound public texts and compare every consequence-bearing normalized field, including each ground result. Storage writes happen after consensus. Failures are fail-closed and cannot set `closure_ready`.

## Verification

```powershell
genvm-lint check contracts/appeal_ground_response_coverage_covenant.py
python -m pytest tests/direct tests/integration -q
```

The final Studionet deployment address, transaction links, exact source hash and E2E receipts will be added only after PRE-DEPLOY approval and successful E2E execution on the exact deployed revision.

## Reuse and limits

The reusable primitive is an argument-set-to-response coverage receipt for downstream case-closure workflows. It performs no payment, access grant, legal determination, external actuation, cross-contract call or private-data processing.
