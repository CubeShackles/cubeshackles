# Developer Entrypoint

**The practical starting point for engineers working on CubeShackles.**

This document orients a new developer: how the repositories are laid out locally,
which ones are required, and how to reason about the system before writing code.
The umbrella repository contains no protocol code, so hands-on work happens in the
component repositories.

---

## 1. Mental model first

Before touching code, internalize four things:

1. **Cube + Shackle.** Cubes are deterministic units of state; Shackles are the
   rules binding them. Everything else is layered around these.
2. **Contracts first.** Shared message shapes live in `cubeshackles-contracts`. Do not
   redefine schemas locally.
3. **The advisory boundary.** AI/intelligence informs; it never mutates consensus
   state. If your change blurs this line, it is wrong.
4. **Determinism / replay / audit.** These are not features to add later — they are
   constraints on every line of consensus-critical code.

Read [`../SYSTEM_ARCHITECTURE.md`](../SYSTEM_ARCHITECTURE.md) and
[`../PRODUCTION_PRINCIPLES.md`](../PRODUCTION_PRINCIPLES.md) before contributing.

## 2. Local repository layout

CubeShackles repositories are developed as **siblings** in one parent directory.
Cross-repo tooling assumes this layout.

```
parent/
├── cubeshackles/                      # umbrella (this repo) — docs only
├── cubeshackles-contracts/            # REQUIRED for contract discipline
├── cubeshackles-core/                 # REQUIRED — protocol logic
├── cubeshackles-node-api/             # REQUIRED — runtime API (dev port 8090)
├── cubeshackles-validator-node/
├── cubeshackles-network-orchestrator/
├── cubeshackles-phone-wedge/
├── cubeshackles-integration/          # cross-repo tests / gates
├── cubeshackles-web/                  # web access client
├── cubeshackles-adviser/              # advisory service (dev port 8080)
├── CubeWallet/
├── kulifikila/                        # private — sovereign
├── BualaBuitu/                        # on disk as "BuilaBuitu" (rename pending)
├── national-transit-app-cubeshackles/
├── cubeshackles-runtime/              # scaffolded — not integrated
├── cubeshackles-ai-runtime/           # scaffolded — private
├── cubeshackles-compute/              # scaffolded — private
├── cubeshackles-hardware/             # scaffolded — private
└── cubeshackles-observability/        # scaffolded — partial public
```

## 3. What you need for what you want to do

| Goal | Minimum repos |
|---|---|
| Read/understand the platform | `cubeshackles` (this repo) |
| Work on interoperability contracts | `cubeshackles-contracts` |
| Work on protocol logic | `cubeshackles-core` |
| Work on validator execution | `cubeshackles-core`, `cubeshackles-validator-node` |
| Work on the API | `cubeshackles-core`, `cubeshackles-node-api` |
| Run cross-repo gates | `cubeshackles-integration` + the repos it checks |
| Work on an access app | that app + `cubeshackles-node-api` |
| Work on scaffolded infra | that repo + umbrella docs; do not assume integration |

`cubeshackles-core` provides protocol implementation and consumes contracts from
`cubeshackles-contracts`. Without `core`, protocol-facing tests fail with import
errors. The integration suite is designed so that absent optional sibling repos
skip gracefully.

## 4. Contract discipline

Every implementing repository should contain:

- `contracts/CONTRACTS.md` — what it owns, consumes, and emits
- `docs/dependencies.md` — repository and contract dependencies

The umbrella declares boundaries in [`../contracts/CONTRACTS.md`](../contracts/CONTRACTS.md)
and [`dependencies.md`](dependencies.md). Read
[`../../cubeshackles-contracts/INTEROPERABILITY_STANDARD.md`](../../cubeshackles-contracts/INTEROPERABILITY_STANDARD.md)
before changing message shapes.

## 5. Getting hands-on

The umbrella repo has nothing to build. To do real work:

1. Clone the component repository you need plus its required siblings (see table).
2. Follow that repository's own README / bootstrap instructions (e.g.
   `cubeshackles-integration` provides a bootstrap script and a venv-based setup).
3. Run that repository's tests before and after your change.
4. For changes that span repositories, run the `cubeshackles-integration` gates.

## 6. Contribution checklist

Before opening a PR, confirm your change:

- [ ] Preserves determinism in consensus-critical paths.
- [ ] Remains replayable from history.
- [ ] Emits/maintains audit attribution.
- [ ] Keeps AI/advisory output out of direct state mutation.
- [ ] Uses versioned contracts from `cubeshackles-contracts` for shared messages.
- [ ] Avoids single-vendor hardware lock-in.
- [ ] Commits no secrets and no sovereign logic to public repos.
- [ ] Uses honest language ("scaffolded" / "planned" vs "implements").

Full rules: [`../CONTRIBUTING.md`](../CONTRIBUTING.md).

## 7. Where to go next

- Protocol details: [`protocol-overview.md`](protocol-overview.md)
- Strategic context: [`sovereign-infrastructure-thesis.md`](sovereign-infrastructure-thesis.md)
- Trust model: [`../SECURITY_MODEL.md`](../SECURITY_MODEL.md)
- Governance policies: [`../governance/policies/`](../governance/policies/)
- Direction: [`../ROADMAP.md`](../ROADMAP.md)
