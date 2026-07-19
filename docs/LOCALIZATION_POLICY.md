# Localization Policy — English/Portuguese

**Owner: CubeShackles (founder-led).**
**Applies to:** every repository in [`REPOSITORY_MAP.md`](../REPOSITORY_MAP.md) whose
visibility is `public` or `mixed`.

---

## 1. Canonical language

English is the canonical technical language of the CubeShackles platform:
code, architecture, API contracts, schemas, security controls, and technical
decisions are authored and reviewed in English first.

Portuguese (`pt-AO` — formal, Angola-appropriate) is a **controlled institutional
translation** of the English source. It is not an independent specification and
must never introduce a claim, scope, or maturity level that does not already
exist in the English canonical document.

This extends [`repo-governance.md`](repo-governance.md) §1 ("One source of
truth") and does not create a second source of truth in Portuguese.

## 2. What gets translated

Every repository classified `public` or `mixed` in `REPOSITORY_MAP.md` carries:

- `README.md` — English, canonical.
- `README.pt.md` — Portuguese, controlled translation.
- A language-navigation line at the top of both files:

  ```
  [English](./README.md) | [Português](./README.pt.md)
  ```

Repositories classified `private` in `REPOSITORY_MAP.md` are Tier 4-P (see
[`REPOSITORY_CLASSIFICATION_TIERS.md`](REPOSITORY_CLASSIFICATION_TIERS.md))
and are **not** given automatic *public* `README.pt.md` translation under
this policy — they are not public-facing, so a public bilingual README has
no institutional-legibility benefit. This is a visibility rule, not a
judgment about technical importance: a private repository can still warrant
excellent *internal* bilingual documentation (e.g. governance pages or
subsidiary-facing consumption views), but that is a separate, explicit,
founder-directed decision per repository — never automatic, and never
published externally. If a private repository is reclassified
`public`/`mixed`, it enters normal localization scope at that point.

Deeper `docs/` content is translated selectively by
[repository tier](REPOSITORY_CLASSIFICATION_TIERS.md) — Tier 1 repositories
carry the fullest bilingual depth; Tier 3 repositories carry a bilingual
summary only. See [`LOCALIZATION_ROLLOUT.md`](LOCALIZATION_ROLLOUT.md) for the
batch sequence.

## 3. What never gets translated

Per [`GLOSSARY.en-pt.md`](GLOSSARY.en-pt.md) and platform convention, the
following are preserved verbatim in Portuguese documents:

- source-code identifiers, commands, environment variables, filenames, paths;
- package names, API routes, schema fields, event names;
- class/function names, protocol constants, cryptographic terminology;
- product and registered brand names (`CubeShackles`, `CubeWallet`,
  `BualaBuitu`, `Kulifikila`, and any name recorded in `REPOSITORY_MAP.md`);
- legal entity names, token symbols, currency codes (`AOA`).

Source code itself is never translated. Machine-readable contracts
(`contracts/*.yaml`, JSON Schemas, OpenAPI specs) are never translated unless a
localized *display* field already exists by design in that contract.

## 4. Maturity vocabulary — do not invent a second one

`REPOSITORY_MAP.md` and [`repo-governance.md`](repo-governance.md) §7 already
define the platform's maturity vocabulary: **planned / scaffolded / active /
integrated / production-ready**, plus the honesty-doctrine verbs **implements /
provides / active** vs. **designed for / intended to / scaffolded** vs.
**planned**. Localization does not add a competing vocabulary — it translates
the existing one, one-to-one, per the glossary:

| English | Português |
|---|---|
| implemented / active | implementado / ativo |
| partially implemented | parcialmente implementado |
| scaffolded | estruturado (sem integração) |
| prototype | protótipo |
| pre-freeze | pré-congelamento |
| experimental | experimental |
| planned | planeado |
| proposed | proposto |
| under evaluation | em avaliação |
| not independently verified | não verificado de forma independente |
| production-ready | pronto para produção |

A Portuguese document must never state a later/stronger maturity stage than its
English canonical source. The validator (§8) checks this mechanically where
the status appears in the required ownership block; anything else is caught in
translation review.

## 5. Review workflow

1. Author or update the English `README.md` first. It is reviewed and merged
   under the platform's normal PR rules (`type:docs`, `layer:*`, `risk:*`
   labels per [`GITHUB_TAXONOMY.md`](GITHUB_TAXONOMY.md)).
