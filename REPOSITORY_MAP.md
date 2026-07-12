# REPOSITORY_MAP.md

**Canonical inventory of all CubeShackles repositories — their roles, layer,
authority, and visibility.**

This map is authoritative. If a repository's purpose, status, or ownership
boundary is unclear, this document settles it. Every repository in the ecosystem
appears here; none are omitted.

**Status vocabulary:**

- **active** — implemented behavior exists, is tested, and is being worked on.
- **pre-freeze** — contract surface defined; structural validation passes; not yet frozen or integrated into the production gate chain.
- **scaffolded** — repository exists with boundaries, doctrine, and module structure; not yet integrated.
- **planned** — committed direction; repository does not yet exist on disk.

---

## Visibility doctrine

- **Public** repositories present truthful, developer-facing architecture. They contain no sovereign orchestration logic, no AI/fraud models, no regulator tooling, no economic intelligence, and no production secrets.
- **Private** repositories protect sovereign infrastructure, AI/fraud models, regulator tooling, economic intelligence, and future Cube Silicon / Shackle Silicon R&D.
- **Mixed** repositories have a public-facing interface and private implementation components.

Public repositories may *reference* private capabilities at the interface level without exposing their implementation.

---

## 1. Umbrella

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles` | Canonical source of truth: doctrine, architecture, repository map, governance, policies, platform thesis. Contains no protocol code. | active | public |

---

## 2. Contracts layer

The contracts layer is the **schema authority** for the entire ecosystem. Protocol, access, and sovereign repositories consume versioned contracts; they do not redefine shared schemas locally.

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-contracts` | Canonical interoperability contracts: versioned JSON schemas, OpenAPI specs, event taxonomy, versioning policy, integration test strategy, and boundary documents for every major layer. The schema authority. Does not run production traffic. | active (v0.1) | public |

---

## 3. Foundation layer — platform knowledge and event language

These five repositories define the platform's **institutional vocabulary**: what events exist, what entities participate in them, how operators respond, how developers learn the system, and how a future AI engineering agent reasons over all four.

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-ciel` | **CIEL (Canonical Institutional Event Language).** The versioned vocabulary of institutional events emitted and consumed across the platform. Defines what happens. | pre-freeze | public |
| `cubeshackles-ontology` | **Institutional Ontology.** Typed entities (banks, validators, regulators, merchants, citizens) and their typed relationships. Defines who and what is involved in every event. | pre-freeze | public |
| `cubeshackles-tfe` | **Terrain Field Engineering.** Versioned, auditable runbook contracts for operational knowledge — how operators respond to platform events and incidents. | pre-freeze | public |
| `cubeshackles-developer-portal` | **Developer Portal.** Versioned human-facing platform knowledge and documentation portal. How developers learn the platform. | pre-freeze | public |
| `cubeshackles-agent` | **AI Engineering Agent (contract surface).** Declares the capability contract for a future local AI engineering agent. The agent itself is not built here; this repository defines the interface it must satisfy. | pre-freeze | public |

---

## 4. Reality modeling layer

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-terrain` | **Terrain — authoritative reality modeling layer.** Source of truth for institutional entities, typed relationships, permissions, jurisdiction, and execution context. All production systems must consume Terrain before execution. Not a blockchain, wallet, analytics platform, AI system, or dashboard. | active (v0.1.0) | public |

---

