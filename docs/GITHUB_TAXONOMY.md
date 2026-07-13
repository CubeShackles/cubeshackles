# GitHub Taxonomy — Institutional Review Surface

**Owner: CubeShackles (founder-led)**  
**Audience:** Coinbase, Circle, sovereign funds, regulators, auditors, and internal operators  
**Purpose:** Make every pull request and issue readable in seconds — what changed, which layer, what risk, which milestone.

GitHub **labels and milestones attach to pull requests and issues**, not to individual commits. Commits must use the conventional prefixes below so history stays attributable when reviewed from `git log` or release notes.

---

## 1. Required PR fields (checklist)

Every PR must set:

1. **One `type:*` label** — what kind of change.
2. **One `layer:*` label** — architectural layer (from `REPOSITORY_MAP.md`).
3. **One `risk:*` label** — institutional risk class.
4. **Milestone** — active platform milestone (see §4).
5. **Commit subjects** — conventional prefix matching the `type:*` label.

Optional but recommended:

- `audience:*` when the change is primarily for external review evidence.
- `freeze:allowed` or `freeze:exception-required` during Feature Freeze Candidate.

---

## 2. Labels

Colors are fixed so the org UI stays consistent.

### Change type (`type:*`) — exactly one

| Label | Color | Meaning |
|---|---|---|
| `type:bug` | `#d73a4a` | Correctness defect; no new product scope |
| `type:fix` | `#d73a4a` | Repair of broken behavior (alias emphasis for ops) |
| `type:feat` | `#1d76db` | New capability (restricted under feature freeze) |
| `type:docs` | `#0075ca` | Documentation / evidence / doctrine |
| `type:security` | `#b60205` | Vulnerability, auth, crypto, trust-boundary hardening |
| `type:compliance` | `#5319e7` | Regulatory / policy / audit evidence alignment |
| `type:test` | `#0e8a16` | Tests, gates, fixtures |
| `type:infra` | `#fbca04` | CI, deploy, repo tooling |
| `type:refactor` | `#c5def5` | Internal structure; no external contract change |
| `type:chore` | `#ffffff` | Maintenance that is not product scope |

### Architectural layer (`layer:*`) — exactly one

| Label | Color | Maps to |
|---|---|---|
| `layer:canonical` | `#000000` | Umbrella doctrine (`cubeshackles`) |
| `layer:contracts` | `#5319e7` | `cubeshackles-contracts` |
| `layer:foundation` | `#1d76db` | CIEL, ontology, TFE, developer-portal, agent |
| `layer:protocol` | `#b60205` | core, validator, settlement, runtime, offline |
| `layer:api` | `#fbca04` | node-api, network-orchestrator, integration |
| `layer:institutional` | `#e99695` | gateway, compliance, clearing, ledger, custody, tokenization, … |
| `layer:access` | `#0e8a16` | CubeWallet, web, phone-wedge, BualaBuitu, national-transit |
| `layer:intelligence` | `#d93f0b` | adviser, AI runtime/sdk, kulifikila (advisory only) |
| `layer:sovereign` | `#6f42c1` | compute, hardware, private sovereign infra |
| `layer:ops` | `#c2e0c6` | ops, infra, security, chaos, disaster-recovery, observability |
| `layer:os` | `#a2eeef` | `cubeshackles-os` (CubeKernel), `cubeshackles-platform-specs` |
| `layer:control-plane` | `#0052cc` | `cubeshackles-control-plane` (cross-cutting request governance — see `SYSTEM_ARCHITECTURE.md` §5a) |

### Risk class (`risk:*`) — exactly one

| Label | Color | Meaning for external reviewers |
|---|---|---|
| `risk:consensus-critical` | `#b60205` | Can affect settlement, ledger, validator, or finality |
| `risk:public-surface` | `#fbca04` | External API / product UX / public docs |
| `risk:advisory-only` | `#0e8a16` | AI/advisory path; must not mutate consensus |
| `risk:ops-only` | `#c5def5` | Internal ops/CI; no protocol semantics |
| `risk:secrets-sensitive` | `#000000` | Credentials, keys, custody, private sovereign material |

### Audience (`audience:*`) — optional, multi-ok

| Label | Color | Use when |
|---|---|---|
| `audience:regulator` | `#5319e7` | Evidence pack, auditability, supervisory narrative |
| `audience:institutional` | `#1d76db` | Exchange/bank/fund integration readiness |
| `audience:developer` | `#0075ca` | DX, contracts, SDK, portal |
| `audience:ops` | `#0e8a16` | Runbooks, SLO, incident |

### Feature freeze (`freeze:*`) — during Feature Freeze Candidate

| Label | Color | Meaning |
|---|---|---|
| `freeze:allowed` | `#0e8a16` | Bug/security/compliance/docs/reliability — allowed |
| `freeze:exception-required` | `#d93f0b` | Needs formal exception under freeze doctrine |

### Governance

| Label | Color | Meaning |
|---|---|---|
| `governance:founder-led` | `#000000` | Ownership/doctrine/authorship surface |
| `status:blocked` | `#b60205` | Cannot merge until dependency clears |
| `status:needs-review` | `#fbca04` | Waiting on institutional/technical review |

---

## 3. Conventional commit prefixes

Align commit subjects with `type:*`:

```
feat: ...
fix: ...
docs: ...
security: ...
compliance: ...
test: ...
infra: ...
refactor: ...
chore: ...
```

Body should state **why** (institutional impact), not only what.

Do **not** require AI-vendor `Co-authored-by` trailers. CubeShackles is founder-led.

---

## 4. Milestones (platform sequence)

Create these milestones on every active repository (closed where complete):

| Milestone | State | Description |
|---|---|---|
| `RC2_FREEZE` | closed | Financial core freeze — settlement/ledger/validator/vault sole execution truth |
| `AI_NATIVE_M5` | closed | Native AI platform stabilized — advisory-only enforcement |
| `PLATFORM_ALPHA_1` | closed | Institutional baseline (2026-06-30) — gates green, contracts canonical |
| `Feature Freeze Candidate` | open | Maintenance/assurance mode — restricted product scope |
| `PLATFORM_BETA_1` | open | Unified OS design language across applications (target) |
| `Angola Pilot` | open | Controlled Angola deployment corridor (planned) |

Canonical narrative: [`ROADMAP.md`](../ROADMAP.md).

---

## 5. How external reviewers should read a PR in seconds

1. **Milestone** → where this sits on the platform clock.  
2. **`type:*` + `risk:*`** → what kind of change and whether it can touch money/finality.  
3. **`layer:*`** → which architectural box.  
4. **Title + conventional commits** → precise delta.  
5. **Docs/evidence links** → regulator pack or gate proof when `audience:regulator` / `type:compliance`.

---

## 6. Sync

Apply this taxonomy with:

```bash
python3 scripts/sync_github_taxonomy.py
```

Requires `gh` authenticated with permission to manage labels and milestones on CubeShackles repositories.
