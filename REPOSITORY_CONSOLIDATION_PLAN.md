# Repository Consolidation Plan — CubeShackles

**Status as of:** 2026-08-16 (classification evidence for the original 58). On 2026-10-09 the org API listed **61** repositories. This plan classifies **60**. `vegemai-demo` is a private repository and is not classified here.
**Method:** Cross-references three sources of truth: (1) `gh api orgs/CubeShackles/repos` — the org's authoritative live repo list; (2) `REPOSITORY_MAP.md` (this repo) — the founder's canonical documented architecture (roles, layers, status, consumers); (3) direct repository inspection (persistence layer checks, module structure) performed for this plan and in the prior `RWA_SYSTEM_MAP.md` audit (`cubeshackles-retail-defi-api`, PR #2). Every repository in scope below is accounted for — 60 in, 60 classified, none of those dropped. `vegemai-demo` is the one org repository not classified here.
**Trigger:** founder-proposed consolidation into authoritative domains, following the RWA lifecycle audit finding that the "clean" microservice decomposition is largely scaffold, while the real persisted system lives in `cubeshackles-retail-defi-api`. This plan keeps 30 repositories independent (11 shared-platform, 7 products, 11 boundary-kept, and `cubeshackles-ledger`) and leaves the retail API repository in place. Founder decisions on 2026-10-09 (§7) also keep `cubeshackles-core`, `cubeshackles-institutional-gateway`, `cubeshackles-security-framework`, and `cubeshackles-node-api` outside the merge, keep `cubeshackles-disaster-recovery` independent, and keep `cubeshackles-cubereg` independent. The earlier whole-repo merge scope was 28. The remaining proposed full-absorption scope is 23. That does not produce the previously published 40-repository end state. This decision updates the plan only. It does not merge repositories, move data, or change runtime behavior.
**Names:** classification tables use the slugs in `REPOSITORY_MAP.md`. GitHub and some local checkouts use a leading capital for the same repository (`Cubeshackles-core`, `Cubeshackles-control-plane`, `Cubeshackles-validator-node`, `Cubeshackles-network-orchestrator`, `Cubeshackles-node-api`, `Cubeshackles-phone-wedge`, `Cubeshackles-web`, `Cubeshackles-retail`, `Cubeshackles-Retail-DeFi-API`). `Cubeshackles-Enterprise-Brain`, `CubeWallet`, and `BualaBuitu` keep the casing already recorded in the map.
**Relationship to prior audit:** this plan assumes the findings in `RWA_SYSTEM_MAP.md` (in `cubeshackles-retail-defi-api`, PR #2) as ground truth for the 14 RWA-chain repos it covered. Nothing here re-litigates those findings; it extends the same evidence standard — IMPLEMENTED/PARTIAL/STUB/DOCUMENTATION-ONLY tags backed by file evidence — to the other 44 repos.

---

## 0. The one fact that governs every decision below

`REPOSITORY_MAP.md` describes 12 of the institutional-finance-stack repos as **"active"** with detailed, specific behavior ("Registers, classifies, validates... lifecycle transitions," "Consumes `asset.validated.v0.1` events; creates and manages tokenization plans..."). Direct inspection for `RWA_SYSTEM_MAP.md` found that **11 of those 12 have no database, no ORM models, no persistence layer at all** — they are Pydantic domain objects and FastAPI routes with nothing behind them. Only `cubeshackles-ledger` has a real schema among that group.

This means: **consolidating the documented 12-repo institutional-finance-stack costs almost nothing in migration risk** — there is no data to move, because there is no data. The real migration risk in this entire plan is concentrated in exactly one place: **absorbing the actually-persisted RWA logic out of `cubeshackles-retail-defi-api`**, which has 58 SQLAlchemy models, 12 live Alembic migrations, one of which (`16c208fbde59`) silently drops 27 production tables, and a currently-broken migration graph (`fix_decimal_precision_20260307`). Every "MERGE INTO" entry below is scored for migration risk with this asymmetry in mind: **merging documentation-only code is LOW risk; merging or extracting anything touching `cubeshackles-retail-defi-api`'s live schema is HIGH risk until the migration-graph and autogenerate-drift issues in `RWA_SYSTEM_MAP.md` §5–§7 are fixed first.**

---

## 1. Full classification — 60 repositories in this plan

Legend: **KEEP** = stays independent as-is. **MERGE INTO** = folds into a named target. **ARCHIVE** = candidate for archival/retirement (not currently load-bearing). **PRODUCT** = customer/end-user-facing surface, kept independent by design. **SHARED PLATFORM** = cross-cutting authority every other repo consumes; consolidating it would break the layer-isolation model. **REQUIRES AUDIT** = insufficient evidence in this pass to classify safely; needs the same file-level treatment `RWA_SYSTEM_MAP.md` gave the RWA chain before a merge decision is made.

### 1.1 → `cubeshackles-rwa-platform` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers (per `REPOSITORY_MAP.md` + audit) | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-asset-registry` | MERGE INTO `rwa-platform/registry` | **DOCUMENTATION-ONLY** — Pydantic-only, no SQLAlchemy dep, no alembic dir (verified) | Standalone FastAPI, no DB | Tokenization Engine consumes `asset.validated.v0.1` (documented, not observed running) | **LOW** — no data to migrate, ~28 Python files |
| `cubeshackles-tokenization-engine` | MERGE INTO `rwa-platform/tokenization`, `rwa-platform/issuance` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic (verified) | Standalone FastAPI, no DB | RWA Custody consumes issuance instructions (documented) | **LOW** — no data to migrate, ~36 Python files |
| `cubeshackles-rwa-custody` | MERGE INTO `rwa-platform/custody` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic (verified) | Standalone FastAPI, no DB | Downstream financial ops (documented) | **LOW** — no data to migrate, ~39 Python files |
| RWA portions of `cubeshackles-retail-defi-api` (`AssetToken`, `AssetTokenBalance`, `Wallet`/`VaultNode` custody, `Loan`/`Stake`/`InvestmentFund`/`InvestmentPosition`/`RecurringInvestment` corporate-actions models) | MERGE INTO `rwa-platform/{tokenization,custody,corporate-actions,redemption}` — **do this LAST, not first** | **IMPLEMENTED** — real Postgres schema, 58 SQLAlchemy models, 12 Alembic migrations, 8 live API endpoint modules depend on adjacent tables | Monolith FastAPI, shared DB with the entire retail product | Retail mobile/web product, `cubeshackles-retail` frontend | **HIGH** — this is the one part of the whole plan with real data. Do not attempt extraction until: (a) `fix_decimal_precision_20260307`'s broken `down_revision` is fixed (`RWA_SYSTEM_MAP.md` §4, §10.1), (b) `16c208fbde59`'s 27-table drop is neutralized (§5.1, §10.2), (c) `app/db/base.py` imports all 58 models so `Base.metadata` is trustworthy for any future extraction migration. Extracting live tables out of a monolith with a currently-broken migration graph is how you turn one outage into two. |

**valuation / lifecycle module** — no repo in this classified set owns this explicitly; `InvestmentFund`/`InvestmentPosition` in the monolith carry some of this responsibility informally. **REQUIRES AUDIT**: decide whether `rwa-platform/valuation` is a new module built fresh, or extracted from monolith investment models — not yet scoped.

### 1.2 → `cubeshackles-regulatory` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-compliance-engine` | MERGE INTO `regulatory/kyc`, `regulatory/aml`, `regulatory/screening`, `regulatory/policy-engine` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified); "mixed" visibility per map | Standalone FastAPI, no DB | Gates Institutional Gateway forwarding and Clearing House intake (documented) | **LOW** — no data, ~40 Python files |
| `cubeshackles-regulatory-reporting` | MERGE INTO `regulatory/regulatory-reporting` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified); 51 Python files but zero persistence | Standalone FastAPI, no DB | Consumes evidence packs from `cubeshackles-integration` (documented) | **LOW** — no data, but see the note under this §1.2 table: this is the audit's flagged weakest link — zero implementation exists **anywhere in the org**, monolith included. Merging two empty rooms doesn't fill either. |
| `cubeshackles-supervision` | MERGE INTO `regulatory/supervision` | Not persistence-checked in this pass — module name `src/supervision` only confirmed | Standalone, read-only per map ("does not approve, enforce, clear, settle, or custody") | Generates supervisory views for BNA/CMC/ARSEG/AGT/BODIVA/MINFIN (documented) | **LOW-MEDIUM** — read-only evidence generator per its own doctrine; verify it has no independent state before merge |
| `cubeshackles-institutional-gateway` | **KEEP — outside consolidation** until the scope-split audit in §7.2 is completed. Previously a partial merge into `regulatory`. | Gateway itself is DOCUMENTATION-ONLY (no sqlalchemy/alembic, verified in `RWA_SYSTEM_MAP.md` §3); "mixed" visibility, real-protocol adapters (REST/FIX/ISO 20022/SWIFT/gRPC) per map | Standalone, normalizes into `InstitutionalInstruction` contract | Compliance Engine, Clearing House (documented) | **MEDIUM** — this repo is genuinely two things (ingress protocol adapters + regulatory normalization). The repository stays whole until that split is written down. |
| `cubeshackles-security-framework` | **KEEP — outside consolidation** until the scope-split audit in §7.2 is completed. Previously claimed by both `regulatory` and `security-platform`, and counted once. | **PARTIAL** — has a real `sqlalchemy` dependency (verified, `pyproject.toml`), no `alembic.ini` found — unclear if that dependency is used for anything live or vestigial | Standalone; per map: "Produces deterministic governance evidence — not a live scanning tool" | Feeds NIST CSF 2.0/ISO 27001 evidence artifacts (documented) | **MEDIUM** — has real code (not a stub). The persistence question stays open before either domain receives it. |

**Note on the audit's own conclusion:** `RWA_SYSTEM_MAP.md` §7/§8 found Regulatory Reporting has **zero implementation anywhere** — not "fragmented across repos" but genuinely absent as working code, in both the pilot-rail repo and the monolith. Consolidating `cubeshackles-regulatory` solves the *organizational* fragmentation (one authoritative home instead of four half-repos) but does **not** by itself solve the *implementation* gap — that's still greenfield work, now with one clear place to put it instead of four candidate places.

### 1.3 → `cubeshackles-market-core` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-settlement-engine` | MERGE INTO `market-core/settlement` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified); map calls it "the sole v0.1 internal ledger finality authority" | Standalone, consumes `transaction.validated.v0.1`, emits `transaction.settled.v0.1` (documented, not observed running against real data) | Downstream of validator path (documented) | **LOW** — no data, ~48 Python files |
| `cubeshackles-clearing-house` | MERGE INTO `market-core/clearing` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified) | Standalone, produces `ClearingDecision` outputs (documented) | Settlement Engine gate ("Settlement may only proceed after `clearing.settlement.eligible.v0.1`" per map) | **LOW** — no data, ~53 Python files |
| `cubeshackles-market-infrastructure` | MERGE INTO `market-core/positions`, `market-core/reconciliation` (CCP-simulation logic) | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified); map: "Risk infrastructure simulation only — not a licensed CCP" | Standalone | Emits deterministic risk control outputs (documented) | **LOW** — no data, ~35 Python files |
| settlement logic embedded in `cubeshackles-retail-defi-api` (`SettlementBatch` model, `settlement_batch` table) | MERGE INTO `market-core/settlement` — **same caution as §1.1's monolith row** | **IMPLEMENTED** — real table, single-table netting (`net_positions` JSON blob), `central_signature`, status enum; audit flagged this as PARTIAL even within the monolith (no real clearing/netting engine, just a JSON blob) | Monolith FastAPI, shared DB | Retail product | **MEDIUM-HIGH** — smaller surface than the RWA extraction (one table, not dozens), but still real data behind a live product; sequence after the monolith's migration-graph is fixed, same reasoning as §1.1 |

