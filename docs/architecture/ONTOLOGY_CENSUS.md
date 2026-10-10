# CubeShackles Organization — Ontology Census & Concept Collision Matrix

**Status:** Discovery output. Evidence-based. Repository names are not treated as evidence of semantic ownership.
**Date:** 2026-09-30

## What `cubeshackles-ontology` actually is

A real, tested, pre-freeze kernel (Gate 4-A): `ObjectType` enum (15 members: INSTITUTION, USER, AGENT, CUSTOMER, ACCOUNT, TRANSACTION, CASE, ALERT, REGULATION, OBLIGATION, EVIDENCE, REPORT, APPROVAL, MODEL, WORKFLOW), per-type schema property sets, immutable `OntologyObject` with versioned revisions, a closed `RelationshipType` enum (9 types, fail-closed on unknown), bounded cycle-safe graph traversal, and a real `reconstruct_case()` demo. A `DataClassification` enum exists but is explicitly not yet adopted by Cubeshackles-control-plane's own two separate classification enums (deferred, "Gate 4-C").

A separate, superseded, flat `contracts/ontology_registry.yaml` (13 untyped entities) exists in parallel — explicitly superseded by the kernel, overlapping the kernel's 15 `ObjectType`s on only 5 names.

**Real consumers: exactly ONE** — Cubeshackles-control-plane, via a SHA-pinned git dependency and a real adapter + test suite (`test_ontology_adapter_contract_parity.py`, `test_ontology_package_compatibility.py`). Every other hit anywhere in the org is documentation-only (no source import).

**Verdict**: canonical by actual usage for exactly one consumer. NOT canonical for the rest of the org today — every domain repo independently defines its own Institution/User/Account/Transaction/Event/Currency/Jurisdiction/Evidence shapes with zero import relationship to the kernel or to each other. Notably, even control-plane — its one real consumer — defines its OWN `Obligation` model rather than using the kernel's `ObjectType.OBLIGATION`, despite already consuming the kernel for other types (a near-miss worth flagging for a future convergence wave).

A second, unrelated ontology-flavored repo exists in the org's wider workspace: **CubeShackles-Enterprise-Brain**, a BIU-G Holdings internal knowledge-management repo with its own `schemas/` directory (entity.md, decision.md, claim.md, jurisdiction.md, legal-entity.md, product.md, regulatory-requirement.md). This is explicitly a different artifact serving a different purpose (enterprise/company knowledge management, not product domain ontology) and must not be conflated with `cubeshackles-ontology`.

## Collision matrix

