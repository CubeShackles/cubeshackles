# Core contract scope (preparation only)

**Date:** 2026-10-10
**Status:** `GATE_3_AUTHORIZED = NO`
**This document requests scope. It does not implement it.**

Before Gate 3, Core's contract surface is exactly the six items below. Core defines them. Core does not become a second monetary posting authority. Journals, settlement, route selection, and balance migration stay outside this scope.

## What Core owns

1. **TransactionIdentity type.** A value that is either a proposed `tx1` wire id or a legacy RC2-A v0 id. The type carries the class from the D2 recognizer. It does not carry a balance.
2. **Serialization and validation.** The proposed D2 field rules: NFC, the namespace pattern, the `citizen:` / `institution:` principal, and the 22–128 character idempotency key. Invalid input is a typed rejection. It is not coerced into an id.
3. **Deterministic derivation.** The proposed length-prefixed preimage and `tx1.<namespace>.<base32(full SHA-256)[:32]>` wire form. Derivation is a pure function of namespace, principal, and idempotency key. `D2_FORMAT` stays **PROPOSED** until independent review. This scope does not finalize it.
4. **Economic-fingerprint contract.** A separate value from the transaction id (D3). Fields, from D6: currency, `amount_minor` as an integer, stable payer account, stable payee account, channel, fee outcome, and a durable business reference. Display names are not fields. The fingerprint is for conflict detection. It is not a posting instruction.
5. **Legacy identity compatibility.** RC2-A v0 ids remain the raw key. Nothing in this scope re-keys a historical journal.
6. **Conformance tests.** The vector file under `docs/architecture/txid/` is the investigation suite a later Core module would have to reproduce. Those tests are not a service, and they are not wired into a repository that posts money.

## What Core does not own

- Posting a journal, proposing a journal, or choosing Ledger A versus Ledger B.
- Settlement, clearing, or route switching.
- Customer balances, production credentials, or a staging deployment.
- Minting identity inside the ledger. The ledger enforces uniqueness. Ingress derives the id.

`cubeshackles-core` remains the named authority for economics, ledger replay, and fee governance in the repository map. That sentence is the existing map role. This scope does not add a posting path to it.

## Remaining evidence before a Gate 3 authorization

- Independent review of the proposed D2 encoding, including the 256-bit digest versus the 160-bit wire id.
- Founder acceptance of this scope.
- A granted feature-freeze exception. The request is separate and is not granted here.
- An implementation plan that names the module and the tests, still without a monetary write.

Until those exist, Gate 3 implementation stays unauthorized.
