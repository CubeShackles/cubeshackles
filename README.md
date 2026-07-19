[English](./README.md) | [Português](./README.pt.md)

# CubeShackles

**Canonical umbrella repository — the institutional source of truth for the
CubeShackles platform.**

**Owner: CubeShackles (founder-led).** Platform narrative, doctrine, and merge
authority are founder-led. AI coding tools may assist engineering; they are not
authors or owners of CubeShackles. See
[`governance/policies/authorship-and-tooling.md`](governance/policies/authorship-and-tooling.md).

> This repository is **not** the protocol implementation. It contains no protocol
> code, no AI models, no fraud logic, no regulator tooling, and no production
> secrets. It is the authoritative description of what CubeShackles is, how its
> 53 repositories fit together, the standards every component is held to, and the
> governance that keeps the ecosystem honest.

---

## What CubeShackles is

CubeShackles is **Angola-native sovereign financial infrastructure** — a
deterministic settlement and coordination platform built to be the financial
operating system for a jurisdiction that is building its rails from first
principles rather than inheriting legacy banking architecture.

It is not a blockchain clone, a token project, or a payments application. It is
engineered as sovereign, regulator-grade infrastructure organized around two
primitives:

- **Cube** — the canonical unit of state: a deterministic, hash-addressed,
  immutable record of economic and identity-aware activity.
- **Shackle** — the constraint and commitment logic that binds Cubes together
  under rules: settlement conditions, identity attestations, validator
  obligations, and (in later phases) AI-assisted policy hooks that remain
  isolated from consensus-critical execution.

Together, Cube + Shackle logic provides:

- deterministic settlement with DAG-based causal ordering,
- identity-aware transactions with regulator-grade audit trails,
- validator coordination with defined eviction and attribution,
- an institutional finance control chain (normalization → compliance → clearing → settlement → ledger),
- an advisory AI layer that is isolated from and cannot corrupt consensus,
- tokenization and real-world asset infrastructure,
- offline-first access for low-connectivity environments,
- and a long-horizon path toward AI-native, hardware-agnostic compute infrastructure.

**AOA (Angolan Kwanza) is the native settlement currency** in all interoperability
contracts and protocol semantics.

---

## Platform status (July 2026)

| Milestone | Status |
|---|---|
| `RC2_FREEZE` — financial core frozen | **Complete** |
| `AI_NATIVE_M5` — 11-agent AI platform, advisory-only boundary enforced | **Complete** |
| `PLATFORM_ALPHA_1` — institutional baseline, full gate suite passing | **Complete** (2026-06-30) |
| Feature Freeze Candidate — maintenance and assurance mode | **Active** |
| `PLATFORM_BETA_1` — unified OS design language across all applications | **Target** |
| Angola Pilot — controlled deployment corridor | **Planned** |

---

## Design posture

CubeShackles is engineered as long-horizon sovereign infrastructure, not a
consumer feature set. The guiding properties are:

- **Deterministic execution** — same inputs produce the same outputs everywhere, always.
- **Replayable state** — every state transition is reproducible from ordered history.
- **Regulator-grade auditability** — every validator action is observable, attributable, and reconstructable by an authorized regulator.
- **AI isolation** — AI components inform; they never corrupt consensus-critical state.
- **Institutional control chain** — compliance gates clearing; clearing gates settlement; no boundary may be bypassed.
- **Hardware-agnostic compute** — designed to migrate across Nvidia CUDA, AMD ROCm, ARM, RISC-V, FPGA, and future Cube Silicon / Shackle Silicon.
- **Offline-first Angola deployment** — connectivity is treated as intermittent by default.
- **AOA-native settlement** — Angolan Kwanza is first-class in all protocol semantics.
- **Security-first modularity** — strict trust boundaries between layers; crossing a boundary requires authentication, validation, and logging.

---

## Honesty doctrine

This repository describes a system that is **partly implemented and partly
planned.** We use precise language deliberately:

