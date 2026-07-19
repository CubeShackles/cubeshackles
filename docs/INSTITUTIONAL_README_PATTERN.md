[English](INSTITUTIONAL_README_PATTERN.md) | [Português](INSTITUTIONAL_README_PATTERN.pt.md)

# Institutional README Pattern

**Owner: CubeShackles (founder-led).**

A stricter documentation pattern for repositories where institutional
wording matters most — financial-market infrastructure and institutional
integration surfaces (Batch 2 and beyond). It supplements, and does not
replace, [`REPOSITORY_README_TEMPLATE.md`](REPOSITORY_README_TEMPLATE.md):
use the ownership block, ownership-block Status field, and general
platform-doctrine language from that template, then structure the body of
an institutional repository's README around the twelve sections below.

Introduced with Batch 2 (2026-07-19). First applied to:
`cubeshackles-ledger`, `cubeshackles-clearing-house`,
`cubeshackles-settlement-engine`, `cubeshackles-institutional-gateway`,
`cubeshackles-regulatory-reporting`, `cubeshackles-contracts`.

## The twelve sections

1. **Purpose** — what the repository does, one paragraph.
2. **Role within CubeShackles** — its position in the institutional finance
   control chain (see `cubeshackles/REPOSITORY_MAP.md` §8); what feeds it,
   what it feeds.
3. **Scope**
4. **Out of Scope** — explicit, not implied.
5. **Functional Architecture** — components, not implementation detail.
6. **Trust Boundary** — what crosses in/out, what is assumed vs. verified.
7. **Data Flow** — state transitions or message flow, if any.
8. **Security Model** — repo-specific; link to `SECURITY_MODEL.md` for the
   platform-wide model rather than restating it.
9. **Regulatory Considerations** — see below; this is the section most
   likely to need Claims Register entries.
10. **Current Implementation Status** — see the Status-tag convention below.
11. **Roadmap** — clearly labeled as roadmap, never restated as current state.
12. **Documentation References**

Omit a section only if it is genuinely inapplicable (e.g. a schema-authority
repo with no live data flow) — state that explicitly rather than deleting
the heading silently, so heading parity between English and Portuguese
stays intact and the omission is visible, not silent.

## Maturity tags: `**Status:**` / `**Estado:**`

Every claim about what the repository currently does — most often inside
"Functional Architecture," "Trust Boundary," "Data Flow," and "Current
Implementation Status" — should be tagged inline with one of the six
controlled maturity terms:

| English | Português |
|---|---|
| `**Status:** Implemented` | `**Estado:** Implementado` |
| `**Status:** Partially implemented` | `**Estado:** Parcialmente implementado` |
| `**Status:** Prototype` | `**Estado:** Protótipo` |
| `**Status:** Experimental` | `**Estado:** Experimental` |
| `**Status:** Planned` | `**Estado:** Planeado` |
| `**Status:** Proposed` | `**Estado:** Proposto` |

`scripts/validate_localization.py` enforces this: the English and Portuguese
tag sequences must match 1:1 through the table above. A translation cannot
soften "Prototype" into "Implementado," and cannot drop a tag on one side
only. This is a stricter subset of the full maturity vocabulary in
[`LOCALIZATION_POLICY.md`](LOCALIZATION_POLICY.md) §4 (which also covers
the ownership block's whole-repo `Status` field) — the six terms above are
specifically for tagging one capability's maturity inline, not the repo as
a whole.

## Claims Register enforcement

`scripts/validate_localization.py` also enforces this (Rule 1, added
2026-07-19): any paragraph in `README.md` using a sensitive institutional
term — regulator, central bank, settlement, clearing, custody, tokenization,
supervision, compliance, audit, sovereign — must either belong to a
repository already listed in
[`CLAIMS_REGISTER.md`](CLAIMS_REGISTER.md), or carry an inline qualifier
(a `**Status:**`/`**Estado:**` tag, or wording like "planned," "prototype,"
"sandbox," "does not represent," "no live," etc.) marking the statement as
scoped rather than a live claim. Every Batch 2 repository gets at least one
Claims Register row as part of its documentation, which is normally the
simpler path.

**Known gap, tracked, not silently ignored:** this rule is not yet
retroactively enforced against `cubeshackles`, `cubeshackles-developer-portal`,
or `.github` — their existing prose legitimately uses this vocabulary as
platform-architecture description but predates the rule and has no register
row. Those Batch 0/1 repositories do **not** wire `docs-localization.yml`
into their own CI today (umbrella `ci.yml` / developer-portal `ci.yml` only
run repository-compliance checks), so the gap is not a live CI break for
them. Batch 2 repositories *do* wire the reusable workflow and carry Claims
Register rows, so Rule 1 is enforced there. Remediation of Batch 0/1 is a
tracked future batch — see `LOCALIZATION_ROLLOUT.md`. Do not enable
`docs-localization.yml` on Batch 0/1 until that remediation lands (or until
each repo has a Claims Register row / qualified prose).

## Ambiguous wording — author discipline, not (yet) a validator rule

Avoid unqualified use of: **regulator-grade**, **institutional-grade**,
**production-ready** (already an absolute-prohibited term, see
`DOCUMENTATION_STANDARD.md` §3), **sovereign infrastructure** — unless the
statement is precisely qualified in the same sentence (what specifically is
regulator-grade, and what evidence backs it). This is currently an authoring
rule for Batch 2, not a blocking validator check: `regulator-grade` and
`sovereign infrastructure` already appear unqualified in the merged
`cubeshackles` umbrella README as part of its founder-approved positioning
language, predating this pattern. Turning it into a hard validator rule
would need a remediation pass on that content first — tracked, not done
here.
