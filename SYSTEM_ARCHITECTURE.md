# SYSTEM_ARCHITECTURE.md

**Canonical architecture of the CubeShackles platform.**

This document is the reference description of how CubeShackles is structured: its
layers, its repositories, its communication paths, the validator lifecycle, the
DAG settlement flow, where AI is permitted to operate, and how the system is
intended to fail safely. It describes both what exists today and what is planned or
scaffolded; status is stated explicitly per component.

---

## 1. Architectural goals

CubeShackles is designed as sovereign financial infrastructure. The architecture
is shaped by a small number of non-negotiable goals:

1. **Determinism** — consensus-critical execution must be reproducible bit-for-bit.
2. **Replayability** — full state must be reconstructable from an ordered history.
3. **Auditability** — every state transition is attributable to a validator and observable by an authorized regulator.
4. **Isolation** — AI, analytics, and experimental compute are physically and logically separated from settlement.
5. **Hardware agnosticism** — the compute layer targets an abstraction, not a vendor.
6. **Offline-first** — the system assumes intermittent connectivity, not continuous broadband.
7. **AOA-native settlement** — Angolan Kwanza is the default native settlement currency in contracts and protocol design.

## 2. Layered model

CubeShackles is organized into horizontal layers. Each layer has a defined
responsibility and communicates with adjacent layers through explicit, versioned
interfaces defined in `cubeshackles-contracts`.

```
+--------------------------------------------------------------+
|  Application / Access Layer                                   |
|  CubeWallet · web · phone-wedge · national-transit · BualaBuitu|
+--------------------------------------------------------------+
|  Intelligence Layer (advisory, isolated)                     |
|  adviser · kulifikila (credit) · ai-runtime (scaffolded)     |
+--------------------------------------------------------------+
|  API & Coordination Layer                                    |
|  node-api · network-orchestrator                             |
+--------------------------------------------------------------+
|  Protocol & Execution Layer                                  |
|  core · validator-node · runtime (scaffolded)                |
+--------------------------------------------------------------+
|  Contracts Layer (cross-cutting schema authority)            |
|  cubeshackles-contracts (schemas · events · versioning)      |
+--------------------------------------------------------------+
|  Sovereign Infrastructure Layer (private, non-consensus)     |
|  compute (scaffolded) · hardware (scaffolded)                |
+--------------------------------------------------------------+
|  Observability (cross-cutting, scaffolded)                   |
|  observability — intended audit-grade telemetry contracts    |
+--------------------------------------------------------------+
```

The single most important rule across layers: **intelligence is advisory.** No
output from the Intelligence or Sovereign layers may directly mutate consensus-critical
state. Its outputs are consumed as signals, scored, recorded, and acted upon only
through deterministic protocol rules.

## 3. Contracts layer

`cubeshackles-contracts` owns versioned message shapes (JSON Schema, OpenAPI, event
taxonomy). Protocol, access, and sovereign repos **consume** contracts; they do not
redefine shared schemas locally. See [`cubeshackles-contracts`](../cubeshackles-contracts/README.md)
(sibling repository) and [`governance/policies/interoperability-policy.md`](governance/policies/interoperability-policy.md).

## 4. Core data primitives

- **Cube** — the canonical unit of state. A Cube is a deterministic, hash-addressed
  record describing an economic and/or identity-aware event. Cubes are immutable
  once committed and are the atoms of replay.
- **Shackle** — the constraint logic binding Cubes. A Shackle expresses the rules a
  Cube must satisfy to be valid: settlement preconditions, identity attestations,
  validator obligations, and policy hooks. Shackles are deterministic;
  AI-assisted policy is referenced through hooks whose *decisions are recorded as
  inputs*, never executed inside consensus.
- **SmartShackle** *(planned)* — programmable Shackles that may reference advisory
  hooks, model-execution triggers, compute references, and inference receipts. These
  remain advisory and verifiable; the long-term intent is zk-verifiable AI outputs
  so that intelligence can be trusted without trusting the executor.

## 5. The settlement DAG

CubeShackles settlement is modeled as a **directed acyclic graph (DAG)** of Cubes,
not a linear chain.

- Each Cube references one or more predecessors, establishing causal order.
- Validators converge on a deterministic ordering of the DAG frontier.
- Ordering + deterministic execution = identical state across all honest validators.
- The DAG is designed to tolerate partition: subgraphs can advance locally offline
  and reconcile deterministically on reconnection (offline-first requirement).

DAG optimization (compaction, indexing, frontier pruning) is a compute-layer
concern and must never alter settlement semantics — only performance.

## 6. Validator lifecycle

A validator moves through a defined lifecycle. Each transition is observable and
auditable.

1. **Provisioning** — hardware attested, keys generated, identity registered.
2. **Join** — validator registers with `network-orchestrator`, syncs DAG state.
3. **Sync** — validator replays history to a verified frontier.
4. **Active** — validator proposes/validates Cubes, applies Shackle rules,
   participates in deterministic ordering.
5. **Advisory consumption** — validator may *read* signals from the Intelligence
   Layer (fraud/risk scores) and attach them as recorded inputs; it never delegates
   consensus decisions to them.
6. **Degraded** — on resource exhaustion or partial fault, validator sheds
   non-critical work and continues settlement.
