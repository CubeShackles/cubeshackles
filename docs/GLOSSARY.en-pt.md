# Controlled Glossary — English/Portuguese (pt-AO)

**Owner: CubeShackles (founder-led).**
**Scope:** binding for every `README.pt.md` and translated `docs/` file across
the CubeShackles organization. See [`LOCALIZATION_POLICY.md`](LOCALIZATION_POLICY.md).

Do not introduce a Portuguese rendering of a controlled term that is not in
this table. Propose additions via the terminology-change issue template
(`.github/ISSUE_TEMPLATE/terminology-change.md` in the `.github` org repo)
rather than translating ad hoc inside a single repository's README.

Columns: **English term** · **Approved pt-AO term** · **Never translate** ·
**Definition** · **Context (repo/layer)** · **Capitalization** · **Prohibited
alternatives** · **Notes**.

---

## Platform-native terms (never translated)

| English | Approved pt-AO | Never translate | Definition | Context | Capitalization | Prohibited alternatives | Notes |
|---|---|---|---|---|---|---|---|
| CubeShackles | CubeShackles | ✅ | Organization/platform name | all | As written | — | Brand name |
| Cube | Cube | ✅ | Canonical unit of state: deterministic, hash-addressed, immutable record | `cubeshackles` doctrine | Capitalized | "Cubo" | Protocol primitive, not a generic noun |
| Shackle | Shackle | ✅ | Constraint/commitment logic binding Cubes under rules | `cubeshackles` doctrine | Capitalized | "Corrente", "Grilhão" | Protocol primitive |
| CubeWallet | CubeWallet | ✅ | Product name | `CubeWallet` | As written | — | Registered product name |
| BualaBuitu | BualaBuitu | ✅ | Product name | `BualaBuitu` | As written | — | Registered product name |
| Kulifikila | Kulifikila | ✅ | Product name | `kulifikila` | As written | — | Registered product name |
| AOA | AOA | ✅ | ISO 4217 currency code, Angolan Kwanza | all financial repos | Uppercase | "Kz" in prose is fine as a display abbreviation, never as the contract field | Currency code, not translated |
| CIEL | CIEL | ✅ | Canonical Institutional Event Language (acronym) | `cubeshackles-ciel` | Uppercase | — | Define on first use: "CIEL (Linguagem Canónica de Eventos Institucionais)" |
| TFE | TFE | ✅ | Terrain Field Engineering (acronym) | `cubeshackles-tfe` | Uppercase | — | Define on first use |
| RC2, PLATFORM_ALPHA_1, etc. | (unchanged) | ✅ | Milestone/tag identifiers | `REPOSITORY_MAP.md` | As written | — | Identifiers, not prose |

## Core financial-infrastructure terms

