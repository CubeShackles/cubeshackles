# Repository Consolidation Plan — CubeShackles

**Status as of:** 2026-08-16
**Method:** Cross-references three sources of truth: (1) `gh api orgs/CubeShackles/repos` — the org's authoritative live repo list, **58 repositories, verified count**; (2) `REPOSITORY_MAP.md` (this repo) — the founder's canonical documented architecture (roles, layers, status, consumers); (3) direct repository inspection (persistence layer checks, module structure) performed for this plan and in the prior `RWA_SYSTEM_MAP.md` audit (`Cubeshackles-Retail-DeFi-API`, PR #2). Every repo below is accounted for — 58 in, 58 classified, none dropped.
**Trigger:** founder-proposed consolidation of ~54 platform repos (all but the 4 kept-independent products/shared-platform tiers) down to 8 authoritative domains, following the RWA lifecycle audit finding that the "clean" microservice decomposition is largely scaffold, while the real persisted system lives in `Cubeshackles-Retail-DeFi-API`.
**Relationship to prior audit:** this plan assumes the findings in `RWA_SYSTEM_MAP.md` (in `Cubeshackles-Retail-DeFi-API`, PR #2) as ground truth for the 14 RWA-chain repos it covered. Nothing here re-litigates those findings; it extends the same evidence standard — IMPLEMENTED/PARTIAL/STUB/DOCUMENTATION-ONLY tags backed by file evidence — to the other 44 repos.

---

## 0. The one fact that governs every decision below

`REPOSITORY_MAP.md` describes 12 of the institutional-finance-stack repos as **"active"** with detailed, specific behavior ("Registers, classifies, validates... lifecycle transitions," "Consumes `asset.validated.v0.1` events; creates and manages tokenization plans..."). Direct inspection for `RWA_SYSTEM_MAP.md` found that **11 of those 12 have no database, no ORM models, no persistence layer at all** — they are Pydantic domain objects and FastAPI routes with nothing behind them. Only `cubeshackles-ledger` has a real schema among that group.

This means: **consolidating the documented 12-repo institutional-finance-stack costs almost nothing in migration risk** — there is no data to move, because there is no data. The real migration risk in this entire plan is concentrated in exactly one place: **absorbing the actually-persisted RWA logic out of `Cubeshackles-Retail-DeFi-API`**, which has 58 SQLAlchemy models, 12 live Alembic migrations, one of which (`16c208fbde59`) silently drops 27 production tables, and a currently-broken migration graph (`fix_decimal_precision_20260307`). Every "MERGE INTO" entry below is scored for migration risk with this asymmetry in mind: **merging documentation-only code is LOW risk; merging or extracting anything touching `Cubeshackles-Retail-DeFi-API`'s live schema is HIGH risk until the migration-graph and autogenerate-drift issues in `RWA_SYSTEM_MAP.md` §5–§7 are fixed first.**

---

## 1. Full classification — all 58 repositories

Legend: **KEEP** = stays independent as-is. **MERGE INTO** = folds into a named target. **ARCHIVE** = candidate for archival/retirement (not currently load-bearing). **PRODUCT** = customer/end-user-facing surface, kept independent by design. **SHARED PLATFORM** = cross-cutting authority every other repo consumes; consolidating it would break the layer-isolation model. **REQUIRES AUDIT** = insufficient evidence in this pass to classify safely; needs the same file-level treatment `RWA_SYSTEM_MAP.md` gave the RWA chain before a merge decision is made.

### 1.1 → `cubeshackles-rwa-platform` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers (per `REPOSITORY_MAP.md` + audit) | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-asset-registry` | MERGE INTO `rwa-platform/registry` | **DOCUMENTATION-ONLY** — Pydantic-only, no SQLAlchemy dep, no alembic dir (verified) | Standalone FastAPI, no DB | Tokenization Engine consumes `asset.validated.v0.1` (documented, not observed running) | **LOW** — no data to migrate, ~28 Python files |
| `cubeshackles-tokenization-engine` | MERGE INTO `rwa-platform/tokenization`, `rwa-platform/issuance` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic (verified) | Standalone FastAPI, no DB | RWA Custody consumes issuance instructions (documented) | **LOW** — no data to migrate, ~36 Python files |
| `cubeshackles-rwa-custody` | MERGE INTO `rwa-platform/custody` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic (verified) | Standalone FastAPI, no DB | Downstream financial ops (documented) | **LOW** — no data to migrate, ~39 Python files |
| RWA portions of `Cubeshackles-Retail-DeFi-API` (`AssetToken`, `AssetTokenBalance`, `Wallet`/`VaultNode` custody, `Loan`/`Stake`/`InvestmentFund`/`InvestmentPosition`/`RecurringInvestment` corporate-actions models) | MERGE INTO `rwa-platform/{tokenization,custody,corporate-actions,redemption}` — **do this LAST, not first** | **IMPLEMENTED** — real Postgres schema, 58 SQLAlchemy models, 12 Alembic migrations, 8 live API endpoint modules depend on adjacent tables | Monolith FastAPI, shared DB with the entire retail product | Retail mobile/web product, `Cubeshackles-retail` frontend | **HIGH** — this is the one part of the whole plan with real data. Do not attempt extraction until: (a) `fix_decimal_precision_20260307`'s broken `down_revision` is fixed (`RWA_SYSTEM_MAP.md` §4, §10.1), (b) `16c208fbde59`'s 27-table drop is neutralized (§5.1, §10.2), (c) `app/db/base.py` imports all 58 models so `Base.metadata` is trustworthy for any future extraction migration. Extracting live tables out of a monolith with a currently-broken migration graph is how you turn one outage into two. |

**valuation / lifecycle module** — no repo in the current 58 owns this explicitly; `InvestmentFund`/`InvestmentPosition` in the monolith carry some of this responsibility informally. **REQUIRES AUDIT**: decide whether `rwa-platform/valuation` is a new module built fresh, or extracted from monolith investment models — not yet scoped.

### 1.2 → `cubeshackles-regulatory` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-compliance-engine` | MERGE INTO `regulatory/kyc`, `regulatory/aml`, `regulatory/screening`, `regulatory/policy-engine` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified); "mixed" visibility per map | Standalone FastAPI, no DB | Gates Institutional Gateway forwarding and Clearing House intake (documented) | **LOW** — no data, ~40 Python files |
| `cubeshackles-regulatory-reporting` | MERGE INTO `regulatory/regulatory-reporting` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified); 51 Python files but zero persistence | Standalone FastAPI, no DB | Consumes evidence packs from `cubeshackles-integration` (documented) | **LOW** — no data, but see §2 below: this is the audit's flagged weakest link — zero implementation exists **anywhere in the org**, monolith included. Merging two empty rooms doesn't fill either. |
| `cubeshackles-supervision` | MERGE INTO `regulatory/supervision` | Not persistence-checked in this pass — module name `src/supervision` only confirmed | Standalone, read-only per map ("does not approve, enforce, clear, settle, or custody") | Generates supervisory views for BNA/CMC/ARSEG/AGT/BODIVA/MINFIN (documented) | **LOW-MEDIUM** — read-only evidence generator per its own doctrine; verify it has no independent state before merge |
| regulatory portions of `cubeshackles-institutional-gateway` | PARTIAL MERGE — only the compliance-adjacent normalization logic, not the whole gateway | Gateway itself is DOCUMENTATION-ONLY (no sqlalchemy/alembic, verified in `RWA_SYSTEM_MAP.md` §3); "mixed" visibility, real-protocol adapters (REST/FIX/ISO 20022/SWIFT/gRPC) per map | Standalone, normalizes into `InstitutionalInstruction` contract | Compliance Engine, Clearing House (documented) | **MEDIUM** — this repo is genuinely two things (ingress protocol adapters + regulatory normalization); splitting it requires deciding which half goes to `regulatory` and which stays as ingress infrastructure. **REQUIRES AUDIT** before the split, not a clean lift. |
| `cubeshackles-security-framework` | **REQUIRES AUDIT before deciding regulatory vs. security-platform** | **PARTIAL** — has a real `sqlalchemy` dependency (verified, `pyproject.toml`), no `alembic.ini` found — unclear if that dependency is used for anything live or vestigial | Standalone; per map: "Produces deterministic governance evidence — not a live scanning tool" | Feeds NIST CSF 2.0/ISO 27001 evidence artifacts (documented) | **MEDIUM** — has real code (not a stub) unlike most of its neighbors; the founder's own §5 (`cubeshackles-security-platform`) proposal and this §2 (`regulatory`) proposal both have a plausible claim on it. Its `sqlalchemy` dependency needs a direct look before folding it anywhere. |

**Note on the audit's own conclusion:** `RWA_SYSTEM_MAP.md` §7/§8 found Regulatory Reporting has **zero implementation anywhere** — not "fragmented across repos" but genuinely absent as working code, in both the pilot-rail repo and the monolith. Consolidating `cubeshackles-regulatory` solves the *organizational* fragmentation (one authoritative home instead of four half-repos) but does **not** by itself solve the *implementation* gap — that's still greenfield work, now with one clear place to put it instead of four candidate places.

### 1.3 → `cubeshackles-market-core` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-settlement-engine` | MERGE INTO `market-core/settlement` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified); map calls it "the sole v0.1 internal ledger finality authority" | Standalone, consumes `transaction.validated.v0.1`, emits `transaction.settled.v0.1` (documented, not observed running against real data) | Downstream of validator path (documented) | **LOW** — no data, ~48 Python files |
| `cubeshackles-clearing-house` | MERGE INTO `market-core/clearing` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified) | Standalone, produces `ClearingDecision` outputs (documented) | Settlement Engine gate ("Settlement may only proceed after `clearing.settlement.eligible.v0.1`" per map) | **LOW** — no data, ~53 Python files |
| `cubeshackles-market-infrastructure` | MERGE INTO `market-core/positions`, `market-core/reconciliation` (CCP-simulation logic) | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic dir (verified); map: "Risk infrastructure simulation only — not a licensed CCP" | Standalone | Emits deterministic risk control outputs (documented) | **LOW** — no data, ~35 Python files |
| settlement logic embedded in `Cubeshackles-Retail-DeFi-API` (`SettlementBatch` model, `settlement_batch` table) | MERGE INTO `market-core/settlement` — **same caution as §1.1's monolith row** | **IMPLEMENTED** — real table, single-table netting (`net_positions` JSON blob), `central_signature`, status enum; audit flagged this as PARTIAL even within the monolith (no real clearing/netting engine, just a JSON blob) | Monolith FastAPI, shared DB | Retail product | **MEDIUM-HIGH** — smaller surface than the RWA extraction (one table, not dozens), but still real data behind a live product; sequence after the monolith's migration-graph is fixed, same reasoning as §1.1 |

