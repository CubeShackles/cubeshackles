# SYSTEM_ARCHITECTURE.md

**Canonical architecture of the CubeShackles platform.**

This document is the reference description of how CubeShackles is structured:
its layers, repositories, communication paths, institutional finance control
chain, validator lifecycle, DAG settlement flow, AI isolation boundary, and
failure posture. It describes both what exists today and what is scaffolded or
planned; status is stated explicitly per component.

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
7. **AOA-native settlement** — Angolan Kwanza is the default native settlement currency in all contracts and protocol semantics.
8. **Institutional control chain** — clearing must precede settlement; compliance must precede clearing; no authority boundary may be bypassed.
9. **Regulatory legibility** — the system is designed for regulator audit from the start, not retrofitted after.

---

## 2. Layered model

CubeShackles is organized into horizontal layers. Each layer has a defined
responsibility and communicates with adjacent layers through explicit, versioned
interfaces defined in `cubeshackles-contracts`.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Access Layer                                                        │
│  phone-wedge · CubeWallet · web (Explorer) · BualaBuitu · transit   │
├─────────────────────────────────────────────────────────────────────┤
│  Intelligence Layer (advisory, isolated from consensus)             │
│  adviser · kulifikila (credit)                                       │
├─────────────────────────────────────────────────────────────────────┤
│  Institutional Finance Stack                                         │
│  gateway → compliance → clearing → market-infra                     │
│  asset-registry → tokenization → rwa-custody → ledger               │
├─────────────────────────────────────────────────────────────────────┤
│  API and Coordination Layer                                          │
│  node-api · network-orchestrator · integration (gate suite)          │
├─────────────────────────────────────────────────────────────────────┤
│  Protocol and Execution Layer                                        │
│  core · validator-node · settlement-engine · runtime (scaffolded)   │
├─────────────────────────────────────────────────────────────────────┤
│  Operating System Layer                                              │
│  cubeshackles-os (CubeKernel) · platform-specs · terrain            │
├─────────────────────────────────────────────────────────────────────┤
│  Foundation Layer                                                    │
│  CIEL · ontology · TFE · developer-portal · agent                   │
├─────────────────────────────────────────────────────────────────────┤
│  Contracts Layer (cross-cutting schema authority)                    │
│  cubeshackles-contracts (schemas · events · versioning)             │
├─────────────────────────────────────────────────────────────────────┤
│  Control Plane Layer (cross-cutting request governance, scaffolded) │
│  cubeshackles-control-plane (identity · policy · AI routing · audit)│
├─────────────────────────────────────────────────────────────────────┤
│  Sovereign Infrastructure Layer (private, advisory, non-consensus)  │
│  ai-runtime · ai-sdk · compute (scaffolded) · hardware (scaffolded) │
└─────────────────────────────────────────────────────────────────────┘
```

The single most important rule across all layers: **intelligence is advisory.**
No output from the Intelligence or Sovereign layers may directly mutate
consensus-critical state. AI outputs are consumed as signals, scored, recorded,
and acted upon only through deterministic protocol rules.

Two layers are drawn cross-cutting rather than adjacent-only, and each carries
an explicit mediation rule so that being cross-cutting does not become a
backdoor around goal 4 (isolation): the **Contracts layer** mediates shared
message *shapes*; the **Control Plane layer** mediates *requests* (identity,
policy, AI routing, audit) against whichever target repository a request
touches, strictly through that repository's own published interface. Neither
layer gains internal coupling to any repository by virtue of appearing in its
integration list — see §3 and §5a.

---

## 3. Contracts layer

`cubeshackles-contracts` owns versioned message shapes (JSON Schema, OpenAPI,
event taxonomy). Protocol, access, institutional finance, and sovereign
repositories **consume** contracts; they do not redefine shared schemas locally.

Schema authority is not a runtime service — it is a versioned repository whose
contracts are consumed by all other layers. See
[`governance/policies/interoperability-policy.md`](governance/policies/interoperability-policy.md).

---

## 4. Foundation layer

The foundation layer defines the platform's institutional vocabulary:

- **`cubeshackles-ciel`** — Canonical Institutional Event Language. The versioned
  vocabulary of events emitted and consumed across the platform. Defines *what
  happens.*
- **`cubeshackles-ontology`** — Typed entities (banks, validators, regulators,
  merchants, citizens) and their typed relationships. Defines *who and what is
  involved.*
- **`cubeshackles-tfe`** — Terrain Field Engineering. Versioned runbook contracts
  for operational knowledge. Defines *how operators respond.*
- **`cubeshackles-developer-portal`** — Human-facing platform knowledge. Defines
  *how developers learn the system.*
- **`cubeshackles-agent`** — Contract surface for a future local AI engineering
  agent. Defines *how a machine engineer reasons over all four.*

All five are **pre-freeze** — contract surfaces defined, structural validation
passing, not yet frozen or integrated into the production gate chain.

---

## 5. Reality modeling and operating system layers

**`cubeshackles-terrain`** is the authoritative reality modeling layer:
institutional entities, typed relationships, permissions, jurisdiction, and
execution context. All production systems must consume Terrain before
execution — it is not a simulation layer, analytics platform, or database. It is
the single truth about what entities exist and their current states.

**`cubeshackles-os`** (CubeKernel) composes platform services into a coherent
operating system: boot sequence, service discovery, dependency graph, AI Runtime
registration, feature flags, and lifecycle orchestration. AI is a first-class OS
service in this model — present in every product workflow through common
interfaces — and is **never** financial authority.

**`cubeshackles-platform-specs`** sits above the design system and governs what
products do: behavior specifications, UX specifications, user flows, state
machines, acceptance criteria.

---

## 5a. Control plane layer (cross-cutting)

**`cubeshackles-control-plane`** governs *requests*, not services: identity,
deterministic policy, AI provider/model routing, cross-repo orchestration,
and immutable audit for every user-, service-, or agent-initiated request.
Scaffolded; no orchestration logic is implemented yet (see the repo's own
`docs/PRODUCT_SCOPE.md`).

Its integration list (`cubeshackles-ai-runtime`, `-ai-sdk`, `-ontology`,
`-agent`, `-security-framework`, `-observability`, `-compliance-engine`,
`-regulatory-reporting`, `-institutional-gateway`) spans four different
layers in the diagram above — Sovereign Infrastructure, Foundation,
Regulatory and Supervision, and Institutional Finance — which is broader
than any single-purpose repository in this map. That breadth is
deliberate and bounded the same way the Contracts layer's breadth is
bounded:

- The control plane calls each target only through that target's own
  published contract/interface — never its internals. It does not merge,
  replace, or bypass any target's existing authority boundary (e.g. it
  cannot make a compliance decision itself; it can only route a request to
  `cubeshackles-compliance-engine` and record the result).
- No target repository gains a dependency *on* the control plane merely by
  appearing in its integration registry — the relationship is one-directional
  until and unless a target repo's own contracts explicitly opt in.
- The control plane never gains settlement, ledger-mutation, validator-approval,
  or signing authority. Goal 4 (isolation) and the RC2 freeze doctrine apply
  to it exactly as they apply to the Intelligence and Sovereign layers.

**Authority boundary vs. `cubeshackles-os`:** CubeKernel composes and boots
platform *services* (§5, above). The control plane governs *requests*
flowing through those services once running. Neither owns the other.

---

## 6. Core data primitives

- **Cube** — the canonical unit of state. A Cube is a deterministic,
  hash-addressed record describing an economic and/or identity-aware event.
  Cubes are immutable once committed and are the atoms of replay.

- **Shackle** — the constraint logic binding Cubes. A Shackle expresses the rules
  a Cube must satisfy to be valid: settlement preconditions, identity
  attestations, validator obligations, and policy hooks. Shackles are
  deterministic; AI-assisted policy is referenced through hooks whose *decisions
  are recorded as inputs*, never executed inside consensus.

- **SmartShackle** *(planned)* — programmable Shackles that may reference
  advisory hooks, model-execution triggers, compute references, and inference
  receipts. These remain advisory and verifiable; the long-term intent is
  zk-verifiable AI outputs so that intelligence can be trusted without trusting
  the executor.

---

## 7. The settlement DAG

CubeShackles settlement is modeled as a **directed acyclic graph (DAG)** of
Cubes, not a linear chain.

- Each Cube references one or more predecessors, establishing causal order.
- Validators converge on a deterministic ordering of the DAG frontier.
- Ordering + deterministic execution = identical state across all honest validators.
- The DAG is designed to tolerate partition: subgraphs can advance locally
  offline and reconcile deterministically on reconnection.

DAG optimization (compaction, indexing, frontier pruning) is a compute-layer
concern and must never alter settlement semantics.

---

## 8. Validator lifecycle

A validator moves through a defined lifecycle. Each transition is observable and
auditable.

1. **Provisioning** — hardware attested, keys generated, identity registered.
2. **Join** — validator registers with `network-orchestrator`, syncs DAG state.
3. **Sync** — validator replays history to a verified frontier.
4. **Active** — validator proposes/validates Cubes, applies Shackle rules,
   participates in deterministic ordering.
5. **Advisory consumption** — validator may *read* signals from the Intelligence
   Layer (fraud/risk scores) and attach them as recorded inputs; it never
   delegates consensus decisions to them.
6. **Degraded** — on resource exhaustion or partial fault, validator sheds
   non-critical work and continues settlement.
7. **Eviction / exit** — on misbehavior or voluntary exit, validator is removed;
   its actions remain in the audit record.

---

## 9. Institutional finance control chain

For institutional flows (bank, broker, exchange, custodian, fund, regulator),
the platform enforces a sequential control chain. Each gate must pass before the
next step is permitted.

```
External institutional participant
          ↓
  Institutional Gateway
  (normalization: REST / FIX / ISO 20022 / SWIFT / gRPC → InstitutionalInstruction)
          ↓
  Compliance Engine
  (KYC / KYB / KYT / sanctions / jurisdiction → ComplianceReview)
          ↓
  Clearing House
  (netting / margin / collateral / liquidity → ClearingDecision)
          ↓
  Settlement Engine     ←  Validator Node (validation authority)
  (internal ledger finality — settlement.finality.recorded.v0.1)
          ↓
  Ledger
  (double-entry journal — append-only, CIEL trace headers, hashchain)
          ↓
  Observability (audit-grade telemetry target — scaffolded)
