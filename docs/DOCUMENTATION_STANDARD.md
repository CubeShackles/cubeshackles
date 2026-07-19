# Documentation Standard

**Owner: CubeShackles (founder-led).**

This document sets the bar every repository's documentation is held to. It
extends [`repo-governance.md`](repo-governance.md) and
[`documentation-templates.md`](documentation-templates.md) with the bilingual
requirement; it does not replace them.

## 1. Baseline (all repositories, from `documentation-templates.md`)

- README ownership block (`Owner`, `Layer`, `Status`, `Visibility`).
- What the repository **is not**.
- Points back to the umbrella repository for doctrine and contribution rules.
- No AI-vendor marketing badges, no required tool `Co-authored-by` lines.

## 2. Bilingual requirement (public/mixed repositories, Tier 1–3)

- `README.md` (English, canonical) and `README.pt.md` (Portuguese, controlled
  translation) both exist and carry the language-navigation line.
- Section depth scales with tier — see
  [`REPOSITORY_CLASSIFICATION_TIERS.md`](REPOSITORY_CLASSIFICATION_TIERS.md)
  and the templates:
  [`REPOSITORY_README_TEMPLATE.md`](REPOSITORY_README_TEMPLATE.md) /
  [`REPOSITORY_README_TEMPLATE.pt.md`](REPOSITORY_README_TEMPLATE.pt.md).
- Terminology follows [`GLOSSARY.en-pt.md`](GLOSSARY.en-pt.md).
- Maturity/status wording follows `LOCALIZATION_POLICY.md` §4 — Portuguese
  must never claim a later maturity stage than English.

## 3. Claims discipline

Every material assertion about capability, security, or regulatory status
must be traceable to one of:

1. Code that implements it.
2. Tests that exercise it.
3. Documentation-only description, explicitly marked as such.
4. Experimental/prototype status.
5. Planned/roadmap status.
6. A stated dependency on regulatory approval.
7. A stated dependency on third-party integration.
8. An explicit "not independently verified" qualifier.

Assertions that cannot be traced to one of these are not published — they are
logged in [`CLAIMS_REGISTER.md`](CLAIMS_REGISTER.md) as **unresolved, needs
founder/legal review** instead of being softened into vague marketing prose.

Prohibited language patterns (checked by the validator, see
[`LOCALIZATION_POLICY.md`](LOCALIZATION_POLICY.md) §8):

- claims of production-readiness, full operationality, uptime guarantees, or
  unbreakability (existing `repository-compliance` CI grep — do not
  reintroduce these outside `PRODUCTION_PRINCIPLES.md` /
  `sovereign-infrastructure-thesis.md`);
- unqualified claims of regulatory approval, central-bank endorsement,
  sovereign status, audited financial results, or user/transaction counts not
  backed by a cited source in the repository.

## 4. What documentation work does not touch

Per the operating principles this initiative was scoped under: no
implementation files, tests unrelated to documentation validation, lockfiles,
generated artifacts, deployment configuration, migrations, infrastructure
state, secrets, licenses, copyright ownership, or legal representations.

## 5. Generated documentation

If a repository later adds a generator (OpenAPI → reference docs, schema →
tables), localize through the generator's input/templates, never by hand-
editing generated output. Record the generator's location in that repository's
`docs/dependencies.md`.

## Related

- [`LOCALIZATION_POLICY.md`](LOCALIZATION_POLICY.md)
- [`GLOSSARY.en-pt.md`](GLOSSARY.en-pt.md)
- [`STYLE_GUIDE.en.md`](STYLE_GUIDE.en.md) / [`STYLE_GUIDE.pt.md`](STYLE_GUIDE.pt.md)
- [`repo-governance.md`](repo-governance.md)
- [`documentation-templates.md`](documentation-templates.md)
