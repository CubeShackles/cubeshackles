# ADR-0004 — Canonical Ledger Authority and Monetary State Ownership

**Status:** PROPOSED — design only. **Target architecture APPROVED by founder (Gate 2, 2026-10-09): Option C.** Implementation, migration and rerouting NOT authorized.
**Date:** 2026-10-09
**Depends on:** ADR-0003 (transaction identity). **Blocks:** ADR-0003 D4/D5 migration.
**Canonical SHAs investigated:** Cubeshackles-core `a4c323d`, Cubeshackles-node-api `1425452`, cubeshackles-ledger `24680f4`, cubeshackles-settlement-engine `c4f5e16`, cubeshackles-institutional-gateway `0332125`, cubeshackles-integration `edd271f`.
Evidence is tagged **[OBSERVED]** (read in code at the SHA), **[INFERRED]** (deduced from code), **[UNVERIFIED]** (not confirmed this pass).

## 1. Problem

Two independent monetary-posting implementations exist and both are reachable in live code. The platform must not keep two independent sources of monetary truth. This ADR establishes which one is authoritative and how the other becomes a non-authoritative consumer — **design only**.

## 2. The two ledgers

### Ledger A — Core embedded ledger (`cubeshackles.ledger`, consumed in-process by node-api)

| Property | Finding |
|---|---|
| 1. Repo / owner | `Cubeshackles-core`, `src/cubeshackles/ledger/{store.py,engine.py}`, `types/transaction.py` [OBSERVED @a4c323d] |
| 2. Posting entry points | `LedgerEngine.apply_transaction()` (engine.py:36) — called by node-api `execute_batch` (via Orchestrator), `wedge_transfer_settlement.py:191,340,350`, `fund_account` [OBSERVED @node-api 1425452] |
| 3. Storage | SQLite file at `CUBESHACKLES_CORE_DB`, **local to the node-api process** [OBSERVED] |
| 4. Journal schema | **None.** Tables: `accounts(account_id PK, balance)`, `execution_receipts`, `processed_transactions(transaction_id PK)`, `shackles`. No double-entry journal, no entry rows [OBSERVED store.py:30-65] |
| 5. Balance authority | `accounts.balance` mutated in place by debit/credit [OBSERVED engine.py:42-47] |
| 6. Account identity | free-string `account_id` [OBSERVED] |
| 7. Transaction identity | Core `Transaction.id` = `uuid4`; `compute_hash()` includes id + wall-clock `created_at` → non-deterministic [OBSERVED types/transaction.py] |
| 8. Idempotency on posting | `apply_transaction` does **not** consult `processed_transactions` [OBSERVED]. Only the wedge path (post #28) now claims that table before posting [OBSERVED]. Citizen `/transfers/*` and `/batches/execute` dedupe at the node-api service layer (`transaction_execution_idempotency` SQLite), not in the ledger [OBSERVED] |
| 9. Unique constraints | PK on account_id / batch_id / transaction_id(processed); none couples a posting to a transaction id [OBSERVED] |
| 10. Atomicity | single-process SQLite writes; `set_balance` per account, no multi-entry transaction boundary [OBSERVED] |
| 11. Receipts | `execution_receipts` + `receipt_crypto` hashed settlement receipts (node-api) [OBSERVED] |
| 12. Audit | node-api `protocol_events` + transaction-rail audit [OBSERVED] |
| 13. Crash recovery | none at the ledger layer (no proposed/posted states) [OBSERVED] |
| 14. Replay | balances-only; a re-applied transaction double-moves unless a caller-layer guard stops it [OBSERVED] |
| 15. Regulatory evidence | execution receipts + hashes; **no immutable double-entry journal, no hash chain** [OBSERVED] |
| 16. Reconciliation | none in Core [OBSERVED] |
| 17. Deployment | embedded library inside node-api; not a service [OBSERVED] |
| 18. Callers | node-api citizen `/transfers/execute`, `/batches/execute`, v0.1 wedge, offline [OBSERVED] |
| 19. Feature flags | wedge path gated `ENABLE_LEGACY_TRANSACTION_ROUTES` (default off) [OBSERVED] |
| 20. Tests | node-api suite (423 passed @1425452) exercises these paths [OBSERVED] |

### Ledger B — `cubeshackles-ledger` service (consumed over the settlement boundary)

| Property | Finding |
|---|---|
| 1. Repo / owner | `cubeshackles-ledger`, `app/` FastAPI service [OBSERVED @24680f4] |
| 2. Posting entry points | `app/ledger/service.py` `propose_journal` + `post_journal`; HTTP `/ledger/journals/*`; consumed in-process by settlement-engine `src/ledger/posting_client.py` and over HTTP by `ledger_http_client.py` [OBSERVED] |
| 3. Storage | SQLite via SQLAlchemy at `DATABASE_URL`; 5 Alembic migrations (`migrations/versions/001..005`) [OBSERVED] |
| 4. Journal schema | **Real double-entry**: `ledger_journals` (status proposed→posted, `idempotency_key UNIQUE`, `hash_prev`, `hash_current`), `ledger_entries`, `ledger_balance_snapshots`, `ledger_hash_chain_head`, `ledger_reconciliation_runs`, `ledger_event_outbox`, `ledger_operational_state`, `ledger_signing_keys`, `ledger_seen_signed_requests` [OBSERVED db/models.py] |
| 5. Balance authority | derived from posted entries + snapshots [OBSERVED] |
| 6. Account identity | `ledger_accounts` rows [OBSERVED] |
| 7. Transaction identity | caller `idempotency_key` (UNIQUE) + generated `journal_id`; after RC2-A, the caller-owned id flows in as the idempotency key [OBSERVED] |
| 8. Idempotency | `reserve_idempotency_key` + `ledger_idempotency_keys` PK + `ledger_journals.idempotency_key` UNIQUE [OBSERVED service.py:380] |
| 9. Unique constraints | idempotency_key UNIQUE on journals; idempotency table PK [OBSERVED] |
| 10. Atomicity | hash-chain tip advanced by a DB compare-and-swap (`_MAX_CHAIN_CAS_ATTEMPTS`, service.py:72,183) [OBSERVED] |
| 11. Receipts | settlement receipts built by settlement-engine from posted journal; hash chain in ledger [OBSERVED] |
| 12. Audit | CIEL signing infra (migration 005), signature verification log, seen-signed-requests [OBSERVED] |
| 13. Crash recovery | proposed→posted crash-window recovery (settlement-engine #9 + ledger service) [OBSERVED] |
| 14. Replay | idempotent: a reused key returns the existing journal without double-posting [OBSERVED] |
| 15. Regulatory evidence | immutable hash-chained journal, reconciliation runs, signing keys, outbox [OBSERVED] |
| 16. Reconciliation | `app/ledger/reconciliation.py` + control + router [OBSERVED] |
| 17. Deployment | standalone service (port 8086 in local backbone) [OBSERVED/INFERRED] |
| 18. Callers | settlement-engine (RC2-A `/v0.1/settle` + institutional router); node-api `settlement_prepare_runtime` over HTTP [OBSERVED] |
| 19. Feature flags | `LEDGER_POSTING_ENABLED` [OBSERVED] |
| 20. Tests | ledger suite (38+) + settlement-engine 154 + cross-repo e2e [OBSERVED] |

### 2.1 Which paths post where (live) [OBSERVED]

```
node-api /v0.1/demo/transfer (RC2-A) ─▶ settlement-engine /v0.1/settle ─▶ Ledger B (cubeshackles-ledger journal)
institutional gateway ──────────────▶ settlement-engine ────────────────▶ Ledger B
node-api /transfers/execute ───────────────────────────────────────────▶ Ledger A (Core balances, node-api SQLite)
node-api /batches/execute ─────────────────────────────────────────────▶ Ledger A
node-api v0.1 wedge settle (default off) ──────────────────────────────▶ Ledger A
node-api offline sync ─────────────────────────────────────────────────▶ Ledger A
```

**Two sources of monetary truth, split by channel, sharing no journal, id scheme, or idempotency mechanism.**

## 3. Financial-integrity threat model

Severity: **C**ritical / **H**igh / **M**edium.

| # | Failure mode | Services | Trigger | Customer impact | Existing control | Evidence | Required control | Verify | Sev |
|---|---|---|---|---|---|---|---|---|---|
| T1 | Duplicate posting | A (wedge) | restart replay | double debit | now: durable claim (#28) | [OBSERVED] | keep; extend pattern to all A paths | restart+replay test | C |
| T2 | Phantom success | A citizen | F-1 class | "paid", no movement | now: per-intent key (#25) | [OBSERVED] | contract-level identity (ADR-0003) | mutation test | C |
| T3 | False dedup of distinct payments | A citizen | identical economics | second payment dropped | per-intent key (#25) | [OBSERVED] | D12 content-hash rule | two-distinct-payment test | C |
| T4 | Conflicting economics on same id | A/B | reused id, new amount | wrong receipt | B: 409 (#9); A citizen: 409 | [OBSERVED] | D7 everywhere | conflict test | C |
| T5 | Diverging balances across ledgers | A vs B | same citizen settles on both | irreconcilable books | **none** | [OBSERVED] | single posting authority (this ADR) | cross-ledger recon | C |
| T6 | Cross-ledger journal mismatch | A+B | channel split | no unified "settled" | **none** | [OBSERVED] | one journal authority | design | C |
| T7 | Missing journal entry | A | balances-only, no entries | no audit trail | execution receipts only | [OBSERVED] | double-entry journal for A paths | schema review | H |
| T8 | Orphan receipt | A/B | receipt without linkage | regulator gap | node-api fail-closed audit linkage | [OBSERVED] | keep | route test | H |
| T9 | Stale settlement status | B | crash mid-finality | stuck transfer | crash-window recovery (#9) | [OBSERVED] | keep; reconcile | recovery drill | H |
| T10 | Crash between authz and posting | A | process kill | lost transfer | none (A) / recovery (B) | [OBSERVED] | claim-then-post on A | chaos test | H |
| T11 | Crash after posting before receipt | A/B | process kill | missing receipt | B derivable from journal | [INFERRED] | derive receipt from journal (D8) | restart test | M |
| T12 | Replay after restart | A/B | at-least-once retry | double/none | B idempotent; A wedge only | [OBSERVED] | durable idempotency on A | restart test | C |
| T13 | Inconsistent account identity | A | display-name as acct | wrong account posted | D6 forbids it | [OBSERVED] | stable account identity | audit | H |
| T14 | Out-of-order settlement events | B | event reordering | wrong state | hash chain ordering | [OBSERVED] | keep | order test | M |
| T15 | Partial migration | A→B | mid-migration | split truth window | none yet | [design] | dual-write/shadow plan + gates | migration test | H |
| T16 | Reconciliation failure | A | no recon in Core | undetected drift | none (A) | [OBSERVED] | recon on authoritative ledger | recon run | H |

No hypothetical control above is described as implemented; "now:" marks controls that landed in the merged F-1/F-2/#9 PRs.

## 4. Ledger-authority options

| Criterion | A: ledger-service sole authority (node-api = client over HTTP) | B: Core engine as canonical library everywhere | **C: Core defines the contract; one designated service owns durable posting; others consume + hold read models** |
|---|---|---|---|
| Correctness | high | depends on every embedder posting correctly | high |
| Fault isolation | strong (service boundary) | weak (in-process everywhere) | strong |
| Deterministic execution | yes | yes | yes |
| Latency | +network hop on citizen path | lowest | hop only where crossing the boundary |
| Operational complexity | higher (service always up) | lowest | moderate |
| Offline / Angola-first | weak (needs the service reachable) | strong (embeddable) | **strong — contract embeddable offline, authoritative posting reconciled on reconnect** |
| Recovery | mature (B's recovery) | must be rebuilt in Core | mature + contract-guaranteed |
| Regulator visibility | one journal+hash chain | none unless Core gains one | one authoritative journal |
| Security boundary | clear | none | clear |
| Deployment risk | citizen path now depends on the service | low | phased |
| Migration cost | high (rewire citizen paths now) | high (add journal to Core) | **moderate, phaseable** |
| Maintainability | two codebases diverge | one, but no isolation | one contract, one authority |

**Recommendation: Option C.** The authoritative durable posting is the `cubeshackles-ledger` journal engine (Ledger B — it already has the double-entry journal, idempotency UNIQUE, hash chain, crash recovery, reconciliation, signing). Core owns the **contract and economic invariants** (reusing the ADR-0002 Money + ADR-0003 identity pattern). node-api's Core balances store (Ledger A) is demoted to a **non-authoritative read model / demo store** and must not create authoritative postings for real money. This is evidence-led: the service already carries the institutional-grade machinery; Core already owns contracts; Option C keeps offline/Angola-first viable (contract embeddable, posting reconciled) without a network hop becoming a hard dependency for every citizen action until a wave explicitly migrates it.

**Not auto-selected for implementation** — recommendation only, pending Gate 2.

### 4.1 Founder ruling — Gate 2 (2026-10-09): Option C APPROVED (target architecture only)

| Component | Approved disposition |
|---|---|
| `cubeshackles-ledger` | Sole authoritative monetary posting service |
| `Cubeshackles-core` | Canonical contracts, economic invariants, validation |
| Node-API embedded ledger (Ledger A) | Transition to **non-authoritative read model** |
| Settlement Engine | Settlement orchestration, **not** independent monetary authority |
| Offline & wedge paths | Remain gated until migrate-or-retire is decided |

**Qualification (binding):** this is the *target design*, not permission to migrate balances or reroute live transactions. Existing monetary state must be **inventoried and reconciled first** (see the companion `MIGRATION_AND_RECONCILIATION_SPEC`). **A read model must never independently post authoritative funds.** Gate 3 (canonical contract implementation) and all migration waves remain **unauthorized**.

## 5. Single-posting invariant (target)

> ONE CANONICAL TRANSACTION → AT MOST ONE AUTHORITATIVE MONETARY POSTING.

For every successful payment: one canonical Transaction ID (ADR-0003), one authoritative posting decision, one immutable double-entry journal, one consistent balance effect, receipts derived from that posting, all downstream systems referencing the same id.

Exactly-once **economic effect** is enforced by the authoritative ledger's UNIQUE idempotency key; at-least-once **message delivery** is allowed above it (retries converge on the same journal).

Behaviour table:
| Event | Required behaviour |
|---|---|
| client retries | same id → same journal, no second posting |
| node-api restarts | no state needed; id is deterministic (ADR-0003 D2) |
| settlement-engine restarts | durable idempotency in the ledger; crash-window completes the interrupted post |
| ledger restarts | journal is durable; UNIQUE holds |
| network times out after posting | retry resolves to the existing journal; no double-post |
| two requests race, same id | one wins the UNIQUE claim; the other returns idempotent |
| two different ids, identical economics | **both post** (distinct journals) — proves economics ≠ identity (D3/D12) |

The last row is the explicit anti-F-1 proof obligation.

## 6. Migration dependency graph (NOT executed)

```
Gate 1  ADR-0003 decisions ratified ........................ DONE (this directive)
Gate 2  ADR-0004 ledger authority chosen: Option C ......... APPROVED 2026-10-09
Gate 3  Canonical contract work authorized
          └ Core: TransactionId module (ADR-0003 D2) + Ledger posting contract
Gate 4  Consumer migration waves (each separately authorized):
          W1 RC2-A/settlement-engine already on Ledger B — adopt tx1 ids (ADR-0003 D10 compat)
          W2 node-api /transfers/execute → authoritative ledger (D4) [needs Gate 2]
          W3 node-api /batches/execute → authoritative ledger
          W4 wedge + offline → authoritative ledger or formal retirement
          W5 Ledger A demoted to read model; stop authoritative postings
Gate 5  Pilot validation (chaos + reconciliation + regulator evidence)
Gate 6  Production deployment
```

Preserved across all waves: historical journals, RC2-A namespace v0, current authenticated interfaces, existing regulator evidence, settlement invariants. **No destructive migration.**

## 7. Feature-freeze classification

- ADR-0003 ratification + ADR-0004 draft: `freeze:allowed` (docs/evidence).
- Gate 3 canonical contract: `freeze:exception-required` (new frozen contract) + likely a new architecture milestone.
- Gates 4–6: `freeze:exception-required`; each a separate PR with its own regression + chaos evidence.

## 8. Open founder decisions (remaining after Gate 2)

Gate 2 resolved: Option C adopted; cubeshackles-ledger authoritative; ADR docs authorized to be persisted as an unmerged PR. Still open before any implementation:

1. **Offline & wedge paths** — migrate to the authoritative ledger, or retire the unsafe posting implementations. (Until decided, they stay gated; wedge posting is default-off.)
2. **D2 TransactionId** — finalize canonical serialization, principal normalization, collision handling, identifier encoding (ADR-0003 D2 condition).
3. **Ledger migration & reconciliation** — how existing balances, journals and in-flight payments reconcile without duplicate postings or loss of historical evidence. **Highest-priority next deliverable: a read-only migration & reconciliation specification** (companion doc) identifying the exact state each ledger holds and defining measurable cutover gates.

Gate 3 (canonical contract implementation) and all migration waves remain **unauthorized**.

## 9. Required regression & chaos tests (for implementation waves, not now)

- Two distinct authorized payments, identical economics → two journals (anti-F-1).
- Same id retried across node-api/settlement/ledger restart → one journal.
- Concurrent same-id race → one posting.
- Conflicting economics on same id → typed 409, zero mutation, no fabricated finality.
- Crash between authz and posting; crash after posting before receipt → recovery from persisted state.
- Cross-ledger reconciliation shows no divergence after migration.
- Regulator evidence: journal + hash chain + reconciliation run present for every settled payment.

## 10. Authorization boundaries

Implementation: **NO.** Push: **NO.** PR: **NO.** Merge: **NO.** Production diff this pass: **ZERO.**