| Concept | Collision status | Key evidence |
|---|---|---|
| **Money** | DUPLICATE ×4 confirmed, plus loose adapter-tier variants | `cubeshackles-institutional-gateway` (canonical origin) + `cubeshackles-cubereg` (deliberate, documented port) + **`cubeshackles-ledger`** (byte-identical, undocumented copy) + **`cubeshackles-settlement-engine`** (byte-identical, undocumented copy). Adapter-tier: Retail-DeFi-API's Pydantic `MoneyAmount`, vegemai-demo's `type Money = number` (a **float** — violates the platform's own "never a binary float" doctrine), CubeWallet's `MoneyAoa`, BualaBuitu's `MoneyAmount`. |
| **Institution** | DUPLICATE, real conflict | 3+ independent, non-interoperable persistence models: Retail-DeFi-API's `Institution(Base)`, institutional-gateway's terrain-adapter-shaped `GatewayInstitutionProfile`, CubeWallet's own separate `Institution(Base)` + separate TS type. Terrain treats institution as an opaque `institution_id` string only — no model at all. None import `cubeshackles-ontology`'s `ObjectType.INSTITUTION`. |
| **Transaction** | DUPLICATE/PARTIAL | 4+ independent full definitions: Cubeshackles-core (ledger primitive, uuid4-based identity), Retail-DeFi-API, CubeWallet, cubeshackles-adviser (Pydantic connector schema). No shared base. Ontology's minimal `{amount, currency}` schema is not mapped onto by any of them. Cubeshackles-retail's frontend alone redefines Transaction 3× internally. Cross-cluster finding: node-api layers its OWN `deterministic_transaction_id`/`replay_correlation_id` scheme on top of, and NOT reconciled with, Core's uuid4-based `Transaction.id`. |
| **Event / AuditEvent** | MOST FRAGMENTED CONCEPT IN THE ORG (~20 independent repo-local definitions) | Core's `cubeshackles.contracts.ciel.event.CIELEvent` is the closest canonical candidate — the one real cross-repo import (node-api imports it) is **undeclared** in node-api's own dependency manifest, resolving only via CI-specific sibling-repo checkouts (`ciel-ci.yml`/`gateway-ci.yml`/`contract-drift.yml`) — weaker coupling than control-plane's SHA-pinned ontology dependency. node-api ALSO defines two more local, non-imported `CIELEvent` variants inside its own repo. Every other repo (BualaBuitu, adviser, control-plane, cubereg, ledger, network-orchestrator, observability, terrain, Retail-DeFi-API, security-framework, CubeWallet, kulifikila, phone-wedge, vegemai-demo) independently defines its own `*Event`/`AuditEvent`. Even Core's own `CoreCIELEventType.TRANSFER_SETTLED` is defined but never actually emitted by any code path. |
| **Currency** | TWO SEPARATE duplication clusters | (1) The Money-module's `CurrencyMeta` (4 copies, see Money row). (2) A separate `core/currency_policy.py` module (`BlockedSettlementCurrencyError`) independently copied into phone-wedge, CubeWallet, AND kulifikila. No single canonical currency vocabulary anywhere in the org. |
| **Jurisdiction** | PARTIAL | `cubeshackles-adviser` and `cubeshackles-compliance-engine` both independently define a bare `Jurisdiction(str, Enum)` (member sets not diffed). `cubeshackles-asset-registry` scopes its own narrower `AssetJurisdiction`. Critically, Terrain's `TerrainContext.jurisdiction` and the ontology kernel's own schema both treat jurisdiction as an **untyped string**, not using any of the enums that exist elsewhere in the org. |
| **Evidence** | Heavily overloaded name, mostly legitimate domain variance, not a true conflict | 10+ distinct `*Evidence*` classes (regulatory-reporting's `RegulatorEvidencePack`, security-framework's `SecurityEvidencePack`/`SigningEvidence`, operations' `EvidenceBundle`, cubereg's `EvidencePackageOut`, supervision's `EvidenceRequest`) — each domain-appropriately shaped, none import the ontology kernel's `EVIDENCE` type or each other. No shared base exists, but the variance appears intentional/domain-specific rather than accidental duplication. |
| **User** | DUPLICATE, multiple | Retail-DeFi-API has TWO Users in the same repo (one explicitly in a file named `user_legacy.py` — confirmed tech debt, not yet cleaned up). CubeWallet has 3+ separate User definitions across its own files. national-transit-app and adviser each define their own. No canonical User anywhere. |
| **Wallet, Loan** | DUPLICATE | Multiple independent per-repo definitions, no canonical source. |
| **Device, Obligation** | Single real definition each, but each locally owned | Retail-DeFi-API's `Device`; control-plane's `Obligation` (notably NOT using ontology's `ObjectType.OBLIGATION` despite already consuming ontology for other types — a near-miss). |
| **Rule, Policy** | GAP, not collision — likely the more important finding | No first-class `class Rule` / `class Policy` domain model found anywhere org-wide under that exact name — only loose demo-app TS object literals. Governance logic lives as ad hoc function/enum modules (e.g. control-plane's `policy/` package) rather than an object model. Flagged **UNRESOLVED** — may be intentional policy-as-code, or a genuine ontology gap that predates and is more fundamental than the collision problem. |
| **Actor** | Near-absent | Only one real hit (vegemai-demo's TS type). Terrain's `actor_id`/`actor_type` is a field pair, not a class. |
| **Person, Organization, Entity, Subject, FiscalSubject, Customer, Merchant, Terminal, Transfer, Payment, Settlement, Invoice, Fee, Refund, Reversal, Credit, Interest, Asset** | UNRESOLVED / UNKNOWN | No exact-name class/type definitions were found in this pass's scan. It is plausible these exist under suffixed/prefixed names not covered by an exact-match search — flagged for a deeper, dedicated follow-up pass, not asserted as absent. |

## Example format cross-check (as requested by the directive)

| Concept | Repo A | Repo B | Repo C | Semantic conflict? |
|---|---|---|---|---|
| Money | institutional-gateway (canonical origin) | cubereg (documented port) | ledger + settlement-engine (undocumented byte-identical copies) | **Yes** — 4 independent copies, only one documented as intentional |
| Institution | Retail-DeFi-API `Institution(Base)` | institutional-gateway `GatewayInstitutionProfile` | CubeWallet `Institution(Base)` + TS type | **Yes** — 3+ non-interoperable shapes |
| Event | Core `CIELEvent` (weak/undeclared import by node-api) | node-api's own 2 local variants | ~17 other independent repo-local shapes | **Yes** — worst fragmentation in the org |
| Transaction | Core (uuid4-based) | node-api (`deterministic_transaction_id`, unreconciled with Core's) | Retail-DeFi-API / CubeWallet / adviser (independent) | **Yes** |

## Key architectural takeaways

1. The ontology kernel is real, tested, and pre-freeze — but has exactly one consumer org-wide. It is a CANONICAL_CANDIDATE for the org, not a CONFIRMED_CANONICAL authority, by actual-usage evidence.
2. Money duplication is worse than previously documented in memory (4 copies now confirmed, including two previously-unknown undocumented byte-identical copies in ledger and settlement-engine).
3. Event/AuditEvent is the single most fragmented concept in the org (~20 independent shapes), and even the one real cross-repo Event import is architecturally fragile (undeclared dependency, CI-only resolution).
4. Currency has two independent duplication clusters, not one.
5. Rule/Policy/Actor/Person/Organization/Settlement/Fee/etc. may be largely **absent** as first-class models org-wide, not merely duplicated — this is a different and arguably more foundational finding for a future consolidation effort than the collision matrix itself, and is flagged UNRESOLVED rather than guessed at.

## UNRESOLVED items from this cluster
- Whether Person/Organization/Entity/Subject/FiscalSubject/Merchant/Terminal/Transfer/Payment/Settlement/Invoice/Fee/Refund/Reversal/Credit/Interest/Asset exist under non-exact names — needs a dedicated deeper pass, not asserted as absent here.
- Whether Rule/Policy absence is intentional (policy-as-code by design) or a genuine gap.
- Local-clone freshness: this census was built from local clones (verified current as of 2026-09-19 per standing memory), not supplemented with live `gh search code` — some findings could be stale if repos changed materially since that verification.
