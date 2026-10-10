# Synthetic staging isolation assessment (static)

**Date:** 2026-10-10
**Authorization:** founder decision after PR #16. Build the Compose file and fixtures. Run ISO-1 through ISO-7 as a static, offline check. Do not start services.
**Result:** `STATIC_ISOLATION = PASS (REPORTED)`. `RUNTIME_ISOLATION = NOT VERIFIED`. A reported static pass is not a runtime pass. `STAGING_ENVIRONMENT` remains **NOT VERIFIED**. Startup remains **not authorized**.

No production database, secret store, endpoint, or account was read. The check cannot claim a diff against production values, because reading those values was outside this authorization.

## What was produced

- `docker-compose.synthetic.yml` — node-api, settlement-engine, and Ledger B on an internal network. Every service is behind the profile `deployment-not-authorized`, so a plain `docker compose up` starts nothing.
- `fixtures/synthetic-accounts.json` — three `stg_acct_*` accounts, AOA minor units, `provenance=synthetic`.
- `synthetic.env.example` — placeholders only.
- `generate_synthetic_env.py` — writes a local `stg_` file. It was run only against a temporary path and that file was not committed.
- `check_isolation.py` — file-level ISO-1..ISO-7. This does not render Compose.
- `check_rendered_compose.py` — `docker compose config` for the default project and for the profile `deployment-not-authorized`. It does not start containers. The profile is a safeguard so a plain `up` selects no services. It is not the isolation boundary. The boundary checked in the rendered file is the internal network, localhost port bindings, named volumes, placeholder environment values, and the absence of an override file.

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

## Rendered configuration

`rendered-config-review.json` is the sanitized result of `docker compose config`. Absolute build paths are not published. The rendered build context is the placeholder directory name `synthetic-local-only`, and Compose fills in `dockerfile: Dockerfile` even though this file does not provide one. That placeholder is not a service checkout. Substituting a real checkout is a new review.

Default `docker compose config`, without the profile, lists no services. With the profile, the three services render on `cubeshackles-staging` with `internal: true`, ports bound to `127.0.0.1`, and named volumes only. No override file is present beside the Compose file. No container was started.

`RENDERED_CONFIG = PASS (REPORTED)` means those rendered fields matched this review. It does not mean a packet was sent, a volume was created, or a production host was proven unreachable.

## Still unauthorized

Staging startup, even with synthetic data. Gate 3 implementation. Ledger migration. Route switching.

The next staging decision, after this rendered review is accepted, would be a separate authorization for one controlled start: synthetic data, disposable volumes, and the rendered network constraints. That start is not authorized here.
