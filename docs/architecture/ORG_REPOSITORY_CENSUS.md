# CubeShackles Organization — Repository Census

**Status:** Discovery output. Evidence-based, not doctrine. No repository name is treated as evidence of architectural authority.
**Date:** 2026-09-30
**Method:** Local clone inspection (code, manifests, tests run where feasible, CI workflows, contracts docs) across ~11 parallel evidence-collection passes, cross-checked and reconciled by the primary agent. Where a subagent's claim could not be independently verified, it is marked UNRESOLVED rather than asserted.
**Scope note:** This census does not re-verify org repo count from `gh api orgs/CubeShackles/repos` at the moment of writing; prior verified count (2026-09-19) was 61 org repos / 62 local clone dirs (2 extras: an `Enterprise-Brain` local duplicate, and a non-org scratch dir). Repos below reflect what the 11 subagents actually inspected.

## Legend
- **Maturity**: PRODUCTION-BOUND / FUNCTIONAL / PARTIAL / SCAFFOLDED / DORMANT / UNKNOWN
- **Canonical alignment**: CONFIRMED_CANONICAL / CANONICAL_CANDIDATE / DOMAIN_AUTHORITY / ADAPTER / DUPLICATED / CONFLICTING / SCAFFOLD / LEGACY / UNRESOLVED (see `CANONICAL_AUTHORITY_MATRIX.md` for the primitive-level version of this)

## Core protocol / ledger / consensus cluster

| Repo | Classification | Maturity | Tests | CI runs tests? | API | DB | Notes |
|---|---|---|---|---|---|---|---|
| Cubeshackles-core | Library (in-process, no server) | FUNCTIONAL (production-depth logic) | 41 files | No (compliance-lint only) | n/a | sqlite (execution receipts) | Real quorum/replay/DAG logic; `TransactionStatus.SETTLED` defined but never assigned by any code path |
| Cubeshackles-node-api | Service | FUNCTIONAL (largest/most-tested repo in org, 154 test files) | 154 files | 5 CI workflows incl. dedicated ciel/gateway/contract-drift | Yes, 3 parallel transaction paths | sqlite (via Core adapter, off by default) | 3 structurally different finality guarantees live simultaneously (see dependency graph doc) |
| Cubeshackles-validator-node | Service | FUNCTIONAL | 26 files | dedicated validator-ci.yml | Yes | n/a | Real Ed25519 crypto; real quorum-check function has zero production callers |
| Cubeshackles-network-orchestrator | Service | SCAFFOLD (self-declared in own README) | 9 files | generic | Yes (1 router mounted) | n/a | Explicitly states validator routing/settlement coordination "designed, no live wiring yet" |
| cubeshackles-runtime | Library/prototype | PARTIAL (real state-machine logic, zero network I/O) | 11 files | generic | n/a | n/a | Optional handoff target for node-api; never itself calls validator-node |
| cubeshackles-ledger | Service | PARTIAL, self-reported honest (code-complete, deployment-incomplete — real KMS/HSM deployment-required) | 137 files, cleanest collection in org | partial (localization only) | Yes | Real Alembic/SQLAlchemy | Most mature repo per self-disclosure; Waves 2-7 financial-integrity hardening in progress |
| cubeshackles-clearing-house | Service (3 coexisting subsystems) | Mixed — persisted path real/tested, legacy+prep paths PROTOTYPE | 110+ (subagent ran, all pass) | No (docs-localization only) | Yes, 3 surfaces | Real SQLAlchemy (persisted path) | Zero org-level import dependencies — fully isolated |
| cubeshackles-settlement-engine | Service (3 coexisting pipelines) | Institutional pipeline production-leaning; RC2A explicitly SANDBOX_ONLY; older state-machine PROTOTYPE | 125 (subagent ran, all pass) | No (docs-localization only) | Yes | via ledger HTTP/in-process | Real dependency on cubeshackles-ledger (both HTTP and in-process); clearing↔settlement link confirmed unwired both ends |
| cubeshackles-compliance-engine | Service | FUNCTIONAL-shaped, self-labeled stubs (KYC/KYB/KYT/sanctions all explicit stubs) | 21 files | partial (localization only) | Yes, auth-aware | unverified (import error in this pass — env issue) | Same unwired-gate-function pattern as clearing/settlement |
| cubeshackles-market-infrastructure | Service | PARTIAL/UNVERIFIED | 7 files | No | Yes | unverified | No org dependencies found |
| cubeshackles-institutional-gateway | Gateway | FUNCTIONAL (real non-stub depth: normalizer, signed HTTP, fail-closed auth) | 23 files | No CI at all despite 23 real tests | Yes | n/a | Confirmed real signed-HTTP consumer of settlement-engine; owns its own event vocabulary independent of contracts/CIEL |

