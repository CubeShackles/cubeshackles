# Repository Governance

**How CubeShackles repositories are created, named, documented, secured, classified,
and integrated into the canonical architecture.**

This document is binding. Any new repository in the CubeShackles platform must
follow this process. Its purpose is to keep strict architectural boundaries from day
one — protocol-facing repositories must never blur into sovereign/private layers, and
no repository may be created with implied maturity it has not earned.

---

## 1. Principles

1. **Boundaries before code.** A repository's layer, role, and visibility are decided
   and recorded *before* substantive code is written.
2. **Unequal maturity is correct.** Repositories are created at the maturity they
   actually have. A scaffolded repository is labeled scaffolded, not "active."
3. **No premature integration.** A new repository is not wired into the protocol or
   into other repositories until it is deliberately promoted (see §7).
4. **Honesty of claims.** Use "implements/provides" only for what exists; use
   "designed for/intended to/planned" otherwise. No fake decentralization, no
   unearned production-readiness, no vendor lock-in language.
5. **One source of truth.** The umbrella repository (`cubeshackles`) is canonical.
   Architecture, repo map, and standards live here.

## 2. Architectural layers

Every repository belongs to exactly one primary layer. Mixing layers in one
repository is prohibited.

| Layer | Purpose | Examples |
|---|---|---|
| **Canonical** | Doctrine and source of truth (no protocol code) | `cubeshackles` |
| **Contracts** | Versioned schemas, events, OpenAPI; no runtime traffic | `cubeshackles-contracts` |
| **Protocol & execution** | Consensus-critical logic and validator execution | `cubeshackles-core`, `cubeshackles-validator-node`, `cubeshackles-runtime` |
| **API & coordination** | External interface and network coordination | `cubeshackles-node-api`, `cubeshackles-network-orchestrator` |
| **Access** | User/product surfaces (Angola-first wedges) | `CubeWallet`, `cubeshackles-web`, `cubeshackles-phone-wedge`, `national-transit-app-cubeshackles`, `BualaBuitu` |
| **Intelligence (advisory)** | AI/analytics, isolated from consensus | `cubeshackles-adviser`, `kulifikila`, `cubeshackles-ai-runtime` |
| **Sovereign infrastructure** | Private compute, hardware, and AI execution (non-consensus) | `cubeshackles-compute`, `cubeshackles-hardware`, `cubeshackles-ai-runtime` |
| **Observability** | Telemetry contracts and audit instrumentation (scaffolded) | `cubeshackles-observability` |
| **Platform operations** | Deployment/environment tooling | `cubeshackles-infra` |
| **Integration** | Cross-repo tests and gates | `cubeshackles-integration` |

**Hard rule:** Intelligence, sovereign infrastructure, and observability (until
integrated) are **isolated** from protocol-facing repositories. Their outputs may
only enter the protocol as recorded advisory signals or append-only audit records —
never as direct state mutation. See [`../SECURITY_MODEL.md`](../SECURITY_MODEL.md)
and [`../governance/policies/security-boundaries.md`](../governance/policies/security-boundaries.md).

### Contracts layer

`cubeshackles-contracts` is the **only** owner of shared message shapes. Other
repositories:

- declare what they consume and emit in `contracts/CONTRACTS.md` and
  `docs/dependencies.md`;
- reference schemas by version;
- never copy canonical schemas into local trees as alternate sources of truth.

See [`../governance/policies/interoperability-policy.md`](../governance/policies/interoperability-policy.md).

### Unequal maturity

Repositories are not equally mature, and that is intentional.

| Maturity | Meaning |
|---|---|
| **active** | Implemented behavior under development or test |
| **scaffolded** | Repo exists; boundaries and docs; not integrated |
| **planned** | Committed but not yet on disk |

A scaffolded repo (e.g. `cubeshackles-runtime`) is **not** "planned to be created."
It exists; it must be labeled **scaffolded** in the map and roadmap until integrated.

### Angola-first posture

Platform defaults assume:

- **AOA** as native settlement currency in contracts unless a product contract
  specifies otherwise;
- **offline-first** and intermittent connectivity for access wedges (especially
  `cubeshackles-phone-wedge`);
- **on-soil sovereign deployment** as a design constraint, not a marketing claim.

Product repos may target national programs (e.g. transit) while protocol repos remain
currency- and region-aware through contracts, not ad-hoc per-repo schemas.

## 3. Naming conventions

- Platform infrastructure repositories use the `cubeshackles-<layer-or-function>`
  prefix in **lowercase kebab-case** (e.g. `cubeshackles-runtime`,
  `cubeshackles-ai-runtime`, `cubeshackles-observability`).
- Branded product surfaces may use PascalCase brand names (e.g. `CubeWallet`) or
  established product names (e.g. `kulifikila`, `BualaBuitu`,
  `national-transit-app-cubeshackles`).
- The **on-disk directory name must equal the canonical repository name.** Any
  divergence (e.g. `BualaBuitu` vs the legacy folder `BuilaBuitu`) is a tracked
  defect and must be reconciled, not normalized away in docs.
