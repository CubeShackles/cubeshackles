# Repository Map Summary (v0.1)

Authoritative inventory: `REPOSITORY_MAP.md` at repository root.

## Protocol layer

- `cubeshackles-contracts` — canonical v0.1 schemas and events
- `cubeshackles-core` — protocol logic
- `cubeshackles-validator-node` — validation authority
- `cubeshackles-settlement-engine` — settlement / finality boundary
- `cubeshackles-offline-infrastructure` — offline queue and sync boundary
- `cubeshackles-runtime` — execution orchestration
- `cubeshackles-node-api` — API ingress
- `cubeshackles-integration` — cross-repo gates (no production traffic)

## Feature-freeze boundaries (v0.1)

Settlement, offline, provincial topology, vault, disaster recovery, chaos, security,
operations, and Angola pilot repos are scaffolded boundaries — not national deployments.

No new repositories beyond the RC-1 closed inventory.