### 1.4 `cubeshackles-ledger` — KEEP, do not merge

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-ledger` | **KEEP — independent** until its relationship with the monolith `LedgerEvent` / `LedgerSync` tables is established (§7.3) | **IMPLEMENTED (isolated)** — real Postgres schema, 1 Alembic migration (`001_initial_ledger_schema.py`), real `sqlalchemy`/`alembic.ini` (verified). Map: "double-entry, hashchain integrity... Posted journals are immutable." Dev port 8086. | Standalone, own DB | Should be consumed by everything downstream of settlement (documented); **not confirmed wired to the monolith's own `LedgerEvent`/`LedgerSync` tables** — flagged as an open P1 in `RWA_SYSTEM_MAP.md` §7.4 | **N/A for merge (staying separate)**. Two schemas may currently exist — this repository, and the monolith's `ledger_event` / `ledger_sync` tables — with no observed reconciliation. Neither is treated as the sole canonical ledger until that trace exists. |

### 1.5 → `cubeshackles-security-platform` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-security` | MERGE INTO `security-platform/security-policy` | Not deep-checked; map: "scaffolded," threat model/static analysis/dependency review/secret scanning gates | Standalone, gate-only | CI/gate suite | **LOW** — scaffolded per map, gate tooling not stateful |
| `cubeshackles-security-framework` | **KEEP — outside consolidation** (§7.2). Same repository as the §1.2 row. Counted once. | See §1.2 — has real `sqlalchemy` dep, no confirmed alembic | Standalone | Control plane orchestrates it (documented: control-plane's integration list) | **MEDIUM** — persistence of that dependency is part of the audit that must finish before this repository enters `regulatory` or `security-platform`. |
| `cubeshackles-vault` | MERGE INTO `security-platform/signing`, `kms`, `key-rotation`, `secrets`, `recovery` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic (verified in `RWA_SYSTEM_MAP.md` §3.1). Confirmed: `src/{signing,recovery,secrets,contracts,keys,rotation,audit}` — a real key-management/signing domain model even without a live DB; aligns with GCP Cloud KMS production-signing work in progress | Standalone, "never stores secrets in the repository" per map | RC2_FREEZE milestone calls it one of the sole execution-truth boundaries (map §16) | **LOW-MEDIUM** — no data to migrate, but this repo carries real institutional weight (RC2_FREEZE named it explicitly as consensus-adjacent truth); the founder's own note to "keep a conceptual distinction internally" between security-platform's sub-modules matters more here than for most merges — do not flatten `signing`/`kms` into generic `security-policy` |
| `cubeshackles-disaster-recovery` | **KEEP — independent.** Operational continuity stays here. Crypto-key recovery is not in this tree. Signing stays in `cubeshackles-vault`. | Scaffolded per map; `src/{recovery,dr_lib,replay,failover,backups,drills}` | Standalone | Regional outage/replay rebuild doctrine (documented) | **N/A for merge.** Full retirement is not justified. |

### 1.6 → `cubeshackles-network` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-validator-node` | MERGE INTO `network/validator` | Has a `src/persistence` module (module-name only, not deep-verified); map: "active," "validation authority only — does not settle" | Standalone | DAG ordering, validator attribution (documented) | **MEDIUM** — has a persistence module unlike most pilot-rail repos; verify what it actually persists before assuming this is a clean, dataless merge like the RWA-chain repos |
| `cubeshackles-network-orchestrator` | MERGE INTO `network/orchestration` | No sqlalchemy dep found (verified) | Standalone; map: "active" | Validator membership, peer gossip (documented) | **LOW** |
| `cubeshackles-provincial-topology` | MERGE INTO `network/provincial-routing`, `topology` | No sqlalchemy dep found (verified); map: "scaffolded," "planning authority only" | Standalone | Angola-first node placement doctrine | **LOW** |
| `cubeshackles-offline-infrastructure` | MERGE INTO `network/offline` | No sqlalchemy dep found (verified); **map itself flags a P0**: "the queue-admission path raises before accepting or persisting work — offline transaction processing is not operational... not merely 'scaffolded' in the usual sense" (§6, dated 2026-07-19) | Standalone | Phone-wedge / offline transaction entry points | **LOW for the merge itself** (no data), but inherits a pre-existing P0 functional blocker the founder's own map already documents — merging doesn't fix it, just relocates it. Worth linking `docs/CLAIMS_REGISTER.md`'s existing entry rather than re-discovering it. |
| `cubeshackles-node-api` | **KEEP — adjacent to `network`** pending deployment verification and runtime dependency analysis (§7.4). Previously counted inside the network merge set. | **PARTIAL/gateway-only** — 111 commits (2nd-most active pilot-rail repo, per `RWA_SYSTEM_MAP.md` §3.1), no sqlalchemy/alembic, `models/` has only query-helper files, not domain models. Map: "Public contract gateway — online ingress authority," dev port 8090 | Standalone | External transaction submission/query (documented) | **MEDIUM** — deployment and runtime dependencies are unaudited. The repository stays adjacent until that evidence exists. |

### 1.7 → `cubeshackles-platform` (proposed consolidation target — "audit first," per founder's own framing)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-core` | **KEEP — independent** pending the Wave 2 authority and ledger audit (§7.1). Previously counted inside the `platform` merge set. | 74 commits, 169 Python files — by far the most developed pilot-rail-adjacent repo (`RWA_SYSTEM_MAP.md` §3 cross-cutting note). Map: "Canonical authority for economics, ledger replay, and fee governance." Persistence not deep-checked in this pass | Standalone; REQUIRED in the local sibling layout for all gate runs | Named as canonical authority for economics, ledger replay, and fee governance in map §15 | **HIGH-UNKNOWN** — unaudited at the scale that matters. It stays the authority repository. It is not an absorption source. |
| `cubeshackles-runtime` | MERGE INTO `platform/runtime` — **contingent on `cubeshackles-core` audit above**, since runtime's map role ("orchestration authority — does not create finality") sits right next to core's | No sqlalchemy dep found (verified); map: "scaffolded" | Standalone | Execution engine, DAG scheduling, settlement handoff orchestration (documented) | **LOW** for the repo itself (scaffolded, no data), but its correct final home depends on how the `cubeshackles-core` audit resolves — don't merge runtime before core is understood, or you may need to re-split immediately |
| `cubeshackles-control-plane` | MERGE INTO `platform/control-plane` — **REQUIRES AUDIT on scope, not on safety** | 153 Python files (verified count), no sqlalchemy dep found; map: "scaffolded," "mixed" visibility. Its own doctrine (`SYSTEM_ARCHITECTURE.md` §5a) explicitly notes its integration reach is broader than any single-layer repo — it touches ai-runtime, ai-sdk, ontology, agent, security-framework, observability, compliance-engine, regulatory-reporting, and institutional-gateway | Standalone | "Sole point through which a user, service, or AI agent request is authenticated, authorized, routed... and recorded" (map) | **MEDIUM** — not a data-migration risk (no persistence found) but a *governance* risk: this repo's entire design purpose is to mediate every other domain without gaining authority over any of them (map's own explicit anti-backdoor rule). Merging it into `platform` is architecturally defensible only if the merge preserves that mediation-not-authority boundary — a structural risk, not a data risk. |
| `cubeshackles-integration` | MERGE INTO `platform/integration` — lowest-risk item in this whole section | 480 Python files (verified count, largest of the group checked here), no sqlalchemy dep found; map: "Cross-repo integration and production gate suite... Does not run production traffic." | Standalone; REQUIRED for gate runs | Every repo in the gate chain (by design) | **LOW-MEDIUM** — no data, but it's a large, actively-maintained test/gate harness (480 files) wired to every other repo's CI; a merge needs a mechanical path migration pass for every repo's CI config pointing at it, more of a plumbing risk than a data risk |

