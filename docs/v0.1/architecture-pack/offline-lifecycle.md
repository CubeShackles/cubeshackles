# Offline Lifecycle (v0.1)

Weak-connectivity path:

1. **Initiated** — `transaction.initiated` captured at edge
2. **Queued** — `offline.transaction.queued`
3. **Sync attempted** — `offline.sync.attempted`
4. **Sync completed** — `offline.sync.completed`
5. **Conflict detected** — `offline.conflict.detected` (classification only)
6. **Audit emitted** — `audit.event.emitted` with replay correlation

## Prohibited on offline path

Validate, reject, settle, reverse, mutate wallet state, mutate ledger state.

Offline infrastructure does not replace validator or settlement authority.
