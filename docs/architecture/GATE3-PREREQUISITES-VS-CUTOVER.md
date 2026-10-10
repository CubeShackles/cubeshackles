# Gate 3 Prerequisites vs Cutover Prerequisites (GOVERNANCE NOTE)

**Date:** 2026-10-10. Clarifies the founder's sequencing qualification: the CG gates are **cutover** gates (for changing monetary posting authority), and not every CG gate must pass before Gate 3 **contract development** begins.

## Two distinct prerequisite sets

### Set 1 — Prerequisites to START Gate 3 (canonical contract development)
These are design/contract activities that do **not** move money or change posting authority, so they do **not** depend on CG-1..CG-9:
- ADR-0003 decisions recorded (done) + ADR-0004 Option C approved (done).
- D2 TransactionId conformance evidence (C1–C10, companion plan) — frozen encoding + cross-language vectors.
- Core contract module scope defined (TransactionId + ledger posting contract), with equivalence/validation tests.
- Baseline CI health (node-api 423 green; ledger/settlement green) — satisfied.
- Feature-freeze exception for new frozen contracts + a new architecture milestone.

**Gate 3 contract work may be requested once Set 1 is satisfied — independent of staging.**

### Set 2 — Prerequisites to CHANGE monetary posting authority (cutover / Gate 4+)
These DO move money/authority and require the full evidence chain:
- Isolated synthetic staging with Ledger B deployed (topology design + ISO-1..ISO-7 proof).
- CG-1..CG-9 all PASS with evidence.
- FT1..FT18 financial-integrity scenarios PASS in staging.
- Reconciliation parity (variance 0) + archived evidence + rehearsed rollback.

**No route switch, balance migration, or read-model demotion happens until Set 2 is complete and separately authorized (Gate 4+).**

## Net
- Gate 3 (contract) can proceed on Set 1 alone — still requires explicit founder authorization, not granted here.
- Gate 4+ (cutover) requires Set 2.
- Keeping them separate lets contract/identity work advance safely while monetary authority stays frozen until staging proves the cutover.