### 1.8 → `cubeshackles-ai` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-ai-runtime` | MERGE INTO `ai/runtime` | No sqlalchemy dep found (verified); map: "active," "private," 55 tests passing, `POST /v0.1/infer`, stabilized at `AI_NATIVE_M5` | Standalone, composed by `cubeshackles-os` | 11 platform AI agents (documented) | **LOW-MEDIUM** — no persistence found, but this is a stabilized, tested, milestone-frozen (`AI_NATIVE_M5` "Complete") service — treat the freeze status as a real constraint, not just a scaffold to fold in casually |
| `cubeshackles-ai-sdk` | MERGE INTO `ai/sdk` | No sqlalchemy dep found (verified); map: "active," "public," 23 tests passing | Standalone consumer library | "Applications must not implement their own HTTP inference clients" (map) — i.e. this is a dependency of other repos, not just a peer | **LOW-MEDIUM** — it's a published library other repos import; merging it changes every consumer's import path, a mechanical but org-wide edit |
| `cubeshackles-agent` | MERGE INTO `ai/agents` | Not persistence-checked; map: "pre-freeze," "public" — "declares the capability contract for a future local AI engineering agent. The agent itself is not built here" | Standalone, contract-only | Foundation layer companion to CIEL/ontology/TFE | **LOW** — explicitly a contract-only repo per its own doctrine, nothing to migrate |
| `Cubeshackles-Enterprise-Brain` | MERGE INTO `ai/enterprise-brain` — **or just don't**, see risk note | **MISSING** — confirmed via GitHub API: private, `size: 0`, no committed content (map §14a, dated 2026-07-18) | N/A | N/A | **NONE** — there is nothing here to merge. This is a placeholder repo. Folding an empty repo into `cubeshackles-ai` is a rename, not a consolidation; consider just deleting/renaming rather than "merging." |
| `cubeshackles-adviser` | MERGE INTO `ai/adviser` — **flagged as the one item in this whole plan closest to a live product** | **IMPLEMENTED** — real `sqlalchemy` dependency AND a real `alembic.ini` at `apps/adviser-api/alembic.ini` (both verified, this is the only repo outside the ledger/monolith/security-framework cluster with a confirmed live migration setup). Map: "active," "mixed," dev port 8080, 5 named agents (PortfolioAI, RebalanceAI, TaxAI, AlertAI, SimulationAI) | Standalone, own DB, own port | Consumes `cubeshackles-ai-sdk`; runs outside consensus-critical path (documented) | **MEDIUM-HIGH** — this is a real, running, data-backed service, not a scaffold. It deserves the same migration-graph check (`alembic heads`) that surfaced the monolith's broken chain before anyone plans an extraction/merge. Do not assume it's dataless like its `cubeshackles-ai` siblings just because they're grouped together in the founder's proposal — verify independently. |