## 5. Operating system layer

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-os` | **CubeKernel — platform composition and operating system.** Composes platform services into a coherent operating system: boot sequence, service discovery, dependency graph, AI Runtime registration, feature flags, and lifecycle orchestration contracts. AI is an OS service in this model, not an application. Does not duplicate service code from sibling repos. | scaffolded | public |
| `cubeshackles-platform-specs` | **Product and UX governance authority.** Defines what products do: behavior specifications, UX specifications, interaction models, user flows, state machines, copy standards, accessibility requirements, and acceptance criteria. Sits above the design system. | scaffolded | public |

---

## 6. Protocol and execution layer

Consensus-critical and settlement-critical repositories. These components must remain deterministic, replayable, and independent of advisory AI for correctness.

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-core` | **Protocol logic and economic core.** Cube/Shackle primitives, deterministic execution rules, settlement semantics, fee governance, AOA-native economic core, DAG reconciliation, and audit events. Canonical authority for economics, ledger replay, and fee governance. | active | public |
| `cubeshackles-validator-node` | **Validator execution.** Runs the validator lifecycle — proposes and validates Cubes, applies Shackle rules, participates in deterministic DAG ordering, emits validator attribution records. **Validation authority only** — does not settle. | active | public |
| `cubeshackles-settlement-engine` | **Settlement engine — internal ledger finality authority.** Consumes `transaction.validated.v0.1` from the validator path; emits `transaction.settled.v0.1`, `settlement.finality.recorded.v0.1`, and per-decision audit events. The **sole v0.1 internal ledger finality authority.** Does not mutate wallet state or external bank balances; no production bank or regulator integration. | active (v0.1 boundary) | public |
| `cubeshackles-runtime` | **Deterministic execution kernel.** Execution engine, memory management, DAG scheduling, validator execution lifecycle, and settlement handoff orchestration. Orchestration authority — does not create finality. | scaffolded | public |
| `cubeshackles-offline-infrastructure` | **Offline transaction infrastructure.** Queueing, delayed sync, conflict classification, and replay preservation under weak connectivity. **Offline sync is not validation. Offline sync is not settlement.** Conflict detected is classification only — not resolution. No wallet or ledger mutation authority. | scaffolded | public |

---

## 7. API and coordination layer

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-node-api` | **Public contract gateway — online ingress authority.** External-facing interface for submitting transactions and querying state. Canonical authority for API contracts. Dev port 8090. | active | public |
| `cubeshackles-network-orchestrator` | **Network coordination.** Validator membership, peer gossip, DAG frontier coordination, and validator join/sync. | active | public |
| `cubeshackles-integration` | **Cross-repo integration and production gate suite.** Validates contracts and interoperability across sibling repositories. Owns CIEL schema validation, canonical authority enforcement, feature-freeze manifest, backbone smoke locks, and the full platform gate chain. Does not run production traffic. | active | public |

---

## 8. Institutional finance stack

This layer implements the control chain required for institutional financial operations: instruction normalization → compliance → clearing → settlement. Each repository has a defined authority boundary; none may be bypassed.

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-institutional-gateway` | **Institutional connectivity ingress.** Receives institutional instructions over REST, FIX, ISO 20022, SWIFT, and gRPC adapters; normalizes all payloads into a deterministic `InstitutionalInstruction` contract; emits gateway interoperability events for downstream consumers. Does not clear, settle, validate, or custody. | active | mixed |
| `cubeshackles-compliance-engine` | **Deterministic compliance layer.** Evaluates KYC, KYB, KYT, sanctions, jurisdiction policy, and compliance profile assignment. Gates gateway forwarding and clearing intake with deterministic compliance outcomes. Compliance controls are separate from clearing and settlement. | active | mixed |
| `cubeshackles-clearing-house` | **Institutional clearing authority.** Receives trade intents for DvP, PvP, bundle, cross-asset, and repo flows; performs deterministic netting, margin, collateral, liquidity, and risk checks; produces immutable `ClearingDecision` outputs. Settlement may only proceed after receiving `clearing.settlement.eligible.v0.1`. | active | mixed |
| `cubeshackles-market-infrastructure` | **Capital market risk infrastructure.** Simulates CCP-style central counterparty decisioning: exposure assessment, margin, collateral haircuts, default-fund contribution requirements, stress testing, and repo-readiness checks. Emits deterministic risk control outputs. Risk infrastructure simulation only — not a licensed CCP. | active | mixed |
| `cubeshackles-ledger` | **Double-entry ledger.** Append-only journals, hashchain integrity, double-entry enforcement, reconciliation, and CIEL-native event emission. All journals carry CIEL trace headers and policy metadata. Posted journals are immutable; reversals create new journals. Dev port 8086. | active | mixed |
| `cubeshackles-asset-registry` | **Native asset registry — source of truth for tokenizable assets.** Registers, classifies, validates, and manages lifecycle transitions for financial and real-world assets. Sits below tokenization, custody, compliance, clearing, settlement, and reporting. Does not tokenize, custody, settle, or authorize. | active | mixed |
| `cubeshackles-tokenization-engine` | **Tokenization lifecycle engine.** Consumes `asset.validated.v0.1` events; creates and manages tokenization plans; builds issuance, redemption, and corporate action instructions; emits frozen interop events for custody and downstream consumers. Does not mint tokens, deploy contracts, or execute blockchain transactions. | active | mixed |
| `cubeshackles-rwa-custody` | **Deterministic custody and ownership-control layer.** Consumes tokenization issuance instructions; creates and manages custody records; records legal and beneficial ownership; builds custody proofs and reserve proofs; maintains a deterministic attestation chain. Sits between tokenization and downstream financial operations. Does not register assets, mint tokens, clear, or settle. | active | mixed |

