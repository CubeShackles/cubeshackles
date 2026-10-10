# Wave 0 / Wave 1 — Exact Implementation Plan

**Status:** PROPOSED. Not authorized for implementation. No code has been changed. This document exists to be approved or amended, not executed.

## Wave 0 — decisions only, zero code changes

1. **Money ownership**: founder decides whether to land `cubeshackles-institutional-gateway` PR #4 (currently CONFLICTING) as-is, resolve its conflicts, or supersede it with a fresh PR. Until this lands, no Money convergence work can proceed anywhere else — ledger's and settlement-engine's own draft PR copies are waiting on the same resolution.
2. **CIEL Family A/B merge decision**: founder decides whether ledger/cubereg's deliberate second schema family should be merged into the primary (node-api/Core) family, or formally recognized as a separate, intentional institutional-ledger-event namespace.
3. **`cubeshackles-ciel` repo's status**: founder decides whether its 6-event registry is still intended to become real, or whether `REPOSITORY_MAP.md` §15 should be corrected to stop naming it canonical, given its own milestone date has passed and zero runtime code connects to it.
4. **Contracts ownership** (per `CONVERGENCE_ANALYSIS.md` §1, re-confirmed this round with a larger real consumer count — 236 imports across 9 repos — but still built on CI-sibling-checkout/undeclared-dependency mechanics): founder decides which of the three "contracts" artifacts (standalone `cubeshackles-contracts` repo, Core's `cubeshackles.contracts` package, Core's `contracts/ontology` subpackage) is meant to become the real, declared, versioned dependency, given real code has already organically converged on Core's package without anyone declaring it so.

None of these require a line of code. All of Wave 1 below is blocked on none of them except where noted.

## Wave 1 — the exact first implementation PR (once authorized)

### Target repo: `cubeshackles-settlement-engine`

**Why this repo, not a Money/Institution pilot**: because the single highest-severity, already-disclosed, already-tracked gap in the entire org is here, and both halves of the fix (`require_clearing_approval`, `require_compliance_before_clearing`) are **already real, tested code** — this PR adds a call, not new logic. It requires no Wave 0 decision to be made first (Money/CIEL/Contracts ownership is irrelevant to this fix). It directly executes the smallest PR the original census identified in point 24, now re-confirmed by independent adversarial verification.

### Exact change

In `src/settlement/settlement_authority_gateway.py`'s `settle()` method (and/or `src/settlement_service/rc2a_router.py`'s `rc2a_settle()` handler — exact insertion point to be confirmed against the live call graph at implementation time, since the verification pass traced `settle()` → `SettlementLifecycle.process_validation_event()` as the real live chain):

1. Before `SettlementLifecycle.process_validation_event()` is allowed to return `"settle"`, call `require_clearing_approval()` (already defined, already tested, in `src/settlement_engine/clearing_gate.py`) against the transaction's clearing-eligibility data.
2. Separately or in combination, call `require_compliance_before_clearing()` — this lives in `cubeshackles-compliance-engine`, a DIFFERENT repo, currently only reachable via its own HTTP endpoint (`POST /api/v1/compliance/clearing-gate`), not an in-process import. This means the fix has two sub-options:
   - **2a (lower risk, smaller PR)**: settlement-engine makes a real HTTP call to compliance-engine's existing endpoint before settling — this requires zero new logic in compliance-engine, only a new outbound client in settlement-engine (mirroring the pattern already used for `ledger_http_client.py` in the institutional pipeline).
   - **2b (larger PR)**: vendor/import compliance-engine's gate logic in-process — NOT recommended, since it would duplicate logic across repos, which is exactly the pattern this whole program exists to reduce.
   - **Recommendation: 2a.**
3. `DeterministicSettlementPolicy.evaluate()` must also be changed to read `validation_decision`, not just `event_type` — confirmed via verification that this field is currently parsed and stored but never checked. This is a one-line conditional addition, not a redesign.
4. The RC2A router's hardcoded `"validation_decision": "APPROVED"` (`src/settlement_service/rc2a_router.py`) must either be replaced with a real upstream check, or — if no real validator service exists to call yet — the demo/sandbox nature of this specific hardcode should be made loudly explicit in the code (e.g., an assertion that this code path is only reachable when a `SANDBOX_ONLY`-equivalent flag is set), since the repo's own README already labels this pipeline `SANDBOX_ONLY`.

