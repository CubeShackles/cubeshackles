# Repository Classification — Localization Tiers

**Owner: CubeShackles (founder-led).**

This document assigns a **localization tier** to every repository already
recorded in [`REPOSITORY_MAP.md`](../REPOSITORY_MAP.md). It does not restate
role, status, or visibility — those are canonical in `REPOSITORY_MAP.md` and
must not be duplicated as a second source of truth here. If a repository's
tier looks wrong given its current role/status/visibility, fix
`REPOSITORY_MAP.md` first, then revisit the tier.

**Tier does not imply maturity.** A `scaffolded` repository can be Tier 2 —
its honest, scaffolded status is exactly what the bilingual README should
say. Tier is about *how much translated documentation surface is warranted*,
not about inflating what exists.

---

## Tier definitions

| Tier | Meaning |
|---|---|
| **1** | Full bilingual institutional documentation. Public entry points, the developer portal, major citizen-facing products, core protocol/architecture, and institutionally sensitive gateways (compliance, regulatory reporting). |
| **2** | Full bilingual `README.md`/`README.pt.md` with concise technical depth. Active or scaffolded technical repositories an external engineer or institutional reviewer may plausibly open. |
| **3** | Bilingual repository summary and status disclosure only — short README, no deep section-by-section translation. |
| **4-P** | Private, security-sensitive, or restricted localization. No automatic *public* localization — visibility, not technical importance, is what excludes it. May still warrant excellent bilingual *internal* documentation; that is a separate, founder-directed decision per repository, not automatic. |
| **4-U** | Unclassified, orphaned, obsolete, or unresolved. Empty repositories, repositories with unresolved factual ambiguity, or repositories pending founder classification. Revisit once resolved — do not default these to 4-P. |

Per `LOCALIZATION_POLICY.md` §2, **`private`-visibility repositories are
Tier 4-P by policy regardless of technical importance** — visibility alone
determines exclusion from *public* localization; it does not determine
whether internal documentation quality matters. A private settlement-grade
repository may still deserve excellent bilingual internal documentation — it
simply does not receive automatic public `README.pt.md` treatment the way a
Tier 1–3 repository does. Any internal bilingual documentation for a 4-P
repository is a distinct, founder-directed decision, tracked in
`LOCALIZATION_ROLLOUT.md`, not part of the default batch sequence.

---

## Assignment

