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

- **Batch 2 (institutional finance)** — narrowed scope (2026-07-19): prove
  the framework scales across financial-market infrastructure and
  institutional-integration repos accurately, not just translate six more
  READMEs. Split into two waves, second only after the first validates:
  - **Wave 2A — financial market infrastructure:** `cubeshackles-ledger`,
    `cubeshackles-clearing-house`, `cubeshackles-settlement-engine`. English
    README review + Portuguese README, following
    [`REPOSITORY_README_TEMPLATE.md`](REPOSITORY_README_TEMPLATE.md) plus
    the required-depth sections (architecture, transaction lifecycle, trust
    boundaries, failure modes, state management, interfaces, maturity
    classification), Claims Register entries, glossary additions only if
    genuinely new terminology appears.
  - **Wave 2B — institutional integration:** `cubeshackles-institutional-gateway`,
    `cubeshackles-regulatory-reporting`, `cubeshackles-contracts`. Follows
    [`INSTITUTIONAL_README_PATTERN.md`](INSTITUTIONAL_README_PATTERN.md) (a
    stricter 12-section structure) plus its `**Status:**`/`**Estado:**`
    maturity-tag convention and Claims Register discipline — this is where
    institutional wording matters most.

  Two new validator rules landed *before* Wave 2A started, per founder
  direction: Claims Register enforcement (sensitive institutional terms
  need a register row or an inline roadmap/strategic-intent qualifier) and
  EN/PT maturity-tag consistency. See
  [`INSTITUTIONAL_README_PATTERN.md`](INSTITUTIONAL_README_PATTERN.md) for
  both. **Known gap, not silently ignored:** Rule 1 is not retroactively
  enforced against `cubeshackles`, `cubeshackles-developer-portal`, or
  `.github` (Batch 0/1) — their prose predates the rule and has no register
  row. Not a live CI break for those repos (they do not wire
  `docs-localization.yml` into their own CI), but a tracked item for a
  future remediation batch — do not enable that workflow on Batch 0/1 until
  remediation lands. Batch 2 repos get the rule applied in full (register
  rows + wired CI).

  **Status (2026-07-19): Wave 2A and Wave 2B both complete.** All 6 repos
  validate at 0 errors (`--claims-register docs/CLAIMS_REGISTER.md`), each
  has a Claims Register entry, `docs-localization.yml` is wired into each
  repo's own CI (new, additive — first repos in the org to actually run the
  validator automatically, alongside `cubeshackles-compliance-engine`
  retroactively enabled from Batch 1). Two `README`s were rewritten rather
  than lightly reviewed, because the review surfaced real, material
  discrepancies between doctrine and code: `cubeshackles-clearing-house`
  described the whole repo as in-memory/no-database when the more mature of
  three coexisting subsystems is SQL-persisted; `cubeshackles-settlement-engine`
  stated "cryptographic ledger persistence... intentionally `NotImplemented`"
  when the RC2A pipeline already does real (sandbox-scoped) ledger postings
  with a genuine SHA-256 receipt hash chain. `cubeshackles-institutional-gateway`
  had two overstatements corrected (implied live institutional connectivity;
  an unenforced "non-bypassable" control-chain claim). One stale project-notes
  figure was corrected: `cubeshackles-contracts`'s "56 shackle specs / 413
  tests" exists only on an unmerged branch, not `main`. All findings are
  cited to specific file:line evidence in each repo's Claims Register entry,
  not asserted from memory. All PRs are open as drafts, none merged.
- **Batch 3 (core protocol):** `Cubeshackles-core`,
  `Cubeshackles-validator-node`, `cubeshackles-runtime`, `Cubeshackles-node-api`,
  `Cubeshackles-network-orchestrator`, `cubeshackles-offline-infrastructure`,
  `cubeshackles-terrain`.

  **Status (2026-07-19): COMPLETE.** Same research-then-write method as
  Batch 2 — 7 parallel research agents read code/tests directly (verifying
  or correcting prior notes) before any README was written. All 7 repos
  validate at 0 errors, each has Claims Register entries, and
  `docs-localization.yml` is wired into each repo's own CI. Real findings
  surfaced, most severe first: `cubeshackles-offline-infrastructure`'s
  entire queue-admission path is unreachable (an unconditional `raise`
  fires before any work happens, not just at the transport layer as a
  prior audit found — confirmed by direct execution); `cubeshackles-terrain`
  (the canonical Terrain system every other repo's stub client is meant to
  call) has no HTTP service of its own — it's a library, same maturity
  tier as the stubs waiting on it; `Cubeshackles-validator-node` has real
  Ed25519 signature verification (no presence-only bug here) but its real,
  tested quorum-computation function has zero production callers;
  `cubeshackles-runtime`'s "scaffolded" self-label was accurate for the
  execution core but didn't disclose a separate, tested boundary/handoff
  layer built alongside it; `Cubeshackles-node-api` had no ownership block
  at all and four dead companion-doc links. One validator bug the pilot
  itself exposed: the prohibited-claims check flagged negated honest
  disclosures ("not production-ready") as if they were the claim itself —
  fixed to be negation-aware. All PRs open as drafts, none merged.
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

## Excluded (Tier 4-P / 4-U)

**Tier 4-P — private/restricted, excluded from public localization by
policy, not oversight:**

- `cubeshackles-ai-runtime`, `cubeshackles-compute`, `cubeshackles-hardware`,
  `kulifikila` — private. Revisit if reclassified public/mixed.
- `Cubeshackles-Enterprise-Brain` — internal operations/enterprise knowledge.
  Confirmed on GitHub (2026-07-18): private, `size: 0`,
  `initialization-pending`. No localization of any kind — public or internal
  — until content, ownership, confidentiality zone, and lifecycle status are
  established by the founder. When that happens, expect *selective internal*
  pt-AO coverage (governance pages, subsidiary-facing consumption views), not
  the standard Tier 1–3 public README treatment. Local clone directory name
  (`CubeShackles-Enterprise-Brain`) doesn't match the canonical GitHub name
  (`Cubeshackles-Enterprise-Brain`) — tracked defect, see `REPOSITORY_MAP.md`
  §14a.

**Tier 4-U — unclassified/orphaned, revisit once resolved (not a visibility
exclusion):**

- `cubeshackles-angola-pilot` — effectively empty; nothing to translate yet.

## Git discipline (every batch)

1. `git status` first; never overwrite unrelated in-progress work.
2. Branch: `docs/pt-en-localization`.
3. Commits: `docs: <scope>`, matching `type:docs` in
   [`GITHUB_TAXONOMY.md`](GITHUB_TAXONOMY.md); no `Co-authored-by` lines.
4. No push, no PR, no merge without explicit founder authorization for that
   batch.
5. Diff summary produced per batch before requesting review.
