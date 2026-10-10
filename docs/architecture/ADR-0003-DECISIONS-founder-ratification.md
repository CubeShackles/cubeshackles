# ADR-0003 — Founder Decision Ratification Record

**Status:** Decisions RECORDED (Gate 1). Implementation NOT authorized.
**Date:** 2026-10-09
**Governs:** `docs/architecture/ADR-0003-canonical-transaction-identity.md` (merged, `cubeshackles` main `010a657`).
**Canonical SHAs at ratification:** cubeshackles `010a657`, Cubeshackles-core `a4c323d`, Cubeshackles-node-api `1425452`, cubeshackles-ledger `24680f4`, cubeshackles-settlement-engine `c4f5e16`, cubeshackles-integration `edd271f`, cubeshackles-institutional-gateway `0332125`.

This record converts the founder directive of 2026-10-09 into the decision table of ADR-0003 §10. It authorizes no code change; each implementation wave is a separate gate.

| # | Decision | Founder ruling | Open conditions before implementation |
|---|---|---|---|
| D1 | Identity authority | **APPROVED IN PRINCIPLE.** Ingress mints: node-api (citizen), institutional gateway (institutional); ledger enforces uniqueness. | Prove no downstream service silently replaces the id (propagation matrix, below). |
| D2 | Deterministic id `tx1.<ns>.<base32(sha256(ns\|principal\|key))[:32]>` | **CONDITIONALLY APPROVED.** | Wire format NOT final until contract-conformance evidence: canonical serialization + domain separation, truncation/collision analysis, principal normalization, key entropy, durable/recoverable input. |
| D3 | Idempotency key ≠ transaction id ≠ economic fingerprint | **APPROVED.** Three distinct concepts; never substitute. | — |
| D4 | `/transfers/execute` adopts canonical identity | **APPROVED AS TARGET.** Keep route + its authz/confirm/audit controls. | Do not migrate until ADR-0004 resolves ledger authority. |
| D5 | Ledger journal is economic source of truth | **APPROVED IN PRINCIPLE.** | **WHICH ledger is authoritative is UNDECIDED → ADR-0004 (Gate 2) before migration.** |
| D6 | Economic equivalence fields | **CONDITIONALLY APPROVED.** currency, amount_minor (int), stable payer acct, stable payee acct, channel, fee outcome, durable business ref. | Investigate further settlement-affecting fields; define canonical serialization + field versioning; never use mutable display names as account identity. |
| D7 | Conflict handling | **APPROVED WITH AUDIT QUALIFICATION.** Same id + conflicting immutable economics → typed 409, no ledger/finality mutation, no success receipt, no fabricated approval. A typed rejection/security event is permitted. | Must not emit misleading SETTLEMENT_AUTHORIZED / LEDGER_POSTED / VALIDATOR_ATTESTED / finality events. |
| D8 | Receipt authority | **APPROVED.** Receipts derive from persisted journal/settlement state, never from the request body. Distinguish Transaction/Receipt/Journal identity. | — |
| D9 | Restart & recovery | **APPROVED.** restart-safe replay, durable uniqueness, crash-window recovery, deterministic reconciliation, no duplicate posting, recovery evidence from persisted state. | — |
| D10 | RC2-A compatibility | **APPROVED.** Existing RC2-A ids = legacy namespace v0; never re-key historical journals; backward-compatible migration only. | — |
| D11 | Cross-service propagation | **APPROVED AS DESIGN OBLIGATION.** | Deliver the per-service matrix (below). |
| D12 | Content-hash restriction | **APPROVED.** A content-derived key is valid only with a durable caller-unique business reference + principal/namespace binding. Explicitly prevents F-1 recurrence. | — |

**Migration approach:** Option A (contract-first) — endorsed in principle, gated by ADR-0004 and per-wave authorization.
**ADR-0004:** authorized to be drafted as PROPOSED design-only (this deliverable).

**Not authorized by this record:** code changes, ledger migration, identifier changes, service deployment, implementation waves. Gates 2–6 remain closed.