## Contracts / Ontology / Integration cluster

| Repo | Classification | Maturity | Tests | CI runs tests? | Notes |
|---|---|---|---|---|---|
| cubeshackles-contracts | JSON Schema repo, not pip-installable | Mostly scaffolded enforcement (existence-only tests, zero `jsonschema.validate()` calls org-wide) | 3 files, existence-checks only | No test/lint step | Consumed only via 22 repos' hand-copied filesystem-path `schema_refs.py`; string constants only |
| cubeshackles-integration | CI/gate harness, not a runtime service | FUNCTIONAL as a verification layer | 173 tests + 15 contract tests | Yes, real cross-repo CI checkout | Under active feature freeze; real CIEL-interop-lock enforcement |
| cubeshackles-ontology | Library (pre-freeze kernel) | FUNCTIONAL, real tested logic | not separately counted | n/a | Exactly ONE real consumer org-wide (Cubeshackles-control-plane, SHA-pinned) |
| CubeShackles-Enterprise-Brain | Knowledge-base repo (BIU-G Holdings), distinct from cubeshackles-ontology | N/A (docs/governance, not software) | none | none | Do not confuse with the product's own ontology repo |
| Cubeshackles-control-plane | Service/orchestration platform | FUNCTIONAL, most actively developed repo in its batch | 37 files | No CI workflow found (surprising given active history) | Real pinned dependency on cubeshackles-ai-sdk; only confirmed real ontology consumer |

## Institutional identity / Terrain cluster

| Repo | Classification | Maturity | Live-wired? |
|---|---|---|---|
| cubeshackles-terrain | Pure validation library, NO live service/DB anywhere | FUNCTIONAL as a library (253 tests, 96%+ coverage locally); zero consumer repos declare it as a dependency | N/A — nothing imports the package itself |
| Terrain-pattern adapters (~11 repos: node-api, validator-node, institutional-gateway, settlement-engine, regulatory-reporting, runtime, observability, ai-runtime, etc.) | Independent copy-paste reimplementations, not imports | Varies | **Only 2 of ~11 are live-wired into a request path**: Cubeshackles-node-api (middleware) and Cubeshackles-validator-node (inline check) |

## Kulifikila / Advisor cluster

| Repo | Classification | Maturity | Canonical alignment |
|---|---|---|---|
| Kulifikila | Credit-scoring service | PARTIAL (real tested scoring logic, 78/78 tests; almost no durable persistence) | ISOLATED — no institution_id concept, CIEL adapter is an explicit stub |
| cubeshackles-adviser | Advisory/recommendation service | PARTIAL (real DB-backed identity/billing + genuine farmer-risk engine; core "AI" advisory output is discarded-LLM/deterministic-stub) | ISOLATED — no Terrain, kulifikila stub, ontology governance-only |

## Wallet / edge / demo cluster

| Repo | Classification | Maturity | Notes |
|---|---|---|---|
| CubeWallet | Application (mobile + backend) | PARTIAL — institutional multisig lifecycle is entirely self-contained/mock (`execute_mock()`, explicit "no real settlement" docstring) | Lifecycle A of two disjoint, non-reconciled transaction lifecycles |
| Phone Wedge | Application | Part of Lifecycle B (→ node-api → settlement-engine RC2-A) | Settlement-engine is the real ID/finality authority in this path |
| BualaBuitu | Application | Has NO transaction/settlement code by design — test-enforced (`test_no_local_settlement.py`) | Architecturally guaranteed never to implement local settlement |
| CubePay | **Does not exist as a repo or service** | N/A | Only a disabled UI screen name in CubeWallet + a cosmetic enum literal in the unrelated vegemai-demo app |
| cubeshackles-demo | Application (Gate 7 demo/evidence service) | FUNCTIONAL for narrow scope | Real FastAPI app producing institutional demo evidence bundles |
| cubeshackles-sandbox-lab | Application (simulation) | PARTIAL, single-shot bootstrap | Produces sandbox evidence for BNA/CMC |

