# ADR-0004 Gate 2 Closure — Founder Decisions + Staging Ledger Inventory (READ-ONLY)

**Status:** PROPOSED — design/record only. **Implementation, migration, deployment, route-switching NOT authorized.**
**Date:** 2026-10-10
**Builds on:** ADR-0003, ADR-0004 (Gate 2, Option C approved), MIGRATION_AND_RECONCILIATION_SPEC — all merged to `cubeshackles` main via PR #15 (merge `f1e4e5e`, docs at base `010a657`).
**SHAs this pass:** cubeshackles `cf089b1`, Cubeshackles-core `a4c323d`, Cubeshackles-node-api `1425452`, cubeshackles-ledger `24680f4`, cubeshackles-settlement-engine `c4f5e16`, cubeshackles-integration `edd271f`.
Evidence tags: **[OBSERVED]** read in code, **[INFERRED]** deduced, **[UNVERIFIED]** not confirmed.

## Phase 2 — Founder decisions recorded

**Decision A — Offline & wedge (APPROVED TARGET).** Migrate supported offline and wedge payment functionality to the authoritative ledger; retire independent monetary posting. Offline intent creation and sync may remain separate workflow stages, but authoritative monetary posting must go through the designated ledger authority. **No current route is authorized for migration or retirement** — the wedge posting path stays gated (`ENABLE_LEGACY_TRANSACTION_ROUTES`, default off) and the offline path unchanged until a Gate 4 wave.

**Decision B — TransactionId format (APPROVED IN PRINCIPLE).** Deterministic, versioned, namespaced identity. The exact `tx1` wire representation stays conditional on: canonical serialization, domain separation, authenticated principal normalization, key entropy, collision resistance, truncation analysis, deterministic cross-language conformance, persistent uniqueness enforcement, and legacy RC2-A compatibility. **No unverified format is finalized.**

**Decision C — First reconciliation environment (APPROVED: STAGING FIRST).** Synthetic balances, synthetic accounts, controlled fault injection. No production customer funds, no production ledger writes, no production-like UAT until staging cutover gates pass.

These decisions change no runtime behavior.

## Phase 3 — Staging ledger inventory

### STAGING_ENVIRONMENT = NOT VERIFIED

No dedicated staging deployment is evidenced in the repos. What exists [OBSERVED]:
- `cubeshackles-integration` `docker-compose.yml`: services = postgres, validator-node-1/2, node-api, orchestrator, phone-wedge, cubewallet, bualabuitu, integration-smoke. **cubeshackles-ledger (Ledger B) and settlement-engine are NOT services in this stack.** node-api runs on `CUBESHACKLES_CORE_DB` (Ledger A, SQLite file).
- `docker-compose.production.yml` present; also no ledger/settlement service.
- Local dev scripts: node-api `scripts/start_full_honest_stack.sh` (node-api on :8000 only), integration `scripts/start_local_backbone.sh`.
- "staging" in ledger/settlement repos appears only in README docs, not deployment config.

**Consequence:** the Option-C authoritative ledger (B) is reachable today only in-process via settlement-engine on the RC2-A/institutional path; it is **not deployed in the orchestrated backbone** at all. Any staging cutover first requires standing B up as a service in the environment.

### Ledger A vs Ledger B — staging-relevant inventory

