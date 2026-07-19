# Repository README Template — English (canonical)

**Owner: CubeShackles (founder-led).**

Use this as the section skeleton for a Tier 1–2 `README.md` (see
[`REPOSITORY_CLASSIFICATION_TIERS.md`](REPOSITORY_CLASSIFICATION_TIERS.md)).
Tier 3 repositories use a short subset (title, ownership block, purpose,
scope, what-it-is-not, status). Omit any section that has nothing material to
say rather than padding it — see
[`DOCUMENTATION_STANDARD.md`](DOCUMENTATION_STANDARD.md) §3.

The **ownership block** (`Owner` / `Layer` / `Status` / `Visibility`) is
already specified in [`documentation-templates.md`](documentation-templates.md)
— use it as-is, do not redefine it here.

```markdown
[English](./README.md) | [Português](./README.pt.md)

# <Repository Name>

| Field | Value |
|---|---|
| **Owner** | CubeShackles (founder-led) |
| **Layer** | <from REPOSITORY_MAP.md> |
| **Status** | <active | pre-freeze | scaffolded | planned> |
| **Visibility** | <public | private | mixed> |

This repository is part of the CubeShackles platform. Doctrine and
contribution rules live in the umbrella repository
[`cubeshackles`](https://github.com/CubeShackles/cubeshackles).

**One-sentence classification.**

> What this repository is NOT.

---

## Purpose

## Position within the CubeShackles architecture

(Link to `REPOSITORY_MAP.md` layer table; do not restate the whole map.)

## Scope

## Out of scope

## Architecture overview

## Core components

## Data flows / transaction lifecycle
(Only if the repository has one — most do not.)

## Security model
(Link to `SECURITY_MODEL.md` for platform-wide model; state repo-specific
boundary here.)

## Compliance and regulatory integration boundaries
(State explicitly if none exist: "This repository has no direct regulatory
integration.")

## Installation / local development

## Configuration

## Usage

## Testing

## Observability and operational considerations

## Failure modes and recovery

## Dependencies and integrations
(Link to `docs/dependencies.md` if present.)

## Repository structure

## API / interface references

## Documentation links

## Contribution
Point to umbrella `CONTRIBUTING.md`; do not restate it.

## Security disclosure
Point to `SECURITY_MODEL.md`.

## License

## Maintainers
State "founder-led" per `authorship-and-tooling.md`; do not invent named
maintainers not evidenced in the repository.

## Roadmap
Label clearly as roadmap — not current state.

## Institutional disclaimer
Public source code does not expose the complete production platform where
private/sovereign components exist outside this repository.

## Translation
| | |
|---|---|
| Portuguese | [`README.pt.md`](README.pt.md) |
| Translation status | see `README.pt.md` metadata footer |
```

## Related

- [`REPOSITORY_README_TEMPLATE.pt.md`](REPOSITORY_README_TEMPLATE.pt.md)
- [`documentation-templates.md`](documentation-templates.md)
- [`DOCUMENTATION_STANDARD.md`](DOCUMENTATION_STANDARD.md)
