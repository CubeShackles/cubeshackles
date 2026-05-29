# Developer Entrypoint

**The practical starting point for engineers working on CubeShackles.**

This document orients a new developer: how the repositories are laid out locally,
which ones are required, and how to reason about the system before writing code.
The umbrella repository contains no protocol code, so hands-on work happens in the
component repositories.

---

## 1. Mental model first

Before touching code, internalize three things:

1. **Cube + Shackle.** Cubes are deterministic units of state; Shackles are the
   rules binding them. Everything else is layered around these.
2. **The advisory boundary.** AI/intelligence informs; it never mutates consensus
   state. If your change blurs this line, it is wrong.
3. **Determinism / replay / audit.** These are not features to add later — they are
   constraints on every line of consensus-critical code.

Read [`../SYSTEM_ARCHITECTURE.md`](../SYSTEM_ARCHITECTURE.md) and
[`../PRODUCTION_PRINCIPLES.md`](../PRODUCTION_PRINCIPLES.md) before contributing.

## 2. Local repository layout

CubeShackles repositories are developed as **siblings** in one parent directory.
Cross-repo tooling assumes this layout.

```
parent/
├── cubeshackles/                      # umbrella (this repo) — docs only
├── cubeshackles-core/                 # REQUIRED — protocol logic / contracts
├── cubeshackles-node-api/             # REQUIRED — runtime API (dev port 8090)
├── cubeshackles-validator-node/
├── cubeshackles-network-orchestrator/
├── cubeshackles-phone-wedge/
├── cubeshackles-integration/          # cross-repo tests / gates
├── CubeWallet/
├── kulifikila/                        # private
├── BualaBuitu/
└── national-transit-app-cubeshackles/
```

Planned repositories (`runtime`, `ai-runtime`, `compute`, `hardware`,
`observability`) join the same parent directory as they are created.

## 3. What you need for what you want to do

| Goal | Minimum repos |
|---|---|
| Read/understand the platform | `cubeshackles` (this repo) |
| Work on protocol logic | `cubeshackles-core` |
| Work on validator execution | `cubeshackles-core`, `cubeshackles-validator-node` |
| Work on the API | `cubeshackles-core`, `cubeshackles-node-api` |
| Run cross-repo gates | `cubeshackles-integration` + the repos it checks |
| Work on an access app | that app + `cubeshackles-node-api` |

`cubeshackles-core` provides the shared contracts (`cubeshackles.contracts`) other
repos import. Without it, protocol-facing tests fail with import errors. The
integration suite is designed so that absent optional sibling repos skip gracefully.

## 4. Getting hands-on

The umbrella repo has nothing to build. To do real work:

1. Clone the component repository you need plus its required siblings (see table).
2. Follow that repository's own README / bootstrap instructions (e.g.
   `cubeshackles-integration` provides a bootstrap script and a venv-based setup).
3. Run that repository's tests before and after your change.
4. For changes that span repositories, run the `cubeshackles-integration` gates.

## 5. Contribution checklist

Before opening a PR, confirm your change:

- [ ] Preserves determinism in consensus-critical paths.
- [ ] Remains replayable from history.
- [ ] Emits/maintains audit attribution.
- [ ] Keeps AI/advisory output out of direct state mutation.
- [ ] Avoids single-vendor hardware lock-in.
- [ ] Commits no secrets and no sovereign logic to public repos.
- [ ] Uses honest language ("planned" vs "implements").

Full rules: [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## 6. Where to go next

- Protocol details: [`protocol-overview.md`](protocol-overview.md)
- Strategic context: [`sovereign-infrastructure-thesis.md`](sovereign-infrastructure-thesis.md)
- Trust model: [`../SECURITY_MODEL.md`](../SECURITY_MODEL.md)
- Direction: [`../ROADMAP.md`](../ROADMAP.md)