7. **Eviction / exit** — on misbehavior or voluntary exit, validator is removed;
   its actions remain in the audit record.

## 7. Communication paths

| From | To | Purpose | Property |
|---|---|---|---|
| Access apps | `node-api` | submit transactions, query state | authenticated, rate-limited |
| `node-api` | `validator-node` | relay validated requests | internal, mutually authenticated |
| `validator-node` | `core` | apply protocol/Shackle logic | in-process / library |
| `validator-node` | `network-orchestrator` | membership, gossip, ordering | authenticated peer protocol |
| `validator-node` | `ai-runtime` | request advisory signals | one-way, advisory, recorded |
| all components | `observability` | metrics, traces, audit logs (target) | append-only, tamper-evident |
| `runtime` / `validator-node` | `compute` | schedule GPU/edge workloads (target) | isolated, non-consensus |
| all producers | `contracts` | schema conformance | versioned, integration-tested |

Trust boundaries are crossed only through explicit interfaces. Crossing a boundary
always implies authentication, validation, and audit logging.

## 8. AI execution boundary

This is the architecturally load-bearing constraint.

- AI runs **outside** the consensus-critical path, in `ai-runtime` / `compute`.
- AI produces **signals** (risk scores, fraud flags, economic indicators), not state.
- Signals enter the protocol only as **recorded inputs** to deterministic rules.
- An AI failure, hallucination, or compromise can degrade *quality of advice* but
  **cannot** fork state, corrupt settlement, or break replay.
- Planned: **inference receipts** and eventually **zk-verifiable inference** so that
  advisory outputs are themselves auditable.

See [`SECURITY_MODEL.md`](SECURITY_MODEL.md) and `FAILURE_MODELS.md` (planned) for the
full treatment.

## 9. Sovereign infrastructure layers

- **`cubeshackles-compute`** *(scaffolded, private)* — intended distributed sovereign
  compute orchestration: GPU scheduling, edge compute, node balancing, AI workload
  federation. Future home of *CubeCompute*.
- **`cubeshackles-hardware`** *(scaffolded, private)* — hardware abstraction and
  silicon roadmap: validator hardware specs, edge/thermal systems, ARM integration,
  RISC-V experimentation, FPGA support, ASIC research, and *Cube Silicon* /
  *Shackle Silicon* pathways.
- **`cubeshackles-ai-runtime`** *(scaffolded, private)* — advisory inference;
  not part of consensus.

The compute layer targets a **hardware abstraction layer** so workloads remain
portable across Nvidia, AMD, ARM, RISC-V, FPGA, and future in-house silicon.

## 10. Observability (cross-cutting, scaffolded)

`cubeshackles-observability` is **scaffolded**. It is intended to host
audit-grade telemetry contracts, metrics and tracing integrations, validator
monitoring hooks, and compliance-oriented log shapes — aligned with
`cubeshackles-contracts`. It does **not** currently ship a production observability
stack. Auditability remains an architectural requirement for consensus paths as they
are implemented in active repos.

## 11. Repository roles (summary)

| Repository | Layer | Status |
|---|---|---|
| `cubeshackles` (this repo) | umbrella / doctrine | active |
| `cubeshackles-contracts` | contracts | active (v0.1 draft) |
| `cubeshackles-core` | protocol & execution | active |
| `cubeshackles-validator-node` | protocol & execution | active |
| `cubeshackles-node-api` | API & coordination | active |
| `cubeshackles-network-orchestrator` | API & coordination | active |
| `cubeshackles-runtime` | protocol & execution | scaffolded |
| `cubeshackles-phone-wedge` | access (Angola phone wedge) | active |
| `cubeshackles-integration` | cross-repo testing / gates | active |
| `cubeshackles-web` | access (web client) | active |
| `CubeWallet` | access (wallet) | active |
| `cubeshackles-adviser` | intelligence (advisory service, port 8080) | active |
| `kulifikila` | sovereign / intelligence (credit) | active |
| `cubeshackles-ai-runtime` | sovereign / intelligence (AI execution) | scaffolded |
| `cubeshackles-compute` | sovereign / compute | scaffolded |
| `cubeshackles-hardware` | sovereign / hardware | scaffolded |
| `BualaBuitu` | access (terminal/data intelligence) | active |
| `national-transit-app-cubeshackles` | access (transit) | active |
| `cubeshackles-observability` | observability | scaffolded |

Full detail and visibility classification: [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md).

## 12. Companion documents

- [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) — the engineering bar.
- [`SECURITY_MODEL.md`](SECURITY_MODEL.md) — trust boundaries and threat posture.
- [`docs/repo-governance.md`](docs/repo-governance.md) — repository creation and classification.
- [`docs/architecture-consistency-audit.md`](docs/architecture-consistency-audit.md) — audit findings and remediations.
- [`governance/policies/`](governance/policies/) — formal policies.
- `FAILURE_MODELS.md` *(planned)* — Byzantine, partition, AI-corruption, regulator override.
- `COMPUTE_ROADMAP.md` *(planned)* — Nvidia/AMD/RISC-V/FPGA and Cube Silicon path.
- [`ROADMAP.md`](ROADMAP.md) — sequencing and milestones.