- Do not introduce new top-level brand prefixes (`Cube*`, `Shackle*`) without
  recording them here first.

## 4. Required repository structure

Every new infrastructure repository is initialized with at least:

```
<repo>/
├── README.md            # what it is, status, boundaries, what it is NOT
├── contracts/CONTRACTS.md   # own / consume / emit (required for message producers)
├── docs/
│   ├── dependencies.md  # repo and contract dependencies
│   └── ...              # architecture, lifecycle, failure models
├── src/                 # source (module boundaries first; no fake implementations)
├── tests/               # unit/ and integration/
├── configs/             # configuration (no secrets)
└── scripts/             # operational scripts
```

README requirements:

- States the **layer** and **visibility** explicitly.
- States current **maturity** honestly (e.g. "scaffolded — interfaces only").
- States what the repository **is NOT** (e.g. "not a blockchain clone, not an EVM
  fork, not a Kubernetes clone").
- Links back to the canonical umbrella repository.

Documentation requirements (infrastructure repos):

- An `architecture.md`.
- A `failure-models.md` (or equivalent) — required for any repo touching execution,
  compute, or consensus-adjacent paths.
- Honest status markers throughout.

## 5. Visibility classification

Decide visibility before creation:

| Visibility | Contains | Examples |
|---|---|---|
| **public** | Truthful developer-facing architecture; no secrets, no models, no sovereign logic | `cubeshackles`, `cubeshackles-core`, `cubeshackles-web` |
| **private** | Sovereign infrastructure, AI/fraud models, regulator tooling, economic intelligence, silicon R&D | `cubeshackles-ai-runtime`, `cubeshackles-compute`, `cubeshackles-hardware`, `kulifikila` |
| **mixed / partial public** | Public interfaces with private implementation | `cubeshackles-adviser`, `cubeshackles-observability`, `BualaBuitu`, `cubeshackles-infra` |

Rules:

- Public repos contain **no** secrets, AI/fraud models, regulator logic, economic
  intelligence, sovereign orchestration logic, or production credentials.
- Private repos enforce access control and never expose model weights or sovereign
  logic through public mirrors.
- Mixed repos keep the public/private split at a clear module boundary.

## 6. Security baseline

Every repository, from creation:

- No secrets in version control (`.env`, credentials, key material excluded).
- Append-only, attributable logging for anything consensus-adjacent.
- Determinism preserved in any consensus-critical path; non-deterministic compute
  (AI, GPU) stays in the intelligence/compute layers.
- Coordinated disclosure per [`../SECURITY_MODEL.md`](../SECURITY_MODEL.md).

## 7. Maturity lifecycle

A repository advances through explicit stages. The umbrella docs record the current
stage honestly.

1. **Planned** — declared in [`../REPOSITORY_MAP.md`](../REPOSITORY_MAP.md); no repo yet.
2. **Scaffolded** — repository exists with structure, README, docs, and module
   boundaries (interfaces only). **Not integrated.** Committed in isolation.
3. **Active** — implemented behavior exists and is tested within the repo.
4. **Integrated** — deliberately wired into other repositories and exercised by
   `cubeshackles-integration` gates.
5. **Production-ready** — satisfies every property in
   [`../PRODUCTION_PRINCIPLES.md`](../PRODUCTION_PRINCIPLES.md). Claimed only when earned.

A repository must not skip stages. In particular, **scaffolded ≠ active**, and
**integrated ≠ production-ready**.

## 8. Creation checklist

Before creating a new repository:

- [ ] Layer chosen (§2) and recorded.
- [ ] Name follows conventions (§3); on-disk name will match canonical name.
- [ ] Visibility classified (§5).
- [ ] Boundary to protocol-facing repos confirmed (no consensus contamination).

At creation:

- [ ] `git init`; base structure created (§4).
- [ ] README states layer, visibility, maturity, and what it is NOT.
- [ ] Core architecture + failure-model docs drafted.
- [ ] No secrets; security baseline (§6) in place.
- [ ] Committed **in isolation** (its own commit, not merged into others).

Before integration:

- [ ] Promoted to "active," then "integrated" per the lifecycle (§7).
- [ ] [`../REPOSITORY_MAP.md`](../REPOSITORY_MAP.md) and
      [`../SYSTEM_ARCHITECTURE.md`](../SYSTEM_ARCHITECTURE.md) updated.
- [ ] `cubeshackles-integration` gates extended to cover the new boundary.

## 9. Updating the canonical record

Any change to a repository's existence, role, name, visibility, or maturity **must**
be reflected in [`../REPOSITORY_MAP.md`](../REPOSITORY_MAP.md) and, where structural,
in [`../SYSTEM_ARCHITECTURE.md`](../SYSTEM_ARCHITECTURE.md). The canonical record and
reality must never silently diverge; where they do (e.g. a pending rename), the
divergence is documented explicitly until resolved.
