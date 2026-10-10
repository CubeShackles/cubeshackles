# Synthetic staging isolation assessment (static)

**Date:** 2026-10-10
**Authorization:** founder decision after PR #16. Build the Compose file and fixtures. Run ISO-1 through ISO-7 as a static, offline check. Do not start services.
**Result:** static checks PASS. Runtime proof was not run. `STAGING_ENVIRONMENT` remains **NOT VERIFIED**. Deployment remains **not authorized**.

No production database, secret store, endpoint, or account was read. The check cannot claim a diff against production values, because reading those values was outside this authorization.

## What was produced

- `docker-compose.synthetic.yml` — node-api, settlement-engine, and Ledger B on an internal network. Every service is behind the profile `deployment-not-authorized`, so a plain `docker compose up` starts nothing.
- `fixtures/synthetic-accounts.json` — three `stg_acct_*` accounts, AOA minor units, `provenance=synthetic`.
- `synthetic.env.example` — placeholders only.
- `generate_synthetic_env.py` — writes a local `stg_` file. It was run only against a temporary path and that file was not committed.
- `check_isolation.py` — the static check below.

Pinned build comments remain the Gate 2 SHAs: ledger `24680f4`, settlement-engine `c4f5e16`, node-api `1425452`. This repository does not clone or build those checkouts.

## Static results

| Check | Static result | What was not done |
|---|---|---|
| ISO-1 | PASS — `DATABASE_URL` is `sqlite:////data/ledger-staging.db`; no remote URL; no external network | No connection attempt |
| ISO-2 | PASS — committed secrets are the placeholder `synthetic-local-only` | No comparison with a production or UAT secret store |
| ISO-3 | PASS — `LEDGER_BASE_URL=http://ledger:8086` and `SETTLEMENT_ENGINE_URL=http://settlement-engine:8087` | No egress test |
| ISO-4 | PASS — account ids are `stg_acct_*`; no phone-like number in the fixture | No customer-account inventory |
| ISO-5 | PASS — `internal: true`; published ports bound to `127.0.0.1` | Containers were not started |
| ISO-6 | PASS — every fixture account has `provenance=synthetic` | No reporter is running |
| ISO-7 | PASS — volumes are `cubeshackles-staging-*`; services stay behind the unauthorized profile | Volumes were not created |

## Still unauthorized

Staging deployment, Gate 3 implementation, ledger migration, and route switching.
