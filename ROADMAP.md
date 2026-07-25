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

## Current priority — PILOT RAIL (supersedes breadth work below)

**Decision (2026-07-25):** the 2026-07-25 institutional readiness audit
(43 of 58 repos, published as the *Institutional Readiness Ledger*) found
that every hard cryptographic and financial-math primitive on the platform
already exists and is independently tested, but the connective tissue
between components — auth, live wiring, consensus enforcement, compliance-gate
calls — is broken or missing at nearly every seam, across all seven
architectural clusters reviewed. Widening surface area (more UI migrations,
more product lines) before that seam is closed produces more of the same
pattern, not less.

**Effective immediately: broad feature development is paused.** All engineering
effort concentrates on one program — **Pilot Rail** — a single production
transaction path, real end to end, that a regulator or institutional partner
can evaluate as one complete lifecycle instead of dozens of isolated
components:

```
Phone Wedge → Institutional Gateway → Compliance → Settlement → Ledger → Validator → Receipt → Audit
```

Every box in that chain must be, simultaneously:

- **real** — not a stub, not a fixture, not a template string standing in for a signature
- **wired** — called from the live route, not merely present and tested in isolation
- **authenticated** — no open door at any inbound or outbound hop
- **tested** — covered by tests that exercise the live path, not just the unit in isolation
- **observable** — state and failures visible to an operator, not silent
- **recoverable** — a real DR/failover story, not a report generator run against stale evidence

No new product surface, business module, or UI migration is approved while
this bar is unmet on the rail above. This supersedes the PLATFORM_BETA_1
breadth criteria further down this document until Pilot Rail exits Phase C.

### Execution phases

**Phase A — Close the open security and wiring gaps.**
Wire already-built, already-tested functions into the live route instead of
building new ones: `institutional-gateway`'s compliance-gate and
clearing-forward calls, `compliance-engine`'s API auth,
`network-orchestrator`'s `coordinate-anchor` auth, the `ml_v1` mislabeling,
and DR evidence regeneration producing genuinely fresh hashes. Days, not
weeks — the code mostly already exists.

**Phase B — Build one complete production transaction rail.**
Make the eight-box Pilot Rail chain above real, wired, authenticated,
tested, observable, and recoverable end to end. Phone Wedge is the closest
citizen entry point today; invest there rather than splitting effort across
CubeWallet, Explorer, and national-transit simultaneously.

**Phase C — Run an institutional pilot.**
Bring one real KYC/sanctions data provider online (or permanently label
compliance-engine a sandbox rules-simulator), stand up real egress to one
of BNA/CMC/BODIVA, and let a regulator or institutional partner evaluate
the complete Pilot Rail lifecycle rather than isolated components.

**Phase D — Expand to additional products and services.**
Only after Phase C: bring the remaining citizen surfaces (CubeWallet,
Explorer, national-transit), additional business lines (asset-registry,
market-infrastructure, tokenization-engine, rwa-custody), and sovereign/
state-entity scale requirements up to the same bar proven on the rail.

**Why this sequencing:** stop optimizing for breadth until one vertical
slice is unquestionably production-ready. A regulator evaluating one
complete, honest transaction lifecycle is worth more than dozens of
independently-impressive but disconnected components.

See the full findings this decision is based on:
https://claude.ai/code/artifact/e3fd2793-0ac9-4dee-9b29-af2d8adc824a

---

## Deferred — PLATFORM_BETA_1 (breadth target, paused for Pilot Rail)

**Definition:** CubeShackles presents as **one unified Operating System** across
all applications — shared design language, shared components, migrated product
UX, explorer redesign, live demos, and pilot deployment tooling.

**Status: paused.** This breadth program resumes at Pilot Rail Phase D, not
before. Requirements as last recorded:

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

See [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) for the org's
full definition of operational readiness standards and maturity criteria.
