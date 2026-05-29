# REPOSITORY_MAP.md

**Canonical inventory of CubeShackles repositories, their roles, and visibility.**

This map is authoritative. If a repository's purpose is unclear, this document
settles it. Status and visibility are stated honestly: "active" means it exists and
is worked on; "planned" means committed but not yet created or not yet functional.

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
| `cubeshackles` | Canonical source of truth: doctrine, architecture, repo map, standards. Contains no protocol code. | active | public |

## 2. Protocol & execution (protocol-facing)

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-core` | Protocol logic. Cube/Shackle primitives, deterministic execution rules, settlement semantics, contract definitions consumed by other repos. | active | public |
| `cubeshackles-validator-node` | Validator execution. Runs the validator lifecycle, applies Shackle rules, participates in deterministic DAG ordering. | active | public |
| `cubeshackles-node-api` | API layer. External-facing interface for submitting transactions and querying state (runtime API, dev port 8090). | active | public |
| `cubeshackles-network-orchestrator` | Network coordination. Membership, peer gossip, DAG frontier coordination, validator join/sync. | active | public |
| `cubeshackles-integration` | Cross-repo integration and production-gate suite. Validates contracts and interoperability across sibling repos; does not run production traffic. | active | public |

## 3. Access layer (products / wedges)

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-phone-wedge` | Angola phone transaction wedge. Offline-first, low-connectivity entry point for phone-based transactions. | active | public |
| `CubeWallet` | Wallet. User custody and transaction UX. | active | public |
| `BualaBuitu` | Terminal / data intelligence access surface. | active | mixed |
| `national-transit-app-cubeshackles` | National transit application built on CubeShackles rails. | active | public |

## 4. Intelligence layer (advisory, isolated)

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `kulifikila` | Credit intelligence. Advisory credit scoring; outputs consumed as recorded signals only. | active | private |
| `cubeshackles-ai-runtime` | AI execution infrastructure: CUDA/ROCm/TensorRT/Triton support, fraud/risk/economic models, model registry, distributed inference. Strictly outside consensus. | planned | private |

## 5. New core infrastructure layer

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-runtime` | Core runtime / "operating system" kernel: execution engine, memory management, AI runtime hooks, DAG scheduling, validator execution lifecycle, orchestration kernel. | planned | public |
| `cubeshackles-compute` | Distributed sovereign compute orchestration: GPU scheduling, edge compute, node compute balancing, AI compute federation, datacenter orchestration (future CubeCompute). | planned | private |
| `cubeshackles-hardware` | Hardware abstraction and silicon roadmap: validator hardware specs, edge/thermal, ARM, RISC-V, FPGA, ASIC research, Cube Silicon / Shackle Silicon. | planned | private |
| `cubeshackles-observability` | Production telemetry: metrics, tracing, audit logs, anomaly detection, AI node health, validator monitoring, sovereign compliance telemetry. | planned | partial public |

## 6. Dependency relationships

- `cubeshackles-core` is the foundational dependency; protocol-facing repos consume
  its contracts.
- `cubeshackles-validator-node` depends on `core` and coordinates via
  `network-orchestrator`.
- `cubeshackles-node-api` fronts `validator-node`.
- Access-layer apps depend on `node-api`.
- Intelligence repos (`kulifikila`, `ai-runtime`) are consumed **one-way** as
  advisory signals; nothing in the protocol path depends on them for correctness.
- `cubeshackles-integration` depends on the public contracts of all of the above to
  run cross-repo gates.

## 7. Local layout convention

For full local development, repositories are checked out as siblings:

```
parent/
├── cubeshackles/                      # umbrella (this repo)
├── cubeshackles-core/                 # REQUIRED — provides cubeshackles.contracts
├── cubeshackles-node-api/             # REQUIRED — runtime API (port 8090)
├── cubeshackles-validator-node/
├── cubeshackles-network-orchestrator/
├── cubeshackles-phone-wedge/
├── cubeshackles-integration/
├── CubeWallet/
├── kulifikila/                        # private
├── BualaBuitu/
├── national-transit-app-cubeshackles/
├── cubeshackles-runtime/              # planned
├── cubeshackles-ai-runtime/           # planned, private
├── cubeshackles-compute/              # planned, private
├── cubeshackles-hardware/             # planned, private
└── cubeshackles-observability/        # planned, partial public
```

Tests and tooling that span repositories assume this sibling layout. Repos that are
absent are expected to skip gracefully where possible.