**Institutional control chain (sequential — each gate must pass before the next):**

```
Institutional Gateway → Compliance Engine → Clearing House → Settlement Engine
                                                                    ↓
Asset Registry → Tokenization Engine → RWA Custody →          Ledger (finality record)
```

---

## 9. Sovereign infrastructure layer

Private or mixed infrastructure for AI execution, compute orchestration, and hardware abstraction. Advisory and isolated from the consensus-critical path. **Nothing in the protocol layer depends on sovereign infrastructure for correctness.**

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-ai-runtime` | **Native AI OS service.** Advisory intelligence layer composed by `cubeshackles-os` (CubeKernel). Provides 11 platform AI agents. Every response carries an advisory-only envelope. AI never produces settlement, ledger mutation, validator approval, or journal postings. Endpoint: `POST /v0.1/infer`. Stabilized at `AI_NATIVE_M5`. 55 tests passing. | active | private |
| `cubeshackles-ai-sdk` | **Consumer library for `cubeshackles-ai-runtime`.** Applications must not implement their own HTTP inference clients. Provides `InferClient`, `ReceiptValidator`, `GovernanceValidator`, `AuditPropagation`, `TracePropagation`, `AgentSelector`, and `CapabilityDiscovery`. 23 tests passing. | active | public |
| `cubeshackles-compute` | **Distributed sovereign compute orchestration.** GPU scheduling, edge compute, node balancing, AI workload placement. Future home of *CubeCompute*. | scaffolded | private |
| `cubeshackles-hardware` | **Hardware abstraction and silicon roadmap.** Validator hardware specifications, edge/thermal systems, ARM integration, RISC-V experimentation, FPGA support, ASIC research, and *Cube Silicon* / *Shackle Silicon* pathways. | scaffolded | private |

---

## 10. Intelligence layer (advisory, isolated from consensus)

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-adviser` | **Advisory service (dev port 8080).** Sovereign, audit-ready, AOA-native AI advisory application: explainable portfolio intelligence, simulations, and approval-first proposal workflows. Agents: PortfolioAI, RebalanceAI, TaxAI, AlertAI, SimulationAI. Consumes `cubeshackles-ai-sdk`; runs outside the consensus-critical path. | active | mixed |
| `kulifikila` | **Credit intelligence — AOA-native credit underwriting layer.** National-scale personal and business credit profiles, informal merchant (FIS) scoring, payment behavior history, wallet identity linkage, lender APIs (consent-gated), regulator export to BNA/AGT/INSS, and province-level analytics. Canonical credit intelligence authority. Advisory only — outputs are recorded signals, not settlement inputs. | active | private |

