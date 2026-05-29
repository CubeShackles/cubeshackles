# ROADMAP.md

**Sequencing and milestones for the CubeShackles platform.**

This roadmap describes direction and ordering, not dates. It separates what exists
from what is planned, and it deliberately sequences the **wedge** (real Angola
transaction utility) ahead of the long-horizon **infrastructure and semiconductor**
ambitions. Building the silicon thesis first would be a mistake; earning the right
to it through working infrastructure is the plan.

---

## Guiding sequence

1. **Make the wedge real** before generalizing.
2. **Harden the protocol** (determinism, replay, audit) before adding intelligence.
3. **Add intelligence as advisory** before deepening compute.
4. **Build compute and observability** before hardware abstraction.
5. **Industrialize upward into silicon** only after the layers below are proven.

---

## Phase 0 — Foundation (in progress)

- [x] Establish protocol-facing repositories (`core`, `validator-node`, `node-api`,
      `network-orchestrator`, `integration`).
- [x] Establish access wedges (`phone-wedge`, `CubeWallet`,
      `national-transit-app-cubeshackles`, `BualaBuitu`).
- [x] Cross-repo integration and production-gate suite.
- [x] Canonical umbrella repository (this repo): architecture, principles, repo map,
      security model, contribution rules.

## Phase 1 — Protocol hardening

- [ ] Formalize Cube/Shackle determinism guarantees and conformance tests.
- [ ] Full replay reproduction from history across all protocol repos.
- [ ] Append-only, attributable audit logging in `validator-node`.
- [ ] Author `FAILURE_MODELS.md` (Byzantine, partition, regional collapse, replay,
      regulator override).
- [ ] Offline-first reconciliation for the Angola phone wedge.

## Phase 2 — Runtime kernel

- [ ] Create `cubeshackles-runtime`: execution engine, memory management, DAG
      scheduling, validator execution lifecycle, orchestration kernel.
- [ ] Define canonical AI runtime *hooks* (interfaces only; advisory, isolated).

## Phase 3 — AI runtime (advisory, isolated)

- [ ] Create `cubeshackles-ai-runtime`.
- [ ] First service surface (advisory only):
  - [ ] `POST /ai/risk-score`
  - [ ] `POST /ai/fraud-check`
  - [ ] `POST /ai/node-health`
  - [ ] `POST /ai/economic-signal`
- [ ] Hardware-portable inference (CUDA / ROCm / TensorRT / Triton) behind an
      abstraction.
- [ ] Inference receipts (model, version, inputs logged for every output).
- [ ] Wire advisory signals into `validator-node` as recorded inputs only.

## Phase 4 — Compute orchestration

- [ ] Create `cubeshackles-compute` (private): GPU scheduling, edge compute, node
      balancing, AI compute federation, datacenter orchestration (CubeCompute).
- [ ] DAG optimization (compaction, indexing, frontier pruning) — performance only,
      never altering settlement semantics.

## Phase 5 — Observability

- [ ] Create `cubeshackles-observability`: metrics, tracing, audit logs, anomaly
      detection, AI node health, validator monitoring, compliance telemetry.

## Phase 6 — Hardware abstraction

- [ ] Create `cubeshackles-hardware` (private): validator hardware specs, edge /
      thermal systems, ARM integration, RISC-V experimentation, FPGA support, ASIC
      research.
- [ ] Author `COMPUTE_ROADMAP.md`: Nvidia/AMD/RISC-V/FPGA interoperability and the
      Cube Silicon pathway.

## Phase 7 — SmartShackles (GPU-aware contracts)

- [ ] Programmable Shackles with AI hooks, model-execution triggers, GPU compute
      references, and inference receipts — all advisory.
- [ ] Path to **zk-verifiable AI outputs** so intelligence is verifiable without
      trusting the executor.

## Long horizon — Sovereign silicon (decades)

- [ ] **Cube Silicon** — general sovereign compute acceleration.
- [ ] **Shackle Silicon** — specialized financial/AI acceleration.

These are explicitly long-term research directions, contingent on every prior phase
being proven. They are not commitments of near-term delivery.

---

## What we will not do

- We will not claim production readiness ahead of the principles in
  [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md).
- We will not architect dependence on a single hardware vendor or supply chain.
- We will not let intelligence components into the consensus-critical path.
- We will not let the long-term silicon thesis distract from the working wedge.
