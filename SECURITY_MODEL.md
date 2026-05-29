# SECURITY_MODEL.md

**Trust boundaries, threat posture, and disclosure for CubeShackles.**

This document describes the security model of the platform: what we trust, what we
do not, where the boundaries are, and how to report problems. It is a design
document, not a certification. Where controls are planned rather than implemented,
that is stated.

---

## 1. Security goals

In priority order:

1. **Settlement integrity** — consensus-critical state cannot be forged, forked, or
   silently corrupted.
2. **Replay & audit guarantees** — history is tamper-evident and reconstructable.
3. **Isolation** — advisory/AI/experimental compute cannot affect settlement.
4. **Sovereignty** — the system can run on-soil without mandatory dependence on
   foreign-controlled infrastructure or a single hardware supply chain.
5. **Confidentiality** — sovereign models, fraud logic, and economic intelligence
   stay in private repositories and controlled environments.

## 2. Trust boundaries

Each boundary crossing requires authentication, input validation, and audit logging.

```
Untrusted ───────────────────────────────────────────────► Trusted
 end users / devices
   │ (authenticated, rate-limited)
   ▼
 node-api  ── boundary 1 ──►  validator-node / core (consensus-critical)
   ▲                                   │
   │                                   │ (one-way, advisory)
   │                                   ▼
 access apps                     ai-runtime / kulifikila / compute
                                       │
                                       ▼
                                 observability (append-only audit)
```

- **Boundary 1 (API → consensus):** all external input is treated as hostile until
  validated. The API authenticates, rate-limits, and canonicalizes requests before
  anything reaches consensus-critical execution.
- **Advisory boundary (consensus → intelligence):** strictly one-way. The protocol
  *requests* signals and *records* them; intelligence components can never push
  decisions into state.
- **Audit boundary:** observability is append-only and tamper-evident. Regulators
  read; they do not mutate.

## 3. Threat model

We design against, at minimum:

| Threat | Posture |
|---|---|
| **Byzantine validators** | Deterministic ordering + attribution; malicious actions are detectable, attributable, and recorded; misbehaving validators are evicted. |
| **Node partitioning / regional internet collapse** | Offline-first DAG; partitions advance locally and reconcile deterministically. |
| **Datacenter outage** | Replay-based recovery; no single datacenter is authoritative. |
| **Replay attacks** | Cubes are hash-addressed and causally ordered; idempotent, deterministic effects prevent double-application. |
| **Corrupted / hallucinating AI inference** | AI is advisory and isolated; bad inference degrades advice only. Planned: inference receipts and zk-verifiable inference. |
| **GPU / compute exhaustion** | Validators degrade gracefully, shedding non-critical compute while continuing settlement. |
| **Supply-chain / vendor coercion** | Hardware-agnostic design; no mandatory single-vendor dependence. |
| **Key compromise** | Per-validator keys, attested provisioning; compromised keys are evicted and their history remains auditable. |
| **Regulator override misuse** | Override procedures are explicit, bounded, logged, and themselves auditable (planned formalization in `FAILURE_MODELS.md`). |

A fuller enumeration — Byzantine failures, regional collapse, malicious validators,
corrupted inference, replay, partitioning, GPU exhaustion, AI hallucination
safeguards, and regulator override procedures — will be maintained in
`FAILURE_MODELS.md` (planned).

## 4. AI security boundary

The AI boundary is the defining security property of CubeShackles.

- AI executes only in `ai-runtime` / `compute`, never in `core` / `validator-node`
  consensus paths.
- AI emits **signals**, consumed as **recorded inputs** to deterministic rules.
- Worst-case AI compromise: degraded advice. It cannot fork state, halt settlement,
  or break replay.
- Planned controls: **inference receipts** (every advisory output is logged with the
  model, version, and inputs) and **zk-verifiable inference** (advisory outputs
  provable without trusting the executor).

## 5. Confidentiality & visibility

- Public repositories must contain no sovereign orchestration logic, no AI/fraud
  models, no regulator tooling, no economic intelligence, and no secrets.
- Private repositories hold those assets under access control.
- Secrets (keys, credentials, tokens) are never committed. Files such as `.env`,
  `credentials.json`, and key material are excluded by policy and review.

## 6. Secrets & key handling

- No secrets in version control, ever — including in this umbrella repo.
- Validator keys are generated during attested provisioning and held per-node.
- Rotation and eviction procedures are deterministic and auditable.

## 7. Coordinated disclosure

If you discover a vulnerability:

1. **Do not** open a public issue or PR describing the vulnerability.
2. Report it privately to the CubeShackles security contact through the channel
   published for the affected repository.
3. Include a description, reproduction steps, and impact assessment.
4. Allow reasonable time for remediation before any public disclosure.

We commit to acknowledging reports, assessing severity, and coordinating a fix and
disclosure timeline with the reporter.

## 8. Status

This security model describes the intended posture. Several controls — inference
receipts, zk-verifiable inference, formal regulator-override procedures, full
`FAILURE_MODELS.md` — are **planned**, not yet implemented. They are documented here
so the design intent is unambiguous and reviewable.