2. Produce `README.pt.md` from the merged English source. New translations are
   marked `translation_status: machine-assisted` (see §7) until a human fluent
   in both formal Portuguese and the subject matter reviews them.
3. A human review flips `translation_status` to `reviewed` and records the
   reviewer and date in the translation metadata block. Do not set `reviewed`
   without an evidenced human pass — see
   [`TRANSLATION_REVIEW_CHECKLIST.md`](TRANSLATION_REVIEW_CHECKLIST.md).
4. Every subsequent change to `README.md` requires a parity pass on
   `README.pt.md` in the same PR or a fast-follow PR referencing it. The
   validator flags drift (§8).

## 6. Exceptions

- Repositories with no material public documentation need are Tier 4-P
  (private/restricted) or Tier 4-U (unclassified, empty, duplicate, or
  awaiting founder classification) and are excluded from automatic public
  localization. See
  [`REPOSITORY_CLASSIFICATION_TIERS.md`](REPOSITORY_CLASSIFICATION_TIERS.md).
  `Cubeshackles-Enterprise-Brain` is Tier 4-P: confirmed to exist on GitHub
  (private, empty, `initialization-pending`) but out of scope for any
  localization — public or internal — until content, ownership,
  confidentiality zone, and lifecycle status are established.
- Security-sensitive implementation detail is never expanded into a public
  Portuguese document beyond what the English canonical document already
  discloses. Translation must not become a second disclosure channel.
- Generated documentation (OpenAPI-derived reference, schema-derived tables)
  is localized through its generator once one exists, not by hand-editing
  generated output.

## 7. Translation metadata (machine-readable)

Every `README.pt.md` ends with:

```html
<!--
localization:
  canonical_file: README.md
  locale: pt-AO
  translation_status: reviewed|machine-assisted|pending-review
  canonical_commit: <commit hash when available>
  last_synchronized: YYYY-MM-DD
-->
```

`translation_status` defaults to `machine-assisted` for new translations.

## 8. Validation

`scripts/validate_localization.py` (this repo) is the deterministic gate. It
checks required-file presence, navigation links, heading parity, code-block
byte-identity, metadata presence, forbidden-claims terms (shared list with
[`repo-governance.md`](repo-governance.md)'s honesty doctrine), untranslated
placeholders, secret patterns, and relative-link resolution. Since 2026-07-19
it also enforces two rules introduced for Batch 2 (see
[`INSTITUTIONAL_README_PATTERN.md`](INSTITUTIONAL_README_PATTERN.md)):
Claims Register coverage for sensitive institutional terms, and EN/PT
maturity-tag consistency (`**Status:**`/`**Estado:**`). It is invoked from
the reusable workflow in the `.github` organization repo. AI review may
supplement this but is never the only CI gate — see the script's own
docstring for full details.

## Related

- [`GLOSSARY.en-pt.md`](GLOSSARY.en-pt.md)
- [`DOCUMENTATION_STANDARD.md`](DOCUMENTATION_STANDARD.md)
- [`REPOSITORY_README_TEMPLATE.md`](REPOSITORY_README_TEMPLATE.md) /
  [`REPOSITORY_README_TEMPLATE.pt.md`](REPOSITORY_README_TEMPLATE.pt.md)
- [`TRANSLATION_REVIEW_CHECKLIST.md`](TRANSLATION_REVIEW_CHECKLIST.md)
- [`LOCALIZATION_ROLLOUT.md`](LOCALIZATION_ROLLOUT.md)
- [`../governance/policies/authorship-and-tooling.md`](../governance/policies/authorship-and-tooling.md)