### 1.4 `cubeshackles-ledger` — KEEP, do not merge

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-ledger` | **KEEP** — sovereign boundary, per founder direction and independently confirmed by the audit | **IMPLEMENTED (isolated)** — real Postgres schema, 1 Alembic migration (`001_initial_ledger_schema.py`), real `sqlalchemy`/`alembic.ini` (verified). Map: "double-entry, hashchain integrity... Posted journals are immutable." Dev port 8086. | Standalone, own DB | Should be consumed by everything downstream of settlement (documented); **not confirmed wired to the monolith's own `LedgerEvent`/`LedgerSync` tables** — flagged as an open P1 in `RWA_SYSTEM_MAP.md` §7.4 | **N/A for merge (staying separate)**, but there is an unresolved risk independent of this plan: **two ledgers may currently exist** — this standalone repo's schema, and the monolith's `ledger_event`/`ledger_sync` tables — with no observed reconciliation. This needs tracing before anyone treats either one as *the* canonical ledger. |

### 1.5 → `cubeshackles-security-platform` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-security` | MERGE INTO `security-platform/security-policy` | Not deep-checked; map: "scaffolded," threat model/static analysis/dependency review/secret scanning gates | Standalone, gate-only | CI/gate suite | **LOW** — scaffolded per map, gate tooling not stateful |
| `cubeshackles-security-framework` | MERGE INTO `security-platform/security-policy`, `audit` — **contingent on the §1.2 audit above** | See §1.2 — has real `sqlalchemy` dep, no confirmed alembic | Standalone | Control plane orchestrates it (documented: control-plane's integration list) | **MEDIUM** — same open question as §1.2; whichever domain (regulatory vs. security-platform) it lands in, verify what its `sqlalchemy` dependency is actually doing first |
| `cubeshackles-vault` | MERGE INTO `security-platform/signing`, `kms`, `key-rotation`, `secrets`, `recovery` | **DOCUMENTATION-ONLY** — no sqlalchemy dep, no alembic (verified in `RWA_SYSTEM_MAP.md` §3.1). Confirmed: `src/{signing,recovery,secrets,contracts,keys,rotation,audit}` — a real key-management/signing domain model even without a live DB; aligns with GCP Cloud KMS production-signing work in progress | Standalone, "never stores secrets in the repository" per map | RC2_FREEZE milestone calls it one of the sole execution-truth boundaries (map §16) | **LOW-MEDIUM** — no data to migrate, but this repo carries real institutional weight (RC2_FREEZE named it explicitly as consensus-adjacent truth); the founder's own note to "keep a conceptual distinction internally" between security-platform's sub-modules matters more here than for most merges — do not flatten `signing`/`kms` into generic `security-policy` |
| `cubeshackles-disaster-recovery` (crypto-recovery portions only) | PARTIAL MERGE INTO `security-platform/recovery` — rest stays put or merges elsewhere | Scaffolded per map; `src/{recovery,dr_lib,replay,failover,backups,drills}` | Standalone | Regional outage/replay rebuild doctrine (documented) | **LOW** — scaffolded, but this repo is two things (crypto-key recovery vs. regional-outage/backup drills) — same "partial merge" caution as the institutional-gateway split in §1.2. The backup/failover/drills portion more plausibly belongs with `cubeshackles-operations` (§1.6 ops-adjacent) than security. **REQUIRES AUDIT** to draw the line cleanly. |

### 1.6 → `cubeshackles-network` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `Cubeshackles-validator-node` | MERGE INTO `network/validator` | Has a `src/persistence` module (module-name only, not deep-verified); map: "active," "validation authority only — does not settle" | Standalone | DAG ordering, validator attribution (documented) | **MEDIUM** — has a persistence module unlike most pilot-rail repos; verify what it actually persists before assuming this is a clean, dataless merge like the RWA-chain repos |
| `Cubeshackles-network-orchestrator` | MERGE INTO `network/orchestration` | No sqlalchemy dep found (verified) | Standalone; map: "active" | Validator membership, peer gossip (documented) | **LOW** |
| `cubeshackles-provincial-topology` | MERGE INTO `network/provincial-routing`, `topology` | No sqlalchemy dep found (verified); map: "scaffolded," "planning authority only" | Standalone | Angola-first node placement doctrine | **LOW** |
| `cubeshackles-offline-infrastructure` | MERGE INTO `network/offline` | No sqlalchemy dep found (verified); **map itself flags a P0**: "the queue-admission path raises before accepting or persisting work — offline transaction processing is not operational... not merely 'scaffolded' in the usual sense" (§6, dated 2026-07-19) | Standalone | Phone-wedge / offline transaction entry points | **LOW for the merge itself** (no data), but inherits a pre-existing P0 functional blocker the founder's own map already documents — merging doesn't fix it, just relocates it. Worth linking `docs/CLAIMS_REGISTER.md`'s existing entry rather than re-discovering it. |
| relevant portions of `Cubeshackles-node-api` | PARTIAL MERGE — only if the org decides the gateway itself becomes part of `network`; more likely stays adjacent | **PARTIAL/gateway-only** — 111 commits (2nd-most active pilot-rail repo, per `RWA_SYSTEM_MAP.md` §3.1), no sqlalchemy/alembic, `models/` has only query-helper files, not domain models. Map: "Public contract gateway — online ingress authority," dev port 8090 | Standalone | External transaction submission/query (documented) | **MEDIUM** — this is the most actively developed repo in the network cluster; folding a 111-commit, actively-maintained gateway into a consolidated repo is a bigger organizational move than folding a 1-commit scaffold. **REQUIRES AUDIT**: confirm whether `node-api` is deployed/used anywhere before deciding its fate — same open question as `cubeshackles-ledger` vs. the monolith's ledger tables. |

### 1.7 → `cubeshackles-platform` (proposed consolidation target — "audit first," per founder's own framing)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `Cubeshackles-core` | **REQUIRES AUDIT — do not casually absorb** (founder's own caveat, independently supported) | 74 commits, 169 Python files — by far the most developed pilot-rail-adjacent repo (`RWA_SYSTEM_MAP.md` §3 cross-cutting note). Map: "Canonical authority for economics, ledger replay, and fee governance." Persistence not deep-checked in this pass — given its size and centrality, this is the single highest-value audit target in the whole consolidation program before any merge decision | Standalone; REQUIRED in the local sibling layout for all gate runs | Named as canonical authority for 3+ domains in map §15 (economics, ledger replay, fee governance) | **HIGH-UNKNOWN** — not because destructive risk is confirmed, but because it is unaudited at the scale that matters. Treat as source repo, not absorption target, until it gets the same file-level pass the RWA chain got. |
| `cubeshackles-runtime` | MERGE INTO `platform/runtime` — **contingent on `Cubeshackles-core` audit above**, since runtime's map role ("orchestration authority — does not create finality") sits right next to core's | No sqlalchemy dep found (verified); map: "scaffolded" | Standalone | Execution engine, DAG scheduling, settlement handoff orchestration (documented) | **LOW** for the repo itself (scaffolded, no data), but its correct final home depends on how the `Cubeshackles-core` audit resolves — don't merge runtime before core is understood, or you may need to re-split immediately |
| `Cubeshackles-control-plane` | MERGE INTO `platform/control-plane` — **REQUIRES AUDIT on scope, not on safety** | 153 Python files (verified count), no sqlalchemy dep found; map: "scaffolded," "mixed" visibility. Its own doctrine (`SYSTEM_ARCHITECTURE.md` §5a) explicitly notes its integration reach is broader than any single-layer repo — it touches ai-runtime, ai-sdk, ontology, agent, security-framework, observability, compliance-engine, regulatory-reporting, and institutional-gateway | Standalone | "Sole point through which a user, service, or AI agent request is authenticated, authorized, routed... and recorded" (map) | **MEDIUM** — not a data-migration risk (no persistence found) but a *governance* risk: this repo's entire design purpose is to mediate every other domain without gaining authority over any of them (map's own explicit anti-backdoor rule). Merging it into `platform` is architecturally defensible only if the merge preserves that mediation-not-authority boundary — a structural risk, not a data risk. |
| `cubeshackles-integration` | MERGE INTO `platform/integration` — lowest-risk item in this whole section | 480 Python files (verified count, largest of the group checked here), no sqlalchemy dep found; map: "Cross-repo integration and production gate suite... Does not run production traffic." | Standalone; REQUIRED for gate runs | Every repo in the gate chain (by design) | **LOW-MEDIUM** — no data, but it's a large, actively-maintained test/gate harness (480 files) wired to every other repo's CI; a merge needs a mechanical path migration pass for every repo's CI config pointing at it, more of a plumbing risk than a data risk |

