# CubeShackles Organization — Contract Ownership Decision, Maturity Scorecard, Convergence Waves

**Status:** Discovery output. Recommendations only — no implementation, no migration, no merge has been performed as part of this census.
**Date:** 2026-09-30

## 1. Contract Ownership Decision (directive §14)

**Question**: Should `cubeshackles-contracts` become the canonical home for shared domain schemas, CIEL event schemas, API contracts, Money, identity references, transaction contracts, evidence references, fiscal event contracts, and SDK-generated models — or remain narrower?

**Evidence-based answer: it should remain narrower than that, based entirely on what the repository actually contains and how it is actually consumed today.**

- `cubeshackles-contracts` is not pip-installable (no `[build-system]`, no package discovery). It is consumed by 22 repos exclusively via hand-copied, sibling-directory filesystem-path references (`schema_refs.py`), never via `import`, and never via `jsonschema.validate()` (zero calls anywhere in the org). Its enforcement mechanism is effectively documentation, not a build-time or run-time contract.
- The package that real code actually imports for DTOs, HMAC signing, and CIEL entity/event types is `cubeshackles.contracts`, which physically lives inside **Cubeshackles-core** (`src/cubeshackles/contracts/`), not inside the `cubeshackles-contracts` repo. This is confirmed by direct source reads and by three independent consumers: Cubeshackles-node-api (~15+ files), kulifikila (`cubeshackles.contracts.ciel.enums`), and cubeshackles-integration's generated client.
- A THIRD claim exists: `cubeshackles-integration/ONTOLOGY_CONTRACT.md` names `Cubeshackles-core/contracts/ontology` (yet another location inside Core, distinct from both of the above) as canonical for domain-ontology terms — explicitly NOT `cubeshackles-contracts` or the repo literally named `cubeshackles-ontology`.

Given this, the model proposed by the directive's framing — *"Ontology defines semantic meaning; Contracts publishes machine-consumable representations; CIEL carries canonical state transitions; Terrain resolves institutional reality; domain engines own domain logic"* — is **not compatible with the architecture that actually exists today**:
- Ontology does not yet define semantic meaning org-wide (one consumer).
- Contracts does not publish machine-consumable representations in an enforced way (existence-only tests, no schema validation anywhere, not installable).
- CIEL does not carry canonical state transitions (4-5 incompatible implementations, zero working subscribers).
- Terrain does not resolve institutional reality (no persistence, no live query surface, pattern copy-pasted and only 2/11 live-wired).

**Recommendation (not a decree)**: Do not designate `cubeshackles-contracts` canonical for anything beyond event-name *vocabulary* until it is made genuinely enforceable (pip-installable, imported rather than path-referenced, validated against at build or runtime). Separately, the org should resolve — as an explicit founder decision, not something this census can decide — which of the three currently-competing "contracts" artifacts (the `cubeshackles-contracts` repo, Core's `cubeshackles.contracts` package, and Core's `contracts/ontology` subpackage) is meant to become the real canonical home, since evidence shows real code has already organically converged on Core's package without anyone having declared it so.

## 2. Repository Maturity / Convergence Scorecard (directive §15)

Full per-repo maturity is in `ORG_REPOSITORY_CENSUS.md`. This section adds the second axis — canonical alignment — with evidence, answering "why only a subset of 60+ repos currently behave as one system."

| Alignment | Repos (representative, not exhaustive — see full census for every repo) | Evidence pattern |
|---|---|---|
| **CANONICALLY ALIGNED** | Cubeshackles-core↔node-api↔validator-node (Path A only), settlement-engine↔ledger, institutional-gateway↔settlement-engine, Control-plane↔ontology, Control-plane/operations↔ai-sdk, integration's own CI-enforced CIEL-interop-lock | Real, tested, load-bearing STATIC or RUNTIME dependencies confirmed by direct code read, not just docs |
| **PARTIALLY ALIGNED** | node-api's Path B/C, kulifikila↔Core's contracts package, validator-node↔CIEL (fragile try/except), clearing-house/settlement-engine's unwired-but-shape-matching gate functions | Real code exists and the shapes agree, but the connecting call is either absent, fragile, or gated behind a feature flag defaulting off |
| **ISOLATED** | cubereg (deliberate — historical reproducibility requires it), kulifikila's persistence/institution model, adviser's identity/credit/audit model, clearing-house (zero org dependencies), BualaBuitu (by design — no settlement code) | No cross-repo dependency found in either direction; some isolation is intentional and correct (cubereg, BualaBuitu), some is an unaddressed gap (kulifikila, adviser) |
| **CONFLICTING** | Money (4 copies), Event/AuditEvent (~20 shapes), Transaction identity (3+ schemes), Institution (3+ models), CIEL envelope (4-5 shapes) | Independently authored, semantically overlapping, non-interoperable artifacts — see `ONTOLOGY_CENSUS.md` collision matrix |
| **UNKNOWN** | Several breadth-pass repos where test collection failed due to local environment/packaging gaps (asset-registry, compliance-engine, market-infrastructure) | Flagged as an environment artifact in this census, not a confirmed defect — needs re-verification with proper `pip install -e` in each repo's own environment |

