# Sibling repository documentation templates

Canonical short forms for every CubeShackles component repository.
Do not invent alternate ownership language.

## README ownership block (required)

Place near the top of each sibling `README.md` (after the title / one-line role):

```markdown
| Field | Value |
|---|---|
| **Owner** | CubeShackles (founder-led) |
| **Layer** | <!-- from REPOSITORY_MAP.md --> |
| **Status** | <!-- active \| pre-freeze \| scaffolded \| planned --> |
| **Visibility** | <!-- public \| private \| mixed --> |

This repository is part of the CubeShackles platform. Doctrine and contribution
rules live in the umbrella repository
[`cubeshackles`](https://github.com/CubeShackles/cubeshackles).
```

Also state **what this repo is not** (one short paragraph or bullets).

## CONTRIBUTING.md stub (required when the repo has no CONTRIBUTING.md)

```markdown
# Contributing

This repository is **CubeShackles (founder-led)**.

Before opening a pull request:

1. Read the umbrella [`CONTRIBUTING.md`](https://github.com/CubeShackles/cubeshackles/blob/main/CONTRIBUTING.md).
2. Follow [`authorship-and-tooling.md`](https://github.com/CubeShackles/cubeshackles/blob/main/governance/policies/authorship-and-tooling.md) — AI tools may assist; they are not authors or owners.
3. Keep claims honest with [`PRODUCTION_PRINCIPLES.md`](https://github.com/CubeShackles/cubeshackles/blob/main/PRODUCTION_PRINCIPLES.md).
4. Update `contracts/CONTRACTS.md` and `docs/dependencies.md` when changing shared shapes (contracts land in `cubeshackles-contracts` first).

Do not add AI-vendor marketing badges or required `Co-authored-by` lines for tools in docs or PR templates.
```