| # | Property | Ledger A (Core embedded, node-api) | Ledger B (cubeshackles-ledger) |
|---|---|---|---|
| 1 | Canonical SHA | Core `a4c323d` | `24680f4` |
| 2 | Active posting routes | `/transfers/execute`, `/batches/execute`, wedge(off), offline [OBSERVED] | RC2-A `/v0.1/settle`, institutional (via settlement-engine) [OBSERVED] |
| 3 | Callers | node-api in-process | settlement-engine (in-process + HTTP), node-api settlement_prepare over HTTP [OBSERVED] |
| 4 | Account schema | `accounts(account_id PK, balance TEXT, currency)` [OBSERVED] | `ledger_accounts` rows [OBSERVED] |
| 5 | Balance representation | TEXT balance, mutated in place [OBSERVED] | derived from posted entries + snapshots (exact MONEY) [OBSERVED] |
| 6 | Journal schema | **none** [OBSERVED] | `ledger_journals`+`ledger_entries` double-entry [OBSERVED] |
| 7 | Idempotency | none on post (wedge claims `processed_transactions`) [OBSERVED] | `idempotency_key` UNIQUE + reservation table [OBSERVED] |
| 8 | Transaction identity | uuid4, non-deterministic hash [OBSERVED] | caller idempotency_key + journal_id [OBSERVED] |
| 9 | DB engine | SQLite file | SQLite via SQLAlchemy + 5 Alembic migrations [OBSERVED] |
| 10 | Persistence config | `CUBESHACKLES_CORE_DB` | `DATABASE_URL` [OBSERVED] |
| 11 | Crash recovery | none at ledger layer | proposed→posted crash-window recovery [OBSERVED] |
| 12 | Reconciliation | none | `reconciliation.py` + runs table [OBSERVED] |
| 13 | Audit evidence | execution receipts + protocol events (node-api) | hash chain + CIEL signing + verification log [OBSERVED] |
| 14 | Feature flags | `ENABLE_LEGACY_TRANSACTION_ROUTES` (wedge/offline) | `LEDGER_POSTING_ENABLED` [OBSERVED] |
| 15 | Environment boundaries | embedded in node-api process | standalone service (not in compose) [OBSERVED] |
| 16 | Test fixtures | node-api suite (423 passed @1425452) [OBSERVED] | ledger suite + settlement 154 + cross-repo e2e [OBSERVED] |
| 17 | Staging deploy status | runs inside node-api container in compose [OBSERVED] | **not deployed in any compose/stack** [OBSERVED] |
| 18 | Production-reachable | citizen/batch/offline paths [OBSERVED] | RC2-A + institutional via settlement-engine [OBSERVED] |

### Proposed synthetic staging config (NOT deployed)
- Add `cubeshackles-ledger` + `cubeshackles-settlement-engine` as services to a staging compose, each with its own isolated SQLite/Postgres volume and synthetic data only.
- Synthetic accounts/balances fixture, no production data, `LEDGER_POSTING_ENABLED=true` in staging only.
- Fault-injection hooks (kill/restart, network timeout) for the Phase 7 tests.
- This is a proposal; **no deployment is authorized.**

## Phase 4 — State inventory

Because STAGING_ENVIRONMENT = NOT VERIFIED, there is **no staging state to inventory**. Per each requested item:

| State | Finding |
|---|---|
| synthetic account balances | NOT VERIFIED — no staging env; not fabricated |
| persisted transaction identities | NOT VERIFIED |
| journal entries | NOT VERIFIED (Ledger B schema supports them; no staging instance) |
| pending settlements | NOT VERIFIED |
| idempotency reservations | NOT VERIFIED |
| orphan receipts | NOT VERIFIED |
| unreconciled transactions | NOT VERIFIED |
| recovery markers | NOT VERIFIED |
| hash-chain / integrity evidence | schema present in B [OBSERVED]; no live staging instance to read |

No live customer records were inspected; no secrets/PII/production data extracted; no balances or journal counts fabricated.

## Phase 5 — Reconciliation parity model (minor units)

Per synthetic account, exact integer minor units:

```
VARIANCE = OBSERVED_CLOSING_BALANCE
         - (OPENING_BALANCE + AUTHORIZED_CREDITS - AUTHORIZED_DEBITS)
REQUIRE: VARIANCE == 0 for every account
```

Representing Ledger A's balances-only state in the future authoritative ledger **without inventing history**:
- Ledger A has no journals, so its balances become **explicit opening-balance entries** in B, each labelled as provenance `"migrated-opening-balance"` — never fabricated per-transaction journals.
- Each opening balance must carry: source snapshot identity (A DB file hash + row), logical cutoff marker (A is quiesced at cutoff), source→destination account mapping, a deterministic reconciliation report, approval evidence, and a rollback procedure.
- A uniqueness guard prevents duplicate opening-balance application (one opening entry per (account, source-snapshot)).
- **No opening-balance postings are created in this mission.**

## Phase 6 — Cutover gates CG-1..CG-9 (status)

Definitions preserved verbatim from MIGRATION_AND_RECONCILIATION_SPEC §3. Status is evidence-based; a gate without evidence is NOT VERIFIED.

