# Architecture Consistency Audit

**Date:** 2026-05-29  
**Scope:** Canonical umbrella repository (`cubeshackles`) and cross-repo documentation alignment.  
**Status:** Remediation applied in this commit.

This audit records inconsistencies found between the stated CubeShackles architecture,
the repository map, and repository maturity on disk. Findings are factual; remediations
are listed with the document or repository each change targets.

---

## Executive summary

The platform documentation treated several **scaffolded** repositories as **planned**
(create-from-nothing), omitted the **contracts** layer, conflated **protocol** and
**sovereign** infrastructure in a single section, and described `cubeshackles-runtime`
with AI-runtime concerns that belong in `cubeshackles-ai-runtime`. Observability was
worded as if production telemetry already exists. The umbrella repository lacked
contract-boundary declarations and formal governance policies.

None of these findings imply that scaffolded code is production-ready. The audit goal
is **documentation honesty** and **layer separation**, not capability claims.

---

## Findings and remediations

### F1 — Missing contracts layer in canonical docs

| Item | Detail |
|---|---|
| **Finding** | `cubeshackles-contracts` exists (schemas, versioning policy, interoperability standard) but was absent from `REPOSITORY_MAP.md`, `SYSTEM_ARCHITECTURE.md`, and the layered diagram. |
| **Risk** | Repositories continue defining ad-hoc message shapes; integration drift. |
| **Remediation** | Add contracts to repository map and architecture diagram; add `contracts/CONTRACTS.md` and `docs/dependencies.md` to the umbrella; link from `README.md` and contributor docs. |

### F2 — Protocol vs sovereign layers conflated

| Item | Detail |
|---|---|
| **Finding** | Private sovereign infrastructure (`ai-runtime`, `compute`, `hardware`, `kulifikila`) was listed adjacent to public protocol repos without a clear sovereign boundary in the map. |
| **Risk** | Contributors treat private compute/AI repos as protocol dependencies. |
| **Remediation** | Split `REPOSITORY_MAP.md` into **Protocol & contracts** and **Sovereign infrastructure** sections; reinforce in `SYSTEM_ARCHITECTURE.md` and `governance/policies/security-boundaries.md`. |

### F3 — Scaffold maturity mislabeled as "planned" / "create"

| Item | Detail |
|---|---|
| **Finding** | `cubeshackles-runtime`, `cubeshackles-ai-runtime`, `cubeshackles-compute`, `cubeshackles-hardware`, and `cubeshackles-observability` exist on disk with READMEs and module boundaries but were marked **planned** and the roadmap used "Create …" language. |
| **Risk** | Implies repositories do not exist; obscures honest scaffold status. |
| **Remediation** | Mark status **scaffolded** in map and architecture tables; update `ROADMAP.md` phases to "Harden scaffold" / integrate, not "Create". |

### F4 — Runtime description included AI runtime hooks

| Item | Detail |
|---|---|
| **Finding** | `REPOSITORY_MAP.md` described `cubeshackles-runtime` with "AI runtime hooks." Advisory AI execution belongs in `cubeshackles-ai-runtime`; the runtime may expose **validator hook interfaces** for **recorded advisory inputs** only. |
| **Risk** | Blurs the consensus / AI isolation boundary. |
| **Remediation** | Revise runtime role text to execution engine, DAG scheduling, validator lifecycle, and deterministic hooks—without AI runtime ownership. |

### F5 — Observability overclaimed

| Item | Detail |
|---|---|
| **Finding** | Observability was described as providing production metrics, tracing, and anomaly detection today. The repository is scaffolded (empty product README until filled). |
| **Risk** | False production-readiness impression. |
| **Remediation** | Describe observability as **scaffolded**; intended scope for audit-grade telemetry contracts and cross-cutting instrumentation—**not** shipped production stacks. |

### F6 — Umbrella lacked contract declarations

| Item | Detail |
|---|---|
| **Finding** | `INTEROPERABILITY_STANDARD.md` requires every repo to declare `contracts/CONTRACTS.md` and `docs/dependencies.md`. The umbrella did not. |
| **Remediation** | Add umbrella `contracts/CONTRACTS.md` and `docs/dependencies.md`. |

### F7 — Governance policies not centralized

| Item | Detail |
|---|---|
| **Finding** | Repository rules lived only in `docs/repo-governance.md` without dedicated policy documents for security, visibility, and interoperability. |
| **Remediation** | Add `governance/policies/` with `repository-policy.md`, `security-boundaries.md`, `public-private-boundaries.md`, `interoperability-policy.md`. |

### F8 — Angola-first / AOA-native currency understated

| Item | Detail |
|---|---|
| **Finding** | Contracts and interoperability standard state AOA as native settlement currency; umbrella `README.md` mentioned African currencies generically. |
| **Remediation** | State **AOA-native** settlement posture in `README.md`, `docs/protocol-overview.md`, and expanded `docs/repo-governance.md`. |

### F9 — Empty READMEs in scaffold repos

| Item | Detail |
|---|---|
| **Finding** | `cubeshackles-observability` and `cubeshackles-hardware` had zero-byte README files despite existing repository scaffolding. |
| **Remediation** | Author honest READMEs in those repositories (scaffolded maturity, boundaries, links to umbrella and contracts). |

---

## Verification checklist

After remediation, the following should hold:

- [x] Every active or scaffolded repo appears in `REPOSITORY_MAP.md` with honest status.
- [x] Contracts layer is visible in architecture docs and governance.
- [x] Protocol repos do not depend on sovereign repos for correctness.
- [x] AI / compute / hardware never described as consensus-critical.
- [x] Scaffold repos are not described as production telemetry or orchestration.
- [x] Umbrella declares contract consume/emit boundaries (none for protocol messages—docs only).

---

## Out of scope (follow-up)

- Renaming on-disk `BuilaBuitu` → `BualaBuitu` (tracked separately).
- Populating schema content in `cubeshackles-contracts` beyond v0.1 skeletons.
- Integration gate updates in `cubeshackles-integration` for new contract enforcement.
- Committing README changes in sibling repos (umbrella commit only unless separately requested).

---

## References

- [`../REPOSITORY_MAP.md`](../REPOSITORY_MAP.md)
- [`../SYSTEM_ARCHITECTURE.md`](../SYSTEM_ARCHITECTURE.md)
- [`../governance/policies/`](../governance/policies/)
- [`../../cubeshackles-contracts/INTEROPERABILITY_STANDARD.md`](../../cubeshackles-contracts/INTEROPERABILITY_STANDARD.md) (sibling repository)