| English | Approved pt-AO | Never translate | Definition | Context | Capitalization | Prohibited alternatives | Notes |
|---|---|---|---|---|---|---|---|
| ledger | livro-razão | — | Append-only record of balances and postings | ledger, settlement-engine | lowercase in prose | "razão" alone (ambiguous) | "livro-razão" is the standard Portuguese banking term |
| settlement | liquidação | — | Final, irrevocable execution of a transfer | settlement-engine | lowercase | "acerto" | Distinguish from "clearing" (compensação) |
| clearing | compensação | — | Matching/netting of obligations prior to settlement | clearing-house | lowercase | "clareamento" (false cognate) | Do not confuse with "liquidação" |
| custody | custódia | — | Safekeeping of assets/keys on behalf of another party | rwa-custody, vault | lowercase | "guarda" | |
| real-world asset (RWA) | ativo do mundo real (RWA) | RWA (acronym) | Off-chain/physical asset represented on the platform | rwa-custody, tokenization-engine | RWA uppercase | — | Spell out on first use, then RWA |
| validator node | nó validador | — | Node performing validation/attestation duties | validator-node | lowercase | "nó verificador" | |
| control plane | plano de controlo | — | Cross-cutting coordination/decision layer | control-plane | lowercase | "plano de controle" (Brazilian variant) | Angola-standard "controlo" |
| runtime | runtime | ✅ | Execution engine | runtime, ai-runtime | lowercase | "ambiente de execução" as a gloss is fine in a definition, not as the term itself | Retained in English per common technical usage |
| institutional gateway | gateway institucional | "gateway" | Entry/normalization point for institutional traffic | institutional-gateway | lowercase | "portão institucional" | "Gateway" retained; "institucional" translated |
| compliance engine | motor de conformidade | — | Deterministic compliance/policy gate | compliance-engine | lowercase | "motor de compliance" (mixed-language, avoid) | |
| regulatory reporting | reporte regulatório | — | Generation of regulator-facing reports/exports | regulatory-reporting | lowercase | "relatório regulador" | |
| asset registry | registo de ativos | — | Canonical record of tokenized/registered assets | asset-registry | lowercase | "registro" (Brazilian spelling) | Angola/European spelling: "registo" |
| orchestration | orquestração | — | Coordinated control of distributed components | network-orchestrator | lowercase | — | |
| disaster recovery | recuperação de desastres | — | Procedures/infrastructure for recovering from major failure | disaster-recovery | lowercase | "recuperação de desastre" (singular, avoid) | |
| offline infrastructure | infraestrutura offline | "offline" | Systems designed for intermittent connectivity | offline-infrastructure | lowercase | "infraestrutura desligada" (wrong meaning) | "Offline" retained, common technical loanword |
| observability | observabilidade | — | Telemetry, logging, tracing, monitoring capability | observability | lowercase | "monitorabilidade" | |
| tokenization | tokenização | "token" | Representing an asset as a platform-native token | tokenization-engine | lowercase | "simbolização" | "Token" retained per §"token symbols" rule |
| supervision | supervisão | — | Regulatory/institutional oversight function | supervision | lowercase | — | |
| market infrastructure | infraestrutura de mercado | — | Systems supporting trading/settlement markets | market-infrastructure | lowercase | — | |
| identity | identidade | — | Identity/attestation subsystem | ontology, node-api | lowercase | — | |
| governance | governança | — | Decision rights and process for the platform | `cubeshackles` governance/ | lowercase | "governação" (European variant, acceptable but keep consistent — use "governança" org-wide) | Pick one spelling org-wide; this glossary fixes "governança" |
| audit trail | trilha de auditoria | — | Append-only attributable record of actions | validator-node, ledger | lowercase | "rasto de auditoria" | |
| finality | finalidade | — | Point at which a transaction cannot be reversed | settlement-engine | lowercase | "finalização" (different meaning — process, not state) | Careful: "finalização" = the act of finalizing; "finalidade" = the state of being final. Confirm context before use |
| reconciliation | reconciliação | — | Matching independent records for consistency | ledger, integration | lowercase | — | |
| reserve | reserva | — | Held balance backing issued value | tokenization-engine | lowercase | — | |
| collateral | colateral | — | Asset pledged to secure an obligation | market-infrastructure | lowercase | "garantia" (broader legal term, avoid in protocol context) | |
| issuance | emissão | — | Creation of new tokenized value | tokenization-engine | lowercase | — | |
| redemption | resgate | — | Conversion of tokenized value back to underlying | tokenization-engine | lowercase | — | |
| wallet | carteira | "CubeWallet" as product name | End-user custody/interface for holding value | CubeWallet, phone-wedge | lowercase (generic) | "wallet" untranslated in prose (only the product name stays English) | |
| smart contract | contrato inteligente | — | Programmable on-platform logic | contracts | lowercase | "contrato esperto" | |
| zero-knowledge proof | prova de conhecimento zero | "ZK" / "zk-*" prefixes | Cryptographic proof without revealing underlying data | security, contracts | lowercase | — | |
| Know Your Customer (KYC) | Conheça o Seu Cliente (KYC) | KYC | Customer identity verification requirement | compliance-engine | KYC uppercase | — | Spell out on first use |
| Know Your Business (KYB) | Conheça o Seu Negócio (KYB) | KYB | Business-entity verification requirement | compliance-engine | KYB uppercase | — | Spell out on first use |
| Know Your Transaction (KYT) | Conheça a Sua Transação (KYT) | KYT | Transaction-monitoring requirement | compliance-engine | KYT uppercase | — | Spell out on first use |
| sanctions screening | rastreio de sanções | — | Checking counterparties against sanctions lists | compliance-engine | lowercase | "triagem de sanções" (acceptable variant, pick one — this glossary fixes "rastreio") | |

## General technical / style terms

| English | Approved pt-AO | Never translate | Notes |
|---|---|---|---|
| user | utilizador | — | Angola/European Portuguese convention, not "usuário" (Brazilian) |
| file | ficheiro | — | Not "arquivo" (Brazilian), unless an existing repository convention already uses it |
| team | equipa | — | Not "time" (Brazilian) |
| implementation | implementação | — | |
| infrastructure | infraestrutura | — | |
| stub | stub | ✅ | Retained — precise engineering term with no clean Portuguese equivalent that isn't misleading |
| sandbox | sandbox | ✅ | Retained per platform convention (e.g. "SANDBOX_POLICY.md") |
| scaffolded | estruturado (sem integração) | — | See `LOCALIZATION_POLICY.md` §4 — always pair with "sem integração" to avoid implying more than exists |
| feature freeze | congelamento de funcionalidades | — | |
| pull request | pull request (PR) | ✅ | Retained — GitHub-native term |
| repository | repositório | — | |
| branch | branch | ✅ | Retained — Git-native term, common in Portuguese engineering usage |
| commit | commit | ✅ | Retained — Git-native term |

## Explicitly not forced into Portuguese

These terms keep their English form in Portuguese technical prose because the
English term is the one actually used by Angolan and broader Lusophone
financial-engineering audiences; a forced translation would reduce, not
improve, legibility:

- **API**, **endpoint**, **webhook**, **backend**, **frontend**, **framework**,
  **deploy** / **deployment** (verb/noun retained; "implantação" may appear as
  a gloss in parentheses on first use only), **pipeline**, **dashboard**,
  **middleware**.

## Maturity vocabulary

See [`LOCALIZATION_POLICY.md`](LOCALIZATION_POLICY.md) §4 for the canonical
implemented/prototype/planned mapping — it is not repeated here to avoid two
tables drifting apart.