**Why only a subset behaves as one system**: the org's real, load-bearing integration exists almost entirely along ONE lineage — Core → node-api → validator-node (Path A) → settlement-engine → ledger, plus the AI-routing lineage (control-plane → ai-sdk ← operations) and the ontology→control-plane pair. Everything else — Terrain, CIEL, Contracts (as a repo), clearing-house, compliance-engine, kulifikila, adviser, network-orchestrator, cubeshackles-runtime — has real, often well-tested code, but exists as an **island**: built to a genuine standard, unreferenced by the lineage that actually moves money end-to-end. This is consistent with `docs/STACK_REPO_ORDER.md`'s own declared build order (core → node-api → integration → wallet layers → orchestrator/validator → web) — the repos built earliest in that order are the most converged; repos meant to be wired in later remain islands because that wiring work has not yet happened, not because it was attempted and failed.

## 3. Proposed Convergence Waves (directive §16 — identification only, NOT implementation)

Derived from the dependency graph in `CROSS_REPO_DEPENDENCY_GRAPH.md`, in dependency order (earlier waves are prerequisites for later ones).

### Wave 0 — Canonical contracts + ontology decision (no code change; a founder decision)
- **Repositories**: cubeshackles-contracts, Cubeshackles-core (`contracts` package), cubeshackles-ontology.
- **Prerequisite**: none — this is a decision wave.
- **Contract affected**: resolves the 3-parallel-contracts-claim finding.
- **Migration risk**: none (no code change in this wave).
- **Compatibility requirement**: must not retroactively invalidate the 22 repos' existing `schema_refs.py` path references without a transition plan.
- **Measurable pass condition**: a single written decision exists naming which of the 3 artifacts is canonical for which sub-scope (vocabulary vs. DTO/schema enforcement vs. ontology terms).

### Wave 1 — Identity/institution/event convergence
- **Repositories**: whichever repo Wave 0 designates for contracts/schemas, Cubeshackles-core, cubeshackles-ontology, node-api, one pilot consumer of the Money/Institution/Event duplication (e.g. cubeshackles-ledger, since it already has an undocumented byte-identical Money copy — lowest-risk place to prove convergence).
- **Prerequisite**: Wave 0 decision made.
- **Contract affected**: Money, Institution, Event/AuditEvent shapes.
- **Migration risk**: MEDIUM — ledger is financially load-bearing; any schema change requires full regression against its 137 tests.
- **Compatibility requirement**: byte-for-byte backward compatibility with ledger's existing Money semantics (Decimal-exact, per its own Waves 2-7 financial-integrity hardening work).
- **Measurable pass condition**: ledger imports Money from the designated canonical source instead of its own undocumented copy, all 137 existing tests still pass unmodified.

### Wave 2 — Transaction/payment/settlement convergence
- **Repositories**: Cubeshackles-core, node-api, validator-node, settlement-engine, clearing-house, compliance-engine.
- **Prerequisite**: Wave 1 identity/event convergence proven on at least one repo.
- **Contract affected**: Transaction identity scheme (reconcile Core's uuid4-hash with node-api's deterministic_transaction_id), the clearing→settlement→compliance broken-chain wiring.
- **Migration risk**: HIGH — touches the org's one real end-to-end financial path (Path A) and its finality guarantees; the institutional pipeline's hardcoded `validation_decision = APPROVED` and RC2A's fabricated CIEL signature are real defects this wave would need to address, not just wire around.
- **Compatibility requirement**: must not weaken Path A's existing 2-of-2 quorum/state-root-divergence guarantees; must not change consensus/finality behavior per the standing non-negotiable invariant.
- **Measurable pass condition**: `require_clearing_approval`/`require_compliance_before_clearing` are actually called from a live route without breaking any of the 125+235 existing passing tests across settlement-engine/clearing-house.