| Gate | Requirement | Evidence required | Current evidence | Status | Blocker | Required action |
|---|---|---|---|---|---|---|
| CG-1 | Both ledgers enumerated at quiesced instant | inventory snapshot + hash | none | NOT VERIFIED | no staging env | stand up staging B; run inventory reporter |
| CG-2 | Account map 1:1 | mapping table, zero orphans | none | NOT VERIFIED | CG-1 | build mapping reporter |
| CG-3 | Balance parity (minor units) | zero-variance report | none | NOT VERIFIED | CG-1/2 | run parity reporter |
| CG-4 | In-flight drained | zero proposed/confirmed-unexecuted/unsynced | none | NOT VERIFIED | CG-1 | drain + verify |
| CG-5 | Idempotency continuity | every real-money A tx has B journal | none | NOT VERIFIED | CG-1 | continuity reporter |
| CG-6 | Evidence archived | immutable A receipts + B chain copy | none | NOT VERIFIED | CG-1 | archive + verify |
| CG-7 | Dual-read shadow, N days, zero divergence | shadow-compare log | none | NOT VERIFIED | B deployed | shadow reader |
| CG-8 | Anti-F-1: 2 distinct identical payments → 2 journals | staging test result | design only | NOT VERIFIED | staging | run Phase 7 T1 |
| CG-9 | Reversibility rehearsed | rollback drill evidence | none | NOT VERIFIED | staging | rehearse rollback |

**All nine gates NOT VERIFIED.** Migration readiness cannot be claimed from design documents alone.

## Phase 7 — Financial-integrity staging test plan (design only, not executed)

Each test: PRECONDITION / ACTION / EXPECTED ECONOMIC EFFECT / EXPECTED JOURNAL EFFECT / EXPECTED RECEIPT / EXPECTED AUDIT / PASS-FAIL.

| # | Scenario | Pass condition (summary) |
|---|---|---|
| FT1 | two distinct identical payments | two journals, two receipts, both balances move; FAIL if deduped |
| FT2 | same-intent retry | one journal; retry returns same receipt; FAIL if second posting |
| FT3 | concurrent duplicate requests | exactly one posting; others idempotent |
| FT4 | conflicting economics, same id | typed 409, zero mutation, no finality/approval event |
| FT5 | restart after authorization | no money moved yet → single posting on resume |
| FT6 | restart after posting | journal intact, no second posting, receipt derivable |
| FT7 | timeout after posting before receipt | retry resolves to existing journal; receipt derived from journal |
| FT8 | failed idempotency reservation | request rejected, no posting |
| FT9 | interrupted ledger migration | no partial opening balances; rollback restores A-authoritative |
| FT10 | duplicate opening-balance application | second attempt rejected by uniqueness guard; variance 0 |
| FT11 | diverging account balances | parity reporter flags non-zero variance; cutover blocked |
| FT12 | orphan receipts | receipt without journal linkage → fail-closed 422 |
| FT13 | missing audit events | settled payment without audit linkage → detected |
| FT14 | cross-service tx identity mismatch | receipt id ≠ caller id → rejected (RC2-A behavior) |
| FT15 | reconciliation variance | any non-zero variance → gate fails |
| FT16 | offline replay | replayed offline intent → one posting |
| FT17 | wedge replay | restart replay → one posting (post-#28 claim) |
| FT18 | institutional HTTP ledger replay | duplicate HTTP post → existing journal, no double-post |

No production execution.

## Phase 8 — Gate 3 readiness assessment

| Input | State |
|---|---|
| ADR-0003 decisions | recorded (Gate 1) |
| ADR-0004 ledger authority | Option C approved (Gate 2) |
| tx1 format conditions | OPEN (Decision B conditions unmet) |
| Core contract ownership | established in principle; contract module not built |
| migration dependencies | spec written; CG-1..CG-9 all NOT VERIFIED |
| current CI coverage | node-api 423 passing; ledger/settlement green; no cross-ledger staging CI |
| baseline test health | green [OBSERVED] |
| staging availability | **NOT VERIFIED (no staging env; Ledger B not deployed)** |
| reconciliation controls | designed, not instrumented |
| feature-freeze exceptions | Gate 3 needs `freeze:exception-required` + new milestone |

**GATE_3_READINESS = NOT READY.** Blockers: no staging environment with Ledger B deployed; tx1 format conditions unmet; CG-1..CG-9 unverified; reconciliation reporters not built.

**GATE_3_AUTHORIZED = NO.** No implementation begins.

## Governance
Production changes: ZERO. Balance migration: ZERO. Route switching: ZERO. Deployment: ZERO. Gate 3 authorized: NO.
