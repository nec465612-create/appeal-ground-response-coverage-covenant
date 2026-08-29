# STAGE 1 — Project Intake và GenLayer-Fit Validation

## Objective and trust problem
Verify that one final institutional response materially addresses every ground in one locked appeal.

Trust problem: A response can appear complete while omitting or evading individual appeal grounds.

## Intended users and downstream integrations
Appellant, responding authority, downstream case-closure system. Downstream integrations consume deterministic read methods and the `closure_ready` signal only.

## Required scope
One small Intelligent Contract; 3 actors; one bounded assessment transaction; immutable evidence revision binding; explicit lifecycle; deterministic readback; one independently validated consequential field.

## Out of scope
Frontend, payments, tokens, cross-contract calls, hidden databases, external orchestration, real-world actuation, private/sensitive data, legal/medical/scientific truth guarantees, and any mechanism not confirmed by current official GenLayer documentation.

## GenLayer fit
GenLayer is necessary because the core decision requires semantic interpretation of unstructured, revision-bound evidence that deterministic code alone cannot reliably resolve. Ordinary deterministic checks handle identity, bounds, lifecycle, hashes, and post-consensus consequences.

## Why nondeterministic consensus is necessary
A leader must extract ground_identity_match, disposition_present, reason_relevant, omitted_ground_ids from the evidence; validators independently re-fetch/re-derive those same consequence-bearing fields. Majority acceptance creates a neutral receipt where no single submitter, administrator, or model controls the result.

## Evidence boundary
Original decision, appeal grounds, final response, exact hashes/revisions. Evidence is public or public-safe, bounded, immutable by hash/revision after locking, and treated as untrusted data. No hidden account, private document, mutable screenshot, or uncited model knowledge may determine the outcome.

## Reusable primitive
Argument-set-to-response coverage receipt.

## Originality and differentiation
Closest existing material: Consultation-fidelity, dispute, and consistency projects.

Overlap: semantic evidence interpretation, consensus-bound normalized decisions, and persistent lifecycle receipts.

Material difference: Exhaustive locked argument-set coverage and correction-to-closure lifecycle; no merits adjudication, persuasion, source scoring, or content selection.

## Actors
Appellant, responding authority, downstream case-closure system. Actor count: 3. Authority is limited to submission, locking, acknowledgement/correction, or deterministic downstream reading; no actor can inject the verdict.

## State machine and transitions
FILED may become GROUNDS_LOCKED; GROUNDS_LOCKED may become RESPONSE_SUBMITTED. RESPONSE_SUBMITTED may become COVERED, GAPS_FOUND, or UNRESOLVED. Only GAPS_FOUND or UNRESOLVED may become CORRECTED and be reassessed. COVERED may become CLOSED directly; a corrected response must be reassessed to COVERED before CLOSED. CLOSED is terminal.

## Contract surface/public methods
file_appeal, lock_grounds, submit_response, assess_coverage, correct_response, close_case, read_case.

## Storage data
Record owner/authorized actors, lifecycle enum, exact evidence URLs/hashes/revisions, bounded evidence IDs, assessment version, normalized decision fields, bounded reason/references, timestamps/counters where deterministic, and `closure_ready`. Use documented typed storage only.

## Decision and consequential fields
Decision fields: ground_identity_match, disposition_present, reason_relevant, omitted_ground_ids. Consequential field: `closure_ready`. Explanations are non-authoritative and cannot alter state.

## Validator-state binding feasibility
High. Validators compare a finite schema of enums, booleans, bounded masks/counts/IDs, and evidence digest. Accepted fields map through a fixed deterministic rule to the consequential state. Disagreement or malformed output cannot commit an approving state.

## Nondeterministic/consensus flow
Exactly one nondeterministic consensus execution per assessment write. Fetch/extract/semantic comparison occurs inside the documented leader/validator wrapper. Storage reads needed by the assessment are copied to memory before entry. Contract calls, events, storage writes, and consequential computation occur outside the nondeterministic block.

## Validator-verifiable evidence
Validators can independently retrieve or inspect Original decision, appeal grounds, final response, exact hashes/revisions. They verify exact revision identity, substance of each decision field, evidence digest, and boundary compliance; they do not validate only response syntax.

## Workflow
File appeal → lock grounds → submit response → assess per-ground coverage → correct only GAPS_FOUND/UNRESOLVED responses → reassess to COVERED → close only a COVERED case.

## Downstream integration/reuse pattern
Any builder can read `closure_ready` plus decision version/evidence digest as a fail-closed gate in an off-chain workflow. No integration must trust explanatory prose.

## Edge cases
Missing/malformed evidence, identity mismatch, duplicate ID, stale or changed revision, unauthorized sender, invalid transition, oversized input, conflicting sources, ambiguous text, timeout, unavailable URL, malformed model output, validator disagreement, duplicate/replay action, correction after terminal state.

## Risks
Primary risks are semantic disagreement, mutable web sources, storage serialization, prompt injection, overclaiming authority, RPC quota, and an incomplete negative matrix. Controls are exact hashes, bounded inputs/outputs, typed storage, independent validator substance checks, one nondeterministic call, fail-closed outcomes, and explicit limitations.

## Complexity and feasibility
One contract; 3 actors; one nondeterministic call per assessment; dependencies limited to current `genlayer-py`/`genlayer-test`. 4 integration tests: file/lock/submit/read; covered response closes; gap correction reassesses then closes; unresolved cannot close. Studionet feasibility is high because there is no cross-contract call, payment, browser automation, EVM dependency, graph, or unbounded batch.

## Duplicate/lightweight/learning-exercise risk
The project is acceptable only while preserving the material difference above and the consequential lifecycle. It becomes duplicate/lightweight if reduced to a generic LLM label, if only names/fields change, if the consequential field is not validator-bound, or if removed speculative orchestration is reintroduced.

## Conclusion
**KEEP — research/specification approved baseline.** This conclusion is bound to this exact Stage 1/2 scope and must be re-reviewed if the trust problem, mechanism, evidence pair, decision vector, lifecycle, API, or consequence changes materially.
