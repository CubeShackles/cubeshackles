# Claims Register

**Owner: CubeShackles (founder-led).**

Tracks material public claims that need explicit evidence, a maturity label,
or founder/legal sign-off before (re)publication in either language. See
[`DOCUMENTATION_STANDARD.md`](DOCUMENTATION_STANDARD.md) §3.

Columns: **Claim** · **Repository** · **Source evidence** · **Maturity** ·
**Verification status** · **Approved EN wording** · **Approved PT wording** ·
**Reviewer** · **Last reviewed**.

| Claim | Repository | Source evidence | Maturity | Verification status | Approved EN wording | Approved PT wording | Reviewer | Last reviewed |
|---|---|---|---|---|---|---|---|---|
| KYC/KYB/KYT and sanctions screening | `cubeshackles-compliance-engine` | README already states "stubs"; boolean-flag evaluation, no live provider integration | Prototype | Not independently verified beyond repo's own README | "Deterministic sandbox compliance control logic. Does not represent legal authorization, regulatory approval, or live AML/KYC integration." (already in repo) | Direct translation, unchanged scope | — | 2026-07-18 (register created) |
| BNA/CMC/BODIVA regulatory connectivity | `cubeshackles-regulatory-reporting` | Repo reformats local JSON only; no outbound connection found | Prototype | Needs founder confirmation before any bilingual doc implies real regulator integration | "Designed to support regulatory reporting integrations; no live connection to BNA, CMC, or BODIVA exists in this repository." | Direct translation | — | 2026-07-18 |
| USSD/telecom bridge | `Cubeshackles-phone-wedge` | Audit found only a browser JS simulator, no real telecom bridge | Prototype | Needs founder confirmation | "This repository provides a browser-based simulator of USSD/telecom access, not a live telecom integration." | Direct translation | — | 2026-07-18 |
| Citizen balance data | `national-transit-app-cubeshackles` | `get_balance()` returns a hardcoded value for any user (per prior audit) | Prototype/demo | Needs founder confirmation before publishing any "live balance" language | "Balance display in this repository is demonstration data, not a live account query." | Direct translation | — | 2026-07-18 |
| Custody signing (HSM/KMS) | `cubeshackles-vault` | Production adapters raise `ProductionSignerNotConfiguredError`; sandbox signer is real and tested | Split: sandbox = implemented, production = planned | Verified in repo tests (sandbox); production path not built | "Sandbox signing is implemented and tested. Production HSM/KMS signing is not yet configured — see `ProductionSignerNotConfiguredError`." | Direct translation, keep the split explicit | — | 2026-07-18 |
| Validator consensus | `Cubeshackles-validator-node` | No raft/pbft/gossip implementation found; "quorum" is a dashboard field | Prototype | Needs founder confirmation | "This repository does not yet implement a live consensus protocol; validator coordination fields are dashboard/reporting surfaces." | Direct translation | — | 2026-07-18 |
| Disaster-recovery drill evidence | `cubeshackles-disaster-recovery` | Prior audit found placeholder-looking hash values and empty RPO/RTO fields on the one recorded drill | Unverified | Do not cite the existing drill as evidence of DR capability in bilingual docs until re-run for real | "A disaster-recovery drill has been recorded but its evidence has not been independently verified; treat current DR capability as unproven." | Direct translation | — | 2026-07-18 |
| Provincial coverage | `cubeshackles-provincial-topology` | Only 5 of 18 Angola provinces modeled; `deploy_live_failover` raises `NotImplementedError` | Prototype | Verified against repo state at audit time; re-check before citing a coverage number | "Provincial topology currently models a subset of Angola's provinces; live failover deployment is not yet implemented." | Direct translation, keep the "subset" qualifier — do not state a specific count without re-verifying against current code | — | 2026-07-18 |

## How to add a row

1. Identify the claim in an English README/doc.
2. Cite the specific code/test/doc that supports (or fails to support) it.
3. Assign a maturity label from `LOCALIZATION_POLICY.md` §4.
4. Draft approved EN/PT wording that matches the evidence, not the aspiration.
5. Leave Reviewer/Last reviewed blank until a human (ideally the founder for
   institutional/regulatory claims) signs off.

## Related

- [`DOCUMENTATION_STANDARD.md`](DOCUMENTATION_STANDARD.md)
- [`LOCALIZATION_POLICY.md`](LOCALIZATION_POLICY.md)