### 1.8 → `cubeshackles-ai` (proposed consolidation target)

| Repo | Classification | Persistence evidence | Deployment boundary today | Key consumers | Migration risk |
|---|---|---|---|---|---|
| `cubeshackles-ai-runtime` | MERGE INTO `ai/runtime` | No sqlalchemy dep found (verified); map: "active," "private," 55 tests passing, `POST /v0.1/infer`, stabilized at `AI_NATIVE_M5` | Standalone, composed by `cubeshackles-os` | 11 platform AI agents (documented) | **LOW-MEDIUM** — no persistence found, but this is a stabilized, tested, milestone-frozen (`AI_NATIVE_M5` "Complete") service — treat the freeze status as a real constraint, not just a scaffold to fold in casually |
| `cubeshackles-ai-sdk` | MERGE INTO `ai/sdk` | No sqlalchemy dep found (verified); map: "active," "public," 23 tests passing | Standalone consumer library | "Applications must not implement their own HTTP inference clients" (map) — i.e. this is a dependency of other repos, not just a peer | **LOW-MEDIUM** — it's a published library other repos import; merging it changes every consumer's import path, a mechanical but org-wide edit |
| `cubeshackles-agent` | MERGE INTO `ai/agents` | Not persistence-checked; map: "pre-freeze," "public" — "declares the capability contract for a future local AI engineering agent. The agent itself is not built here" | Standalone, contract-only | Foundation layer companion to CIEL/ontology/TFE | **LOW** — explicitly a contract-only repo per its own doctrine, nothing to migrate |
| `Cubeshackles-Enterprise-Brain` | MERGE INTO `ai/enterprise-brain` — **or just don't**, see risk note | **MISSING** — confirmed via GitHub API: private, `size: 0`, no committed content (map §14a, dated 2026-07-18) | N/A | N/A | **NONE** — there is nothing here to merge. This is a placeholder repo. Folding an empty repo into `cubeshackles-ai` is a rename, not a consolidation; consider just deleting/renaming rather than "merging." |
| `cubeshackles-adviser` | MERGE INTO `ai/adviser` — **flagged as the one item in this whole plan closest to a live product** | **IMPLEMENTED** — real `sqlalchemy` dependency AND a real `alembic.ini` at `apps/adviser-api/alembic.ini` (both verified, this is the only repo outside the ledger/monolith/security-framework cluster with a confirmed live migration setup). Map: "active," "mixed," dev port 8080, 5 named agents (PortfolioAI, RebalanceAI, TaxAI, AlertAI, SimulationAI) | Standalone, own DB, own port | Consumes `cubeshackles-ai-sdk`; runs outside consensus-critical path (documented) | **MEDIUM-HIGH** — this is a real, running, data-backed service, not a scaffold. It deserves the same migration-graph check (`alembic heads`) that surfaced the monolith's broken chain before anyone plans an extraction/merge. Do not assume it's dataless like its `cubeshackles-ai` siblings just because they're grouped together in the founder's proposal — verify independently. |

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
| `Cubeshackles-retail` | Retail-facing Next.js frontend, consumes `Cubeshackles-Retail-DeFi-API` |
| `Cubeshackles-phone-wedge` | Device-initiation product surface |
| `Cubeshackles-web` | Institutional/public explorer surface |

