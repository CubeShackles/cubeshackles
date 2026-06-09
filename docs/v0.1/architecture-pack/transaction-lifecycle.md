# Transaction Lifecycle (v0.1)

Online path (simplified):

1. **Initiated** — ingress via node-api / runtime (`transaction.initiated`)
2. **Validated** — validator-node (`transaction.validated` or `transaction.rejected`)
3. **Settled** — settlement-engine consumes validated events only
4. **Finality recorded** — settlement-engine (`settlement.finality.recorded`)
5. **Audit emitted** — append-only `audit.event.emitted` at decision points

## Rules

- Settlement does not consume `transaction.initiated` directly.
- Validation does not settle.
- Runtime orchestrates handoff; it does not hold finality authority.

This document describes the frozen v0.1 lifecycle. No new event families.
