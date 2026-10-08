# ADR-0003: Canonical Transaction Identity

**Status:** PROPOSED — design only.
**Founder decisions:** PENDING (D1–D12, §10).
**Implementation:** NOT AUTHORIZED.
**Date:** 2026-10-08
**Resolves (when approved):** the `TransactionIdentity` item left `UNRESOLVED` in `ADR-0001-canonical-authority.md` §5.
**Supersedes:** nothing.

## Governance

This ADR is a design record and a founder decision record. It does not
authorize code changes, and approving it does not authorize implementation.

- **Gate 1, design approval:** the founder approves (or amends) the decisions
  in §10.
- **Gate 2, implementation authorization:** each wave in §8 is authorized
  separately. Each one is classified under the Feature Freeze Candidate change
  policy (`ROADMAP.md`): `freeze:allowed` for bug, security and reliability
  fixes; `freeze:exception-required` for new public API surface or breaking
  changes to frozen contracts.

Nothing in this ADR changes the RC2-A rail proven on 2026-10-07 (see §2.1).
Two items stay **independently tracked** and are not absorbed into this
redesign: the node-api test-suite baseline debt (`docs/TEST_SUITE_GAP_LIST.md`
in that repo), and replay verification on the institutional HTTP ledger path
(§9).

---

## 1. Problem

The org has no single answer to "is this the same transaction?". ADR-0001
counted three incompatible identity schemes. After RC2-A closure, one rail now
has a proven caller-owned identity; the rest of the platform does not. An
identity question is also a money question: if identity is wrong, either a
retry moves money twice or a new payment is mistaken for a retry and silently
not executed. Both failure modes have been observed (§9).

## 2. Evidence (read-only investigation, 2026-10-08)

Canonical SHAs inspected: `Cubeshackles-node-api` `59be44c`,
`cubeshackles-settlement-engine` `c4f5e16`, `cubeshackles-ledger` `24680f4`,
`cubeshackles-institutional-gateway` `0332125`, `Cubeshackles-core` `1061fa3`,
`Cubeshackles-validator-node` `ddd9b5d`.

### 2.1 What is already proven (RC2-A rail)