## 4. Kept separately for release/audience/security boundary reasons

| Repo | Note |
|---|---|
| `.github` | Org governance repo — confirmed present via GitHub org API; not counted in `REPOSITORY_MAP.md`'s 55 by the map's own convention, but is part of the org's real 58 |
| `cubeshackles-demo` | Regulator/bank-grade demo environment, no real money movement — a distinct evidence-artifact product, not infrastructure |
| `cubeshackles-sandbox-lab` | Deterministic sandbox rail for BNA/BODIVA/CMC discussions — same reasoning as `cubeshackles-demo` |
| `cubeshackles-angola-pilot` | Controlled pilot-corridor scope document/boundary, not a service |
| `cubeshackles-chaos` | Test-only controlled-failure harness |
| `cubeshackles-observability` | Scaffolded target for future audit-grade telemetry; map: "No production telemetry stack is shipped" — genuinely nothing to consolidate yet, revisit once it has real content |
| `cubeshackles-operations` | Deployment/rollback/incident/SLO doctrine, 43 tests passing per map — active and cross-cutting by nature, doesn't belong inside any single domain |
| `cubeshackles-infra` | Deployment/environment tooling; also confirmed to contain Docker build-context copies of `CubeWallet`'s backend (found during this pass) — worth a light cleanup pass independent of consolidation, since stale copies of another repo's `requirements.txt` inside infra tooling are exactly the kind of drift this whole plan is trying to reduce |
| `cubeshackles-compute` | Scaffolded, private, future sovereign compute — no current consumers to disrupt |
| `cubeshackles-hardware` | Scaffolded, private, silicon roadmap — same reasoning |

