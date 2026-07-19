# Localization Rollout Plan

**Owner: CubeShackles (founder-led).**

Founder-approved execution order (2026-07-18). Batches of **5–8 repositories
per pull-request cycle** — never all repositories in one pass. Each batch is
its own set of per-repo `docs/pt-en-localization` branches, reviewed before
merge. See [`REPOSITORY_CLASSIFICATION_TIERS.md`](REPOSITORY_CLASSIFICATION_TIERS.md)
for tier assignments referenced below.

## Batch 0 — control plane (this change)

- `cubeshackles/docs/`: `LOCALIZATION_POLICY.md`, `GLOSSARY.en-pt.md`,
  `DOCUMENTATION_STANDARD.md`, `REPOSITORY_CLASSIFICATION_TIERS.md`,
  `REPOSITORY_README_TEMPLATE.md` (+ `.pt.md`), `TRANSLATION_REVIEW_CHECKLIST.md`,
  `LOCALIZATION_ROLLOUT.md` (this file), `CLAIMS_REGISTER.md`,
  `STYLE_GUIDE.en.md` / `STYLE_GUIDE.pt.md`.
- `cubeshackles/CLAUDE.md`: org-level bilingual-governance section.
- `.github` (org repo, local path `.github-org`): `scripts/validate_localization.py`
  equivalent as a composite action, reusable `docs-localization.yml` workflow,
  issue templates for terminology-change and translation-defect reports.

## Batch 1 — pilot (structurally distinct, exposes template/glossary gaps)

Founder-selected pilot set:

1. `cubeshackles` — organization/platform entry point (Tier 1).
2. `cubeshackles-developer-portal` — technical/developer-facing (Tier 1).
3. `cubeshackles-compliance-engine` — institutionally sensitive (Tier 1).

Each gets: language nav on `README.md`, new `README.pt.md`, repo-level
`CLAUDE.md` bilingual-governance section, and a validator run. Do not merge
without founder review — branches stay local/pushed-to-branch only, per
[`../../CONTRIBUTING.md`](../../CONTRIBUTING.md) and standing instruction.

Pilot goal: find glossary gaps, template friction, and regulatory-language
edge cases (especially in `cubeshackles-compliance-engine`, which carries
sandbox-only scope language that must not be softened in translation) before
they propagate to 50+ repositories.

## Batch 2+ — remaining Tier 1–2 repositories, 5–8 per cycle

Sequencing after the pilot passes review, grouped to keep each PR cycle
thematically coherent (mirrors `REPOSITORY_MAP.md` layers):

- **Batch 2 (institutional finance):** `cubeshackles-institutional-gateway`,
  `cubeshackles-regulatory-reporting`, `cubeshackles-ledger`,
  `cubeshackles-clearing-house`, `cubeshackles-settlement-engine`,
  `cubeshackles-contracts`.
- **Batch 3 (core protocol):** `Cubeshackles-core`,
  `Cubeshackles-validator-node`, `cubeshackles-runtime`, `Cubeshackles-node-api`,
  `Cubeshackles-network-orchestrator`, `cubeshackles-offline-infrastructure`,
  `cubeshackles-terrain`.
- **Batch 4 (access/products, Tier 1–2 only — private repos excluded):**
  `Cubeshackles-web`, `CubeWallet`, `Cubeshackles-phone-wedge`, `BualaBuitu`,
  `national-transit-app-cubeshackles`, `cubeshackles-adviser`.
- **Batch 5 (foundation + security):** `cubeshackles-ciel`,
  `cubeshackles-ontology`, `cubeshackles-tfe`, `cubeshackles-agent`,
  `cubeshackles-vault`, `cubeshackles-security-framework`,
  `cubeshackles-security`, `cubeshackles-supervision`.
- **Batch 6 (design/DX + remaining Tier 2):** `cubeshackles-design-system`,
  `cubeshackles-ai-sdk`, `cubeshackles-provincial-topology`.

## Tier 3 sweep

Short bilingual summaries only, batched loosely (not one PR per repo where
avoidable): `cubeshackles-os`, `cubeshackles-platform-specs`,
`cubeshackles-control-plane`, `cubeshackles-integration`,
`cubeshackles-market-infrastructure`, `cubeshackles-asset-registry`,
`cubeshackles-tokenization-engine`, `cubeshackles-rwa-custody`,
`cubeshackles-storybook`, `cubeshackles-demo`, `cubeshackles-sandbox-lab`,
`cubeshackles-disaster-recovery`, `cubeshackles-chaos`,
`cubeshackles-operations`, `cubeshackles-infra`, `cubeshackles-observability`.

## Excluded (Tier 4)

- Private-visibility repositories (`cubeshackles-ai-runtime`,
  `cubeshackles-compute`, `cubeshackles-hardware`, `kulifikila`) — excluded by
  policy, not oversight. Revisit if reclassified public/mixed.
- `cubeshackles-angola-pilot` — effectively empty; nothing to translate yet.
- `CubeShackles-Enterprise-Brain` — not in `REPOSITORY_MAP.md`, no recorded
  remote. Needs founder classification before this initiative touches it.

## Git discipline (every batch)

1. `git status` first; never overwrite unrelated in-progress work.
2. Branch: `docs/pt-en-localization`.
3. Commits: `docs: <scope>`, matching `type:docs` in
   [`GITHUB_TAXONOMY.md`](GITHUB_TAXONOMY.md); no `Co-authored-by` lines.
4. No push, no PR, no merge without explicit founder authorization for that
   batch.
5. Diff summary produced per batch before requesting review.