---

## 11. Access layer — products and wedges

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-phone-wedge` | **Angola phone transaction wedge — device initiation authority.** Offline-first, low-connectivity entry point for phone-based transactions. Migrating to CubeShackles Design System (P4-1). | active | public |
| `CubeWallet` | **Wallet — user initiation authority.** Identity-linked wallet infrastructure and transaction UX. Migrated to CubeShackles Design System (P4-2). | active | public |
| `cubeshackles-web` | **Explorer — institutional and public web surface.** Browser-based client for transactions, validator state, audit views, and account management over `node-api`. Institutional admin canonical authority. | active | public |
| `BualaBuitu` | **Market intelligence terminal.** Angola market data and intelligence access surface. | active | mixed |
| `national-transit-app-cubeshackles` | **National transit infrastructure.** AOA-native transit platform for Angola: fare visibility, driver/passenger flows, QR/digital ticket flows, operator settlement support, and transit analytics on CubeShackles economic rails. | active | public |

---

## 12. Design and developer experience layer

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-design-system` | **Single authority for the CubeShackles OS design language.** Design tokens (color, typography, spacing, radius, shadows, motion), icons and logo usage rules, canonical components, layout primitives, chart visual language, accessibility and responsive breakpoints, and institutional/government dashboard patterns. Every frontend must consume this package. | active | public |
| `cubeshackles-storybook` | **Visual reference catalog for `cubeshackles-design-system`.** Showcases every design-system component with states, variants, and accessibility documentation. Not a design authority — documents and validates the authority repo. | active | public |
| `cubeshackles-demo` | **Gate 7 — institutional demonstration environment.** Regulator-grade, bank-grade demo environment for five canonical scenarios. No real money movement; all flows end at `APPROVAL_REQUIRED` or `SIMULATION_ONLY`. Produces evidence artifacts for technical discussions. Dev port 8099. | active | public |
| `cubeshackles-sandbox-lab` | **Deterministic sandbox demonstration rail.** Simulates realistic institutional participants (bank, broker, exchange, custodian, regulator, government, fund) for controlled demonstration scenarios. Produces sandbox evidence artifacts for BNA/BODIVA/CMC technical discussions. No production execution. | active | mixed |

---

## 13. Regulatory and supervision layer

