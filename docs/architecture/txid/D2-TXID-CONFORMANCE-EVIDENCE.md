# ADR-0003 D2 conformance evidence (investigation)

**Date:** 2026-10-10
**Authorization:** generate the frozen candidate encoding and test vectors. No production identity change. No `TransactionId` module in a service.
**Status of the format:** **RECOMMENDED**, not founder-finalized, not implemented. Gate 3 remains **not authorized**.

The candidate wire shape is unchanged:

```text
tx1.<namespace>.<base32(sha256(preimage))[:32]>
```

The hash input is revised. A raw `namespace|principal|key` join is ambiguous if any field can contain `|`. The recommended preimage is length-prefixed:

```text
CS-TXID-v1 NUL
u32be(length) || UTF-8 NFC(namespace)
u32be(length) || UTF-8 NFC(principal)
u32be(length) || UTF-8 NFC(idempotency_key)
```

Base32 is RFC 4648, no padding, lowercased. Truncation keeps the first 32 characters (160 bits).

`docs/architecture/txid/reference_txid.py` generated `vectors.json`. `verify_vectors.mjs` recomputed the same four ids in Node. Both are investigation tools. Neither is imported by a service.

## C1–C10

| # | Evidence | Result |
|---|---|---|
| C1 | One encoding id, `cs-txid-v1-length-prefix`. Python and Node emit the same ids. | Met for this recommendation |
| C2 | `c2-domain-a` (`namespace=ab`, `principal=citizen:c`) and `c2-domain-b` (`namespace=a`, `principal=citizen:bc`) produce different ids. A principal containing `\|` is rejected. | Met |
| C3 | Principal is `citizen:` or `institution:` plus an ASCII stable id. Display names, phone-shaped values, and non-ASCII ids are rejected. Accepted inputs are ASCII, so NFC does not change them. | Met as a rejection rule |
| C4 | The key alphabet is 66 characters (`A–Z`, `a–z`, `0–9`, `.`, `_`, `:`, `-`). The minimum length is 22, about 133 bits when every character is uniform. A shorter key is rejected. The same inputs always return the same id. A conflicting economic replay stays D7 and is not implemented here. | Met for the length floor |
| C5 | 160-bit truncation. Approximate birthday bound `n(n-1)/2^161`: about `1e-30.5` at one billion ids and `1e-24.5` at one trillion. A second distinct preimage that truncates to an existing id must be rejected and not posted. The ledger UNIQUE constraint remains the backstop. That rejection path is specified, not built. | Quantified; enforcement not built |
| C6 | 32 base32 characters keep 160 bits. That is above a 128-bit uniqueness target and keeps the wire id inside the existing 128-character bound. The full digest is not required for the margin these volumes imply. | Rationale recorded |
| C7 | Four vectors reproduced byte-for-byte by Python and Node. No other language was checked, because this investigation did not find another identity implementation to bind. | Met for Python and Node |
| C8 | The enforcement point stays the authoritative ledger UNIQUE constraint from ADR-0004. A conflict is a typed rejection (D7), not a second id. | Specified; not built |
| C9 | `tx1.` classifies as canonical. `idem-rc2a-example-key-0001` classifies as `rc2a-v0` and is not rewritten. | Met on the example |
| C10 | `tx2.` classifies as `future-version` and this encoder does not mint it. A later version needs its own preimage label. | Policy recorded |

## Recommendation

Adopt the length-prefixed preimage and the wire shape above as the D2 candidate. Do not treat this file as a finalized contract and do not implement it in a service until Gate 3 is separately authorized.

## What did not change

No production identifier, journal, route, or credential was read or written.
