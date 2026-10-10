# ADR-0003 D2 conformance evidence (proposed)

**Date:** 2026-10-10
**Status:** `D2_FORMAT = PROPOSED`
**Authorization:** investigation and test-vector generation only. No production identity change. No service module.

This package is not an independent review and it does not finalize the format. Python and Node agreement shows that two implementations of this proposal match. It does not close conformance.

## Proposed encoding

Wire id:

```text
tx1.<namespace>.<base32(full 256-bit SHA-256 digest)[:32]>
```

Preimage, length-prefixed rather than joined on `|`:

```text
CS-TXID-v1 NUL
u32be(length) || UTF-8 NFC(namespace)
u32be(length) || UTF-8 NFC(principal)
u32be(length) || UTF-8 NFC(idempotency_key)
```

Base32 is RFC 4648, no padding, lowercased. The first 32 characters are 160 bits. The other characters of that base32 string are the rest of the same 256-bit digest. The wire id is not a second hash.

`reference_txid.py` writes `vectors.json`. `verify_vectors.mjs` recomputes every wire id, the full digest, and the truncation. Both tools stay outside node-api, settlement-engine, and the ledger.

## Field rules

| Field | Canonical rule | Rejection |
|---|---|---|
| Namespace | NFC, then `^[a-z][a-z0-9_-]{0,31}$` (1–32 characters). No case folding. | `namespace_rejected` |
| Principal | NFC, then `citizen:` or `institution:` plus 1–128 ASCII characters from `[A-Za-z0-9._:-]`. Stable subject id only. | `principal_rejected` |
| Idempotency key | NFC, then 22–128 characters from the 66-character alphabet `A–Z a–z 0–9 . _ : -`. | `idempotency_key_rejected` |

Accepted values are ASCII, so NFC does not change them. A display name, a phone-shaped principal, and a non-ASCII principal are rejected rather than folded into an id.

The 66-character alphabet at 22 uniform characters is about 133 bits. A canonical UUID v4 is 36 characters, so it passes the length floor, and its own entropy is 122 bits. Those are different statements. A key shorter than 22 characters is rejected. This encoder does not mint a replacement id for a rejected key.

The same namespace, principal, and key always return the same full digest and the same wire id (`c1-canonical` and `c1-repeat`). A conflicting economic replay is D7: a typed conflict, no second id, no ledger mutation. This encoder has no economic fields, so it does not emit that conflict.

## Domain separation

`c2-domain-a` (`namespace=ab`, `principal=citizen:c`) and `c2-domain-b` (`namespace=a`, `principal=citizen:bc`) differ in both the 256-bit digest and the 160-bit wire id.

A raw `|` join of (`a|b`, `c`, `d`×22) is the same byte string as (`a`, `b|c`, `d`×22). The length-prefixed preimage of those two tuples hashes to two different digests. The accepted alphabet also rejects `|` inside a principal, so that ambiguous pair cannot be minted as a `tx1` id.

## Collision properties

| Object | Size | Approximate birthday bound at 1e9 ids | at 1e12 ids |
|---|---|---|---|
| Full SHA-256 digest | 256 bits | `1e-59.4` | `1e-53.4` |
| Wire truncation | 160 bits | `1e-30.5` | `1e-24.5` |

The bound is `n(n-1)/2^(bits+1)`. A collision of the wire id is a 160-bit event even when the digest is 256 bits. Detecting that case means storing the full digest beside the wire id and rejecting a second distinct digest that truncates to the same 32 base32 characters. That store is specified here and is not built. The ledger UNIQUE constraint remains the backstop from ADR-0004. It is not implemented by this pull request.

## Legacy v0

| Input | Class | Action |
|---|---|---|
| A `tx1.` id matching the wire pattern | `tx1` | Recognized. Not a reason to rewrite history. |
| `idem-rc2a-example-key-0001` | `rc2a-v0` | Left unchanged. RC2-A identity stays the raw key. |
| `tx2.`… | `future-version` | Recognized. This encoder does not mint it. |
| `tx1.` that fails the wire pattern | `ambiguous` | Not treated as v0 and not rewritten. |

## What this does not close

Independent review of the proposal. Founder finalization. A `TransactionId` module. Gate 3. Any production identity write.
