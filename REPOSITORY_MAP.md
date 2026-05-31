# REPOSITORY_MAP.md

**Canonical inventory of CubeShackles repositories, their roles, and visibility.**

This map is authoritative. If a repository's purpose is unclear, this document
settles it. Status is stated honestly:

- **active** — implemented behavior exists and is worked on.
- **scaffolded** — repository exists with structure, README, and boundaries; not integrated.
- **planned** — committed direction; repository does not yet exist on disk.

---

## Visibility doctrine

- **Public** repositories present truthful, developer-facing architecture. They
  contain no sovereign orchestration logic, no AI/fraud models, no regulator
  tooling, no economic intelligence, and no production secrets.
- **Private** repositories protect sovereign infrastructure, AI/fraud models,
  regulator tooling, economic intelligence, and future Cube Silicon / Shackle
  Silicon R&D.

Public repositories may *reference* private capabilities at the interface level
without exposing their implementation.

---

## 1. Umbrella

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles` | Canonical source of truth: doctrine, architecture, repo map, governance, policies. Contains no protocol code. | active | public |

## 2. Contracts layer

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-contracts` | Canonical interoperability contracts: versioned schemas, events, OpenAPI, versioning and interoperability standards. Does not run production traffic. | active (v0.1 draft schemas) | public |

## 3. Protocol layer (protocol-facing)

Consensus-critical and coordination repositories. They must remain deterministic,
replayable, and independent of sovereign AI/compute for correctness.

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-core` | Protocol logic. Cube/Shackle primitives, deterministic execution rules, settlement semantics; implements contracts consumed by sibling repos. | active | public |
| `cubeshackles-validator-node` | Validator execution. Runs the validator lifecycle, applies Shackle rules, participates in deterministic DAG ordering. **Validation authority only** — does not settle. | active | public |
| `cubeshackles-settlement-engine` | Settlement engine. **Internal ledger finality authority** in v0.1; consumes validated transactions, emits settlement and finality records. Does not mutate wallet or external bank balances. | scaffolded | public |
| `cubeshackles-node-api` | API layer. **Public contract gateway** (ingress authority). External-facing interface for submitting transactions and querying state (runtime API, dev port 8090). | active | public |
| `cubeshackles-network-orchestrator` | Network coordination. Membership, peer gossip, DAG frontier coordination, validator join/sync. | active | public |
| `cubeshackles-integration` | Cross-repo integration and production-gate suite. Validates contracts and interoperability across sibling repos; does not run production traffic. | active | public |
| `cubeshackles-runtime` | Deterministic execution kernel: execution engine, memory management, DAG scheduling, validator execution lifecycle, **settlement handoff orchestration**. Orchestration authority — does not create finality. | scaffolded | public |

## 4. Sovereign infrastructure layer

Private (or mixed) infrastructure for advisory AI, compute orchestration, hardware
abstraction, and credit intelligence. **Not** in the consensus-critical path.

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-ai-runtime` | Advisory AI execution: fraud/risk/economic models, inference infrastructure (CUDA/ROCm/Triton/TensorRT). Strictly outside consensus. **Infrastructure only.** | scaffolded | private |
| `cubeshackles-compute` | Distributed sovereign compute orchestration: GPU scheduling, edge compute, node balancing, AI workload placement (future CubeCompute). **Infrastructure only.** | scaffolded | private |
| `cubeshackles-hardware` | Hardware abstraction and silicon roadmap: validator specs, edge/thermal, ARM, RISC-V, FPGA, ASIC research, Cube Silicon / Shackle Silicon. **Infrastructure only.** | scaffolded | private |
| `kulifikila` | Credit intelligence. Advisory credit scoring; outputs consumed as recorded signals only. | active | private |

## 5. Access layer (products / wedges)

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-phone-wedge` | Angola phone transaction wedge. **Device initiation authority.** Offline-first, low-connectivity entry point for phone-based transactions. | active | public |
| `CubeWallet` | Wallet. **User initiation authority.** User custody and transaction UX. | active | public |
| `cubeshackles-web` | Web access surface. Browser-based client for transactions and account views over `node-api`. | active | public |
| `BualaBuitu` [^name] | Terminal / data intelligence access surface. | active | mixed |
| `national-transit-app-cubeshackles` | National transit application built on CubeShackles rails. | active | public |

## 6. Intelligence layer (advisory, isolated)

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-adviser` | Advisory service (dev port 8080). Surfaces advisory financial guidance and signals; runs outside the consensus-critical path. | active | mixed |

> `cubeshackles-ai-runtime` and `kulifikila` are listed under **Sovereign infrastructure**; they are intelligence producers, not protocol dependencies.