- **"implements" / "provides" / "active"** — exists and is exercised by tests.
- **"designed for" / "intended to" / "scaffolded"** — a committed direction with structure on disk, not yet integrated into the production gate chain.
- **"planned"** — committed direction; repository does not yet exist.

We do not use fake decentralization language, and we do not claim production
readiness where it does not exist. See [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md)
for the org's definition of readiness.

---

## Repository visibility

CubeShackles is split across public and private repositories by design:

- **Public** repositories present truthful, developer-facing architecture. They contain no sovereign orchestration logic, no AI/fraud models, no regulator tooling, no economic intelligence, and no production secrets.
- **Private** repositories protect sovereign infrastructure, AI/fraud models, regulator tooling, economic intelligence, and future Cube Silicon / Shackle Silicon R&D.

The complete inventory lives in [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) — 53 repositories across 14 layers.

---

## Platform layers (summary)

| Layer | Key repositories |
|---|---|
| Contracts | `cubeshackles-contracts` |
| Foundation | CIEL · Ontology · TFE · Developer Portal · Agent |
| Reality modeling | `cubeshackles-terrain` |
| Operating system | `cubeshackles-os` · `cubeshackles-platform-specs` |
| Protocol and execution | core · validator-node · settlement-engine · runtime · offline-infrastructure |
| API and coordination | node-api · network-orchestrator · integration |
| Institutional finance | gateway · compliance · clearing · market-infrastructure · ledger · asset-registry · tokenization · rwa-custody |
| Sovereign infrastructure | ai-runtime · ai-sdk · compute · hardware |
| Intelligence | adviser · kulifikila (credit) |
| Access | phone-wedge · CubeWallet · web (Explorer) · BualaBuitu · national-transit |
| Design and DX | design-system · storybook · demo · sandbox-lab |
| Regulatory and supervision | supervision · regulatory-reporting · security-framework |
| Platform operations | provincial-topology · vault · disaster-recovery · chaos · security · operations · angola-pilot · infra · observability |

---

## Start here

| If you want to… | Read |
|---|---|
| Understand the complete repository ecosystem | [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) |
| Understand the platform architecture | [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md) |
| Understand what production readiness means here | [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) |
| Understand the trust and security model | [`SECURITY_MODEL.md`](SECURITY_MODEL.md) |
| Understand the strategic thesis | [`docs/sovereign-infrastructure-thesis.md`](docs/sovereign-infrastructure-thesis.md) |
| Understand the protocol | [`docs/protocol-overview.md`](docs/protocol-overview.md) |
| See the platform roadmap and milestones | [`ROADMAP.md`](ROADMAP.md) |
| Understand the developer entrypoint | [`docs/developer-entrypoint.md`](docs/developer-entrypoint.md) |
| Understand contract and interoperability rules | [`contracts/CONTRACTS.md`](contracts/CONTRACTS.md) |
| Understand governance and repository policy | [`governance/policies/`](governance/policies/) |
| Create or classify a new repository | [`docs/repo-governance.md`](docs/repo-governance.md) |
| Review the architecture consistency audit | [`docs/architecture-consistency-audit.md`](docs/architecture-consistency-audit.md) |
| Founder-led authorship and tooling rules | [`governance/policies/authorship-and-tooling.md`](governance/policies/authorship-and-tooling.md) |
| Ecosystem documentation audit (founder-led sweep) | [`docs/FOUNDER_LED_DOCUMENTATION_AUDIT.md`](docs/FOUNDER_LED_DOCUMENTATION_AUDIT.md) |
| GitHub labels, milestones, and commit taxonomy | [`docs/GITHUB_TAXONOMY.md`](docs/GITHUB_TAXONOMY.md) |
| Contribute | [`CONTRIBUTING.md`](CONTRIBUTING.md) |

---

## License and disclosure

Licensing terms are defined per repository. Security disclosure procedures are
described in [`SECURITY_MODEL.md`](SECURITY_MODEL.md). Coordinated disclosure
only — do not open public issues describing vulnerabilities.

---

*CubeShackles — sovereign coordination infrastructure for Angola-native financial systems.*