### Wave 3 — CubeReg fiscal integration
- **Repositories**: cubeshackles-cubereg, settlement-engine (at the identified best-fit hook point), whichever repo Wave 0/1 designated canonical for Money/Institution.
- **Prerequisite**: Wave 2 proves the settlement-finality path is trustworthy enough to hook into.
- **Contract affected**: CubeReg's `FiscalScopeContext`/`fiscal_subject_id` against org-wide Institution/Actor concepts (currently UNRESOLVED — no FiscalSubject equivalent found org-wide).
- **Migration risk**: MEDIUM — CubeReg's historical reproducibility/provenance invariants (LAW/INTERPRETATION/EXECUTION separation) must survive contact with real transaction data; this is an explicit non-negotiable preserve-item from the original directive.
- **Compatibility requirement**: must never present an unvalidated fiscal interpretation as authoritative; the hook must be additive (event consumption) not a mutation of settlement-engine's existing finality logic.
- **Measurable pass condition**: a real settlement event from settlement-engine's finality-record hook point produces a CubeReg evidence package end-to-end, all 144 existing CubeReg tests still pass.

### Wave 4 — Kulifikila/Advisor projections
- **Repositories**: kulifikila, cubeshackles-adviser, whichever repo becomes the canonical transaction/event source per Waves 1-2.
- **Prerequisite**: Waves 1-2 provide a real, consumable canonical event stream (today neither exists — this wave cannot start until CIEL or an equivalent actually works).
- **Contract affected**: kulifikila's currently caller-fed payment-history model, adviser's currently caller-fed portfolio/transaction model.
- **Migration risk**: LOW-MEDIUM — both repos are already structured to accept external data; the risk is in the event-stream reliability they'd depend on, not in these repos' own logic (do not change scoring models, per the standing directive).
- **Compatibility requirement**: kulifikila's 78/78 tests and adviser's farmer-risk-engine tests must remain green.
- **Measurable pass condition**: kulifikila and adviser read at least one real field from a canonical source instead of 100% caller-supplied data, without changing either repo's scoring/recommendation logic.

### Wave 5 — Regulatory/field infrastructure
- **Repositories**: cubeshackles-regulatory-reporting, cubeshackles-supervision, cubeshackles-security-framework, cubeshackles-vault.
- **Prerequisite**: a real, canonical evidence/event stream exists (post Wave 2-3).
- **Contract affected**: whatever the reconciled "Regulatory Reporting still unbuilt" vs. "real code exists but unintegrated" finding resolves to.
- **Migration risk**: LOW — these repos are largely read-only consumers by design (supervision is explicitly read-only).
- **Compatibility requirement**: must not weaken any existing security scanner or evidence chain (standing non-negotiable).
- **Measurable pass condition**: regulatory-reporting's existing 16 tests still pass while consuming at least one real upstream evidence artifact instead of none.

### Wave 6 — Remaining repo adoption
- **Repositories**: everything else — the ~30 remaining repos across the observability/operations/infra/design/frontend clusters.
- **Prerequisite**: Waves 0-5 establish the patterns these repos would adopt.
- **Contract affected**: varies per repo; generally the Terrain-pattern and Contracts-path-reference conventions, which could be formalized into real package dependencies once Wave 0-1 decisions are made.
- **Migration risk**: LOW individually, but LARGE in aggregate (mass-editing prohibition applies — must be incremental, never a single mass PR).
- **Compatibility requirement**: per-repo, no global requirement beyond "do not break that repo's own existing tests."
- **Measurable pass condition**: each repo's own existing test suite remains green after adoption; no org-wide measurable condition applies to this wave as a whole.

## Recommended sequencing note
Waves 0-2 are the only ones that touch the org's real financial truth path and therefore carry the actual risk in this program. Waves 3-6 are lower-risk, additive, and can be resequenced or run partially in parallel with Wave 2 once Wave 1 is proven. This sequencing is a recommendation derived from dependency order, not a directive — implementation approval for any wave was explicitly out of scope for this census.
