# Ledger Migration & Reconciliation Specification (READ-ONLY)

**Status:** PROPOSED — read-only design. **No migration, no rerouting, no writes authorized.**
**Companion to:** ADR-0004 (Gate 2, Option C approved). **Blocks:** any migration wave (Gate 4+).
**Date:** 2026-10-09
**SHAs:** Cubeshackles-core `a4c323d`, Cubeshackles-node-api `1425452`, cubeshackles-ledger `24680f4`, cubeshackles-settlement-engine `c4f5e16`.

Purpose: define exactly what monetary state each ledger holds and the **measurable cutover gates** that must pass before Ledger A (Core embedded) stops posting and becomes a read model. Everything here is inventory and verification — **no step mutates money or reroutes traffic.** A read model must never post authoritative funds.

## 1. State inventory — what each ledger holds

### Ledger A — Core embedded (node-api-local SQLite at `CUBESHACKLES_CORE_DB`) [OBSERVED]
| State | Location | Read-only inventory |
|---|---|---|
| Balances | `accounts(account_id, balance TEXT, currency)` | `SELECT account_id, balance, currency FROM accounts` |
| Execution receipts | `execution_receipts(batch_id, batch_hash, state_root, decisions_json, created_at)` | `SELECT batch_id, created_at FROM execution_receipts` |
| Processed/claimed tx | `processed_transactions(transaction_id PK)` (incl. `wedge-settlement:*` claims from #28) | `SELECT transaction_id FROM processed_transactions` |
| **No journal / no entries** | — | balances are the only monetary truth; there is no immutable per-posting record to replay |

**Consequence for migration:** Ledger A cannot produce a double-entry history. Reconciliation can only compare *net balance per account*, not per-transaction journals. Any cutover must treat A's balances as a point-in-time snapshot to be *reconciled into* B, never replayed as journals.

### Ledger B — cubeshackles-ledger service (SQLite at `DATABASE_URL`) [OBSERVED]
| State | Location | Read-only inventory |
|---|---|---|
| Journals | `ledger_journals(journal_id, idempotency_key UNIQUE, status, hash_prev, hash_current, reversal_of, created_at)` | `SELECT journal_id, idempotency_key, status FROM ledger_journals` |
| Entries | `ledger_entries(entry_id, journal_id, account_id, side, amount MONEY, currency)` | `SELECT journal_id, account_id, side, amount, currency FROM ledger_entries` |
| Balance snapshots | `ledger_balance_snapshots(account_id, debit_total, credit_total, net_position)` | `SELECT account_id, net_position FROM ledger_balance_snapshots` |
| Hash chain | `ledger_hash_chain_head` | tip integrity check |
| Idempotency | `ledger_idempotency_keys(idempotency_key PK)` | duplicate detection |
| Recon runs | `ledger_reconciliation_runs(status, ...)` | last-run status |

### In-flight state (neither ledger's steady state) [OBSERVED]
| In-flight | Where | Risk at cutover |
|---|---|---|
| Proposed-not-posted journals | B `ledger_journals.status='proposed'` | crash-window; must drain/complete before snapshot |
| node-api transfer sessions | `transfer_sessions.json` / execution-idempotency SQLite | a prepared+confirmed-but-not-executed intent |
| settlement-engine RC2-A receipts / replay cache | process memory (lost on restart) | not durable; must be quiesced |
| offline intents awaiting sync | node-api offline reconciliation SQLite | unsettled intents |

## 2. Reconciliation model

Because Ledger A has no journals, reconciliation is **balance-level**, not journal-level:

- **R1 Account mapping:** build a verified map from A `account_id` → B `ledger_accounts.account_id`. Unmapped accounts on either side are a hard stop.
- **R2 Balance parity:** for every mapped account, `A.balance` (as exact minor units) must equal B `net_position`. Any delta is itemized; a non-zero unexplained delta blocks cutover.
- **R3 Currency parity:** currency per account matches; no cross-currency mapping.
- **R4 In-flight = 0:** no proposed journals in B, no confirmed-unexecuted sessions in node-api, no unsynced offline intents, for the accounts in scope.
- **R5 Idempotency continuity:** every A `processed_transactions` entry that represents real money has a corresponding B journal (or is explicitly classified demo-only).
- **R6 Evidence preservation:** A's `execution_receipts` and B's hash chain are both archived read-only before any disposition change; historical RC2-A namespace v0 ids are never re-keyed.

## 3. Measurable cutover gates (all must be GREEN, evidence attached)

| Gate | Measure | Pass condition |
|---|---|---|
| CG-1 Inventory complete | both ledgers enumerated at a quiesced instant | 100% accounts listed, snapshot hash recorded |
| CG-2 Account map | R1 | every in-scope account mapped 1:1; zero orphans |
| CG-3 Balance parity | R2 (exact minor units) | zero unexplained delta |
| CG-4 In-flight drained | R4 | zero proposed/confirmed-unexecuted/unsynced in scope |
| CG-5 Idempotency continuity | R5 | zero real-money A tx without a B journal |
| CG-6 Evidence archived | R6 | immutable copy of A receipts + B chain stored; verified |
| CG-7 Dual-read shadow | serve reads from B, compare to A for N days | zero divergence over the window |
| CG-8 Anti-F-1 proof | two distinct authorized payments, identical economics | both produce distinct B journals |
| CG-9 Reversibility | documented rollback to A-authoritative | rehearsed, evidence captured |

**Cutover is a read/route change, not a balance move:** CG-3 proves balances already agree, so no funds are "migrated" — authority is switched only after parity is proven, and A keeps its balances as a frozen read model.

## 4. Sequencing (design only — each step a separate Gate 4 wave)
1. Instrument read-only inventory + reconciliation reporters (no writes).
2. Run CG-1..CG-6 against UAT/staging; itemize every delta.
3. Shadow-read window CG-7.
4. Wave-by-wave route switch (RC2-A already on B; then `/transfers/execute`, `/batches/execute`, then wedge/offline per their migrate-or-retire decision), each behind a flag with CG-8/CG-9 proven.
5. Demote Ledger A to read model; disable its authoritative posting paths.

## 5. Explicit non-goals / prohibitions
- No balance writes, no journal backfill, no traffic rerouting under this spec.
- Read model must never post authoritative funds.
- No destructive migration; historical journals and RC2-A v0 ids preserved.
- Offline/wedge disposition (migrate vs retire) is an open founder decision; until then they stay gated.

## 6. Open inputs needed from founder
- Offline & wedge: migrate or retire (gates the scope of CG-4/CG-5).
- D2 TransactionId final encoding (affects idempotency-key continuity, R5).
- Target environment for the first inventory run (UAT vs staging).