These repositories produce read-only, deterministic supervisory and security evidence. They do not execute, settle, or alter state.

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-supervision` | **Deterministic read-only regulatory supervision layer.** Generates regulator-specific supervisory views for BNA, CMC, ARSEG, AGT, BODIVA, MINFIN, and the Sandbox Authority from platform evidence packs. Does not approve, enforce, clear, settle, or custody. | active | mixed |
| `cubeshackles-regulatory-reporting` | **Regulator-facing reporting.** Consumes deterministic evidence packs from `cubeshackles-integration`; generates sandbox readiness, audit evidence, trace integrity, and contract freeze status reports as JSON, Markdown, and CSV. Does not produce execution authority or alter state. | active | mixed |
| `cubeshackles-security-framework` | **Security governance and evidence framework.** Defines threat models (11 categories), security controls (10 canonical controls), trust boundaries (7 zones), key management and incident response policies, NIST CSF 2.0 and ISO 27001:2022 mappings, and six security evidence artifacts. Produces deterministic governance evidence — not a live scanning tool. | active | mixed |

---

## 14. Platform operations and readiness

| Repository | Role | Status | Visibility |
|---|---|---|---|
| `cubeshackles-provincial-topology` | Angola-first node placement, routing, and provincial failover planning. Planning authority only — no settlement or validation authority. | scaffolded | public |
| `cubeshackles-vault` | **Key custody boundary.** Signing boundaries, key rotation, recovery. Secrets boundary — never stores secrets in the repository. | scaffolded | mixed |
| `cubeshackles-disaster-recovery` | Regional outage, replay rebuild, and backup verification plans. Does not create finality. | scaffolded | mixed |
| `cubeshackles-chaos` | Controlled failure scenarios (test-only). Does not create settlement finality. | scaffolded | mixed |
| `cubeshackles-security` | Threat model, static analysis, dependency review, and secret scanning gates. | scaffolded | mixed |
| `cubeshackles-operations` | Deployment, rollback, incident response, and SLO doctrine. No product features. 43 tests passing at `PLATFORM_ALPHA_1`. | active | mixed |
| `cubeshackles-angola-pilot` | **Controlled pilot corridor scope.** Defines the boundaries for an initial Angola deployment. **No national deployment claim.** | scaffolded | mixed |
| `cubeshackles-infra` | Deployment, environment, and operations tooling for the platform. | active | mixed |
| `cubeshackles-observability` | **Audit visibility authority (target).** Intended home for audit-grade telemetry contracts, metrics and tracing integrations, validator monitoring hooks, and compliance-oriented log shapes. No production telemetry stack is shipped. | scaffolded | mixed |

---

## 15. Canonical authority map

| Domain | Canonical authority repository |
|---|---|
| Economics engine, ledger replay, fee governance | `cubeshackles-core` |
| API contracts and online ingress | `cubeshackles-node-api` |
| Validator settlement truth and attribution | `cubeshackles-validator-node` |
| Internal ledger finality | `cubeshackles-settlement-engine` |
| Network orchestration | `cubeshackles-network-orchestrator` |
| JSON schemas and event contracts | `cubeshackles-contracts` |
| CIEL event vocabulary | `cubeshackles-ciel` |
| Institutional entity ontology | `cubeshackles-ontology` |
| Reality modeling (entities, jurisdiction, context) | `cubeshackles-terrain` |
| Platform composition and OS kernel | `cubeshackles-os` |
| Product behavior and UX specifications | `cubeshackles-platform-specs` |
| Institutional instruction normalization | `cubeshackles-institutional-gateway` |
| Compliance gating | `cubeshackles-compliance-engine` |
| Clearing decisions and eligibility | `cubeshackles-clearing-house` |
| Asset registration and classification | `cubeshackles-asset-registry` |
| Tokenization lifecycle | `cubeshackles-tokenization-engine` |
| Custody and ownership attestation | `cubeshackles-rwa-custody` |
| Advisory AI inference | `cubeshackles-ai-runtime` |
| AI consumer SDK | `cubeshackles-ai-sdk` |
| Design language | `cubeshackles-design-system` |
| Design component documentation | `cubeshackles-storybook` |
| Advisory financial intelligence | `cubeshackles-adviser` |
| Credit intelligence and underwriting | `kulifikila` |
| Device initiation (retail/mobile) | `cubeshackles-phone-wedge` |
| Wallet and user initiation | `CubeWallet` |
| Institutional and public web surface | `cubeshackles-web` |
| Market data terminal | `BualaBuitu` |
| National transit infrastructure | `national-transit-app-cubeshackles` |
| Cross-repo gate orchestration | `cubeshackles-integration` |
| Regulatory supervision views | `cubeshackles-supervision` |
| Regulator-facing reporting | `cubeshackles-regulatory-reporting` |
| Security governance and evidence | `cubeshackles-security-framework` |

---

## 16. Platform milestones (as of July 2026)

| Milestone | Status | Description |
|---|---|---|
| `RC2_FREEZE` | **Complete** | Financial core frozen — settlement, ledger, validator, vault remain sole execution truth |
| `AI_NATIVE_M5` | **Complete** | Native AI platform stabilized — 11 platform agents, advisory-only enforcement, `cubeshackles-ai-sdk` consumer kit |
| `PLATFORM_ALPHA_1` | **Complete** (2026-06-30) | Convergence baseline: RC2 frozen, AI_NATIVE M5 stabilized, Phase 2 legacy migration complete, full gate suite passing, canonical contracts governing interoperability, zero duplicate financial authority |
| Feature Freeze Candidate | **Active** | Engineering in maintenance and assurance mode: bug fixes, security, compliance evidence, reliability. No new product surface or contract mutations without exception process. |
| `PLATFORM_BETA_1` | **Target** | One unified CubeShackles OS across all applications: shared design language, migrated product UX, explorer redesign, live demos, pilot deployment tooling. **Not yet achieved.** |
| Angola Pilot | **Planned** | Controlled Angola deployment corridor following `PLATFORM_BETA_1`. |

---

## 17. Local layout convention

For full local development, all repositories are checked out as siblings:

```
parent/
├── cubeshackles/                          # umbrella — this repo
│
├── cubeshackles-contracts/                # REQUIRED — schema authority
│
├── # Foundation layer
├── cubeshackles-ciel/
├── cubeshackles-ontology/
├── cubeshackles-tfe/
├── cubeshackles-developer-portal/
├── cubeshackles-agent/
│
├── # Reality modeling
├── cubeshackles-terrain/                  # REQUIRED — reality modeling layer
│
├── # Operating system
├── cubeshackles-os/
├── cubeshackles-platform-specs/
│
├── # Protocol and execution — REQUIRED for all gate runs
├── cubeshackles-core/                     # REQUIRED — economic core
├── cubeshackles-validator-node/           # REQUIRED — validator
├── cubeshackles-settlement-engine/
├── cubeshackles-runtime/                  # scaffolded
├── cubeshackles-offline-infrastructure/   # scaffolded
│
├── # API and coordination — REQUIRED
├── cubeshackles-node-api/                 # REQUIRED — runtime API (port 8090)
├── cubeshackles-network-orchestrator/
├── cubeshackles-integration/              # REQUIRED — gate suite
│
├── # Institutional finance stack
├── cubeshackles-institutional-gateway/
├── cubeshackles-compliance-engine/
├── cubeshackles-clearing-house/
├── cubeshackles-market-infrastructure/
├── cubeshackles-ledger/                   # port 8086
├── cubeshackles-asset-registry/
├── cubeshackles-tokenization-engine/
├── cubeshackles-rwa-custody/
│
├── # Sovereign infrastructure
├── cubeshackles-ai-runtime/               # private — native AI OS service
├── cubeshackles-ai-sdk/
├── cubeshackles-compute/                  # scaffolded — private
├── cubeshackles-hardware/                 # scaffolded — private
│
├── # Intelligence layer
├── cubeshackles-adviser/                  # advisory service (port 8080)
├── kulifikila/                            # private — credit intelligence
│
├── # Access layer
├── cubeshackles-phone-wedge/
├── CubeWallet/
├── cubeshackles-web/
├── BualaBuitu/
├── national-transit-app-cubeshackles/
│
├── # Design and developer experience
├── cubeshackles-design-system/
├── cubeshackles-storybook/
├── cubeshackles-demo/                     # port 8099
├── cubeshackles-sandbox-lab/
│
├── # Regulatory and supervision
├── cubeshackles-supervision/
├── cubeshackles-regulatory-reporting/
├── cubeshackles-security-framework/
│
└── # Platform operations and readiness
    ├── cubeshackles-provincial-topology/  # scaffolded
    ├── cubeshackles-vault/                # scaffolded
    ├── cubeshackles-disaster-recovery/    # scaffolded
    ├── cubeshackles-chaos/                # scaffolded
    ├── cubeshackles-security/             # scaffolded
    ├── cubeshackles-operations/
    ├── cubeshackles-angola-pilot/         # scaffolded
    ├── cubeshackles-infra/
    └── cubeshackles-observability/        # scaffolded
```

Tests and tooling that span repositories assume this sibling layout.
Repositories that are absent are expected to skip gracefully where possible.

---

*Last updated: July 2026. Total repositories: 53.*
