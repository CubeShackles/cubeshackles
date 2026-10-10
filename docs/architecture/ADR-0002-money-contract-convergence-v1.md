# ADR-0002: Money Contract Convergence V1 — Governance Authorization

**Status:** AUTHORIZED, Wave 1 executing.
**Date:** 2026-10-06
**Milestone:** `MONEY-CONTRACT-CONVERGENCE-V1` (GitHub milestone, created in `Cubeshackles-core` and `cubeshackles-institutional-gateway`; will be added to `cubeshackles-ledger`, `cubeshackles-settlement-engine`, `cubeshackles-cubereg` in later waves if authorized).
**Supersedes:** Nothing. Resolves the "Money ownership" item left `UNRESOLVED` in `ADR-0001-canonical-authority.md` primitive #1.

## Purpose

Converge the already founder-designated canonical Money primitive —
`Money(currency: str, amount_minor: int)`, as it exists today in
`cubeshackles-institutional-gateway/src/institutional_gateway/money.py` —
onto the existing `cubeshackles.contracts` distribution mechanism in
`Cubeshackles-core`, without changing Money semantics, external service
contracts, HTTP boundaries, CIEL/security boundaries, or service
deployability.

This milestone exists because changing physical contract authority and
adding a shared package dependency can affect dependency topology even
where runtime behavior is unchanged — it is treated as an explicitly
authorized architecture-convergence operation under the org's existing
feature-freeze governance, not an exception to it.

## Why this, and why now

Per the Money Contract Provenance investigation (this session, read-only):
institutional-gateway's `Money(currency, amount_minor)` shape is already
founder-designated canonical — evidenced verbatim in `cubeshackles-cubereg`'s
own port docstring, which quotes the instruction "You already have the
canonical primitive: Money(currency, amount_minor). Use it." That
designation was never backed by an actual shared package, so `ledger` and
`settlement-engine` independently re-created the identical shape rather
than depending on it. All three copies are confirmed byte-identical
(MD5 `9e0c943c6a6cc7722139850a2a0a7457`) as of this ADR.

`Cubeshackles-core`'s `cubeshackles.contracts` package is the only
mechanism in the org that is both (a) genuinely pip-installable
(real `[build-system]`, setuptools) and (b) already consumed by 9 real
repos today. Placing Money there is reuse of an existing, proven
mechanism — not the creation of a 4th contracts mechanism alongside the
standalone `cubeshackles-contracts` JSON-schema repo, Core's own
`contracts/ontology` subpackage, and any SDK repo.

## Scope — Allowed

- Add a canonical Money module to the existing `cubeshackles.contracts` package.
- Add contract/equivalence tests proving behavioral identity with the pre-migration source.
- Migrate one consumer at a time, starting with `cubeshackles-institutional-gateway` (the founder-designated source shape).
- Change imports/dependency declarations strictly as required to consume the existing package.
- Delete a consumer's local Money implementation only after equivalence is proven.
- Add a narrowly scoped drift/conformance test.

## Scope — Forbidden

- Any Money semantic change (fields, types, currency registry, rounding behavior, precision bound).
- Any wire-schema or HTTP/API change.
- Any CIEL, authentication, signing, or authorization change.
- Service mergers or monorepo conversion.
- A new shared-package architecture (a 4th contracts mechanism).
- Broad dependency cleanup or unrelated refactors.
- Migrating `cubeshackles-ledger`, `cubeshackles-settlement-engine`, or `cubeshackles-cubereg` in this wave — those are explicitly deferred to later, separately authorized waves.

## Frozen Money contract (restated, not redefined)

```python
Money(currency: str, amount_minor: int)  # frozen dataclass
```
- Integer minor units are the canonical, hashed, compared, persisted identity. `Decimal` is the human-facing I/O form only. No binary float anywhere in monetary arithmetic.
- `CURRENCY_REGISTRY`: AOA(2), USD(2), EUR(2), JPY(0), BHD(3). Unknown/unsupported currency fails explicitly (`UnsupportedCurrencyError`).
- `normalize_amount()`: the one normalization path. Rejects comma-grouped input, malformed/non-finite values, and excess precision (no implicit rounding, ever). `MAX_ABS_MINOR_UNITS = 10**18`.
- `digest_fields()` exposes exactly `{currency, amount_minor}`.
- Equality/hash: dataclass field equality on `(currency, amount_minor)`.

This ADR authorizes moving this exact shape, not redesigning it.

## Wave plan

- **Wave 1** (this authorization): establish canonical authority in `Cubeshackles-core`; migrate `cubeshackles-institutional-gateway` as first consumer. Hard stop after Gateway merges and canonical verification completes.
- **Wave 2+** (not authorized by this ADR — requires separate founder authorization): migrate `cubeshackles-ledger`, `cubeshackles-settlement-engine`, `cubeshackles-cubereg` one at a time, same equivalence-before-deletion discipline.

## Non-negotiable invariants preserved

AOA-first behavior; deterministic monetary semantics; current HTTP service boundaries; current CIEL security boundary; service deployability; existing wire compatibility; all frozen security/governance invariants (Pilot Rail baseline, Post-Remediation Canonical Security Baseline V1 — neither touched by this change).
