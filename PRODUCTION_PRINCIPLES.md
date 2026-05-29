# PRODUCTION_PRINCIPLES.md

**What "production ready" means at CubeShackles.**

Production readiness here is not measured by deployment, polish, or feature count.
It is measured by structural properties of the system. A component is production
ready when it satisfies the principles below — and we say so honestly when it does
not yet.

---

## The six properties

### 1. Deterministic infrastructure
Same inputs produce the same outputs, on every node, in every region, on every
supported hardware target. Non-determinism (wall-clock dependence, unordered map
iteration, floating-point divergence, vendor-specific math) is forbidden in
consensus-critical paths. AI inference, which is inherently non-deterministic, is
kept strictly outside those paths (see principle 4).

### 2. Replayable infrastructure
Every state transition is reproducible from an ordered history of Cubes. Given the
genesis state and the DAG, any honest node can rebuild current state exactly.
Replay is the foundation of audit, recovery, and dispute resolution. Anything that
cannot be replayed cannot be trusted.

### 3. Auditable infrastructure
Every validator action is observable and attributable. Audit logs are append-only
and tamper-evident. Authorized regulators can reconstruct who did what, when, and
under which rules — without being granted the ability to alter state. If an action
is not observable, it is not allowed in a consensus-critical path.

### 4. Isolated infrastructure
AI cannot corrupt consensus. Intelligence components (fraud, risk, economic
signals, credit) are advisory only. Their outputs enter the protocol as recorded
inputs to deterministic rules, never as direct state mutations. A compromised,
failing, or hallucinating model degrades advice quality — it must never fork,
stall, or corrupt settlement.

### 5. Recoverable infrastructure
Regional collapse is survivable. The system assumes datacenter outages, regional
internet partitions, and node loss as normal events, not emergencies. Offline-first
operation, deterministic reconciliation on reconnection, and replay-based recovery
are designed in from the start.

### 6. Hardware-agnostic infrastructure
Workloads can migrate across Nvidia, AMD, ARM, RISC-V, FPGA, and future Cube
Silicon / Shackle Silicon. The platform targets a hardware abstraction layer and
never architects dependence on a single vendor or supply chain.

---

## Operating doctrine

These principles translate into concrete engineering rules.

- **Deterministic execution by default.** Consensus-critical code uses ordered
  data structures, fixed-point or canonicalized arithmetic, and no hidden
  environmental inputs.
- **Replay safety.** No side effect occurs that cannot be reproduced from history.
  External effects (notifications, payouts) are derived deterministically and are
  idempotent.
- **Rollback strategy.** State can be wound back to any committed frontier and
  re-derived. Rollbacks are deterministic operations, not manual surgery.
- **Regulator visibility.** Audit interfaces are designed for regulators as a
  first-class consumer, with read access and zero mutation capability.
- **AI isolation.** A hard boundary separates advisory compute from settlement.
  Crossing it is only ever "signal in," never "decision out."
- **Sovereign deployment modes.** The system supports fully sovereign, on-soil
  deployment with no mandatory dependence on foreign-controlled infrastructure.
- **Offline-first assumptions.** Connectivity is treated as intermittent.
  Transactions can be captured offline and settled deterministically later.
- **Eventual semiconductor compatibility.** Interfaces are defined so that future
  Cube Silicon / Shackle Silicon can implement them without protocol changes.

## Honesty in claims

We hold ourselves to precise language:

- **"implements" / "provides"** — exists and is exercised by tests.
- **"designed for" / "intended to" / "planned"** — a committed direction, not shipped.
- We do **not** claim decentralization we have not built.
- We do **not** claim production readiness a component has not earned.

A component may be merged and useful while still being explicitly *not* production
ready. Stating that accurately is itself a production principle.

## Definition of done (consensus-critical components)

A consensus-critical component is production ready only when all of the following hold:

- [ ] Deterministic across all supported targets (verified, not assumed).
- [ ] Full replay reproduces state exactly from history.
- [ ] Every action emits append-only, attributable audit records.
- [ ] No AI/non-deterministic input can reach state except as a recorded signal.
- [ ] Documented recovery path for partition and regional outage.
- [ ] No hard dependency on a single hardware vendor.
- [ ] Failure modes enumerated in `FAILURE_MODELS.md` (planned) with mitigations.
- [ ] Cross-repo gates in `cubeshackles-integration` pass.

Until every box is checked, the component is documented as **designed for** /
**planned**, not production ready.