```

**Parallel track — tokenized and real-world assets:**

```
Asset Registry  →  Tokenization Engine  →  RWA Custody
(register/classify)  (plans + instructions)  (ownership + attestation chain)
```

**Market infrastructure** (CCP-style risk assessment) gates clearing decisions
for complex trades. It is a risk infrastructure simulation layer — not a licensed
clearing house or central counterparty in any jurisdiction.

**Regulatory supervision** reads completed evidence; it does not participate in
the execution chain.

---

## 10. Communication paths

| From | To | Purpose | Property |
|---|---|---|---|
| Access apps | `node-api` | Submit transactions, query state | Authenticated, rate-limited |
| `node-api` | `validator-node` | Relay validated requests | Internal, mutually authenticated |
| `validator-node` | `core` | Apply protocol/Shackle logic | In-process / library |
| `validator-node` | `network-orchestrator` | Membership, gossip, DAG ordering | Authenticated peer protocol |
| `validator-node` | `ai-runtime` (via SDK) | Request advisory signals | One-way, advisory, recorded |
| `institutional-gateway` | `compliance-engine` | Compliance gate | Sequential, blocking |
| `compliance-engine` | `clearing-house` | Clearing intake (post-compliance) | Sequential, blocking |
| `clearing-house` | `settlement-engine` | Settlement eligibility | Sequential, `clearing.settlement.eligible.v0.1` required |
| `settlement-engine` | `ledger` | Finality record | Append-only |
| All components | `observability` | Metrics, traces, audit logs (target) | Append-only, tamper-evident |
| `runtime` / `validator-node` | `compute` | Schedule GPU/edge workloads (scaffolded) | Isolated, non-consensus |
| All producers | `contracts` | Schema conformance | Versioned, integration-tested |
| All systems | `terrain` | Reality context before execution | Read-only consumption |

Trust boundaries are crossed only through explicit interfaces. Crossing a
boundary always implies authentication, validation, and audit logging.

---

## 11. AI execution boundary

This is the architecturally load-bearing constraint.

- AI runs **outside** the consensus-critical path, in `ai-runtime` / `compute`.
- AI is composed by `cubeshackles-os` (CubeKernel) as a first-class OS service.
- Applications consume AI only through `cubeshackles-ai-sdk` — no direct HTTP
  inference clients in product repositories.
- AI produces **signals** (risk scores, fraud flags, credit assessments,
  economic indicators, portfolio recommendations), not state mutations.
- Signals enter the protocol only as **recorded inputs** to deterministic rules.
- An AI failure, hallucination, or compromise can degrade *quality of advice* but
  **cannot** fork state, corrupt settlement, or break replay.
- Every advisory response carries an `advisory_only: true` envelope.
- Planned: **inference receipts** (every advisory output logged with model,
  version, and inputs) and **zk-verifiable inference** (advisory outputs
  provable without trusting the executor).

See [`SECURITY_MODEL.md`](SECURITY_MODEL.md) for the full treatment.

---

## 12. Sovereign infrastructure layers

- **`cubeshackles-ai-runtime`** *(active, private)* — 11 platform AI agents
  stabilized at `AI_NATIVE_M5`. Native OS service composed by CubeKernel. 55
  tests passing.
- **`cubeshackles-ai-sdk`** *(active, public)* — mandatory consumer library for
  all AI-consuming applications. 23 tests passing.
- **`cubeshackles-compute`** *(scaffolded, private)* — intended distributed
  sovereign compute orchestration: GPU scheduling, edge compute, node balancing,
  AI workload placement.
- **`cubeshackles-hardware`** *(scaffolded, private)* — hardware abstraction and
  silicon roadmap: validator hardware specifications, edge/thermal systems,
  ARM, RISC-V, FPGA, ASIC research, and *Cube Silicon* / *Shackle Silicon*.

The compute layer targets a **hardware abstraction layer** so workloads remain
portable across Nvidia, AMD, ARM, RISC-V, FPGA, and future in-house silicon.

---

## 13. Design system and developer experience

**`cubeshackles-design-system`** is the single authority for the CubeShackles OS
design language. Every frontend must consume it — no independent UX languages.
Consumer migration status as of July 2026:

| Application | Status |
|---|---|
| `CubeWallet` | Migrated — P4-2 complete |
| `cubeshackles-phone-wedge` | Migrating — P4-1 in progress |
| `cubeshackles-adviser` | Planned consumer |
| `cubeshackles-web` | Planned consumer (Explorer redesign) |
| `BualaBuitu` | Planned consumer |
| `kulifikila` | Planned consumer |
| `national-transit-app-cubeshackles` | Planned consumer |

**`cubeshackles-storybook`** documents and validates the design system — it is
a reference catalog, not a design authority.

---

## 14. Regulatory and supervision architecture

The platform is designed for regulator legibility from the start:

- **`cubeshackles-supervision`** — generates deterministic read-only supervisory
  views for BNA, CMC, ARSEG, AGT, BODIVA, MINFIN, and the Sandbox Authority.
  Regulators read; they do not mutate.
- **`cubeshackles-regulatory-reporting`** — consumes evidence packs from the
  integration gate suite; exports JSON, Markdown, and CSV reporting artifacts.
- **`cubeshackles-security-framework`** — NIST CSF 2.0 and ISO 27001:2022
  aligned; 11 threat categories; 10 canonical controls; 7 trust boundary zones;
  6 security evidence artifacts.
- **`cubeshackles-demo`** — Gate 7 institutional demonstration environment; five
  canonical scenarios; all flows terminate at `APPROVAL_REQUIRED` or
  `SIMULATION_ONLY`; no real money movement.
- **`cubeshackles-sandbox-lab`** — deterministic institutional participant
  simulation for BNA/BODIVA/CMC technical discussions.

---

## 15. Observability (cross-cutting, scaffolded)

`cubeshackles-observability` is **scaffolded**. It is intended to host
audit-grade telemetry contracts, metrics and tracing integrations, validator
monitoring hooks, and compliance-oriented log shapes — aligned with
`cubeshackles-contracts`. It does not currently ship a production observability
stack. Auditability remains an architectural requirement for consensus paths as
they are implemented in active repositories.

---

## 16. Repository roles (full summary)

| Repository | Layer | Status |
|---|---|---|
| `cubeshackles` (this repo) | umbrella | active |
| `cubeshackles-contracts` | contracts | active (v0.1) |
| `cubeshackles-ciel` | foundation | pre-freeze |
| `cubeshackles-ontology` | foundation | pre-freeze |
| `cubeshackles-tfe` | foundation | pre-freeze |
| `cubeshackles-developer-portal` | foundation | pre-freeze |
| `cubeshackles-agent` | foundation | pre-freeze |
| `cubeshackles-terrain` | reality modeling | active (v0.1.0) |
| `cubeshackles-os` | operating system | scaffolded |
| `cubeshackles-platform-specs` | operating system | scaffolded |
| `cubeshackles-control-plane` | control plane (cross-cutting) | scaffolded |
| `cubeshackles-core` | protocol & execution | active |
| `cubeshackles-validator-node` | protocol & execution | active |
| `cubeshackles-settlement-engine` | protocol & execution | active (v0.1 boundary) |
| `cubeshackles-runtime` | protocol & execution | scaffolded |
| `cubeshackles-offline-infrastructure` | protocol & execution | scaffolded |
| `cubeshackles-node-api` | API & coordination | active |
| `cubeshackles-network-orchestrator` | API & coordination | active |
| `cubeshackles-integration` | API & coordination | active |
| `cubeshackles-institutional-gateway` | institutional finance | active |
| `cubeshackles-compliance-engine` | institutional finance | active |
| `cubeshackles-clearing-house` | institutional finance | active |
| `cubeshackles-market-infrastructure` | institutional finance | active |
| `cubeshackles-ledger` | institutional finance | active |
| `cubeshackles-asset-registry` | institutional finance | active |
| `cubeshackles-tokenization-engine` | institutional finance | active |
| `cubeshackles-rwa-custody` | institutional finance | active |
| `cubeshackles-ai-runtime` | sovereign infrastructure | active |
| `cubeshackles-ai-sdk` | sovereign infrastructure | active |
| `cubeshackles-compute` | sovereign infrastructure | scaffolded |
| `cubeshackles-hardware` | sovereign infrastructure | scaffolded |
| `cubeshackles-adviser` | intelligence | active |
| `kulifikila` | intelligence | active |
| `cubeshackles-phone-wedge` | access | active |
| `CubeWallet` | access | active |
| `cubeshackles-web` | access | active |
| `BualaBuitu` | access | active |
| `national-transit-app-cubeshackles` | access | active |
| `cubeshackles-design-system` | design & DX | active |
| `cubeshackles-storybook` | design & DX | active |
| `cubeshackles-demo` | design & DX | active |
| `cubeshackles-sandbox-lab` | design & DX | active |
| `cubeshackles-supervision` | regulatory & supervision | active |
| `cubeshackles-regulatory-reporting` | regulatory & supervision | active |
| `cubeshackles-security-framework` | regulatory & supervision | active |
| `cubeshackles-provincial-topology` | platform operations | scaffolded |
| `cubeshackles-vault` | platform operations | scaffolded |
| `cubeshackles-disaster-recovery` | platform operations | scaffolded |
| `cubeshackles-chaos` | platform operations | scaffolded |
| `cubeshackles-security` | platform operations | scaffolded |
| `cubeshackles-operations` | platform operations | active |
| `cubeshackles-angola-pilot` | platform operations | scaffolded |
| `cubeshackles-infra` | platform operations | active |
| `cubeshackles-observability` | platform operations | scaffolded |

Full detail and visibility classification: [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md).

---

## 17. Companion documents

- [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) — the engineering bar.
- [`SECURITY_MODEL.md`](SECURITY_MODEL.md) — trust boundaries and threat posture.
- [`ROADMAP.md`](ROADMAP.md) — sequencing and milestones.
- [`docs/sovereign-infrastructure-thesis.md`](docs/sovereign-infrastructure-thesis.md) — strategic thesis.
- [`docs/repo-governance.md`](docs/repo-governance.md) — repository creation and classification.
- [`docs/architecture-consistency-audit.md`](docs/architecture-consistency-audit.md) — audit findings.
- [`governance/policies/`](governance/policies/) — formal policies.
- `FAILURE_MODELS.md` *(planned)* — Byzantine, partition, AI-corruption, regulator override.
- `COMPUTE_ROADMAP.md` *(planned)* — Nvidia/AMD/RISC-V/FPGA and Cube Silicon path.
