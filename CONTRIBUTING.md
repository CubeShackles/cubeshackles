# CONTRIBUTING.md

**How to contribute to CubeShackles.**

This is the umbrella repository — the canonical source of truth. Most code lives in
the component repositories listed in [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md). This
guide covers contribution rules for both this repo and the platform as a whole.

---

## Before you contribute

Read, in order:

1. [`README.md`](README.md) — what CubeShackles is.
2. [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md) — how it fits together.
3. [`PRODUCTION_PRINCIPLES.md`](PRODUCTION_PRINCIPLES.md) — the engineering bar.
4. [`SECURITY_MODEL.md`](SECURITY_MODEL.md) — trust boundaries.

Contributions that violate the architecture or principles will not be merged, even
if they are well written.

## Where to contribute

| Change type | Repository |
|---|---|
| Doctrine, architecture, repo map, standards | `cubeshackles` (this repo) |
| Protocol logic | `cubeshackles-core` |
| Validator execution | `cubeshackles-validator-node` |
| API surface | `cubeshackles-node-api` |
| Network coordination | `cubeshackles-network-orchestrator` |
| Cross-repo tests / gates | `cubeshackles-integration` |
| Access apps | `CubeWallet`, `phone-wedge`, `national-transit-app-cubeshackles`, `BualaBuitu` |

Intelligence, compute, and hardware repositories are private; contribution happens
through controlled channels.

## Non-negotiable rules

These derive directly from the production principles. A change is rejected if it:

1. Introduces **non-determinism** into a consensus-critical path.
2. Breaks **replay** — i.e. produces state that cannot be reconstructed from history.
3. Removes or weakens **audit** attribution.
4. Allows **AI / advisory output** to mutate consensus-critical state directly.
5. Introduces a **hard dependency on a single hardware vendor**.
6. Commits **secrets** (`.env`, credentials, key material) or sensitive sovereign
   logic into a public repository.
7. Adds **fake decentralization** language or **overstates production readiness**.

## Honest language

Use precise wording in code, docs, and commit messages:

- "implements" / "provides" — exists and is tested.
- "designed for" / "intended to" / "planned" — committed direction, not shipped.

Do not describe planned capability as if it ships today.

## Documentation changes (this repo)

- Keep documents consistent with each other. If you change a repository's role,
  update [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) **and** the relevant section of
  [`SYSTEM_ARCHITECTURE.md`](SYSTEM_ARCHITECTURE.md).
- Preserve the institutional, precise, no-hype tone.
- Prefer tables and explicit status markers over prose where it aids clarity.

## Commit & pull request conventions

- Write clear, imperative commit messages describing the *why*.
- Keep changes focused; one concern per PR where practical.
- Reference the architectural principle or document a change affects.
- For cross-repo changes, ensure `cubeshackles-integration` gates pass.

## Security

Never report vulnerabilities through public issues or PRs. Follow the coordinated
disclosure process in [`SECURITY_MODEL.md`](SECURITY_MODEL.md).

## Review standard

Reviewers evaluate every contribution against:

- determinism, replayability, auditability, isolation, recoverability,
  hardware-agnosticism;
- honesty of claims and language;
- security and secret hygiene;
- consistency with the canonical documents.

Thank you for helping build sovereign infrastructure carefully.
