# CubeShackles Organization — Cross-Repository Dependency Graph

**Status:** Discovery output. Evidence-based. Distinguishes static / runtime / vendored-schema / semantic-duplication / documentation-only relationships, per the directive.
**Date:** 2026-09-30

## Relationship-type legend
- **STATIC** — a real package import or pinned dependency declared in a manifest (pyproject.toml/package.json/requirements.txt), resolvable without any special environment setup.
- **RUNTIME** — a real HTTP/RPC call, or an in-process import that only resolves because of a specific sibling-checkout/PYTHONPATH assumption (fragile static).
- **VENDORED/COPIED SCHEMA** — a hand-copied constant, filesystem-path reference, or hand-reimplemented module, not a package dependency.
- **SEMANTIC DUPLICATION** — an independently authored, functionally-equivalent artifact with no import relationship at all.
- **DOCUMENTATION-ONLY** — named as a dependency in a README/CONTRACTS.md/architecture doc, with no corresponding code-level evidence found.

## Confirmed real dependencies (STATIC or RUNTIME, code-verified)

| Consumer | Producer | Type | Evidence |
|---|---|---|---|
| Cubeshackles-node-api | Cubeshackles-core | RUNTIME (in-process import, real) | `app/services/core_runtime.py` imports `cubeshackles.core.orchestrator.Orchestrator` directly; genuine Core Orchestrator invocation in Path A |
| Cubeshackles-node-api | Cubeshackles-validator-node (×2 instances) | RUNTIME (HTTP, real, genuine 2-of-2 quorum) | `app/services/validator_client.py` — hardcoded 2 base URLs, cross-verified signatures, state-root divergence check — the single strongest real cross-repo integration found in the org |
| Cubeshackles-node-api | Cubeshackles-contracts (Core's package) | STATIC (undeclared in manifest, CI-sibling-only) | imports `cubeshackles.contracts.ciel.event.CIELEvent` from Core; resolves only via `ciel-ci.yml`/`gateway-ci.yml`/`contract-drift.yml` sibling checkouts — a fragile, undeclared coupling |
| Cubeshackles-validator-node | Core's `cubeshackles.contracts.ciel.enums` + `cubeshackles_ciel_sdk` | RUNTIME (fragile — try/except ModuleNotFoundError fallback) | `app/ciel/policy_client.py`; neither package is in `requirements.txt` |
| kulifikila | Core's `cubeshackles.contracts.ciel.enums` | RUNTIME (real import, confirmed) | corroborated independently by both the Kulifikila and Contracts+Integration subagents |
| cubeshackles-integration (generated client) | Core's `cubeshackles.contracts` package | STATIC (real) | generated Python client imports Core's package directly |
| cubeshackles-settlement-engine | cubeshackles-ledger | RUNTIME (real, both in-process AND real HTTP client) | `pyproject.toml` sets `pythonpath = ["src", "../cubeshackles-ledger"]` for RC2A sandbox path; `ledger/ledger_http_client.py` for the institutional path — genuine dual-mode dependency |
| cubeshackles-institutional-gateway | cubeshackles-settlement-engine | RUNTIME (real, signed HTTP via httpx + Ed25519) | `interoperability/settlement_client.py` |
| Cubeshackles-control-plane | cubeshackles-ontology | STATIC (real, SHA-pinned git dependency) | the ONLY confirmed real ontology consumer in the org |
| Cubeshackles-control-plane | cubeshackles-ai-sdk | STATIC (real, pinned) | confirmed via commit messages ("consume cubeshackles-ai-sdk as a real pinned dependency") and requirements |
| cubeshackles-operations | cubeshackles-ai-sdk | STATIC (real) | confirmed via refactor commits ("consume AI Runtime via cubeshackles-ai-sdk") |
| Cubeshackles-node-api / Cubeshackles-validator-node | cubeshackles-terrain PATTERN (not the package) | N/A — copy-paste reimplementation, not a dependency | the ONLY 2 of ~11 Terrain-pattern adapters that are actually live-wired into a request path (middleware / inline check respectively) |
| CubeWallet | Cubeshackles-node-api | RUNTIME (real HTTP, confirmed) | `offline_sync_service.py` calls node-api's `/offline/intents`, `/offline/sync` (Path C) — which in default config terminates locally and never reaches Core or validator-node |

## Confirmed VENDORED / COPIED-SCHEMA relationships (not real dependencies)

| Consumer(s) | Nominal producer | Pattern |
|---|---|---|
| 22 repos (cubeshackles-runtime, node-api, settlement-engine, validator-node, vault, observability, ai-runtime, operations, compute, network-orchestrator, offline-infrastructure, disaster-recovery, provincial-topology, chaos, angola-pilot, security, +7 more) | cubeshackles-contracts | Each hand-maintains a local `src/contracts/schema_refs.py` hardcoding a **sibling-directory filesystem path** into `cubeshackles-contracts/schemas/json/v0.1/...`. Works only if checked out as a literal sibling directory. Not declared in any manifest anywhere. String-constant/Path-object usage only — `jsonschema.validate()` is called nowhere in the entire org. |
| ~11 repos (institutional-gateway, settlement-engine, regulatory-reporting, runtime, observability, ai-runtime, node-api, validator-node, +others) | cubeshackles-terrain | Each independently copy-paste-reimplements `TerrainContext`-shaped validation logic with its own field names/error codes/event constants — none actually import the `cubeshackles-terrain` package (zero consumer repos declare it as a dependency). |
| Every terrain adapter's own `REGISTERED_DESTINATION_REPOS`-equivalent list | cubeshackles-terrain's canonical `REPO_REGISTRY` | Registry-content mismatch in both directions: adapters exist for repos with no canonical entry (institutional-gateway, regulatory-reporting, settlement-engine), and canonical entries exist with no adapter found anywhere (BualaBuitu, Kulifikila, NationalTransit). |

## Confirmed SEMANTIC DUPLICATION (independently authored, no import relationship)

| Concept/module | Independent copies |
|---|---|
| Money | institutional-gateway (origin) / cubereg (documented port) / **ledger** (undocumented copy) / **settlement-engine** (undocumented copy) |
| `currency_policy.py` (`BlockedSettlementCurrencyError`) | Core's version copied into phone-wedge, CubeWallet, and kulifikila |
| `clearing_gate.py`-style "gate function, tested, never called" pattern | settlement-engine's `clearing_gate.py`, clearing-house's `gateway_intake.py`, compliance-engine's `clearing_gate.py` — three near-identical instances, independently authored, each unwired |
| Event/AuditEvent shapes | ~20 independent repo-local definitions (see `ONTOLOGY_CENSUS.md`) |
| CIEL envelope schema | 4-5 mutually incompatible implementations org-wide (see below) |
| Transaction identity schemes | at least 3 independent generation schemes (Core's uuid4-hash, node-api's `deterministic_transaction_id`/`replay_correlation_id`, settlement-engine's own `deterministic_transaction_id` usage) with no cross-references |

## Confirmed DOCUMENTATION-ONLY relationships (named, not code-backed)

| Claim | Reality |
|---|---|
| `cubeshackles-integration/ONTOLOGY_CONTRACT.md` names `Cubeshackles-core/contracts/ontology` as canonical for domain ontology terms | No code-level verification performed of this claim beyond the doc's own assertion; distinct from and NOT the same artifact as `cubeshackles-ontology` (the repo literally named "ontology") |
| `Cubeshackles-ciel` repo's own README implies it is the canonical CIEL vocabulary source | It is a standalone YAML schema-linter over its own un-consumed registry; its 6 registered event names appear NOWHERE ELSE in the org |
| `cubeshackles-settlement-engine/settlement_terrain/settlement_terrain_context.py` lists CubeWallet and node-api in a `REGISTERED_DESTINATION_REPOS` set | Descriptive/config data only, inside a fully unwired Terrain namespace — not an active call |
| `cubeshackles-institutional-gateway` documented as caller of `institutional_router.py` in settlement-engine | Confirmed real from the settlement-engine side (RUNTIME, real signed HTTP); gateway's own call-site code was outside this cluster's scope — the RUNTIME classification above reflects the confirmed side |
| REPOSITORY_MAP.md §15 "Canonical authority map" (org's own declared doctrine) | See `CANONICAL_AUTHORITY_MATRIX.md` for the full cell-by-cell reconciliation against this evidence |

## The CIEL "graph" — actually 4-5 disconnected islands, not a bus

```
Cubeshackles-core (cubeshackles_ciel_sdk lives here, real code)
   │  fragile try/except import (undeclared dep)
   ├──> Cubeshackles-validator-node (policy_client.py, falls back to local vendored copy on failure)
   │
   │  undeclared, CI-sibling-only import
   └──> Cubeshackles-node-api (CIELEvent type; ALSO has 2 more local non-imported variants)
              │
              └──> Cubeshackles-node-api's own /ciel/* REST routes = the one real "server"
                        (in-memory + JSONL CIELStore; a better SQLiteCIELEventStore sits dead beside it)

Cubeshackles-ciel (repo) ─── standalone YAML linter, zero runtime consumers, vocabulary
                             used NOWHERE ELSE in the org (isolated island)

cubeshackles-ledger, cubeshackles-adviser ─── NATS/JetStream publish paths exist,
                             ZERO working subscribers anywhere (adviser's own
                             subscriber.py is a literal no-op placeholder)

cubeshackles-cubereg's FiscalEventEnvelope ─── CIEL-shaped by convention only,
                             zero network egress, zero CIEL import (100% local)
```
`causation_id` (part of the org's own doctrinal CIEL envelope) is absent from every actual implementation found.

## The broken institutional lifecycle chain

```
institutional-gateway  →  [normalize, policy]  →  settlement-engine institutional_router.py
                                                         │
                                                         ▼ (validation_decision HARDCODED = APPROVED)
                                                    real Ed25519-verified HTTP → cubeshackles-ledger
```
Compliance-engine and clearing-house sit BESIDE this path, not IN it — their gate functions
(`require_compliance_before_clearing`, `require_clearing_approval`) are real, tested,
field-for-field schema-compatible with each other, and confirmed **never called from any live route
on either side**. The only end-to-end real path in the org works by skipping both stages entirely.

## Best-fit future fiscal-event hook point (identified, not implemented)

`cubeshackles-settlement-engine/src/finality/finality_record.py::record_internal_ledger_finality`
— immediately after `FinalityGuard.assert_finality_record(event)` succeeds and before returning
`settlement.finality.recorded.v0.1`. This is the one point in the org where a canonical transaction
ID + settled amount + guaranteed internal finality already coexist. Caveat: this path's RC2A
implementation trusts an unverified upstream event-type string and attaches a fabricated,
non-cryptographic CIEL signature — so this is the *best available* hook point today, not a fully
trustworthy one.

## Nodes represented (per directive §12 minimum list)
Ontology, Contracts, CIEL, Terrain, Integration, Institutional Gateway, CubeReg, Wallet, Phone Wedge,
BualaBuitu, CubePay (does not exist as a repo), Kulifikila, Advisor, Clearinghouse, Core, Network
Orchestrator, Validator — all represented above via their confirmed relationships (or confirmed absence
of relationships, in CubePay's case).