### 1.9 Repositories created after the 2026-08-16 pass

`gh api orgs/CubeShackles/repos` on 2026-10-09 returned 61 repositories. Two of the three created after 2026-08-16 are classified in this plan. `vegemai-demo` is a private repository and is not classified here.

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-cubereg` | **KEEP — independent.** Canonical candidate for the fiscal-rule, calculation, conformance, discrepancy, and evidence service (§7.5, §8). It is not assigned to `regulatory` or `platform`. | Repository description: fiscal rule registry, deterministic tax calculation, conformance testing, and a discrepancy/evidence engine. Default branch uses SQLAlchemy; `app/db/base.py` states that the v1 slice uses SQLite. No `alembic.ini` was present in the default-branch tree. Created 2026-09-28. Database migration and production-readiness are unverified. | Not re-audited in this update | Not a row in the current `REPOSITORY_MAP.md` | **UNKNOWN** — the repository stays independent. Folding it is outside this decision. |

`cubeshackles-corporate-web` (created 2026-08-18) is kept in §4. Its repository description calls it the official corporate website. The default branch is a Next.js tree, and that tree had no Alembic or Prisma path.

---

## 2. KEEP — shared platform / foundational singletons (not part of any consolidation wave)

These sit above or across the domains being consolidated; folding them in would break the layer-isolation model the map itself documents (§5a's explicit "no target gains authority by appearing in an integration list" rule generalizes to all of these).

| Repo | Why it stays independent |
|---|---|
| `cubeshackles` | Umbrella doctrine repo — contains no protocol code, is the authority this very plan defers to (and where this plan itself now lives) |
| `cubeshackles-contracts` | Schema authority for the entire ecosystem — every consolidated domain still needs one shared, versioned contract source, not five |
| `cubeshackles-ciel` | Canonical Institutional Event Language — the event vocabulary every domain emits into |
| `cubeshackles-ontology` | Typed entity/relationship authority — who and what participates in every event |
| `cubeshackles-terrain` | Reality-modeling layer — "all production systems must consume Terrain before execution" (map) |
| `cubeshackles-tfe` | Runbook contract authority — operational knowledge, cross-cutting by design |
| `cubeshackles-os` | Platform composition/OS kernel — composes services, does not duplicate their code |
| `cubeshackles-platform-specs` | Product/UX governance authority, sits above the design system |
| `cubeshackles-developer-portal` | Developer-facing knowledge surface — a distinct audience/publishing boundary from any engineering domain |
| `cubeshackles-design-system` | "Every frontend must consume this package" (map) — a dependency of the product tier, not a peer of any backend domain |
| `cubeshackles-storybook` | Documents the design system; not itself an authority |

## 3. PRODUCT — kept independently recognizable (per founder direction, confirmed consistent with map §11)

| Repo | Note |
|---|---|
| `CubeWallet` | Confirmed real backend: `sqlalchemy` in `requirements.txt` (verified) — a genuine product with its own persistence, not a scaffold |
| `BualaBuitu` | Confirmed real backend: `sqlalchemy` in `backend/requirements.txt` (verified) |
| `national-transit-app-cubeshackles` | Product surface per map §11 |
| `kulifikila` | Private credit-intelligence product; map explicitly names it canonical authority for its domain |
| `cubeshackles-retail` | Retail-facing Next.js frontend, consumes `cubeshackles-retail-defi-api` |
| `cubeshackles-phone-wedge` | Device-initiation product surface |
| `cubeshackles-web` | Institutional/public explorer surface |

## 4. Kept separately for release/audience/security boundary reasons

| Repo | Note |
|---|---|
| `.github` | Org governance repo — confirmed present via GitHub org API; not counted in `REPOSITORY_MAP.md`'s role tables. The org list on 2026-10-09 is 61 repositories. This plan classifies 60. `vegemai-demo` is a private repository and is not classified here. |
| `cubeshackles-demo` | Regulator/bank-grade demo environment, no real money movement — a distinct evidence-artifact product, not infrastructure |
| `cubeshackles-sandbox-lab` | Deterministic sandbox rail for BNA/BODIVA/CMC discussions — same reasoning as `cubeshackles-demo` |
| `cubeshackles-angola-pilot` | Controlled pilot-corridor scope document/boundary, not a service |
| `cubeshackles-chaos` | Test-only controlled-failure harness |
| `cubeshackles-observability` | Scaffolded target for future audit-grade telemetry; map: "No production telemetry stack is shipped" — genuinely nothing to consolidate yet, revisit once it has real content |
| `cubeshackles-operations` | Deployment/rollback/incident/SLO doctrine, 43 tests passing per map — active and cross-cutting by nature, doesn't belong inside any single domain |
| `cubeshackles-infra` | Deployment/environment tooling; also confirmed to contain Docker build-context copies of `CubeWallet`'s backend (found during this pass) — worth a light cleanup pass independent of consolidation, since stale copies of another repo's `requirements.txt` inside infra tooling are exactly the kind of drift this whole plan is trying to reduce |
| `cubeshackles-compute` | Scaffolded, private, future sovereign compute — no current consumers to disrupt |
| `cubeshackles-hardware` | Scaffolded, private, silicon roadmap — same reasoning |
| `cubeshackles-corporate-web` | Official corporate website (repository description, created 2026-08-18). Default branch is a Next.js tree with no Alembic or Prisma path. Distinct publishing surface, not a domain merge source. |

---

## 5. Consolidation wave sequencing

Matches the founder's proposed sequencing, annotated with the migration-risk evidence gathered in this pass:

### Wave 1 (P0) — `rwa-platform`, `regulatory`, `market-core`
- **Mechanically safe today**: 8 of the 10 source repos across these three targets are DOCUMENTATION-ONLY (verified, no persistence) — folding them is a code-move + import-path exercise, not a data migration.
- **Sequencing constraint discovered in this pass**: within each of the three targets, do the DOCUMENTATION-ONLY repos first (asset-registry, tokenization-engine, custody, compliance-engine, regulatory-reporting, settlement-engine, clearing-house, market-infrastructure — 8 repos, low risk, can start immediately), and treat pulling the corresponding *live* logic out of `cubeshackles-retail-defi-api` (asset tokens/custody/settlement-batch) as a **separate, later sub-phase gated on** `RWA_SYSTEM_MAP.md` §10 items 1–2 (fix the broken migration graph, neutralize the 27-table-drop migration) being resolved first. Don't let Wave 1's "P0, do it now" urgency pull the monolith extraction forward before its prerequisite is met — that's the one place in this entire plan an outage is actually possible.
- **Founder decision (§7.2):** `cubeshackles-institutional-gateway` and `cubeshackles-security-framework` stay outside Wave 1 until the scope-split audit is completed. They are not merge sources in the remaining 23.

### Wave 2 (P1) — `network`, `security-platform`, `platform` (audit-gated), `ai`
- **`platform`**: `cubeshackles-core` stays independent (§7.1). It is not a merge source. The remaining platform sources are still proposals.
- **`network`**: `cubeshackles-node-api` stays adjacent (§7.4). `cubeshackles-validator-node`'s `src/persistence` module still deserves a closer look before treating that repository as dataless.
- **`security-platform`**: `cubeshackles-vault`'s RC2_FREEZE-named role means its sub-module boundaries (signing/kms/key-rotation/secrets/recovery) should be preserved structurally even inside a consolidated repo, per the founder's own note — this pass independently agrees.
- **`ai`**: `cubeshackles-adviser` is the one repo in this wave with a confirmed live `alembic.ini` + real data — treat it with the same caution as the Wave-1 monolith extraction, not as dataless as its `cubeshackles-ai-runtime`/`ai-sdk`/`agent` siblings. `Cubeshackles-Enterprise-Brain` has zero content — a rename/delete, not a merge.

---

## 6. Summary count

- **61 repositories in the org** on 2026-10-09 (`gh api orgs/CubeShackles/repos`). **60 are classified here.** `vegemai-demo` is a private repository and is not one of those 60. No further description is recorded.
- **`REPOSITORY_MAP.md` on this branch records 56 mapped repositories** (2026-10-09), including `cubeshackles-corporate-web`. That is the documented architecture map. It is not the organization list of 61, and it is not the 60 classified in this plan. `cubeshackles-cubereg` is classified here and is not a row in that map. `vegemai-demo` is not a row in that map.
- **11 shared-platform / foundational singletons** — kept (§2, includes this repo).
- **7 products** — kept (§3).
- **11 kept for release/audience/security boundary reasons** — kept (§4, including `cubeshackles-corporate-web`).
- **1 (`cubeshackles-ledger`)** — kept independent until the monolith trace in §7.3.
- **1 (`cubeshackles-retail-defi-api`)** — the repository stays. Extraction of live tables is a later migration, not a repository deletion.
- **1 (`cubeshackles-cubereg`)** — kept independent (§7.5). It is inside the recounted end state.
- **5 held independent** — `cubeshackles-core`, `cubeshackles-institutional-gateway`, `cubeshackles-security-framework`, `cubeshackles-node-api`, and `cubeshackles-disaster-recovery`. 11 + 7 + 11 + 1 + 1 + 1 + 5 + 23 = 60.
- **23 repos** — proposed full absorptions. The earlier 28 included the five repositories now held independent. `cubeshackles-security-framework` is counted once, in the held set.
- **Seven named targets, none present in the organization list:** `rwa-platform`, `regulatory`, `market-core`, `security-platform`, `network`, `platform`, `ai`. No eighth target is named.
- **Nothing in this update retires or creates a repository.** The classified count remains 60. If those 23 retirements were later accepted and the seven targets were created, the result would be 60 − 23 + 7 = **44**. The previously published 40 counted 28 absorptions and 8 new repositories. `vegemai-demo` is not in the 60 or the 44.

---

## 7. Founder decisions (2026-10-09)

These dispositions are decided. The audits they name are still open. This section authorizes planning and documentation only.

1. Keep `cubeshackles-core` independent pending the Wave 2 authority and ledger audit.
2. Keep `cubeshackles-institutional-gateway` and `cubeshackles-security-framework` outside consolidation until the scope-split, persistence, and migration audit is completed.
3. Keep `cubeshackles-ledger` independent until its relationship with the monolith `LedgerEvent` / `LedgerSync` tables is established.
4. Keep `cubeshackles-node-api` adjacent to network pending deployment verification and runtime dependency analysis.
5. Keep `cubeshackles-cubereg` independent as the canonical candidate for the fiscal-rule, calculation, conformance, discrepancy, and evidence service. It is not assigned to `regulatory` or `platform`. Service boundary: §8. Database migration and production-readiness stay unverified.

---

## 8. CubeReg service boundary

`cubeshackles-cubereg` stays its own repository. It is the canonical candidate for fiscal rules, calculation, conformance, discrepancy, and evidence.

AGT and the applicable legal framework remain the statutory authority. CubeReg does not decide what Angola's tax law means. This plan does not record integrations with other products as implemented. Database migration and production-readiness are unverified.

The proposed full-absorption sources, after the five holds above, are:

| Proposed target | Full-absorption sources (23) |
|---|---|
| `cubeshackles-rwa-platform` | `cubeshackles-asset-registry`, `cubeshackles-tokenization-engine`, `cubeshackles-rwa-custody` |
| `cubeshackles-regulatory` | `cubeshackles-compliance-engine`, `cubeshackles-regulatory-reporting`, `cubeshackles-supervision` |
| `cubeshackles-market-core` | `cubeshackles-settlement-engine`, `cubeshackles-clearing-house`, `cubeshackles-market-infrastructure` |
| `cubeshackles-security-platform` | `cubeshackles-security`, `cubeshackles-vault` |
| `cubeshackles-network` | `cubeshackles-validator-node`, `cubeshackles-network-orchestrator`, `cubeshackles-provincial-topology`, `cubeshackles-offline-infrastructure` |
| `cubeshackles-platform` | `cubeshackles-runtime`, `cubeshackles-control-plane`, `cubeshackles-integration` |
| `cubeshackles-ai` | `cubeshackles-ai-runtime`, `cubeshackles-ai-sdk`, `cubeshackles-agent`, `Cubeshackles-Enterprise-Brain`, `cubeshackles-adviser` |
