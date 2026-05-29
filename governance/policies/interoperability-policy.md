# Interoperability Policy

**Applies to:** Every repository that sends or receives platform messages.  
**Authoritative schemas:** `cubeshackles-contracts`  
**Enforcement:** `cubeshackles-integration` (when gates are extended)

---

## Single source of truth

1. All shared message shapes are defined **only** in `cubeshackles-contracts`.
2. Repositories reference contracts by **name and version** (e.g. `transaction.initiated.v0.1`).
3. Local copies of schemas are prohibited except generated stubs explicitly tied to a
   pinned version.

## Per-repository declarations

Each implementing repository must maintain:

- `contracts/CONTRACTS.md` — own / consume / emit
- `docs/dependencies.md` — repo and contract dependencies
- README section linking to `cubeshackles-contracts`

The umbrella repository satisfies this policy via its own declarations (documentation
only).

## Versioning

Follow [`VERSIONING_POLICY.md`](../../../cubeshackles-contracts/VERSIONING_POLICY.md)
in the contracts repository. Breaking changes require version bumps and coordinated
integration updates.

## Financial messages

- Native settlement currency: **AOA** (Angolan Kwanza), unless a contract explicitly
  documents another regional currency for a specific product surface.
- Required envelope fields per `INTEROPERABILITY_STANDARD.md` (`schema_version`,
  `event_id`, `event_type`, `occurred_at`, deterministic identifiers where applicable).

## Advisory messages

AI and credit-intelligence outputs are **advisory** contract types. Consumers must
treat them as recorded inputs to deterministic rules, never as settlement authority.

## Compliance verification

A repository is interoperability-compliant when:

1. Its declarations are current.
2. It does not redefine owned contract types elsewhere.
3. `cubeshackles-integration` tests pass for its declared boundaries (when covered).

Full standard: [`INTEROPERABILITY_STANDARD.md`](../../../cubeshackles-contracts/INTEROPERABILITY_STANDARD.md).
