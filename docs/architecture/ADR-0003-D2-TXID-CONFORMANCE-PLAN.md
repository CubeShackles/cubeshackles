# ADR-0003 D2 — TransactionId Contract-Conformance Investigation Plan (DESIGN ONLY)

**Status:** PROPOSED — investigation authorized; **implementation NOT authorized.**
**Date:** 2026-10-10
**Resolves the D2 condition:** finalize the exact `tx1` wire format only after these pass.
**Candidate format (not final):** `tx1.<namespace>.<base32(sha256(namespace | principal | idempotency_key))[:32]>`

The exact wire representation stays conditional. This plan defines the conformance evidence required before any `TransactionId` module is built. No code is authorized.

## Conformance requirements & how each is proven

| # | Requirement | Investigation | Pass condition |
|---|---|---|---|
| C1 | Canonical encoding | define the exact byte encoding of each field (UTF-8 NFC? case? separators) and the output alphabet (base32 RFC4648 no-pad, lowercased?) | one documented encoding; a reference vector set reproduces identical output |
| C2 | Domain separation | the hash input must be unambiguous — length-prefixed or a reserved non-occurring separator so `a|b` ≠ `a'|b'` for any field values | proof that no two distinct field tuples collide via separator ambiguity |
| C3 | Principal normalization | define how the authenticated principal is normalized (institution id vs citizen subject vs phone) before hashing; forbid mutable display names | one normalization function; same principal → same bytes across channels |
| C4 | Key entropy | the idempotency key's entropy/uniqueness assumptions; what a client must guarantee; server behavior on low-entropy or reused keys | documented minimum; reuse handled per D3/D7 (map or conflict, never silent new tx) |
| C5 | Collision behavior | sha256 truncated to 32 base32 chars = 160 bits; analyze birthday bound at projected volumes; define behavior on the (astronomically rare) truncated collision | quantified collision probability; a defined detection/rejection path (ledger UNIQUE is the backstop) |
| C6 | Truncation analysis | justify `[:32]` vs full digest; show it preserves the security margin for the identity namespace | documented rationale + margin |
| C7 | Cross-language determinism | the same inputs must produce the same id in every implementation language in the stack (Python today; others if any) | a shared vector file; each language reproduces every vector byte-for-byte |
| C8 | Persistent uniqueness enforcement | which store enforces uniqueness (the authoritative ledger's UNIQUE idempotency key per ADR-0004) and how collisions surface | one enforcement point; typed conflict on violation |
| C9 | Legacy RC2-A compatibility | existing RC2-A ids remain valid as namespace v0; the `tx1.` prefix makes new vs legacy syntactically distinguishable; never re-key history | prefix check recognizes both; no historical journal re-keyed |
| C10 | Versioning | `tx1` version token; how a future `tx2` coexists without collision | documented version policy |

## Deliverable of the investigation (design only)
- A conformance spec with a frozen encoding and a canonical **test-vector file** (inputs → expected id), usable later as a cross-language conformance suite.
- A recommendation to finalize or revise the candidate format.
- No `TransactionId` module is built until the founder reviews the conformance evidence (this remains Gate 3 territory).

## Relationship to gates
C1–C10 are **prerequisites to Gate 3 contract development** for the identity module — they can be completed before any staging cutover, because they do not touch monetary posting authority. They do **not** require CG-1..CG-9.