Proven on canonical main with real processes, real SQLite and real restarts
(node-api #22 + settlement-engine #9):

```
client Idempotency-Key K
  → node-api           transaction_id = K
  → settlement-engine  deterministic_transaction_id = K
  → ledger             journal idempotency_key = K  (UNIQUE)
```

- An identical replay returns the same journal, both warm and after a restart.
- A conflicting replay (same K, different amount or currency) gets a 409. No
  journal is written, and no finality or settlement-audit state is recorded.
- The receipt's amount and currency match the persisted journal.

This is the **reference behaviour** the canonical contract must preserve
(requirement R9).

### 2.2 Identity surfaces today

| Surface | Mounted by default | Who mints the identity | Idempotency key | Durable dedupe | Payload-conflict check | Ledger |
|---|---|---|---|---|---|---|
| node-api `POST /v0.1/demo/transfer` (RC2-A) | yes | **caller** (`Idempotency-Key`) | same as identity | ledger UNIQUE | yes (node-api + settlement-engine) | cubeshackles-ledger (via settlement-engine) |
| node-api `/transfers/preview→prepare→confirm→execute` | yes | Core `Transaction.id` = **uuid4** per execution | path-specific (not caller-owned) | SQLite execution record | yes (canonical payload hash) | **Core `LedgerStore` in node-api's own SQLite** |
| node-api `POST /batches/execute` | yes | caller-supplied `transaction_id` if present, else uuid4 | caller `idempotency_key` | SQLite execution record | yes | Core `LedgerStore` (node-api SQLite) |
| node-api v0.1 wedge intents/finalize/settle | **no** (legacy quarantine flag) | content hash (`build_wedge_idempotency_key`) | content hash, or caller-supplied | process-scoped | no | Core `LedgerStore` |
| node-api offline intents/sync | yes | **caller/device** `transaction_id` | (device, transaction_id, nonce) | SQLite reconciliation | at sync time | Core `LedgerStore` |
| gateway → settlement-engine (institutional) | yes | `Idempotency-Key` header, else bank `instruction_id`, else full-content hash (includes `trade_id`, settlement date) | same | settlement-engine replay cache + ledger UNIQUE | key bound into the CIEL request signature; HTTP-ledger replay economics **unverified** | cubeshackles-ledger (HTTP) |
| Core `Transaction` | n/a | uuid4 at construction; `compute_hash()` includes `id` and wall-clock `created_at` | n/a | `processed_transactions(transaction_id)` | n/a | — |
| validator-node attestations | n/a | echoes `transaction_id` from the request | — | — | — | — |
| CIEL events (node-api hub) | yes | references `transaction_id`; has its own `event_id`/`correlation_id` | — | — | — | — |

### 2.3 Structural findings

1. **Two ledgers.** Citizen and wedge paths post to Core's `LedgerStore` in
   node-api's own SQLite. RC2-A and institutional paths post to
   `cubeshackles-ledger`. Identity can be unified without unifying ledgers,
   but "one transaction settled once" cannot be guaranteed across ledgers
   that don't share an identity namespace. **Ledger authority is a separate
   decision (proposed ADR-0004), not decided here.**
2. **Content hashes used as identity.** Where a content hash includes a
   caller-unique business reference (the gateway's hash includes `trade_id`),
   it is safe. Where it contains only the economic parameters, two genuinely
   distinct payments with the same parameters are indistinguishable from a
   retry. Defects of this class are tracked privately (§9).
3. **The idempotency key and the transaction identity are conflated.** On
   RC2-A they are the same string by design (interoperability shim). On other
   paths they are produced by unrelated mechanisms, and the transaction identity
   is not stable across executions.
4. **Restart-stable dedupe only exists where the ledger enforces it.**
   In-memory registries (wedge explorer, settlement-engine replay cache,
   RC2-A receipts) are lost on restart. The ledger's UNIQUE `idempotency_key`
   is the only durable guard on the RC2-A rail.
5. **Receipts are not restart-stable.** RC2-A receipts get a fresh
   `receipt_id` after a restart for the same journal, and participant→account
   mapping is process-scoped.
6. **Audit can record a rejected attempt as attested.** settlement-engine's
   RC2-A router records `TRANSFER_INITIATED` and a self-asserted
   `VALIDATOR_ATTESTED` before settlement runs, so a request that is then
   rejected as a conflict still leaves a validator-attestation entry in the
   (process-scoped) timeline. No finality entry is written.
7. **CIEL identifiers are not transaction identity.** CIEL `event_id`,
   `correlation_id` and `trace_id` describe events and causality chains;
   `causation_id` is absent org-wide (ADR-0001 §6). They must reference the
   transaction identity, never substitute for it.

---

## 3. Definitions (normative once approved)

- **Idempotency key.** A request-scoped retry token chosen by the client for
  one *intent to pay*. Its only meaning: "if you have seen this before, give
  me the same outcome." It is not an identity and carries no economics.
- **Transaction identity (`TransactionId`).** The durable identifier of one
  economic transfer, for the lifetime of the platform. One per transfer,
  never reused, never reassigned.
- **Economic fingerprint.** A hash over the immutable economic fields (§6).
  Used to detect conflicts. Never used as an identity on its own.
- **Journal ID.** The ledger's identifier for the double-entry record that
  implements a transaction. One transaction → exactly one posted journal per
  ledger.
- **Receipt ID.** The identifier of an attestation *about* a settled
  transaction. Derived, never authoritative.
- **CIEL / trace / correlation IDs.** Observability and causality metadata.
  They reference a `TransactionId` and are never compared for idempotency.

## 4. Requirements

- **R1 (authority).** Exactly one component class mints `TransactionId` for a
  given channel. No downstream service mints a replacement.
- **R2 (representation).** `TransactionId` is versioned, namespaced,
  URL-path-safe, at most 128 characters, and validated identically everywhere.
- **R3 (idempotency).** The idempotency key maps to exactly one
  `TransactionId` within its namespace, permanently. Reusing a key with
  different economics is a conflict, never a new transaction and never a
  replay.
- **R4 (dual path).** Every live money-moving path either adopts the canonical
  identity or has a dated retirement decision.
- **R5 (persistence).** The ledger journal is the authority for economic
  facts. Dedupe and replay must survive restart without relying on process
  memory.
- **R6 (equivalence).** The fields that define "the same transaction" are
  fixed and enumerated (§6).
- **R7 (audit correctness).** A rejected request never produces
  authorization, validator-attestation or finality evidence. Rejections are
  recorded only as explicit rejection events.
- **R8 (propagation).** node-api, settlement-engine, ledger, CIEL, explorer,
  audit, validator-node and phone-wedge carry the same `TransactionId`
  unchanged.
- **R9 (compatibility).** The proven RC2-A behaviour (§2.1) keeps working
  throughout migration, without re-identifying existing journals.

---

## 5. Decisions and options

Each decision lists the options considered and the recommendation. Final
choices are recorded in §10.

### D1. Who mints `TransactionId`?

| Option | For | Against |
|---|---|---|
| a. The client mints it | Simplest; already true on RC2-A | An untrusted party owns platform identity; collisions across clients are possible |
| **b. The ingress service mints it** from (namespace, authenticated principal, client idempotency key) — node-api for citizen channels, the gateway for institutional | Identity is owned by the first trusted boundary; the client keeps control of retries | Requires a defined derivation and namespace per ingress |
| c. settlement-engine mints it | Close to finality | Too late: ingress, CIEL and audit have already referenced the transfer |
| d. The ledger mints it | Strongest persistence | Far too late; the ledger should enforce uniqueness, not create identity |

**Recommendation: (b).** The ledger keeps its UNIQUE constraint as the final
enforcement point.

### D2. Representation

**Recommendation:** a deterministic derivation, not a random ID:

```
TransactionId = "tx1." + <namespace> + "." + base32( SHA-256( namespace | principal_id | idempotency_key ) )[:32]
```

- Character set `[A-Za-z0-9._:-]`, at most 128 characters. This is compatible
  with the RC2-A `Idempotency-Key` bounds, the ledger's 256-character column
  (leaving room for its `reverse:` prefix) and URL paths.
- Deterministic, so it survives restart and works across multiple nodes with
  no coordination or lookup store.
- `principal_id` prevents two clients' identical keys from colliding.
- `tx1` versions the scheme, so a future change never collides with
  existing IDs.
- Required by doctrine: `PRODUCTION_PRINCIPLES.md` §1 (no wall-clock
  dependence on consensus-critical paths) and §2 (replay is the foundation of
  audit). Core's `Transaction.compute_hash()`, which includes a uuid4 and a
  wall-clock `created_at`, does not meet §1 and cannot serve as identity.

Alternative: mint a ULID or UUIDv7 and persist an (namespace, principal, key)
→ id mapping. This gives time-ordered IDs but adds a durable mapping store
that becomes part of the money path. Not recommended.

### D3. Is the idempotency key the `TransactionId`?

**Recommendation: no, it is mapped to one** via D2. RC2-A's current
`transaction_id = K` is retained as **compatibility mode v0** (D10).

### D4. `/transfers/execute`: adopt or retire?

This path carries the richest risk controls on the platform (preview,
confirmation, fraud decision bands, validator quorum, state attestations), so
retiring it would remove controls RC2-A doesn't have.

**Recommendation: adopt the canonical identity.** Require a client
`Idempotency-Key` at `prepare` and derive the `TransactionId` from it. Ledger
convergence is deferred to ADR-0004. Path-specific defects found during this
investigation are fixed on their own tracks (§9) and are not deferred to this
migration.

### D5. Persistence and replay authority

**Recommendation:**

- The **ledger journal** is the authority for economic facts: amount,
  currency, debit and credit accounts, posted status.
- The **replay authority** is the ledger's UNIQUE idempotency constraint plus
  the economic-fingerprint check. Process caches are optimizations only.
- **Receipts are derived:** `receipt_id` is a deterministic function of
  (`TransactionId`, `journal_id`, journal hash), so a replay after restart
  reproduces the same receipt instead of minting a new one.

### D6. Economic equivalence (what must match on replay)

**Included:** `currency`, `amount_minor` (canonical Money, ADR-0002), payer
principal, payee principal, channel namespace, and fee schedule outcome.
Once account resolution is durable, resolved payer and payee *ledger
accounts* are added.

**Excluded:** timestamps, request, trace and correlation IDs, signatures,
display names, device metadata, and receipt or journal IDs.

RC2-A today compares amount and currency only, because its demo account
mapping is process-scoped. That is acceptable for v0 but not for the
canonical contract.

### D7. What is a conflict?

Same `TransactionId` and **any** field in §6 differs: respond 409 with no
state write of any kind (journal, finality, settlement audit, or
authorization or attestation timeline). The rejection may be recorded once,
as an explicit `request.rejected.idempotency_conflict` event that references
the `TransactionId`.

### D8. Receipt fields that must come from persisted state

Amount, currency, debit and credit accounts, `journal_id`, ledger hash,
posted status and finality reference are read from the journal and finality
record. **Never** from the request. The request may only supply the
`TransactionId` used to look them up.

### D9. Restart and recovery

- Identity derivation is stateless (D2), so nothing needs recovering.
- Dedupe is enforced by the ledger. The crash window (journal proposed, not
  posted) is completed only after the economic check passes. This is already
  implemented in settlement-engine #9.
- Receipt identity is reproducible (D5).
- Demo account mapping must become durable before §6 adds resolved accounts
  to the equivalence check.

### D10. Compatibility with RC2-A

| Option | Meaning |
|---|---|
| **a. Namespace v0 = identity** | For the RC2-A namespace, existing IDs are the raw K. New clients may opt into `tx1.` IDs. Lookup recognizes both forms by prefix, and no journal is ever re-keyed. |
| b. Re-key | Migrate existing journals to `tx1.` IDs. Rejected: it rewrites ledger history. |

**Recommendation: (a).** The `tx1.` prefix makes legacy and canonical IDs
syntactically distinguishable forever.

### D11. Cross-service propagation

| Component | Obligation |
|---|---|
| node-api | Derive the `TransactionId` at ingress; forward it unchanged; reject a receipt carrying a different ID (already true on RC2-A) |
| institutional-gateway | Derive the `TransactionId` from its existing key priority; keep binding it into the CIEL signature |
| settlement-engine | Never mint; use the caller's ID as `deterministic_transaction_id`; derive receipts per D5 |
| ledger | Enforce UNIQUE; expose lookup by `TransactionId` |
| validator-node | Attest over the `TransactionId` it was given; never invent one |
| CIEL / audit / explorer | Reference the `TransactionId`; keep `event_id`/`correlation_id` separate; record rejections per D7 |
| phone-wedge and other citizen apps | Generate one idempotency key per user *intent to pay*, at preview time; resend it on every retry; never regenerate it on retry |

### D12. Institutional content-hash fallback

The gateway falls back to a full-content hash when a bank supplies no key.
**Recommendation:** keep it only because it includes a bank-unique business
reference (`trade_id`) and settlement date. State the general rule: **a
content hash may serve as an idempotency key only if it includes a
caller-unique business reference.**

---

## 6. Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Migration re-identifies existing journals | low with D10(a) | critical (history rewrite) | Never re-key; prefix-versioned IDs |
| A distinct payment is treated as a retry (false success) | present (tracked privately) | critical | Independent bug-fix track; D3 + D12 rule |
| A retry is treated as a new payment (double post) | latent on a default-off path (tracked privately) | critical | Ledger UNIQUE on canonical ID; no process-memory-only dedupe |
| Dual ledgers report "settled" for different facts | present | high | ADR-0004 (ledger authority) |
| Audit shows attestation for a rejected request | present (process-scoped) | medium–high for regulator evidence | D7 |
| Receipt identity unstable across restart | present | medium | D5 deterministic receipts |
| Cross-tenant key collision | possible under D1(a) | high | `principal_id` in the D2 derivation |
| Freeze violation by scope creep | medium | governance | Gate 2 per wave; this ADR authorizes nothing |

## 7. Migration options

**A. Contract first (recommended).** Specify `TransactionId` in
`cubeshackles.contracts` (Core) as a pure validation and derivation module
with conformance tests, then move consumers one at a time: the ADR-0002
pattern.

**B. Path first.** Fix each path's identity locally and converge later.
Faster, but it reproduces the copy-drift problem ADR-0002 just resolved for
Money.

**C. Big bang.** Rejected: it touches every money path simultaneously during
a feature freeze.

## 8. Proposed waves (each requires separate Gate 2 authorization)

| Wave | Content | Freeze class |
|---|---|---|
| I-0 | Privately tracked path-specific defect fixes (independent bug track; not dependent on this ADR) | `freeze:allowed` (bug fix) |
| I-1 | `TransactionId` contract module + conformance tests in Core; no consumer changes | `freeze:exception-required` (new frozen contract) |
| I-2 | RC2-A: accept `tx1.` IDs alongside v0 (D10); deterministic receipts (D5) | exception-required if response shape changes, else allowed |
| I-3 | `/transfers/*`: `Idempotency-Key` at prepare, derive the `TransactionId` | `freeze:exception-required` (API change) |
| I-4 | Audit correctness (D7) in settlement-engine and the CIEL hub | `freeze:allowed` (compliance/correctness) |
| I-5 | phone-wedge propagation (with its missing platform-write auth) | allowed (bug/security) + exception for the new header |
| I-6 | Institutional reconciliation (D11/D12) after the HTTP-ledger replay item (§9) is verified | per change |

## 9. Independently tracked (not absorbed by this ADR)

- **F-1 (P0, live):** a path-specific idempotency defect in which distinct
  payments can be conflated. Tracked in a private issue; fixed on its own bug
  track (wave I-0).
- **F-2 (P1, latent):** a path-specific restart-safety gap on a default-off
  path. Tracked in a private issue; investigation only.
- **Institutional HTTP ledger replay economics:** unverified (RC2-A residual D).
- **node-api test-suite baseline debt:** 9 failures and 2 collection errors
  pending founder design decisions.
- **RC2-A self-asserted `validation_decision`:** clearing and compliance
  enforcement remain off by default (RC2-A residual B).

## 10. Founder decision record

| # | Decision | Recommendation | Founder decision |
|---|---|---|---|
| D1 | Identity authority | Ingress mints (node-api citizen, gateway institutional) | ☐ |
| D2 | Representation | `tx1.<ns>.<base32(sha256(ns\|principal\|key))[:32]>` | ☐ |
| D3 | Idempotency key vs identity | Mapped, not identical; RC2-A v0 kept | ☐ |
| D4 | `/transfers/execute` | Adopt canonical identity; ledger question → ADR-0004 | ☐ |
| D5 | Persistence / replay authority | Ledger journal authoritative; deterministic receipts | ☐ |
| D6 | Equivalence fields | As listed in §5 D6 | ☐ |
| D7 | Conflict definition | Any §6 field differs → 409, zero state writes, explicit rejection event | ☐ |
| D8 | Receipt derivation | All economic receipt fields from persisted state | ☐ |
| D9 | Restart / recovery | Stateless derivation + ledger UNIQUE + verified crash-window completion | ☐ |
| D10 | RC2-A compatibility | Namespace v0 = identity; never re-key | ☐ |
| D11 | Propagation obligations | As tabled | ☐ |
| D12 | Content-hash rule | Allowed only with a caller-unique business reference | ☐ |
| — | Migration approach | Option A (contract first) | ☐ |
| — | Open ADR-0004 (ledger authority) | Yes | ☐ |

## 11. Out of scope

Ledger unification (ADR-0004), CIEL Family A/B convergence (ADR-0001 §6),
Money migration waves 2+ (ADR-0002), and any change to the RC2-A rail beyond
what an authorized wave specifies.
