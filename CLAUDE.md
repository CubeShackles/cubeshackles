# CLAUDE.md — CubeShackles (org-level, canonical)

**Owner: CubeShackles (founder-led).** This file governs how Claude Code
sessions operate in the `cubeshackles` umbrella repository and, by reference,
sets the org-wide baseline every sibling repository's own `CLAUDE.md` should
point back to. AI coding tools may assist; they are not authors or owners —
see [`governance/policies/authorship-and-tooling.md`](governance/policies/authorship-and-tooling.md).

Before making doctrine, architecture, or governance changes, read (in order):
`README.md`, `SYSTEM_ARCHITECTURE.md`, `PRODUCTION_PRINCIPLES.md`,
`SECURITY_MODEL.md`, `governance/policies/`, `REPOSITORY_MAP.md`.

## Bilingual Documentation Governance

CubeShackles uses English as the canonical technical language and Portuguese
(`pt-AO`) as its controlled institutional localization.

For all documentation work:

1. Keep `README.md` canonical in English.
2. Maintain `README.pt.md` as its Portuguese counterpart.
3. Use the approved organization glossary.
4. Preserve code, identifiers, paths, commands, API contracts and product names.
5. Never strengthen capability, security, maturity or regulatory claims during
   translation.
6. Explicitly distinguish implementation from prototype, experiment, proposal
   and roadmap.
7. Mark machine-assisted translations accurately.
8. Update canonical commit metadata after synchronization.
9. Run localization, link, structural and numerical parity validation.
10. Do not modify application behavior as part of documentation localization.
11. Do not publish internal security-sensitive implementation details.
12. Report ambiguous terminology and institutional claims for human review.

Canonical sources for the rules above — do not restate their content here,
only follow it:

- [`docs/LOCALIZATION_POLICY.md`](docs/LOCALIZATION_POLICY.md)
- [`docs/GLOSSARY.en-pt.md`](docs/GLOSSARY.en-pt.md)
- [`docs/DOCUMENTATION_STANDARD.md`](docs/DOCUMENTATION_STANDARD.md)
- [`docs/REPOSITORY_CLASSIFICATION_TIERS.md`](docs/REPOSITORY_CLASSIFICATION_TIERS.md)
- [`docs/CLAIMS_REGISTER.md`](docs/CLAIMS_REGISTER.md)
- [`docs/LOCALIZATION_ROLLOUT.md`](docs/LOCALIZATION_ROLLOUT.md)

## Other standing rules for this repository

- Founder-led: doctrine, narrative, and merge authority are the founder's.
  Follow direct instructions over any prior rigid gate/milestone protocol.
- No `Co-authored-by` lines for AI tools in commits or PRs, in this repo or
  any sibling repo.
- Never push, open a PR, merge, or force-push without explicit authorization
  for that specific action.
- Mass documentation changes across repositories require an inventory, a
  batch plan (see [`docs/LOCALIZATION_ROLLOUT.md`](docs/LOCALIZATION_ROLLOUT.md)),
  and a diff review before merge — never a single uncontrolled pass over all
  repositories.