| Repository | Visibility (map) | Tier | Why |
|---|---|---|---|
| `cubeshackles` | public | **1** | Umbrella entry point; canonical source of truth |
| `cubeshackles-contracts` | public | **1** | Schema authority for the whole ecosystem |
| `Cubeshackles-core` | public | **1** | Core protocol; active, tested, foundational |
| `cubeshackles-settlement-engine` | public | **1** | Core rail; active, live demo, institutional relevance |
| `cubeshackles-developer-portal` | public | **1** | Explicit developer entry point (Foundation layer) |
| `cubeshackles-institutional-gateway` | mixed | **1** | Institutional gateway by name and role |
| `cubeshackles-compliance-engine` | mixed | **1** | Institutionally sensitive — regulator/institutional audience |
| `cubeshackles-regulatory-reporting` | mixed | **1** | Institutionally sensitive — regulator/institutional audience |
| `Cubeshackles-web` | public | **1** | Public product surface (Explorer, Adviser UI) |
| `CubeWallet` | public | **1** | Primary citizen-facing product |
| `cubeshackles-ciel` | public | **2** | Foundation vocabulary layer; pre-freeze, developer-relevant |
| `cubeshackles-ontology` | public | **2** | Foundation vocabulary layer; pre-freeze, developer-relevant |
| `cubeshackles-tfe` | public | **2** | Foundation vocabulary layer; pre-freeze, developer-relevant |
| `cubeshackles-agent` | public | **2** | Foundation contract surface; pre-freeze |
| `cubeshackles-terrain` | public | **2** | Active, real depth, referenced by other repos |
| `cubeshackles-os` | public | **3** | Scaffolded, spec-only pre-freeze |
| `cubeshackles-platform-specs` | public | **3** | Scaffolded, spec-only pre-freeze |
| `cubeshackles-control-plane` | mixed | **3** | Scaffolded, cross-cutting, mixed visibility |
| `Cubeshackles-validator-node` | public | **2** | Active, public, but claims need heavy honesty-doctrine care (no real consensus yet) |
| `cubeshackles-runtime` | public | **2** | Public, honestly self-labeled `NotImplementedError` core |
| `cubeshackles-offline-infrastructure` | public | **2** | Public, core citizen promise, claims need heavy care |
| `Cubeshackles-node-api` | public | **2** | Active API surface |
| `Cubeshackles-network-orchestrator` | public | **2** | Active coordination layer |
| `cubeshackles-integration` | public | **3** | Internal cross-repo test/gate repo; limited external audience |
| `cubeshackles-ledger` | mixed | **2** | Active, core institutional finance |
| `cubeshackles-clearing-house` | mixed | **2** | Active, real persistence layer |
| `cubeshackles-market-infrastructure` | mixed | **3** | Active but dormant/not wired into core rail |
| `cubeshackles-asset-registry` | mixed | **3** | Active but dormant/not wired into core rail |
| `cubeshackles-tokenization-engine` | mixed | **3** | Active but dormant/not wired into core rail |
| `cubeshackles-rwa-custody` | mixed | **3** | Active but dormant/not wired into core rail |
| `cubeshackles-ai-runtime` | **private** | **4-P** | Private by policy |
| `cubeshackles-ai-sdk` | public | **2** | Public consumer kit; advisory-boundary enforcement is a real, documentable asset |
| `cubeshackles-compute` | **private** | **4-P** | Private by policy |
| `cubeshackles-hardware` | **private** | **4-P** | Private by policy |
| `cubeshackles-adviser` | mixed | **2** | Active, public-facing advisory UI with private model backend |
| `kulifikila` | **private** | **4-P** | Private by policy — product name preserved untranslated if/when reclassified |
| `cubeshackles-phone-wedge` | public | **2** | Public citizen entry point; claims need heavy care (simulator, not a real telecom bridge) |
| `BualaBuitu` | mixed | **2** | Active citizen-facing product |
| `national-transit-app-cubeshackles` | public | **2** | Public citizen-facing product; claims need heavy care (hardcoded demo balance) |
| `cubeshackles-design-system` | public | **2** | Active, real depth, developer-facing |
| `cubeshackles-storybook` | public | **3** | Dev-tooling companion to design system |
| `cubeshackles-demo` | public | **3** | Demonstration repository |
| `cubeshackles-sandbox-lab` | mixed | **3** | Sandbox/experimental |
| `cubeshackles-supervision` | mixed | **2** | Regulatory-adjacent |
| `cubeshackles-regulatory-reporting` | mixed | **1** | *(listed above — institutionally sensitive)* |
| `cubeshackles-security-framework` | mixed | **2** | Security posture legibility matters even at current maturity |
| `cubeshackles-provincial-topology` | public | **2** | Public, but scaffolded — claims need heavy care (5/18 provinces modeled) |
| `cubeshackles-vault` | mixed | **2** | Custody/signing; sandbox vs. production distinction must be explicit — see [[project_production_signing_m1]] |
| `cubeshackles-disaster-recovery` | mixed | **3** | Scaffolded; prior DR-drill evidence looked unverifiable — do not restate it as fact, see Claims Register |
| `cubeshackles-chaos` | mixed | **3** | Scaffolded |
| `cubeshackles-security` | mixed | **2** | Security posture overview |
| `cubeshackles-operations` | mixed | **3** | Internal ops; known unresolved CI issue, not public-audience critical |
| `cubeshackles-angola-pilot` | mixed | **4-U** | Effectively empty (dataclasses only, no logic/tests/CI) — unclassified/orphaned, not private; revisit once content exists |
| `cubeshackles-infra` | mixed | **3** | Platform operations tooling |
| `cubeshackles-observability` | mixed | **3** | Scaffolded telemetry contracts |
| `Cubeshackles-Enterprise-Brain` | **private** | **4-P** | Internal operations and enterprise knowledge base. Confirmed via GitHub API (2026-07-18) to exist as `Cubeshackles-Enterprise-Brain`, private, `size: 0`. Class: internal operations and enterprise knowledge. Status: initialization-pending. Localization: none until content, ownership, confidentiality zone, and lifecycle status are established — when it is, expect *selective internal* pt-AO coverage (governance pages and subsidiary-facing consumption views only), not automatic public `README.pt.md` treatment. See `REPOSITORY_MAP.md` §14a. |

Local/remote name casing defect tracked on this row: the workspace clone is
named `CubeShackles-Enterprise-Brain`; the canonical GitHub name is
`Cubeshackles-Enterprise-Brain`. Reconcile per `repo-governance.md` §3.

---

## Batch sequencing

See [`LOCALIZATION_ROLLOUT.md`](LOCALIZATION_ROLLOUT.md) for how tiers map to
execution batches. Batches are 5–8 repositories per pull-request cycle, not
all repositories at once.
