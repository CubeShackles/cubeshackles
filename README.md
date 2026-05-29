# CubeShackles

**Canonical umbrella repository — the institutional source of truth for the CubeShackles platform.**

> This repository is **not** the protocol implementation. It contains no protocol code,
> no AI models, no fraud logic, no regulator tooling, and no production secrets.
> It is the public, developer-facing description of what CubeShackles is, how its
> repositories fit together, and the standards every component is held to.

---

## What CubeShackles is

CubeShackles is **Angola-native sovereign financial infrastructure**.

It is not a blockchain clone, a token project, or a payments app. It is a
deterministic settlement and coordination platform built around two primitives:

- **Cube** — the unit of state and value: a deterministic, auditable record of
  economic and identity-aware activity.
- **Shackle** — the constraint and commitment logic that binds Cubes together
  under rules: settlement conditions, identity attestations, validator
  obligations, and (in later phases) AI-assisted policy hooks that remain
  isolated from consensus-critical execution.

Together, Cube + Shackle logic is designed to provide:

- deterministic settlement,
- identity-aware transactions,
- validator coordination,
- regulator-grade auditability,
- offline-first access for low-connectivity environments,
- and a path toward AI-native, hardware-agnostic compute infrastructure.

## Design posture

CubeShackles is being engineered as long-horizon sovereign infrastructure, not a
consumer feature set. The guiding standards are:

- **Deterministic execution** — same inputs produce the same outputs everywhere.
- **Replayable state transitions** — every state change is reproducible from history.
- **Regulator-grade auditability** — every validator action is observable and attributable.
- **AI isolation** — AI components inform; they never corrupt consensus-critical state.
- **Hardware-agnostic compute** — designed to migrate across Nvidia CUDA, AMD ROCm,
  ARM, RISC-V, FPGA, and future Cube Silicon / Shackle Silicon.
- **Offline-first Angola deployment** — connectivity is treated as intermittent by default.
- **African currency compatibility** — the Kwanza and regional currencies are first-class.
- **Security-first modularity** — strict trust boundaries between components.

## Honesty doctrine

This repository describes a system that is **partly implemented and partly planned.**
We use precise language deliberately:

- "implements" / "provides" — exists today.
- "designed for" / "intended to" / "planned" — a committed direction, not yet shipped.

We do not use fake decentralization language, and we do not claim production
readiness where it does not exist. See [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md)
for what "production ready" actually means here.

## Repository visibility

CubeShackles is split across public and private repositories by design:

- **Public** repositories present truthful, developer-facing architecture.
- **Private** repositories protect sovereign infrastructure, AI/fraud models,
  regulator tooling, economic intelligence, and future Cube Silicon / Shackle
  Silicon R&D.

The full inventory lives in [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md).

## Start here

| If you want to… | Read |
|---|---|
| Understand the whole system | [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md) |
| Know which repo does what | [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) |
| Understand our engineering bar | [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) |
| Understand the trust model | [`SECURITY_MODEL.md`](SECURITY_MODEL.md) |
| See where this is going | [`ROADMAP.md`](ROADMAP.md) |
| Contribute | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Create/classify a new repo | [`docs/repo-governance.md`](docs/repo-governance.md) |
| Get hands-on as a developer | [`docs/developer-entrypoint.md`](docs/developer-entrypoint.md) |
| Understand the protocol | [`docs/protocol-overview.md`](docs/protocol-overview.md) |
| Understand the strategic thesis | [`docs/sovereign-infrastructure-thesis.md`](docs/sovereign-infrastructure-thesis.md) |

## License & disclosure

Licensing terms are defined per repository. Security disclosure procedures are
described in [`SECURITY_MODEL.md`](SECURITY_MODEL.md).

---

*CubeShackles — sovereign coordination infrastructure for Angola-native financial systems.*
