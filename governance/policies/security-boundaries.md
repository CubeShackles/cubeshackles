# Security Boundaries Policy

**Applies to:** All CubeShackles repositories.  
**Companion:** [`SECURITY_MODEL.md`](../../SECURITY_MODEL.md).

---

## Boundary model

| Zone | Repositories (examples) | Trust level |
|---|---|---|
| **Untrusted input** | Access apps, phone wedge, web | Hostile until validated |
| **Protocol & contracts** | `core`, `validator-node`, `node-api`, `network-orchestrator`, `contracts`, `runtime` (when integrated) | Consensus-critical |
| **Sovereign infrastructure** | `ai-runtime`, `compute`, `hardware`, `kulifikila` | Private; advisory or operational only |
| **Cross-cutting audit** | `observability` | Append-only readers; no state mutation |

## Rules

1. **API → consensus (Boundary 1):** External input is authenticated, rate-limited,
   and validated before reaching validator execution.
2. **Advisory boundary:** Intelligence and AI outputs flow **one way** into the
   protocol as **recorded inputs** only. They never approve, reject, settle, or
   mutate consensus state directly.
3. **Sovereign isolation:** Private repos must not be required for correctness of
   public protocol paths. Their absence must degrade advice or ops visibility, not
   settlement.
4. **Audit:** Actions on consensus paths must be attributable. If an action cannot be
   logged, it is not permitted on that path (target state; scaffold repos document
   intent until implemented).

## Secrets

- No secrets in version control.
- Production credentials live only in controlled deployment environments (`cubeshackles-infra`, private).

## Disclosure

Coordinated disclosure per [`SECURITY_MODEL.md`](../../SECURITY_MODEL.md). No public
issues for exploitable vulnerabilities.
