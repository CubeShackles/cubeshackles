# Feature-freeze exception request (not granted)

**Date:** 2026-10-10
**Status:** REQUESTED. Not granted. No implementation follows from this file.

## Request

A later Gate 3 change would add frozen contract types for transaction identity and the economic fingerprint described in `CORE-CONTRACT-SCOPE.md`. Under the Feature Freeze Candidate milestone, that kind of new contract needs an exception before implementation.

This request asks for that exception to be considered. It does not approve it.

## Boundary of the request

- Docs and the investigation vectors in this pull request are already inside `freeze:allowed` documentation work.
- The exception, if it were later granted, would cover only the Core contract surface in `CORE-CONTRACT-SCOPE.md`.
- It would not cover staging startup, a ledger migration, a route switch, or a second monetary posting authority.

## Decision

`GATE_3_AUTHORIZED = NO`. The exception is not recorded as granted in `docs/v0.1/feature-freeze-doctrine.md` or in the taxonomy.