### Affected consumers

- settlement-engine's own `/v0.1/settle` route and its 79 existing tests.
- Any caller of this route — confirmed to be `Cubeshackles-node-api`'s `rc2a_transfer_runtime.py` (the RC2A/demo transfer path), per the Core/Network/Validator verification pass.
- compliance-engine's `/api/v1/compliance/clearing-gate` endpoint gains a new real caller (currently has none) — its own 18 tests are unaffected since the endpoint's contract doesn't change, only its caller population.

### Compatibility strategy

- The new clearing/compliance checks must be **additive and fail-closed by default, but feature-flagged** during rollout (e.g., `SETTLEMENT_REQUIRE_CLEARING_COMPLIANCE_CHECK=true`, defaulting to the CURRENT (unchecked) behavior until explicitly enabled) — this lets the org turn on the real invariant deliberately rather than as a silent breaking change to whatever currently relies on the sandbox's permissive behavior.
- Existing 79 settlement-engine tests, 139 clearing-house tests, 18 compliance-engine tests must all remain green. New tests are added, not substituted.
- `DeterministicSettlementPolicy.evaluate()`'s signature should not change — only its internal logic gains a `validation_decision` check, so no caller needs to change its call site.

### Rollback strategy

- Feature flag above means rollback is a config change, not a code revert, during the initial rollout window.
- If the flag is later made the only behavior (flag removed), rollback would require reverting the specific commit(s) that removed the flag — standard git revert, no data migration involved since no schema/persistence change is part of this PR.

### Tests required (new, beyond the existing 79+139+18)

1. Mutation/adversarial test (per the founder's explicit Phase 6 instruction): construct a `transaction.validated` event with `validation_decision == "REJECTED"` and `event_type == "transaction.validated"`, assert settlement is now refused (this test currently would FAIL against today's code — it is the proof the gap existed and is now closed).
2. A clearing-not-approved scenario: assert `require_clearing_approval` rejection propagates to a refused settlement.
3. A compliance-not-approved scenario (via the new HTTP call to compliance-engine): assert the same.
4. A positive-path regression test: a transaction with valid clearing AND compliance AND a correct `validation_decision` still settles exactly as today.
5. Feature-flag-off regression test: with the flag disabled, today's existing (permissive) behavior is preserved exactly — proves the rollout is non-breaking by default.

### CubeReg dependencies this unblocks vs. still blocks

**Unblocked by Wave 1** (none of CubeReg's own primitives depend on settlement-engine's compliance/clearing wiring directly — CubeReg is isolated by design): technically Wave 1 does not unblock any CubeReg dependency directly, since CubeReg's own corpus pipeline has no live coupling to settlement-engine today. The closest connection is the previously-identified **best-fit fiscal-event hook point** (`finality_record.py::record_internal_ledger_finality`) — Wave 1 makes that hook point more trustworthy (real compliance/clearing checks upstream of it) but does not itself wire CubeReg into it.

**Still blocked regardless of Wave 1**:
- Money ownership (Wave 0 decision #1) — CubeReg's own Money port cannot be assessed for "drift from canonical" until a canonical Money actually exists on a merged main somewhere.
- `fiscal_subject_id` — confirmed genuinely absent org-wide; CubeReg's own documentation already self-flags this as a placeholder for a future org-wide entity/subject ontology. Not blocked by anything in Wave 1; this is a CubeReg-side gap, not an org-dependency gap.
- TransactionIdentity reconciliation (ADR primitive 5) — if CubeReg ever needs to attach fiscal events to a specific settled transaction ID, it currently has 3 incompatible candidate ID schemes to choose from, none canonical. This is a real, structural blocker for any future CubeReg↔settlement integration, independent of Wave 1.
