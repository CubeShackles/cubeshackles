# CubeShackles Roadmap

**Platform sequencing, milestones, and current status.**

This document states what has been built, what is in progress, and what is
planned. Status is stated honestly. We do not claim readiness we have not earned.

---

## Completed milestones

### RC2 — Financial core freeze

The RC2 financial core is frozen. Settlement, ledger, validator, and vault remain
the sole execution truth. No AI path may settle, post journals, approve
validators, or sign.

**Frozen invariants:**
- Deterministic settlement — same inputs, same outputs, on every node.
- Sole financial authority — the protocol layer, not the intelligence layer.
- Replay-safe — every state transition reproducible from ordered history.

### AI_NATIVE_M5 — Native AI platform

The AI platform is stabilized through milestone M5. 11 platform AI agents are
operational through `cubeshackles-ai-runtime`. `cubeshackles-ai-sdk` enforces the
advisory-only boundary for all consumer applications.

**Invariants:**
- Advisory only — every inference response carries `advisory_only: true`.
- No embedded models in applications — all AI consumption through SDK.
- Single AI runtime composed by CubeKernel (`cubeshackles-os`).

### PLATFORM_ALPHA_1 — Institutional baseline

**Achieved: 2026-06-30.**

PLATFORM_ALPHA_1 records the convergence point where:

- RC2 financial core remains frozen (`RC2_FREEZE`).
- Native AI platform is stabilized through `AI_NATIVE_M5`.
- Phase 2 legacy migration (CS23 knowledge, payments advisory, lending and governance boundaries) is complete.
- Full platform gate suite passes on source trees.
- Canonical contracts govern interoperability — zero duplicate financial authority.
- Integration gate chain enforces feature-freeze manifest.
- 43 operations tests passing. 55 AI runtime tests passing. 23 AI SDK tests passing.

This is the institutional baseline before pilot integrations and before
PLATFORM_BETA_1 design-system migration.

---

## Current state — Feature Freeze Candidate (active)

Engineering is in **maintenance and assurance mode.** The change policy enforced
by `make feature-freeze-check` and `make platform-gates` applies:

**Allowed without exception:**
- Bug fixes — correctness defects, no contract or API expansion.
- Security fixes — vulnerability remediation and auth hardening.
- Compliance fixes — regulatory or policy alignment without new product scope.
- Audit evidence — documentation and gate evidence for external reviewers.
- Reliability fixes — availability, recovery, and operational stability.
- Documentation corrections — factual corrections to existing docs and runbooks.

**Restricted (require formal exception):**
- New product surface or business modules.
- New tokenomics or fee model changes.
- New public API surfaces.
- Breaking changes to frozen CIEL, economics, or platform contracts.

---

## Next milestone — PLATFORM_BETA_1 (target)

**Definition:** CubeShackles presents as **one unified Operating System** across
all applications — shared design language, shared components, migrated product
UX, explorer redesign, live demos, and pilot deployment tooling.

**Requirements:**

| Criterion | Status |
|---|---|
| `cubeshackles-design-system` canonical authority with all tokens, icons, layout shells | In progress |
| `CubeWallet` UI on platform theme (P4-2) | **Complete** |
| `cubeshackles-phone-wedge` UI on platform theme (P4-1) | In progress |
| `cubeshackles-adviser` UI on platform theme (P4-3) | In progress |
| `cubeshackles-web` Explorer redesign on platform theme | Planned |
| `BualaBuitu`, `kulifikila`, `national-transit-app` on platform theme | Planned |
| Institutional demo path operational end-to-end | In progress |
| Settlement + explorer + advisory visible in one OS narrative | Planned |

PLATFORM_BETA_1 precedes pilot deployments with institutional partners.

---

## Post-BETA_1 — Angola Pilot (planned)

Controlled pilot corridor in Angola. Scope defined in `cubeshackles-angola-pilot`.

**No national deployment claim. No production bank or regulator integration at
this stage.** The pilot corridor establishes an initial operational footprint
under controlled conditions before any broader deployment is considered.

---

## Long-horizon — sovereign infrastructure stack (planned)

The long-term architecture is layered. Each layer is only credible once the
layer below it works.

| Layer | Objective | Status |
|---|---|---|
| CubeShackles | Sovereign financial operating system | Active development |
| CubeVault | Data and security infrastructure | Scaffolded (`cubeshackles-vault`) |
| CubeNodes | Compute infrastructure | Scaffolded (`cubeshackles-compute`) |
| CubeCompute | AI orchestration layer | Scaffolded (`cubeshackles-compute`) |
| CubeFabric | Hardware manufacturing | Planned (`cubeshackles-hardware`) |
| Cube Silicon | Sovereign general compute semiconductors | Planned |
| Shackle Silicon | Specialized financial / AI chips | Planned |

This is a decades-long ladder. The discipline is to climb it in order, not to
start at the top.

---

## What this roadmap does not claim

- No production bank or telecom integration.
- No national-scale deployment.
- No regulatory approval in any jurisdiction.
- No claims of decentralization we have not built.
- No production-ready language for components that have not earned it.

See [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) for the full
definition of what "production ready" means here.
