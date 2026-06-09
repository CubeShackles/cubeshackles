# Audit Boundary (v0.1)

Audit uses canonical schema `audit.event.emitted.v0.1` from `cubeshackles-contracts`.

## Properties

- Append-only references at decision boundaries
- Requires `replay_correlation_id` where replay applies
- Actor identifies repo and role; not a regulator submission channel

## Consumers

Settlement, offline, runtime handoff, and pilot audit hooks emit audit events.
Audit visibility supports operator review — not approval claims.

No new audit event families at v0.1.
