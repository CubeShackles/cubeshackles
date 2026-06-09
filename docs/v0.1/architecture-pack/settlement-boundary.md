# Settlement Boundary (v0.1)

Source: `cubeshackles-settlement-engine/docs/v0.1/settlement-engine-boundary.md`

## Authority

The settlement engine is the **only v0.1 component with finality authority** for
internal ledger v0.1 scope.

## Consumes

- `transaction.validated.v0.1`
- `transaction.rejected.v0.1` (non-settlement outcome only)

## Emits

- `transaction.settled.v0.1`
- `settlement.finality.recorded.v0.1`
- `settlement.rejected.v0.1`
- `audit.event.emitted.v0.1`

## Prohibited

Wallet mutation, external bank balance mutation, bypass validation/audit.
No production-ready claims.