## 7. Observability (cross-cutting, scaffolded)

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-observability` | **Audit visibility authority.** Intended home for audit-grade telemetry contracts, metrics, tracing, and validator monitoring integrations. Repository is **scaffolded** — module boundaries and docs only; no production telemetry stack is shipped. | scaffolded | partial public |

## 8. Platform operations

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-infra` | Deployment / environment / operations tooling for the platform. Exact scope to be confirmed and reconciled with `cubeshackles-observability`. | active (role to confirm) | mixed |

> Repositories whose role is not yet fully classified are listed here honestly with
> a "role to confirm" status rather than omitted. New repositories must be classified
> per [`docs/repo-governance.md`](docs/repo-governance.md) before reaching "active".

## 9. Dependency relationships

- `cubeshackles-contracts` is the **schema authority**; protocol and access repos
  consume versioned contracts rather than defining shared shapes locally.
- `cubeshackles-core` is the foundational protocol implementation; protocol-facing
  repos consume its logic and published contracts.
- `cubeshackles-validator-node` depends on `core` and coordinates via
  `network-orchestrator`. Emits validation decisions only.
- `cubeshackles-settlement-engine` consumes `transaction.validated` from the validator
  path; it is the **sole v0.1 internal ledger finality authority**. It does not mutate
  wallet state or external bank balances; no production bank/regulator integration.
- `cubeshackles-node-api` fronts `validator-node` as the **public contract gateway**.
- `cubeshackles-runtime` orchestrates validator and settlement handoffs; it does not
  create finality.
- Access-layer apps depend on `node-api`.
- Sovereign repos (`ai-runtime`, `compute`, `hardware`, `kulifikila`) are consumed
  **one-way** as advisory signals or operational sidecars; nothing in the protocol
  path depends on them for correctness.
- `cubeshackles-integration` depends on the public contracts of participating repos to
  run cross-repo gates.
- `cubeshackles-runtime` (when integrated) executes under `core` rules; it does not
  host AI models, define advisory inference, or create settlement finality.
- `cubeshackles-observability` provides audit visibility; it is not a finality authority.

## 10. v0.1 authority model (Phase C gate)

| Layer | Authority |
|---|---|
| Node API | Ingress / public contract gateway |
| Runtime | Orchestration |
| Validator | Validation |
| Settlement engine | Internal ledger finality |
| Observability | Audit visibility |
| Wallet | User initiation |
| Phone Wedge | Device initiation |
| AI / Compute / Hardware / Network | Infrastructure only |

Settlement engine finality is **internal ledger finality only** in v0.1. Wallet state
mutation and external bank balance mutation are not v0.1 settlement engine authority.
No production bank, BNA, telecom, or regulator integration claims.

## 11. Local layout convention

For full local development, repositories are checked out as siblings:

```
parent/
├── cubeshackles/                      # umbrella (this repo)
├── cubeshackles-contracts/            # REQUIRED for contract discipline
├── cubeshackles-core/                 # REQUIRED — protocol logic
├── cubeshackles-node-api/             # REQUIRED — runtime API (port 8090)
├── cubeshackles-validator-node/
├── cubeshackles-settlement-engine/    # scaffolded — internal ledger finality authority
├── cubeshackles-network-orchestrator/
├── cubeshackles-phone-wedge/
├── cubeshackles-integration/
├── cubeshackles-web/
├── cubeshackles-adviser/              # advisory service (dev port 8080)
├── cubeshackles-infra/                # operations (role to confirm)
├── CubeWallet/
├── kulifikila/                        # private — sovereign
├── BualaBuitu/                        # on disk currently as "BuilaBuitu" — see note
├── national-transit-app-cubeshackles/
├── cubeshackles-runtime/              # scaffolded — not integrated
├── cubeshackles-ai-runtime/           # scaffolded — private — not integrated
├── cubeshackles-compute/              # scaffolded — private — not integrated
├── cubeshackles-hardware/             # scaffolded — private — not integrated
└── cubeshackles-observability/        # scaffolded — partial public — not integrated
```

Tests and tooling that span repositories assume this sibling layout. Repos that are
absent are expected to skip gracefully where possible.

[^name]: **Canonical name: `BualaBuitu`.** The on-disk directory is currently
`BuilaBuitu`. This is a tracked naming discrepancy: the repository should be renamed
to the canonical `BualaBuitu` so that documentation, tooling, and the filesystem
agree. Until reconciled, treat `BualaBuitu` as authoritative and `BuilaBuitu` as the
legacy folder name.