## Regulatory / compliance / evidence cluster

| Repo | Classification | Maturity |
|---|---|---|
| cubeshackles-regulatory-reporting | Service | FUNCTIONAL/PARTIAL — real FastAPI app + 16 tests + coverage data. **Contradicts prior memory ("still unbuilt")** — likely means "not integrated into the production monolith," not "no code exists." Flagged for reconciliation, not resolved here. |
| cubeshackles-supervision | Service (read-only regulator views for BNA/CMC/ARSEG/AGT/BODIVA/MINFIN/Sandbox Authority) | FUNCTIONAL |
| cubeshackles-rwa-custody | Service | PARTIAL, single-shot bootstrap |
| cubeshackles-tokenization-engine | Service | PARTIAL, single-shot bootstrap |
| cubeshackles-security | Library (audit/evidence tooling) | SCAFFOLDED |
| cubeshackles-security-framework | Service | FUNCTIONAL — genuine 4-phase feature development (fraud risk, device trust, tx-signing policy, BIP-39 account recovery) |
| cubeshackles-vault | Library (signing boundary) | PARTIAL→FUNCTIONAL — real GCP KMS Ed25519 provider implemented (M1-A/M1-B), self-labeled "scaffolded"/"SANDBOX ONLY" honestly despite this |
| cubeshackles-cubereg | Service | FUNCTIONAL — 144/144 tests, LAW/INTERPRETATION/EXECUTION provenance model implemented (Angola Fiscal Corpus v0, PR #4 open) |

## Frontend / product surface cluster

| Repo | Classification | Maturity |
|---|---|---|
| Cubeshackles-retail | Frontend (citizen/small-business) | FUNCTIONAL, active bugfix cadence, deployed via Cloudflare — **0 test files** |
| Cubeshackles-Retail-DeFi-API | Service (backend monolith) | FUNCTIONAL→PRODUCTION-BOUND — real JWT+RBAC+Institution/User models confirmed fresh; 35 currency codes (was 29 in prior memory, needs reconciliation); committed `.env` file (secrets-hygiene flag) |
| Cubeshackles-web | Frontend (institutional operator dashboard) | FUNCTIONAL — has own `src/ciel/` dir, flagged as an undiscovered CIEL producer/consumer candidate |
| cubeshackles-corporate-web | Frontend (marketing site) | PRODUCTION-BOUND, live via Cloudflare/OpenNext |
| cubeshackles-design-system | Library | FUNCTIONAL, real multi-product build output |
| cubeshackles-storybook | Docs/companion | FUNCTIONAL as a catalog, depends on design-system via sibling path reference |
| cubeshackles-developer-portal | Docs/registry stub | SCAFFOLDED/DORMANT — no actual portal product exists despite the name |
| national-transit-app-cubeshackles | Application | PARTIAL — real backend logic, 0 tests, stray planning-note files at root |
| vegemai-demo | **External client application** (Vegemai, Lda./GIRO — contract MT-VEG-2026-001), not a CubeShackles platform component | FUNCTIONAL→PRODUCTION-BOUND-leaning — most mature, real-world-facing app found in this census; recommend confirming its scope in future censuses |

## Infrastructure / operations / governance cluster

| Repo | Classification | Maturity |
|---|---|---|
| cubeshackles-infra | Deployment config (not an app) | PARTIAL — real 3-env compose/nginx/Prometheus, never iterated since single bootstrap commit |
| cubeshackles-operations | Service | PARTIAL — real FastAPI app, genuine dependency on cubeshackles-ai-sdk |
| cubeshackles-observability | Service | SCAFFOLDED (self-declared) |
| cubeshackles-offline-infrastructure | Library/service | SCAFFOLDED/DORMANT — README itself discloses the queue-admission path is non-functional |
| cubeshackles-disaster-recovery | Tooling | PARTIAL — real ledger backup/CIEL-replay scripts |
| cubeshackles-chaos | Library | SCAFFOLDED — real module structure, zero tests |
| cubeshackles-compute | Library | SCAFFOLDED — unstable CI history |
| cubeshackles-os | Docs/validation script | SCAFFOLDED/DORMANT — no `src/` at all despite the "OS/kernel" framing |
| cubeshackles-platform-specs | Docs-only | DORMANT |
| cubeshackles-provincial-topology | Library | SCAFFOLDED |
| cubeshackles-hardware | Docs/spec-only | DORMANT/SCAFFOLDED, self-admitted |
| cubeshackles-agent | Registry stub | SCAFFOLDED — no agent logic exists |
| cubeshackles-ai-runtime | Service | FUNCTIONAL — real FastAPI inference/advisory boundary |
| cubeshackles-ai-sdk | Library (real packaged SDK) | FUNCTIONAL — genuinely consumed by Cubeshackles-control-plane, cubeshackles-operations |
| cubeshackles-angola-pilot | Application (jurisdiction boundary) | PARTIAL |
| cubeshackles-asset-registry | Service | PARTIAL/UNVERIFIED (env import error, not a confirmed code defect) |
| cubeshackles-tfe | Library (runbook contracts) | PARTIAL |
| cubeshackles (umbrella) | Docs/governance root | N/A as a runtime system; doc-tooling itself is FUNCTIONAL |
| .github | Org-meta | N/A — source of shared `docs-localization.yml` workflow |

## Maturity breakdown (all inspected repos)

- **PRODUCTION-BOUND**: cubeshackles-corporate-web, (Cubeshackles-Retail-DeFi-API borders this)
- **FUNCTIONAL**: Cubeshackles-core, Cubeshackles-node-api, Cubeshackles-validator-node, cubeshackles-ledger (self-reported partial-but-code-complete), cubeshackles-ai-runtime, cubeshackles-ai-sdk, Cubeshackles-control-plane, cubeshackles-integration, cubeshackles-ontology, cubeshackles-terrain (as a library), cubeshackles-institutional-gateway, cubeshackles-security-framework, cubeshackles-supervision, cubeshackles-regulatory-reporting, cubeshackles-cubereg, Cubeshackles-retail, Cubeshackles-Retail-DeFi-API, Cubeshackles-web, cubeshackles-design-system, cubeshackles-storybook, cubeshackles-demo, cubeshackles-operations, vegemai-demo (external)
- **PARTIAL**: cubeshackles-runtime, cubeshackles-clearing-house (mixed), cubeshackles-settlement-engine (mixed), cubeshackles-compliance-engine, cubeshackles-market-infrastructure, Kulifikila, cubeshackles-adviser, CubeWallet, cubeshackles-vault, cubeshackles-angola-pilot, cubeshackles-asset-registry, cubeshackles-rwa-custody, cubeshackles-tokenization-engine, cubeshackles-sandbox-lab, cubeshackles-tfe, cubeshackles-disaster-recovery, cubeshackles-infra, national-transit-app-cubeshackles
- **SCAFFOLDED**: Cubeshackles-network-orchestrator (self-declared), cubeshackles-agent, cubeshackles-chaos, cubeshackles-compute, cubeshackles-observability, cubeshackles-provincial-topology, cubeshackles-security, terrain-pattern adapters not live-wired (9 of 11)
- **DORMANT**: cubeshackles-developer-portal, cubeshackles-os, cubeshackles-platform-specs, cubeshackles-hardware, cubeshackles-offline-infrastructure
- **N/A (docs/governance, not software)**: cubeshackles (umbrella), CubeShackles-Enterprise-Brain, .github

## Cross-cutting environmental caveats
- 3-4 repos in the breadth passes (asset-registry, compliance-engine, market-infrastructure) had real FastAPI apps whose test suites returned `ModuleNotFoundError` in the sandboxed inspection shell (package not `pip install -e`'d) — this is an **environment/packaging gap**, not a confirmed test failure, and should be re-verified in each repo's own venv/CI before being treated as a defect.
- No repo in the org except cubeshackles-corporate-web, vegemai-demo, and Cubeshackles-Retail-DeFi-API (partially) shows a CI workflow that actually runs the application test suite against a real database. Most `cubeshackles-*` platform-layer Python services have `docs-localization.yml` only, or no CI at all, despite having real test directories.
