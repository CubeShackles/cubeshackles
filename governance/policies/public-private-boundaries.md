# Public / Private Boundaries Policy

**Applies to:** All CubeShackles repositories.

---

## Visibility classes

| Class | May contain | Must not contain |
|---|---|---|
| **Public** | Truthful architecture, protocol code, contract schemas, developer docs | Secrets, fraud models, regulator tooling, sovereign orchestration logic, production credentials |
| **Private** | Sovereign AI, compute topology, hardware R&D, credit intelligence (`kulifikila`) | Misrepresentation of public protocol behavior |
| **Mixed / partial public** | Public interfaces; private implementation | Undocumented leakage of private logic through public APIs |

## Public repository list (protocol & access)

Includes: `cubeshackles`, `cubeshackles-contracts`, `cubeshackles-core`,
`cubeshackles-validator-node`, `cubeshackles-node-api`,
`cubeshackles-network-orchestrator`, `cubeshackles-integration`, access-layer apps,
and scaffolded public repos (`runtime`, partial `observability` interfaces).

## Private repository list (sovereign)

Includes: `cubeshackles-ai-runtime`, `cubeshackles-compute`, `cubeshackles-hardware`,
`kulifikila`.

## Interface rule

Public repos may **reference** private capabilities at the interface level (e.g.
"advisory risk signal consumed as recorded input") without exposing implementation,
weights, or sovereign deployment details.

## Mirrors and forks

Private logic is not published to public mirrors. Contract **shapes** for advisory
messages live in `cubeshackles-contracts`; model weights and training data do not.

## Angola-first deployment

Public documentation describes Angola-native, offline-first assumptions. Private
repos may hold deployment-specific capacity and topology data that must not be exposed.
