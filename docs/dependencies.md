# Dependencies — `cubeshackles` (umbrella)

**Repository role:** Canonical source of truth (documentation and governance only).

---

## Runtime dependencies

None. This repository contains no application code, no Python/Node services, and no
deployable artifacts.

## Repository dependencies (documentation)

| Repository | Required? | Relationship |
|---|---|---|
| `cubeshackles-contracts` | reference | Defines interoperability rules and schema ownership; umbrella docs must not contradict |
| All platform repos | inventory | Described in [`REPOSITORY_MAP.md`](../REPOSITORY_MAP.md); maturity tracked honestly |

## Contract consumption

| Contract family | Version | Consumed how |
|---|---|---|
| Platform-wide interoperability standard | v0.1 draft | Referenced in governance and contributor docs |
| Individual JSON/OpenAPI schemas | — | **Not consumed** — no code path |

## Contract emission

The umbrella **does not emit** versioned platform events or API payloads.

## Development layout

Sibling checkout layout is documented in [`developer-entrypoint.md`](developer-entrypoint.md).
Cloning this repository alone is sufficient to read architecture and governance.

## Security

- No `.env`, credentials, or key material.
- No private sovereign logic.
- Vulnerability reports follow [`SECURITY_MODEL.md`](../SECURITY_MODEL.md).

## Related files

- [`../contracts/CONTRACTS.md`](../contracts/CONTRACTS.md)
- [`../docs/repo-governance.md`](repo-governance.md)
- [`../../cubeshackles-contracts/VERSIONING_POLICY.md`](../../cubeshackles-contracts/VERSIONING_POLICY.md) (sibling)