---

## 5. Consolidation wave sequencing

Matches the founder's proposed sequencing, annotated with the migration-risk evidence gathered in this pass:

### Wave 1 (P0) — `rwa-platform`, `regulatory`, `market-core`
- **Mechanically safe today**: 8 of the 10 source repos across these three targets are DOCUMENTATION-ONLY (verified, no persistence) — folding them is a code-move + import-path exercise, not a data migration.
- **Sequencing constraint discovered in this pass**: within each of the three targets, do the DOCUMENTATION-ONLY repos first (asset-registry, tokenization-engine, custody, compliance-engine, regulatory-reporting, settlement-engine, clearing-house, market-infrastructure — 8 repos, low risk, can start immediately), and treat pulling the corresponding *live* logic out of `Cubeshackles-Retail-DeFi-API` (asset tokens/custody/settlement-batch) as a **separate, later sub-phase gated on** `RWA_SYSTEM_MAP.md` §10 items 1–2 (fix the broken migration graph, neutralize the 27-table-drop migration) being resolved first. Don't let Wave 1's "P0, do it now" urgency pull the monolith extraction forward before its prerequisite is met — that's the one place in this entire plan an outage is actually possible.
- **New open item found in this pass, not in the founder's original scoping**: `cubeshackles-institutional-gateway` and `cubeshackles-security-framework` both need a scope split before they can cleanly land in `regulatory` (§1.2) — flag for a short audit pass before Wave 1 closes.

