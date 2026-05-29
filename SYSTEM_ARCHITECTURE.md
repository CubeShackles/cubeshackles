# SYSTEM_ARCHITECTURE.md

**Canonical architecture of the CubeShackles platform.**

This document is the reference description of how CubeShackles is structured: its
layers, its repositories, its communication paths, the validator lifecycle, the
DAG settlement flow, where AI is permitted to operate, and how the system is
intended to fail safely. It describes both what exists today and what is planned;
status is stated explicitly per component.

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

## 2. Layered model

CubeShackles is organized into horizontal layers. Each layer has a defined
responsibility and communicates with adjacent layers through explicit, versioned
interfaces.

```
+--------------------------------------------------------------+
|  Application / Access Layer                                   |
|  CubeWallet · phone-wedge · national-transit · BualaBuitu    |
+--------------------------------------------------------------+
|  Intelligence Layer (advisory, isolated)                     |
|  kulifikila (credit) · ai-runtime (fraud/risk/economic)      |
+--------------------------------------------------------------+
|  API & Coordination Layer                                    |
|  node-api · network-orchestrator                             |
+--------------------------------------------------------------+
|  Protocol & Execution Layer                                  |
|  core (protocol logic) · validator-node · runtime (kernel)   |
+--------------------------------------------------------------+
|  Compute Layer                                               |
|  compute (GPU/edge orchestration)                            |
+--------------------------------------------------------------+
|  Hardware Layer                                              |
|  hardware (specs · ARM/RISC-V/FPGA · Cube/Shackle Silicon)   |
+--------------------------------------------------------------+
|  Observability (cross-cutting)                               |
|  observability (metrics · tracing · audit · anomaly)         |
+--------------------------------------------------------------+
```

The single most important rule across layers: **intelligence is advisory.** No
output from the Intelligence Layer may directly mutate consensus-critical state.
Its outputs are consumed as signals, scored, recorded, and acted upon only
through deterministic protocol rules.

## 3. Core data primitives

- **Cube** — the canonical unit of state. A Cube is a deterministic, hash-addressed
  record describing an economic and/or identity-aware event. Cubes are immutable
  once committed and are the atoms of replay.
- **Shackle** — the constraint logic binding Cubes. A Shackle expresses the rules a
  Cube must satisfy to be valid: settlement preconditions, identity attestations,
  validator obligations, and policy hooks. Shackles are deterministic;
  AI-assisted policy is referenced through hooks whose *decisions are recorded as
  inputs*, never executed inside consensus.
- **SmartShackle** *(planned)* — programmable Shackles that may reference AI hooks,
  model-execution triggers, GPU compute references, and inference receipts. These
  remain advisory and verifiable; the long-term intent is zk-verifiable AI outputs
  so that intelligence can be trusted without trusting the executor.

## 4. The settlement DAG

CubeShackles settlement is modeled as a **directed acyclic graph (DAG)** of Cubes,
not a linear chain.

- Each Cube references one or more predecessors, establishing causal order.
- Validators converge on a deterministic ordering of the DAG frontier.
- Ordering + deterministic execution = identical state across all honest validators.
- The DAG is designed to tolerate partition: subgraphs can advance locally offline
  and reconcile deterministically on reconnection (offline-first requirement).

DAG optimization (compaction, indexing, frontier pruning) is a compute-layer
concern and must never alter settlement semantics — only performance.

## 5. Validator lifecycle

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
6. **Degraded** — on resource exhaustion (e.g. GPU exhaustion) or partial fault,
   validator sheds non-critical work and continues settlement.
7. **Eviction / exit** — on misbehavior or voluntary exit, validator is removed;
   its actions remain in the audit record.

## 6. Communication paths

| From | To | Purpose | Property |
|---|---|---|---|
| Access apps | `node-api` | submit transactions, query state | authenticated, rate-limited |
| `node-api` | `validator-node` | relay validated requests | internal, mutually authenticated |
| `validator-node` | `core` | apply protocol/Shackle logic | in-process / library |
| `validator-node` | `network-orchestrator` | membership, gossip, ordering | authenticated peer protocol |
| `validator-node` | `ai-runtime` | request advisory signals | one-way, advisory, recorded |
| all components | `observability` | metrics, traces, audit logs | append-only, tamper-evident |
| `runtime`/`validator-node` | `compute` | schedule GPU/edge workloads | isolated, non-consensus |

Trust boundaries are crossed only through explicit interfaces. Crossing a boundary
always implies authentication, validation, and audit logging.

## 7. AI execution boundary

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

## 8. Compute & hardware layers

- **`cubeshackles-compute`** *(planned)* — distributed sovereign compute
  orchestration: GPU scheduling, edge compute, node compute balancing, AI compute
  federation, datacenter orchestration. This is the home of future *CubeCompute*.
- **`cubeshackles-hardware`** *(planned)* — hardware abstraction and silicon
  roadmap: validator hardware specs, edge/thermal systems, ARM integration,
  RISC-V experimentation, FPGA support, ASIC research, and the *Cube Silicon* /
  *Shackle Silicon* pathways.

The compute layer targets a **hardware abstraction layer** so workloads remain
portable across Nvidia, AMD, ARM, RISC-V, FPGA, and future in-house silicon. The
platform must never architect dependence on a single vendor or geopolitical supply
chain.

## 9. Observability (cross-cutting)

`cubeshackles-observability` *(planned/partial)* provides metrics, distributed
tracing, append-only audit logs, anomaly detection, AI node health, validator
monitoring, and sovereign compliance telemetry. Auditability is a first-class
architectural property, not an add-on: if an action is not observable, it is not
permitted in a consensus-critical path.

## 10. Repository roles (summary)

| Repository | Layer | Status |
|---|---|---|
| `cubeshackles` (this repo) | umbrella / doctrine | active |
| `cubeshackles-core` | protocol & execution | active |
| `cubeshackles-validator-node` | protocol & execution | active |
| `cubeshackles-node-api` | API & coordination | active |
| `cubeshackles-network-orchestrator` | API & coordination | active |
| `cubeshackles-phone-wedge` | access (Angola phone wedge) | active |
| `cubeshackles-integration` | cross-repo testing / gates | active |
| `CubeWallet` | access (wallet) | active |
| `kulifikila` | intelligence (credit) | active |
| `BualaBuitu` | access (terminal/data intelligence) | active |
| `national-transit-app-cubeshackles` | access (transit) | active |
| `cubeshackles-runtime` | execution kernel | planned |
| `cubeshackles-ai-runtime` | intelligence (AI execution) | planned |
| `cubeshackles-compute` | compute orchestration | planned (private) |
| `cubeshackles-hardware` | hardware / silicon | planned (private) |
| `cubeshackles-observability` | observability | planned (partial public) |

Full detail and visibility classification: [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md).

## 11. Companion documents

- [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) — the engineering bar.
- [`SECURITY_MODEL.md`](SECURITY_MODEL.md) — trust boundaries and threat posture.
- `FAILURE_MODELS.md` *(planned)* — Byzantine, partition, AI-corruption, regulator override.
- `COMPUTE_ROADMAP.md` *(planned)* — Nvidia/AMD/RISC-V/FPGA and Cube Silicon path.
- [`ROADMAP.md`](ROADMAP.md) — sequencing and milestones.
