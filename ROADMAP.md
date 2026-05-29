# ROADMAP.md

**Sequencing and milestones for the CubeShackles platform.**

This roadmap describes direction and ordering, not dates. It separates what exists
from what is planned or scaffolded, and it deliberately sequences the **wedge**
(real Angola transaction utility) ahead of the long-horizon **infrastructure and
semiconductor** ambitions. Building the silicon thesis first would be a mistake;
earning the right to it through working infrastructure is the plan.

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
      security model, contribution rules, governance policies.
- [x] Establish `cubeshackles-contracts` (v0.1 draft schemas and interoperability standard).
- [x] Scaffold sovereign and runtime repos (`runtime`, `ai-runtime`, `compute`,
      `hardware`, `observability`) with honest READMEs and module boundaries.

## Phase 1 — Protocol hardening

- [ ] Formalize Cube/Shackle determinism guarantees and conformance tests.
- [ ] Full replay reproduction from history across all protocol repos.
- [ ] Append-only, attributable audit logging in `validator-node`.
- [ ] Author `FAILURE_MODELS.md` (Byzantine, partition, regional collapse, replay,
      regulator override).
- [ ] Offline-first reconciliation for the Angola phone wedge.
- [ ] Align active repos with `cubeshackles-contracts` v0.1 declarations and gates.

## Phase 2 — Runtime kernel (scaffold → integrate)

- [ ] Harden `cubeshackles-runtime` scaffold: execution engine, memory management, DAG
      scheduling, validator execution lifecycle, orchestration kernel.
- [ ] Define validator hook interfaces for **recorded advisory inputs** (not AI execution).
- [ ] Integrate runtime with `validator-node` and integration gates when behavior is tested.

## Phase 3 — AI runtime (scaffold → advisory, isolated)

- [ ] Harden `cubeshackles-ai-runtime` scaffold.
- [ ] First service surface (advisory only):
  - [ ] `POST /ai/risk-score`
  - [ ] `POST /ai/fraud-check`
  - [ ] `POST /ai/node-health`
  - [ ] `POST /ai/economic-signal`
- [ ] Hardware-portable inference (CUDA / ROCm / TensorRT / Triton) behind an
      abstraction.
- [ ] Inference receipts (model, version, inputs logged for every output).
- [ ] Wire advisory signals into `validator-node` as recorded inputs only.

## Phase 4 — Compute orchestration (scaffold → private ops)

- [ ] Harden `cubeshackles-compute` scaffold: GPU scheduling, edge compute, node
      balancing, AI compute federation, datacenter orchestration (CubeCompute).
- [ ] DAG optimization (compaction, indexing, frontier pruning) — performance only,
      never altering settlement semantics.

## Phase 5 — Observability (scaffold → audit-grade)

- [ ] Harden `cubeshackles-observability` scaffold: telemetry contracts, metrics,
      tracing hooks, audit log shapes, validator monitoring integrations.
- [ ] Align observability contracts with `cubeshackles-contracts`; no claim of
      production telemetry until integration gates pass.

## Phase 6 — Hardware abstraction (scaffold → R&D track)

- [ ] Harden `cubeshackles-hardware` scaffold: validator hardware specs, edge /
      thermal systems, ARM integration, RISC-V experimentation, FPGA support, ASIC
      research.
- [ ] Author `COMPUTE_ROADMAP.md`: Nvidia/AMD/RISC-V/FPGA interoperability and the
      Cube Silicon pathway.

## Phase 7 — SmartShackles (GPU-aware contracts)

- [ ] Programmable Shackles with advisory hooks, model-execution triggers, compute
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
- We will not describe scaffolded repositories as if they already run production workloads.