### Wave 2 (P1) — `network`, `security-platform`, `platform` (audit-gated), `ai`
- **`platform`**: do not start until `Cubeshackles-core` gets its own audit pass (74 commits, 169 files, named canonical authority for economics/ledger-replay/fee-governance in map §15) — this is the founder's own caveat and this pass found no reason to relax it.
- **`network`**: `Cubeshackles-validator-node`'s `src/persistence` module and `Cubeshackles-node-api`'s 111-commit activity level both deserve a closer look before assuming this cluster is as dataless as the RWA/regulatory/market-core scaffolds — flagged as MEDIUM risk items, not LOW.
- **`security-platform`**: `cubeshackles-vault`'s RC2_FREEZE-named role means its sub-module boundaries (signing/kms/key-rotation/secrets/recovery) should be preserved structurally even inside a consolidated repo, per the founder's own note — this pass independently agrees.
- **`ai`**: `cubeshackles-adviser` is the one repo in this wave with a confirmed live `alembic.ini` + real data — treat it with the same caution as the Wave-1 monolith extraction, not as dataless as its `cubeshackles-ai-runtime`/`ai-sdk`/`agent` siblings. `Cubeshackles-Enterprise-Brain` has zero content — a rename/delete, not a merge.

---

## 6. Summary count

- **58 repositories total** (org API ground truth).
- **7 shared-platform / foundational singletons** — kept (§2, includes this repo).
- **7 products** — kept (§3).
- **10 kept for release/audience/security boundary reasons** — kept (§4).
- **1 (`cubeshackles-ledger`)** — kept as a deliberate sovereign boundary (§1.4).
- **1 (`Cubeshackles-Retail-DeFi-API`)** — not itself consolidated (it's the product backend `Cubeshackles-retail` depends on); its *RWA-relevant internals* are a merge source into `rwa-platform`/`market-core`, high risk, sequenced last.
- **31 repos** — MERGE INTO one of the 8 proposed domains (`rwa-platform` ×3, `regulatory` ×3–4, `market-core` ×3, `security-platform` ×3–4, `network` ×4–5, `platform` ×3, `ai` ×4).
- **Net result if fully executed**: 58 → roughly **16–18** independently recognizable repos (8 consolidated domains + `cubeshackles-ledger` + `Cubeshackles-Retail-DeFi-API` + 7 shared-platform + 7 products − overlaps in the §4 boundary-kept set that could plausibly fold into `platform`/`security-platform` later). This lands above the founder's "~8–12" target because the shared-platform and boundary-kept tiers (§2, §4) are doing real, distinct governance work the map itself insists must stay layer-isolated — the "8–12" figure fits the *domain* repos alone, not the full org.

---

## 7. What this plan does not resolve (flag for the founder, not decided here)

1. Whether `Cubeshackles-core` absorption into `platform` happens at all, pending its own audit.
2. Where `cubeshackles-institutional-gateway` and `cubeshackles-security-framework` land — both are two-things-in-one-repo and need a scope split before either merges cleanly.
3. Whether `cubeshackles-ledger` and the monolith's `LedgerEvent`/`LedgerSync` tables are two live ledgers or one dead one — unresolved from the prior audit, load-bearing for how confidently "keep ledger separate" can be stated as settled.
4. Whether `Cubeshackles-node-api` (111 commits, actively maintained) is deployed anywhere, which determines whether folding it into `network` is a real migration or a scaffold cleanup.
