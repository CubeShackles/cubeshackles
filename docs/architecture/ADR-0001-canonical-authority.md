# ADR-0001: Canonical Authority for Core CubeShackles Primitives

**Status:** PROPOSED — awaiting founder decision. Not yet adopted. No code has been changed as a result of this ADR.
**Date:** 2026-10-01
**Supersedes:** Nothing. Extends `CANONICAL_AUTHORITY_MATRIX.md` (PR #11) with corrections from an adversarial 8-cluster re-verification pass against current canonical branches (not PR #11's prose).
**Scope:** Ownership proposal only. No migration performed. No repository created, moved, or deleted.

## How to read this document

For every primitive: CURRENT IMPLEMENTATIONS, CURRENT RUNTIME AUTHORITY, TARGET AUTHORITY (proposed, not decided), MIGRATION PATH, DEPENDENTS, COMPATIBILITY RISK, MIGRATION ORDER. Where the evidence is genuinely split or the "canonical" source itself isn't stable, the entry says so plainly rather than forcing a verdict.

Per the founder's explicit instruction: **no new primitive is proposed merely to resolve duplication.** Every TARGET AUTHORITY below reuses the strongest existing implementation.

---

## 1. Money

**CURRENT IMPLEMENTATIONS** (re-verified against current `main`, not PR #11's prose):
- `cubeshackles-cubereg` — `app/calc/money.py`, MERGED on main. Real, tested, genuinely used (`routers/calculate.py`, `calc/engine.py`, `calc/reproducibility.py`, `corpus/service.py`).
- `cubeshackles-institutional-gateway` — Money class exists ONLY on an open, **CONFLICTING** (merge-conflicted), unmerged PR (#4). **On main there is no Money class at all** — just a plain `amount: Decimal` field.
- `cubeshackles-ledger` — Money class exists ONLY on an open, unmerged PR (#7). On main: `Decimal` (Pydantic) persisted via a separate `ExactMoney` SQLAlchemy TypeDecorator, with the wire/response layer explicitly using `float`.
- `cubeshackles-settlement-engine` — Money class exists ONLY on an open, unmerged PR (#7). On main: plain `float`, not even `Decimal`.
- Adapter-tier: Retail-DeFi-API's `MoneyAmount` (Decimal-backed, real), vegemai-demo's `type Money = number` (confirmed real doctrine violation — binary float used in live fee arithmetic, external-client repo), BualaBuitu's generated (not hand-authored) `MoneyAmount` OpenAPI mirror (both fields nullable). CubeWallet's previously-claimed `MoneyAoa` **could not be found anywhere in current main or full git history** — struck from this ADR as unconfirmed.
- The three unmerged PR copies (institutional-gateway, ledger, settlement-engine) are confirmed byte-identical to each other — but git timestamps show **ledger's copy was committed first**, 78 seconds before institutional-gateway's, with all three by the same author in one apparent batch operation. "institutional-gateway is the origin" is **not supported by chronology**.

**CURRENT RUNTIME AUTHORITY**: None. No live, merged Money implementation is shared across any two repos today. The real duplication risk on main right now is **three incompatible raw numeric representations for money** across three financially load-bearing repos (Decimal / Decimal+float / bare float), not duplicate Money classes.

**TARGET AUTHORITY**: Cannot be named yet — the presumed source (institutional-gateway's PR #4) is conflicted and unmerged. **This ADR does not designate a canonical Money owner today.** Recommendation: resolve institutional-gateway PR #4's conflicts and merge it (or supersede it) before any Money convergence work begins elsewhere. Once merged, institutional-gateway's Money is the strongest existing candidate (most complete, already has a working documented port in cubereg).

**MIGRATION PATH** (once a canonical Money is merged somewhere): ledger and settlement-engine adopt it as a real package dependency (not a copied file) first, since their PRs already contain a byte-identical copy — converting a copy to a dependency is lower-risk than introducing a new type into untouched code.

**DEPENDENTS**: cubereg (already ported, no immediate action needed), every money-moving endpoint across Retail-DeFi-API, CubeWallet, ledger, settlement-engine, institutional-gateway.

**COMPATIBILITY RISK**: HIGH for ledger (changing from float-on-the-wire to a structured Money type touches the API contract of a financially live-ish service) and settlement-engine (currently uses bare float — the biggest real precision risk in the org today, independent of this ADR).

**MIGRATION ORDER**: (1) land institutional-gateway PR #4 cleanly; (2) convert ledger's and settlement-engine's own already-drafted PR copies into real dependencies rather than duplicated files; (3) revisit adapter-tier variants (Retail-DeFi-API, BualaBuitu) only after the above is stable.

---

## 2. Currency

**CURRENT IMPLEMENTATIONS**: Two independent duplication clusters, confirmed:
- Currency metadata bundled inside each Money implementation (see above).
- `BlockedSettlementCurrencyError`-pattern currency-policy guards, independently authored in **4 repos** (kulifikila, CubeWallet, phone-wedge, and — newly found — `Cubeshackles-network-orchestrator` under the different name `ForeignFiatInChainError`, same underlying constant set), plus 1 vendored (not independently authored) Docker-build-context copy in cubeshackles-infra. These 4 have **diverged from each other** in sophistication (kulifikila's is the most elaborate, phone-wedge's error constructor is a bare `pass`).

**CURRENT RUNTIME AUTHORITY**: None shared. Each repo's currency gate runs independently against its own hardcoded constant set.

**TARGET AUTHORITY**: Reuse kulifikila's version as the base (it is the most complete: adds an African-currency allow-list, AOA-only-mode, extra error handling) rather than inventing a new one.

**MIGRATION PATH**: Extract kulifikila's `currency_policy.py` into a real shared dependency; the other 3 repos replace their local copies with an import, preserving their existing call sites' signatures via a thin compatibility shim if names differ (e.g., network-orchestrator's `ForeignFiatInChainError` could alias the canonical error type).

**DEPENDENTS**: kulifikila, CubeWallet, phone-wedge, network-orchestrator, cubeshackles-infra (regenerate its vendored copy from the new source instead of hand-copying CubeWallet's file).

**COMPATIBILITY RISK**: LOW — these are guard functions, not data models; call-site signatures are small and easy to shim.

**MIGRATION ORDER**: Can proceed independently of the Money ADR resolution; lowest-risk item in this entire document, good Wave-1 or Wave-2 pilot candidate.

---

## 3. Identity / Person / Account

**CURRENT IMPLEMENTATIONS**: No first-class, exact-named `Person`/`Identity` class was found anywhere org-wide in this or the prior census pass. `Account` has independent shapes per financial repo (not separately re-verified this round — carried over from PR #11 as UNRESOLVED, not re-audited).

**CURRENT RUNTIME AUTHORITY**: UNRESOLVED — genuinely not established by either census pass.

**TARGET AUTHORITY**: UNRESOLVED. Do not force a designation.

**MIGRATION PATH / DEPENDENTS / COMPATIBILITY RISK / MIGRATION ORDER**: N/A until a dedicated inspection pass is run — flagged for future work, not guessed at here.

---

## 4. Organization / Institution / LegalEntity / OperatingEntity

**CURRENT IMPLEMENTATIONS** (re-verified, worse than PR #11 stated): **4 distinct shapes across 3 repos**, not 3:
- Retail-DeFi-API: real SQLAlchemy `Institution(Base)`.
- `cubeshackles-institutional-gateway`: `GatewayInstitutionProfile` — explicitly NOT a system of record, a frozen dataclass docstring-labeled "derived from Terrain-backed institutional records," pointing at an `institution_id` rather than owning one.
- CubeWallet backend: separate SQLAlchemy `Institution(Base)`, near-zero field overlap with Retail-DeFi-API's.
- **CubeWallet mobile** (new finding): a THIRD, independent TypeScript `Institution` type with almost no field-name overlap with CubeWallet's OWN backend model — CubeWallet alone has 2 non-interoperable Institution shapes internally.
- `cubeshackles-terrain`: no model at all — `institution_id: str`, opaque.
- `cubeshackles-ontology`'s `ObjectType.INSTITUTION` exists, schema-backed, tested — but is consumed by **zero** of the above 4 real implementations.

No "LegalEntity"/"OperatingEntity" class was found under those exact names anywhere — UNRESOLVED, not confirmed absent via exhaustive search this round (carried over from prior ontology census, not re-audited this round).

**CURRENT RUNTIME AUTHORITY**: Split 4 ways in production, with no code anywhere converting between the 4 representations or validating a shared `institution_id` namespace across them (explicitly flagged UNRESOLVED by the verifying subagent — "same ID space" is highly likely but not code-proven).

**TARGET AUTHORITY**: `cubeshackles-ontology`'s `ObjectType.INSTITUTION` schema, consumed via the SAME adapter pattern Cubeshackles-control-plane already uses and has proven out (`OntologyKernelAdapter` + contract-parity tests) — not a new mechanism.

**MIGRATION PATH**: Per the verifying subagent's evidence-based recommendation — start with `cubeshackles-institutional-gateway`, NOT Retail-DeFi-API or CubeWallet. Gateway's `GatewayInstitutionProfile` is already a read-side derived view (not a system of record it owns), structurally matching control-plane's existing `OntologyReader` port pattern almost exactly. Estimated ~150-250 lines for a new adapter (`GatewayOntologyReader`) + ~100-150 lines for a contract-parity test suite mirroring control-plane's. Retail-DeFi-API's and CubeWallet's live OLTP Institution tables are NOT touched in this first step — that migration is a separate, much higher-risk, multi-week project.

**DEPENDENTS**: institutional-gateway's `gateway_route_policy.py` and `gateway_terrain_guard.py` (downstream consumers of the profile — unaffected if the adapter preserves the existing `GatewayInstitutionProfile` output shape).

**COMPATIBILITY RISK**: LOW for the gateway-only first step (read-side, additive, doesn't touch existing OLTP tables). HIGH for ever touching Retail-DeFi-API's or CubeWallet's live Institution tables — explicitly out of scope for Wave 1.

**MIGRATION ORDER**: institutional-gateway first (becomes ontology's 2nd real consumer); Retail-DeFi-API/CubeWallet consolidation deferred to a much later wave, if ever, given OLTP migration risk.

---

## 5. TransactionIdentity

**CURRENT IMPLEMENTATIONS** (re-verified, confirmed WORSE than PR #11 stated — this is the most severe correction in this ADR):
- **Scheme A** — `Cubeshackles-core`'s `Transaction.id` (uuid4) + `compute_hash()`, which depends on that uuid4 AND a wall-clock `created_at`, so two functionally-identical transfers produce different hashes. `TransactionStatus.SETTLED` is defined but **never assigned anywhere in Core, including its own tests** — confirmed by exhaustive grep.
- **Scheme B** — `Cubeshackles-node-api`'s `build_wedge_idempotency_key()` — a genuinely deterministic sha256(phone|phone|amount|currency|session) scheme.
- **Scheme C** — `cubeshackles-settlement-engine`'s RC2A router: `txn_id = body.transaction_id or f"demo-{uuid.uuid4().hex}"`, which the code LABELS `deterministic_transaction_id` in its output but is actually a random uuid4 unless the caller explicitly resupplies the same value.
- **Confirmed by tracing the actual live HTTP call**: node-api's POST to settlement-engine's `/v0.1/settle` sends **no `transaction_id` field at all** — so Scheme B's value is computed and stored ONLY inside node-api's own local audit/explorer layer and never reaches settlement-engine. Settlement-engine therefore ALWAYS falls through to random uuid4 (Scheme C) on this route. **Schemes B and C share a field name but are never the same value for the same real transfer.**
- **New finding**: node-api itself runs **two fully disjoint, mutually-inconsistent LIVE settlement code paths** — one settling in-process against Core's ledger on a node-api-local SQLite DB (using Core's bare uuid4 as the real ledger-entry ID, with Scheme B's value as inert audit metadata only), and one calling the separate settlement-engine microservice over HTTP into an entirely different SQLite DB. Neither shares a ledger, an ID scheme, or an idempotency mechanism with the other, and both are reachable via live FastAPI routes.
- Settlement-engine's own documented architecture claims "deterministic_transaction_id as idempotency_key — replay returns same journal_id, no double-post." **This claim is not borne out by the actual node-api caller code**, which never resends a transaction_id at all.

**CURRENT RUNTIME AUTHORITY**: For the one live end-to-end path actually exercised (node-api→settlement-engine), the ID actually used in production is Scheme C (random uuid4). For node-api's separate in-process wedge path, the ID actually written to the ledger is Scheme A (Core's bare uuid4). **Neither live path uses `TransactionStatus.SETTLED` from Core at all.**

**TARGET AUTHORITY**: UNRESOLVED by design — this ADR does not propose a winner among A/B/C. Reconciling Core's and node-api's ID schemes is a stated prerequisite of Wave 2 (per `CONVERGENCE_ANALYSIS.md`), not something to decide here. What this ADR does assert: **Scheme B is the only one of the three that is genuinely deterministic from transaction content**, and should be the starting point for discussion, not Scheme A (non-deterministic hash) or Scheme C (not actually deterministic despite its name).

**MIGRATION PATH**: Not proposed in this ADR — flagged as the highest-complexity item in Wave 2, requiring a founder decision on which of node-api's two disjoint settlement paths is meant to be the real one going forward (or whether both are meant to coexist for different transfer types).

**DEPENDENTS**: Core, node-api (both internal paths), settlement-engine, ledger (indirectly, via whichever path actually posts to it).

**COMPATIBILITY RISK**: VERY HIGH — this is the org's real transaction-identity surface; any change risks breaking whichever of node-api's two live paths is currently relied upon in practice.

**MIGRATION ORDER**: Deliberately NOT Wave 0 or Wave 1. This requires a dedicated design decision before any code change — recommend treating it as its own mini-ADR once Wave 1 is complete.

---

## 6. EventEnvelope / AuditEvent / CorrelationId

**CURRENT IMPLEMENTATIONS**: Confirmed WORSE than PR #11 stated. Real count of independent Event/AuditEvent-shaped type definitions (Python classes + TypeScript types/interfaces, excluding pure exception classes) is **well over 20, closer to 50+** once TypeScript is counted — CubeWallet alone has 11 independent TS event shapes. Core itself has an **internal duplicate** — `cubeshackles/ciel/events.py` vs `src/cubeshackles/ciel/events.py` — byte-identical class names in two live top-level packages within the SAME repo (UNRESOLVED whether intentional migration scaffolding or drift).

For CIEL specifically (re-verified, LESS severe than PR #11's "4-5 incompatible schemas" framing): only **2 real LIVE, mutually-incompatible wire families** exist, not 4-5:
- **Family A** (entity_id/event_type/source/correlation_id/transaction_id/metadata): Core's declared shape = node-api's actual LIVE wire shape (node-api's own copy, not imported from Core, but currently schema-identical) = kulifikila's ad hoc dict.
- **Family B** (actor_id/source_service/payload/schema_version/trace_id): ledger ↔ cubereg, **deliberately matched to each other by design** per cubereg's own docstring — a coherent, intentional second schema, not an accidental near-miss.
- The other 2 "variants" the original census counted are confirmed **dead code** (Core's orphaned root-level non-`src` package, node-api's unimported `app/ciel/models.py`) — deletable with zero consumer impact.
- `cubeshackles-ciel` (the repo named for this) has **zero runtime relevance** — a standalone YAML linter + CI gate, no server/client/persistence code anywhere, and its own `foundation_ciel_reconciliation.yaml` reveals this gap is an **explicit, documented, pre-freeze architectural seam the org already knows about** (a two-tier "foundation vocabulary" vs "runtime vocabulary" design), not a hidden defect.
- `causation_id` confirmed absent from every implementation, org-wide, zero exceptions.
- node-api's import of Core's CIELEvent type is confirmed undeclared and CI-sibling-checkout-only — but this is now confirmed to be true of node-api's **entire domain layer**, not just CIELEvent (Core, economics, ledger-engine imports are ALL undeclared the same way).

**CURRENT RUNTIME AUTHORITY**: node-api's `app/ciel/{types,routes,store,event_store}.py` is the actual live hub — every other repo's CIEL client is configured to point at it. `cubeshackles-ciel` has none.

**TARGET AUTHORITY**: node-api's `app/ciel/{types,routes,store,event_store}.py` + Core's `contracts/ciel/` enum/schema package — NOT `cubeshackles-ciel`. This reuses the strongest existing implementation rather than inventing a new one, per the non-negotiable rule.

**MIGRATION PATH**: (1) declare `cubeshackles-core`/`cubeshackles_ciel_sdk` as a real installable package dependency everywhere currently using CI-sibling-checkout or hard-unwrapped imports — this is packaging work, not a redesign; (2) delete the 2 confirmed-dead duplicate CIELEvent copies; (3) add `causation_id` to the one live schema and propagate; (4) explicitly decide — as a founder decision, not a cleanup task — whether Family B (ledger/cubereg) remains a deliberate separate institutional-ledger namespace or should be merged into Family A; (5) either build real NATS consumers for the existing publish paths or stop describing the publish side as "the nervous system" until a consumer exists.

**DEPENDENTS**: BualaBuitu, kulifikila, CubeWallet, phone-wedge, network-orchestrator, validator-node (all current CIEL client consumers).

**COMPATIBILITY RISK**: MEDIUM for step (1) — packaging changes are mechanical but touch every consumer's build/CI config. LOW for steps (2)-(3). The Family A/B merge decision (step 4) carries HIGH risk if decided wrong, since ledger/cubereg's Family B is load-bearing for cubereg's own historical-reproducibility invariant.

**MIGRATION ORDER**: Steps (1)-(3) are good Wave 1 candidates (low-risk, mechanical). Step (4) is explicitly a founder decision point, not an implementation step — flag for a dedicated mini-ADR.

---

## 7. Jurisdiction

**CURRENT IMPLEMENTATIONS**: Not re-verified this round (carried over from PR #11 — `adviser`/`compliance-engine` each define a bare `Jurisdiction(str, Enum)`; Terrain and Ontology both treat it as an untyped string). UNRESOLVED whether the two enum member sets match.

**TARGET AUTHORITY**: UNRESOLVED — needs the dedicated follow-up pass PR #11 already flagged.

---

## 8. PolicyDecision / Rule / Permission

**CURRENT IMPLEMENTATIONS**: Confirmed absent as first-class, exact-named domain models anywhere org-wide (not re-verified this round, carried from PR #11 as an open finding). Control-plane's `Obligation`/`ObligationType` (policy-decision annotation) is now confirmed, on re-verification, to be a **name collision only** with ontology's `ObjectType.OBLIGATION` (a persisted regulatory-duty record) — the two concepts live in genuinely different domains and share no real semantic overlap beyond the English word. This downgrades PR #11's "near-miss duplication" framing.

**TARGET AUTHORITY**: UNRESOLVED. Per the founder's explicit instruction, this ADR does not assume policy-as-code is the intended design without confirmation.

---

## 9. Evidence / SettlementFinality

**CURRENT IMPLEMENTATIONS**: `cubeshackles-settlement-engine` is the real internal-ledger finality authority (genuine SHA-256 evidence hashes, confirmed). Two confirmed, real defects in that authority, both **already disclosed in the org's own `cubeshackles/docs/CLAIMS_REGISTER.md` since 2026-07-19** — these are not new discoveries:
1. The CIEL signature attached at settlement is a fabricated string template (`f"settlement-finality:{instruction.settlement_reference}"`), not a cryptographic signature — confirmed by direct code read; the ledger side only checks the signature field is non-empty.
2. `DeterministicSettlementPolicy.evaluate()` checks ONLY the `event_type` string (`"transaction.validated"`) and never reads the `validation_decision` field — confirmed by reading the full function body. An event with `event_type=="transaction.validated"` and `validation_decision=="REJECTED"` would still settle today.
3. The `validation_decision` that reaches this check is itself hardcoded `"APPROVED"` by settlement-engine's own RC2A router (`src/settlement_service/rc2a_router.py`, not `institutional_router.py` as previously misnamed) — there is no real upstream validator service; it is entirely synthetic, generated in-process.
4. `require_clearing_approval` (settlement-engine) and `build_settlement_eligible_event` (clearing-house) are confirmed to have zero callers outside their own unit tests.
5. `require_compliance_before_clearing` (compliance-engine) IS wired — but only to compliance-engine's own endpoint, which has **zero cross-service callers anywhere in the org**. Net effect is identical to (4): clearing and settlement proceed with zero compliance check.
6. **Topology correction**: institutional-gateway does not currently call settlement-engine at all — the real end-to-end live path is entirely inside settlement-engine itself. Clearing-house and compliance-engine are not "bypassed by a live call" — they are "never wired into the call graph."
7. No fix has landed for any of this since 2026-07-01 (confirmed via git log across all 5 repos).

**CURRENT RUNTIME AUTHORITY**: settlement-engine, with the above confirmed, disclosed gaps.

**TARGET AUTHORITY**: settlement-engine remains finality authority — this evidence does NOT support replacing it, only closing its wiring gaps. This is Phase 6, treated as P0.

**MIGRATION PATH**: see Wave 0/Wave 1 plan below — the smallest implementation PR (section 13 of the final report) targets exactly this.

**DEPENDENTS**: every live transaction currently settling through `POST /v0.1/settle`.

**COMPATIBILITY RISK**: the gating work itself is additive (checking something that currently isn't checked) — low risk of breaking existing passing tests if done as a feature-flagged addition; HIGH risk if done carelessly, since this is the org's one real money-moving path.

**MIGRATION ORDER**: P0, but explicitly NOT authorized for implementation in this ADR — awaiting founder go-ahead per the standing instruction to stop before implementation.

---

## Summary table

| Primitive | Target authority (proposed) | Confidence |
|---|---|---|
| Money | Cannot be named — presumed source (institutional-gateway) is unmerged and conflicted | Low — blocked on a merge decision outside this program's control |
| Currency policy | kulifikila's implementation | High — straightforward, low-risk |
| Identity/Person/Account | UNRESOLVED | N/A — not yet inspected |
| Institution | ontology's `ObjectType.INSTITUTION`, via institutional-gateway as 2nd adapter | Medium-High — proven adapter pattern exists, scope is modest |
| TransactionIdentity | UNRESOLVED by design | N/A — requires its own founder decision before any target can be named |
| EventEnvelope/CorrelationId | node-api's `app/ciel/*` + Core's `contracts/ciel/` | High for the mechanism; Family A/B merge decision still open |
| Jurisdiction | UNRESOLVED | N/A — not yet inspected this round |
| PolicyDecision/Rule/Permission | UNRESOLVED | N/A — likely absent org-wide, not merely duplicated |
| SettlementFinality | settlement-engine (confirmed, with disclosed gaps to close) | High — authority is sound, wiring is not |

This ADR intentionally leaves 4 of 9 primitives UNRESOLVED. That is the honest state of the evidence, not a gap in this document.
