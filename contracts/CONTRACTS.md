# Contract boundaries — `cubeshackles` (umbrella)

**Layer:** Canonical / doctrine  
**Maturity:** active (documentation only — no protocol messages emitted)

This repository does not implement protocol logic or run production traffic. It owns
**no** versioned message schemas. Cross-repository contracts are defined in
[`cubeshackles-contracts`](https://github.com/biu-gholdings/cubeshackles-contracts).

---

## What this repository owns

| Asset | Description |
|---|---|
| Doctrine & architecture | `README.md`, `SYSTEM_ARCHITECTURE.md`, `REPOSITORY_MAP.md`, principles, security model |
| Governance | `docs/repo-governance.md`, `governance/policies/` |
| Contract references | Links and requirements; not schema definitions |

## What this repository consumes

| Source | Version | Purpose |
|---|---|---|
| `cubeshackles-contracts` | v0.1 (reference) | Authoritative definitions for how sibling repos must interoperate; umbrella docs must stay aligned with the interoperability standard |

The umbrella does **not** import or validate schemas at runtime.

## What this repository emits

| Output | Contract? |
|---|---|
| Markdown documentation | No versioned event/API contracts |
| Governance policy | No machine-readable platform messages |

## Private vs public

- **Public:** All content in this repository.
- **Private:** None. No secrets, models, or sovereign orchestration logic.

## Integration tests

`cubeshackles-integration` may check that umbrella documentation references required
repos and contract discipline. The umbrella itself is not a producer in the event bus.

## Maintainer rules

1. When contract requirements change, update [`docs/dependencies.md`](../docs/dependencies.md) and this file.
2. Do not copy schemas from `cubeshackles-contracts` into this tree.
3. Record architectural changes in [`docs/architecture-consistency-audit.md`](../docs/architecture-consistency-audit.md) when remediations apply.

See also: [`../docs/dependencies.md`](../docs/dependencies.md).
