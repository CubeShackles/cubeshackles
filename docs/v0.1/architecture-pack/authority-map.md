# Authority Map (v0.1)

Frozen v0.1 authority boundaries. No component may exceed its declared scope.

| Component | Authority | Does not |
|---|---|---|
| `cubeshackles-validator-node` | Validation | Settle, mutate wallet |
| `cubeshackles-node-api` | Online ingress / contract gateway | Finality, settlement decisions |
| `cubeshackles-runtime` | Execution orchestration, settlement handoff | Create finality |
| `cubeshackles-settlement-engine` | Internal ledger finality | Wallet mutation, external bank rails |
| `cubeshackles-offline-infrastructure` | Queue, sync, conflict classification | Validate, settle, ledger mutation |
| `cubeshackles-contracts` | Canonical schemas (read-only reference) | Runtime authority |

No production deployment or regulator approval claims at v0.1.
