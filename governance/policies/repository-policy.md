# Repository Policy

**Applies to:** Every repository in the CubeShackles platform.  
**Canonical owner:** `cubeshackles` (this umbrella repository).

---

## Purpose

Define how repositories are created, named, classified, and promoted through maturity
stages so that architectural boundaries remain enforceable as the platform grows.

## Requirements

1. **Single layer per repo.** Each repository has exactly one primary architectural
   layer (see [`docs/repo-governance.md`](../../docs/repo-governance.md)).
2. **Honest maturity.** Status must be one of: planned, scaffolded, active,
   integrated, production-ready. Scaffolded repositories are not "active."
3. **README contract.** Every repo README states layer, visibility, maturity, and what
   the repo is **not**.
4. **Canonical record.** Changes to existence, role, visibility, or maturity update
   [`REPOSITORY_MAP.md`](../../REPOSITORY_MAP.md) and, when structural,
   [`SYSTEM_ARCHITECTURE.md`](../../SYSTEM_ARCHITECTURE.md).
5. **Isolation commit.** New infrastructure repos are first committed in isolation;
   integration is a deliberate later step.

## Prohibited

- Creating a repository without layer and visibility classification.
- Marking a scaffold as production-ready.
- Mixing consensus-critical code with sovereign AI/compute models in one repo without
  a documented, enforced module boundary (default: do not mix).

## Promotion

Advancement through maturity stages requires explicit review. Integration into
`cubeshackles-integration` gates is mandatory before a repo is marked **integrated**.

## Related policies

- [`security-boundaries.md`](security-boundaries.md)
- [`public-private-boundaries.md`](public-private-boundaries.md)
- [`interoperability-policy.md`](interoperability-policy.md)
