# Synthetic Staging Topology — Design & Isolation Proof (DESIGN ONLY)

**Status:** PROPOSED — design & preparation authorized; **deployment NOT authorized.**
**Date:** 2026-10-10
**Authorized by:** founder directive 2026-10-10 (staging design/prep, not deployment).
**Companion to:** ADR-0004, MIGRATION_AND_RECONCILIATION_SPEC, GATE2-CLOSURE-AND-STAGING-INVENTORY.
**SHAs:** Cubeshackles-node-api `1425452`, cubeshackles-ledger `24680f4`, cubeshackles-settlement-engine `c4f5e16`.

Goal: a reproducible, **isolated** synthetic staging topology that stands up the Option-C chain — node-api → settlement-engine → **Ledger B (`cubeshackles-ledger`)** — with real service authentication and durable test storage, so CG-1..CG-9 and the 18 financial-integrity scenarios can later be run against synthetic data only. **No deployment, no production access, no monetary migration under this mission.**

## 1. Why this is needed
Per the staging inventory: Ledger B and settlement-engine are not in any current compose/backbone; node-api runs on the Core embedded Ledger A. There is no environment where the authoritative chain actually runs end to end. This design creates one — on paper first.

## 2. Services (synthetic staging)
| Service | Image/build | Port | Durable store | Auth |
|---|---|---|---|---|
| cubeshackles-ledger (Ledger B) | build @`24680f4` | 8086 | **named volume** (SQLite `DATABASE_URL=sqlite:////data/ledger-staging.db`, or dedicated Postgres `ledger-staging`) | `LEDGER_API_KEYS` (staging-only value) |
| cubeshackles-settlement-engine | build @`c4f5e16` | 8087 | named volume (`SETTLEMENT_STORE_DB_PATH`, `SETTLEMENT_SECURITY_DB_PATH`) | `SETTLEMENT_API_KEYS` + CIEL Ed25519 signing (staging keypair) |
| Cubeshackles-node-api | build @`1425452` | 8000 | named volume (`CUBESHACKLES_CORE_DB`) | platform-write (dev token + HMAC + role), `SETTLEMENT_API_KEY` |
| (optional) validator-node | build | 8081 | named volume | `VALIDATOR_API_KEY` |

Wiring: node-api `SETTLEMENT_ENGINE_URL=http://settlement-engine:8087`; settlement-engine `LEDGER_BASE_URL=http://ledger:8086`, `LEDGER_POSTING_ENABLED=true`. All on a dedicated bridge network `cubeshackles-staging` with **no route to any production network**.

## 3. Real service authentication (not shortcuts)
- Reuse the existing mechanisms unchanged: node-api platform-write (dev token + HMAC + role), settlement-engine `require_api_key` + CIEL signature verification, ledger API keys + CIEL signing infra.
- Generate **staging-only** credentials/keypairs at environment creation; never reuse production or UAT values. Fail-closed if unset (existing behavior).
- No phone-only or parallel auth; no auth bypass.

## 4. Durable test storage
- Each service gets its own named Docker volume (or dedicated Postgres database) so state survives container restarts — required to exercise the restart/crash-window scenarios (FT5–FT7, FT17, FT18) and reseed durability.
- Volumes are seeded only from a synthetic fixture (Section 6); never from a production dump.

## 5. Isolation proof — REQUIRED before any deployment is requested
Deployment stays unauthorized until every item is demonstrated and evidenced:
| # | Isolation requirement | Proof |
|---|---|---|
| ISO-1 | No production database reachable | env has only staging `DATABASE_URL`/`*_DB_PATH`; a connection attempt to any prod host fails (network-blocked); assert no prod hostnames in any env var |
| ISO-2 | No production credentials | all secrets are freshly generated staging-only; diff against prod/UAT secret stores shows zero overlap; `grep` the compose/env for known prod/UAT values returns nothing |
| ISO-3 | No production settlement endpoints | egress from the staging network to prod/UAT settlement URLs is blocked; `SETTLEMENT_ENGINE_URL`/`LEDGER_BASE_URL` resolve only to in-network services |
| ISO-4 | No customer accounts / PII | seed fixture contains only synthetic accounts (e.g. `stg_acct_*`); a scan for real phone patterns / identity ids finds none |
| ISO-5 | Network egress contained | the staging bridge has no gateway to prod; outbound to the internet/prod denied by default |
| ISO-6 | Data provenance | every seeded balance/account tagged `provenance=synthetic`; reconciliation reporter refuses any row lacking it |
| ISO-7 | Teardown leaves no shared state | volumes are namespaced to staging and removable without touching any other environment |

An automated `staging-isolation-check` (design) must output PASS for ISO-1..ISO-7 and attach evidence; a single FAIL blocks deployment authorization.

## 6. Synthetic fixture (design)
- A small set of synthetic accounts with explicit opening balances (minor units), all `provenance=synthetic`.
- Deterministic so CG-3 parity and FT1–FT18 are reproducible.
- No production or UAT identifiers.

## 7. Fault injection (for later CG/FT execution)
- Container kill/restart (node-api, settlement-engine, ledger) for restart/crash-window tests.
- Network timeout injection between node-api↔settlement-engine↔ledger for timeout-after-posting tests.
- Concurrency driver for duplicate-request races.

## 8. Explicit non-goals
- **No deployment** is authorized by this doc — design and isolation proof only.
- No production data, credentials, endpoints, or networks.
- No monetary migration, no route switching, no Gate 3 implementation.

## 9. Outputs to request next (separate authorization each)
1. Authorize building the staging compose + fixture (still no deploy).
2. Run and evidence ISO-1..ISO-7.
3. Only then: authorize bringing the environment up and running CG-1..CG-9 + FT1..FT18.
