# Scanner V1 -- CI Observation / Diff Mode V1

## What this is

A deterministic observation/diff mode that compares a fresh canonical scan
against the **Post-Remediation Canonical Security Baseline V1** and
classifies every finding as `UNCHANGED`, `NEW`, `RESOLVED`, `REGRESSED`,
`SCOPE_CHANGED`, or `UNKNOWN`. It is observation only: it does not fail a
build because findings exist, does not remediate anything, does not change
detection semantics, and does not modify either frozen baseline.

This is a separate loop from remediation. The scanner observes canonical
state; a human-reviewed remediation wave decides what is actually a
defect. Only after enough observation data demonstrates a low
false-positive/regression error rate should `REGRESSED` or narrowly
defined high-confidence findings become blocking gates -- not yet, and not
by this change.

## The two baselines -- never conflated

- **Frozen historical Pilot Rail baseline**
  (`security_baselines/pilot-rail-v1-2026-09-25.json`, sha256
  `9cbdfffb3e8a0f728ba39d456a73f374096428271e0eb6747aa8c8d549301821`,
  10-repo scope, 263 findings). Historical evidence of state-at-creation-
  time. Never modified, never used as a diff target by this tool.
- **Post-Remediation Canonical Security Baseline V1**
  (`baseline_name: canonical-main-v1-2026-09-27`, sha256
  `38f7fbd61fca6d8da3b275fa0792b4a62330db8daee6ca9677ce70737e6474f6`,
  60-repo org scope, 668 findings, 20 `resolved_history` entries). This is
  the only baseline `security_ci_diff.py` compares against. It is **not
  committed to this repository** -- `cubeshackles` is public, and this
  file would expose unfixed org-wide weaknesses. It lives at a private
  location and must be supplied to any run (locally via `--baseline`, in
  CI via the `CUBESHACKLES_SECURITY_BASELINE_B64` secret -- see below).

## Classification semantics

- `UNCHANGED` -- identity present in both baseline `findings` and the
  current scan.
- `NEW` -- identity absent from both baseline `findings` and
  `resolved_history`. **Not automatically a vulnerability** -- requires
  human triage. Identity does not include line number, so ordinary code
  movement never produces a spurious `NEW`.
- `RESOLVED` -- identity present in baseline `findings`, absent from a
  successful current scan of that same in-scope repository.
- `REGRESSED` -- identity absent from baseline `findings` but present in
  `resolved_history` (i.e. explicitly recorded fixed), and reappears under
  the same structural identity (same canonical repo, file, kind, enclosing
  scope, stable key) -- not merely the same literal value in an unrelated
  location. A changed line number alone never causes this.
- `SCOPE_CHANGED` -- a repository entirely outside the baseline's
  `repository_scope` (e.g. created after the baseline was captured). Its
  findings are never labeled `NEW`, since the baseline had no visibility
  into that repository either way.
- `CHECKOUT_STATE_DIFFERENCE` -- reserved classification for a scenario
  this tool's canonical-source discipline is designed to prevent from ever
  occurring: local branch/dirty-worktree state never enters the diff,
  because every scan materializes `origin/<default-branch>` fresh via
  `git archive`, independent of what is checked out locally. Verified by
  mutation test (see below); not expected to ever populate in practice.
- `UNKNOWN` -- a repository's current state could not be established
  (fetch failure, git-archive failure, scanner exception). That
  repository's baseline findings are reported `UNKNOWN`, **never**
  silently `RESOLVED` -- a scanner/infrastructure failure must never look
  like a fixed vulnerability.

## Known Scanner V1 blind spots (unchanged, carried through verbatim)

See `security_scan.py::KNOWN_V1_BLIND_SPOTS` and this tool's own
`known_v1_blind_spots` output field -- no cross-repo call-graph, Python
only, AST-based (dynamically built credentials invisible), cannot trace an
intermediate variable into `compare_digest`, `ROUTE_NO_AUTH_DEPENDENCY` is
call-site not resolved-path based, repo display name can collide across
checkouts (identity does not), no per-occurrence disambiguator, and
`REGRESSED` requires matching structural scope, not just a matching
literal value.

## Output

`security_ci_diff.py` writes deterministic JSON (`schema_version`,
`scanner_version`, `baseline_id`, `baseline_sha256`,
`repository_manifest`, `current_scan_hash`, `summary`, and the six
classification buckets, each finding carrying `repo`, `file`, `line`,
`finding_type`, `stable_identity`, `classification`, `severity`,
`confidence`, `baseline_state`, `current_state`, `evidence`) and a
Markdown summary rendered from that same JSON. **JSON is authoritative;
Markdown is presentation.**

`severity` is a label this tool derives (`derive_severity`), not a field
`security_scan.py`'s own schema carries -- documented explicitly so it is
never mistaken for something the underlying scanner itself computed.

## Determinism

Two independent full 60-repo runs against identical canonical SHAs
produced byte-identical authoritative JSON (`current_scan_hash` and the
full canonical serialization both matched exactly). If a future run's
determinism check fails, stop before any CI integration change -- do not
proceed.

## Usage

```
python3 security_ci_diff.py \
  --baseline /path/to/canonical-main-v1-2026-09-27.json \
  --workspace /path/to/Cubeshackles \
  --out-json observation.json \
  --out-md observation.md
```

`--verify-baselines-only` prints the SHA-256/schema verification report
for both baseline artifacts without running a scan.
`--only-repos <canonical-repo-id...>` scopes the run (used by CI, which
only has this one repository checked out).

## CI integration (`.github/workflows/security-observation.yml`)

Runs on every PR, non-blocking (`continue-on-error: true` plus an
always-exit-0 summary step). Scoped to this repository only -- it does
not check out and scan the rest of the org from inside this repo's CI.
Publishes JSON + Markdown as build artifacts and writes the Markdown
summary to the job summary. Reads the canonical baseline from the
`CUBESHACKLES_SECURITY_BASELINE_B64` repository/org secret (base64 of the
baseline JSON); if that secret is unset or the decoded content is not
valid JSON, the job reports that condition explicitly as an
infrastructure/configuration state in the summary and still exits 0 --
never as a security finding, never as a build failure.

**Populating that secret is a separate, manual, explicit step** (setting
an org secret containing organization-wide finding data is a sensitive
action this change does not take on its own authority) -- see the task's
completion report for what remains outstanding.

This workflow is not a required check and must not be added to branch
protection as one.
