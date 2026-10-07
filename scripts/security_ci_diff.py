"""Scanner V1 -- CI Observation / Diff Mode V1.

This module is deliberately separate from `security_scan.py` and does not
modify it. It reuses, unmodified, that module's detectors, identity
algorithm (`compute_identity`, `stable_detail_key`, `canonical_repo_id`),
and `KNOWN_V1_BLIND_SPOTS`. It adds no new detection semantics and changes
no finding identity.

Purpose: compare a fresh scan of canonical repository content (never a
dirty local worktree) against the frozen Post-Remediation Canonical
Security Baseline V1, and classify every current/baseline finding as
UNCHANGED, NEW, RESOLVED, REGRESSED, SCOPE_CHANGED,
CHECKOUT_STATE_DIFFERENCE, or UNKNOWN. This is observation, not
enforcement: nothing here fails a CI run, remediates a finding, or
rewrites either baseline.

Two baseline artifacts exist and must never be conflated:
  - the FROZEN HISTORICAL Pilot Rail baseline (10-repo scope, 2026-09-25):
    historical evidence of state-at-creation-time, never modified, never
    used as the diff target.
  - the CANONICAL SECURITY BASELINE V1 (60-repo org scope, 2026-09-27,
    post-Wave-2-remediation... actually pre-Wave-2, see below): the only
    baseline this tool diffs against.

Severity is NOT a field security_scan.py's Finding/baseline schema
carries. This module derives a deterministic, documented severity label
from `kind` + `classification` purely for this diff tool's own output --
it is an addition of THIS tool, not a retroactive claim about what the
scanner itself computed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import security_scan as ss

SCHEMA_VERSION = 1
DIFF_TOOL_COMMIT_SOURCE = __file__

# Deterministic, documented severity derivation (diff-tool addition; not
# part of security_scan.py's own schema). production-reachable findings of
# a kind in FAILS_RUN are "high"; production-reachable CREDENTIAL_READ /
# ROUTE_NO_AUTH_DEPENDENCY are "medium"; anything not production-reachable
# (test-fixture, documentation-example, intentional-denylist) is "info".
def derive_severity(kind: str, classification: str) -> str:
    if classification != "production-reachable":
        return "info"
    if kind in ss.FAILS_RUN:
        return "high"
    return "medium"


# --- canonical source discipline --------------------------------------------


def git_out(args: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=timeout
    )


def default_branch_of(local_clone: Path) -> str:
    """Best-effort default branch: prefer origin/HEAD symbolic ref, then
    try 'main', then 'master'."""
    proc = git_out(["symbolic-ref", "refs/remotes/origin/HEAD"], local_clone)
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip().rsplit("/", 1)[-1]
    for candidate in ("main", "master"):
        proc = git_out(["rev-parse", "--verify", f"origin/{candidate}"], local_clone)
        if proc.returncode == 0:
            return candidate
    return "main"


def current_head_sha(local_clone: Path, branch: str) -> str | None:
    proc = git_out(["rev-parse", f"origin/{branch}"], local_clone)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def remote_url(local_clone: Path) -> str | None:
    proc = git_out(["config", "--get", "remote.origin.url"], local_clone)
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return proc.stdout.strip()


def materialize_canonical(local_clone: Path, branch: str, sha: str, scratch_dir: Path) -> Path | None:
    """Deterministic canonical-content materialization: `git archive` of
    origin/<branch> at `sha`, extracted into a throwaway scratch directory
    that is NOT the developer's working checkout. A `.git` with the
    original remote is re-established in the scratch copy solely so
    `canonical_repo_id()` resolves identically to how it resolves for a
    real checkout -- no history, no working-tree state, no dirty files
    survive into the materialized copy. This is the same discipline used
    to build the canonical-main-v1-2026-09-27 baseline itself."""
    target = scratch_dir
    target.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(
        ["git", "-C", str(local_clone), "archive", sha],
        capture_output=True, timeout=120,
    )
    if archive.returncode != 0:
        return None
    tar = subprocess.run(
        ["tar", "-x", "-C", str(target)], input=archive.stdout, capture_output=True, timeout=120,
    )
    if tar.returncode != 0:
        return None
    url = remote_url(local_clone)
    if url:
        subprocess.run(["git", "init", "-q", str(target)], capture_output=True, timeout=30)
        subprocess.run(
            ["git", "-C", str(target), "remote", "add", "origin", url],
            capture_output=True, timeout=30,
        )
    return target


# --- repo resolution ---------------------------------------------------------


@dataclass
class RepoObservation:
    canonical_repo: str
    baseline_name: str | None
    baseline_head_sha: str | None
    baseline_supported: bool
    local_clone: Path | None
    branch: str | None = None
    current_head_sha: str | None = None
    scan_status: str = "NOT_SCANNED"  # SCANNED | FAILED | NOT_SCANNED | UNSUPPORTED_LANGUAGE
    scope_status: str = "IN_BASELINE_SCOPE"  # IN_BASELINE_SCOPE | NOT_IN_BASELINE_SCOPE
    findings: list = field(default_factory=list)
    note: str = ""


def find_local_clone(workspace: Path, name: str) -> Path | None:
    exact = workspace / name
    if exact.is_dir() and (exact / ".git").exists():
        return exact
    lname = name.lower()
    for p in workspace.iterdir():
        if p.is_dir() and p.name.lower() == lname and (p / ".git").exists():
            return p
    return None


def observe_repo(obs: RepoObservation, scratch_root: Path) -> None:
    if obs.local_clone is None:
        obs.scan_status = "FAILED"
        obs.note = "no local clone found in workspace"
        return
    obs.branch = default_branch_of(obs.local_clone)
    fetch = git_out(["fetch", "-q", "origin", obs.branch], obs.local_clone, timeout=120)
    if fetch.returncode != 0:
        obs.scan_status = "FAILED"
        obs.note = f"git fetch failed: {fetch.stderr.strip()[:200]}"
        return
    sha = current_head_sha(obs.local_clone, obs.branch)
    if not sha:
        obs.scan_status = "FAILED"
        obs.note = "could not resolve origin HEAD sha"
        return
    obs.current_head_sha = sha
    scratch = scratch_root / f"{obs.canonical_repo.replace('/', '_')}"
    materialized = materialize_canonical(obs.local_clone, obs.branch, sha, scratch)
    if materialized is None:
        obs.scan_status = "FAILED"
        obs.note = "git archive materialization failed"
        return
    result = ss.ScanResult()
    try:
        ss.scan_repo(materialized, result)
    except Exception as exc:  # scanner/infra failure, not a finding
        obs.scan_status = "FAILED"
        obs.note = f"scanner exception: {exc!r}"
        return
    obs.scan_status = "SCANNED"
    obs.findings = result.findings


# --- diff classification -----------------------------------------------------


@dataclass
class ChangedFinding:
    repo: str
    file: str
    line: int | None
    finding_type: str
    stable_identity: str
    classification: str
    severity: str
    confidence: str
    baseline_state: str | None
    current_state: str | None
    evidence: str

    def to_dict(self) -> dict:
        return {
            "repo": self.repo,
            "file": self.file,
            "line": self.line,
            "finding_type": self.finding_type,
            "stable_identity": self.stable_identity,
            "classification": self.classification,
            "severity": self.severity,
            "confidence": self.confidence,
            "baseline_state": self.baseline_state,
            "current_state": self.current_state,
            "evidence": self.evidence,
        }


def build_diff(
    baseline: dict,
    observations: list[RepoObservation],
    baseline_repo_scope: set[str],
) -> dict:
    """Deterministic classification. REGRESSED strictly requires the
    identity to be present in the baseline's `resolved_history` (i.e. it
    was explicitly recorded fixed) -- matching security_scan.py's own
    compare_to_baseline semantics. A changed line number never enters
    identity, so it cannot by itself cause NEW/REGRESSED. A NEW finding is
    a classification label, not an automatic vulnerability verdict."""
    baseline_by_id = {f["identity"]: f for f in baseline.get("findings", [])}
    resolved_history_ids = {e["identity"] for e in baseline.get("resolved_history", [])}

    buckets: dict[str, list[ChangedFinding]] = {
        "unchanged": [], "new": [], "resolved": [], "regressed": [],
        "scope_changed": [], "unknown": [],
    }

    seen_current_ids: set[str] = set()

    for obs in observations:
        in_scope = obs.canonical_repo in baseline_repo_scope
        if obs.scan_status != "SCANNED":
            # Cannot establish current state for this repo at all. Every
            # baseline finding for it, and any resolved_history entry,
            # becomes UNKNOWN -- never silently RESOLVED, never NEW.
            for bf in baseline.get("findings", []):
                if bf["canonical_repo"] == obs.canonical_repo:
                    buckets["unknown"].append(ChangedFinding(
                        repo=obs.canonical_repo, file=bf["file"], line=None,
                        finding_type=bf["kind"], stable_identity=bf["identity"],
                        classification=bf["classification"],
                        severity=derive_severity(bf["kind"], bf["classification"]),
                        confidence="heuristic", baseline_state="present",
                        current_state=None,
                        evidence=f"scan_status={obs.scan_status}: {obs.note}",
                    ))
            continue

        if not in_scope:
            # A repo the baseline had no visibility into at all (new repo,
            # or otherwise out of the baseline's repository_scope). Its
            # findings are SCOPE_CHANGED, not NEW -- the baseline could not
            # have reported on them either way.
            for f in obs.findings:
                buckets["scope_changed"].append(ChangedFinding(
                    repo=obs.canonical_repo, file=f.file, line=f.line,
                    finding_type=f.kind, stable_identity=f.identity,
                    classification=f.classification,
                    severity=derive_severity(f.kind, f.classification),
                    confidence=f.confidence, baseline_state=None,
                    current_state="present",
                    evidence="repository not in baseline repository_scope",
                ))
            continue

        for f in obs.findings:
            seen_current_ids.add(f.identity)
            if f.identity in baseline_by_id:
                buckets["unchanged"].append(ChangedFinding(
                    repo=obs.canonical_repo, file=f.file, line=f.line,
                    finding_type=f.kind, stable_identity=f.identity,
                    classification=f.classification,
                    severity=derive_severity(f.kind, f.classification),
                    confidence=f.confidence, baseline_state="present",
                    current_state="present", evidence="identity present in both",
                ))
            elif f.identity in resolved_history_ids:
                buckets["regressed"].append(ChangedFinding(
                    repo=obs.canonical_repo, file=f.file, line=f.line,
                    finding_type=f.kind, stable_identity=f.identity,
                    classification=f.classification,
                    severity=derive_severity(f.kind, f.classification),
                    confidence=f.confidence, baseline_state="resolved_history",
                    current_state="present",
                    evidence="identity previously recorded resolved; now present again "
                             "under the same structural scope",
                ))
            else:
                buckets["new"].append(ChangedFinding(
                    repo=obs.canonical_repo, file=f.file, line=f.line,
                    finding_type=f.kind, stable_identity=f.identity,
                    classification=f.classification,
                    severity=derive_severity(f.kind, f.classification),
                    confidence=f.confidence, baseline_state=None,
                    current_state="present",
                    evidence="identity absent from both baseline findings and "
                             "resolved_history -- NOT automatically a vulnerability; "
                             "requires human triage",
                ))

    # RESOLVED: baseline findings, in-scope, successfully-rescanned repos,
    # whose identity did not reappear in the current scan.
    scanned_in_scope = {
        obs.canonical_repo for obs in observations
        if obs.scan_status == "SCANNED" and obs.canonical_repo in baseline_repo_scope
    }
    for bf in baseline.get("findings", []):
        if bf["canonical_repo"] not in scanned_in_scope:
            continue
        if bf["identity"] in seen_current_ids:
            continue
        buckets["resolved"].append(ChangedFinding(
            repo=bf["canonical_repo"], file=bf["file"], line=None,
            finding_type=bf["kind"], stable_identity=bf["identity"],
            classification=bf["classification"],
            severity=derive_severity(bf["kind"], bf["classification"]),
            confidence="heuristic", baseline_state="present", current_state=None,
            evidence="identity present in baseline, absent from current scan of the "
                     "same in-scope, successfully-scanned repository",
        ))

    return buckets


# --- baseline verification ---------------------------------------------------


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashed_payload_sha256(baseline_path: Path) -> str:
    """Recompute the deterministic hash of the baseline payload EXCLUDING
    `_meta_not_part_of_hashed_payload`, exactly as it was computed at
    baseline-creation time."""
    data = json.loads(baseline_path.read_text())
    data.pop("_meta_not_part_of_hashed_payload", None)
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_baselines(canonical_path: Path, pilot_rail_path: Path) -> dict:
    report = {}
    for label, path in (("canonical_security_baseline_v1", canonical_path),
                         ("frozen_historical_pilot_rail_baseline", pilot_rail_path)):
        if not path.exists():
            report[label] = {"path": str(path), "error": "not found"}
            continue
        data = json.loads(path.read_text())
        entry = {
            "path": str(path),
            "sha256": sha256_file(path),
            "schema_version": data.get("schema_version"),
            "scanner_commit": data.get("scanner_commit"),
            "repository_scope_count": len(data.get("repository_scope", [])),
            "findings_count": len(data.get("findings", [])),
            "resolved_history_count": len(data.get("resolved_history", [])),
        }
        if "baseline_name" in data:
            entry["baseline_name"] = data["baseline_name"]
        if "creation_source" in data:
            entry["creation_source"] = data["creation_source"]
        meta = data.get("_meta_not_part_of_hashed_payload")
        if meta:
            entry["recorded_payload_sha256"] = meta.get("payload_sha256")
            entry["recomputed_payload_sha256"] = hashed_payload_sha256(path)
            entry["payload_hash_matches"] = (
                entry["recorded_payload_sha256"] == entry["recomputed_payload_sha256"]
            )
        report[label] = entry
    return report


# --- orchestration -----------------------------------------------------------


def run_observation(
    baseline_path: Path,
    workspace: Path,
    scratch_root: Path,
    only_repos: list[str] | None = None,
) -> tuple[dict, list[RepoObservation]]:
    baseline = json.loads(baseline_path.read_text())
    baseline_repo_scope = set(baseline.get("repository_scope", []))
    repo_meta_by_canonical = {r["canonical_repo"]: r for r in baseline.get("repositories", [])}

    observations: list[RepoObservation] = []
    for canonical_repo, meta in sorted(repo_meta_by_canonical.items()):
        if only_repos and canonical_repo not in only_repos:
            continue
        local = find_local_clone(workspace, meta.get("name", canonical_repo))
        obs = RepoObservation(
            canonical_repo=canonical_repo,
            baseline_name=meta.get("name"),
            baseline_head_sha=meta.get("head_sha"),
            baseline_supported=bool(meta.get("supported")),
            local_clone=local,
        )
        if not meta.get("supported"):
            obs.scan_status = "UNSUPPORTED_LANGUAGE"
            obs.note = meta.get("scan_reason", "unsupported")
            observations.append(obs)
            continue
        observe_repo(obs, scratch_root)
        observations.append(obs)

    # Repos present locally but entirely absent from the baseline's scope
    # (e.g. a repo created after the baseline was captured) -- these need
    # SCOPE_CHANGED handling too, not silent omission.
    if not only_repos:
        for p in sorted(workspace.iterdir()):
            if not p.is_dir() or not (p / ".git").exists():
                continue
            cid = ss.canonical_repo_id(p)
            if cid in repo_meta_by_canonical:
                continue
            obs = RepoObservation(
                canonical_repo=cid, baseline_name=p.name, baseline_head_sha=None,
                baseline_supported=True, local_clone=p, scope_status="NOT_IN_BASELINE_SCOPE",
            )
            observe_repo(obs, scratch_root)
            observations.append(obs)

    diff = build_diff(baseline, observations, baseline_repo_scope)
    return baseline, observations, diff  # type: ignore[return-value]


def canonical_scan_hash(observations: list[RepoObservation]) -> str:
    rows = []
    for obs in sorted(observations, key=lambda o: o.canonical_repo):
        for f in sorted(obs.findings, key=lambda f: f.identity):
            rows.append(f.identity + "\x1f" + obs.canonical_repo)
    payload = "\n".join(sorted(rows))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def repository_manifest(observations: list[RepoObservation]) -> list[dict]:
    out = []
    for obs in sorted(observations, key=lambda o: o.canonical_repo):
        scope_status = (
            "NOT_IN_BASELINE_SCOPE" if obs.scope_status == "NOT_IN_BASELINE_SCOPE"
            else "IN_BASELINE_SCOPE"
        )
        out.append({
            "repo": obs.canonical_repo,
            "canonical_branch": obs.branch,
            "head_sha": obs.current_head_sha,
            "baseline_head_sha": obs.baseline_head_sha,
            "scanner_version": ss._scanner_commit(),
            "scan_status": obs.scan_status,
            "scope_status": scope_status,
            "note": obs.note or None,
        })
    return out


def build_output_json(
    baseline_path: Path,
    baseline: dict,
    observations: list[RepoObservation],
    diff: dict,
) -> dict:
    scan_hash = canonical_scan_hash(observations)
    summary = {
        "unchanged": len(diff["unchanged"]),
        "new": len(diff["new"]),
        "resolved": len(diff["resolved"]),
        "regressed": len(diff["regressed"]),
        "scope_changed": len(diff["scope_changed"]),
        "unknown": len(diff["unknown"]),
        "repositories_observed": sum(1 for o in observations if o.scan_status == "SCANNED"),
        "repositories_unsupported": sum(1 for o in observations if o.scan_status == "UNSUPPORTED_LANGUAGE"),
        "repositories_failed": sum(1 for o in observations if o.scan_status == "FAILED"),
    }
    out = {
        "schema_version": SCHEMA_VERSION,
        "scanner_version": ss._scanner_commit(),
        "baseline_id": baseline.get("baseline_name"),
        "baseline_sha256": sha256_file(baseline_path),
        "repository_manifest": repository_manifest(observations),
        "current_scan_hash": scan_hash,
        "summary": summary,
        "unchanged": [c.to_dict() for c in sorted(diff["unchanged"], key=lambda c: c.stable_identity)],
        "new": [c.to_dict() for c in sorted(diff["new"], key=lambda c: c.stable_identity)],
        "resolved": [c.to_dict() for c in sorted(diff["resolved"], key=lambda c: c.stable_identity)],
        "regressed": [c.to_dict() for c in sorted(diff["regressed"], key=lambda c: c.stable_identity)],
        "scope_changed": [c.to_dict() for c in sorted(diff["scope_changed"], key=lambda c: c.stable_identity)],
        "unknown": [c.to_dict() for c in sorted(diff["unknown"], key=lambda c: c.stable_identity)],
        "known_v1_blind_spots": ss.KNOWN_V1_BLIND_SPOTS,
        "semantics_note": (
            "Observation only. A NEW finding is not automatically a vulnerability. "
            "A REGRESSED finding requires the identity to have been explicitly "
            "recorded resolved in the baseline's resolved_history -- a changed line "
            "number alone never causes REGRESSED or NEW, since identity does not "
            "include line number. A repository absent from baseline scope reports "
            "SCOPE_CHANGED, never NEW. A scan/fetch/materialization failure reports "
            "as scanner/infrastructure failure (scan_status=FAILED), and that "
            "repository's baseline findings are reported UNKNOWN, never silently "
            "RESOLVED."
        ),
    }
    return out


def canonical_json_bytes(data: dict) -> bytes:
    """Deterministic serialization for hashing / determinism comparison:
    sort keys, fixed separators. The caller must strip any
    explicitly-non-semantic fields (e.g. a run timestamp) before calling
    this, if such fields exist."""
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def render_markdown(out: dict) -> str:
    lines = [f"# Security Scanner V1 -- CI Observation Report\n"]
    lines.append(f"Baseline: `{out['baseline_id']}` (sha256 `{out['baseline_sha256'][:16]}...`)")
    lines.append(f"Scanner version: `{out['scanner_version']}`")
    lines.append(f"Current canonical scan hash: `{out['current_scan_hash'][:16]}...`\n")
    s = out["summary"]
    lines.append(
        f"**Repositories:** {s['repositories_observed']} observed, "
        f"{s['repositories_unsupported']} unsupported, {s['repositories_failed']} failed.\n"
    )
    lines.append(
        f"| UNCHANGED | NEW | RESOLVED | REGRESSED | SCOPE_CHANGED | UNKNOWN |\n"
        f"|---|---|---|---|---|---|\n"
        f"| {s['unchanged']} | {s['new']} | {s['resolved']} | {s['regressed']} | "
        f"{s['scope_changed']} | {s['unknown']} |\n"
    )
    if out["regressed"]:
        lines.append("## REGRESSED (previously resolved finding reappeared)\n")
        lines.append("| Repo | File | Kind | Identity | Severity |")
        lines.append("|---|---|---|---|---|")
        for c in out["regressed"]:
            lines.append(f"| {c['repo']} | {c['file']} | {c['finding_type']} | {c['stable_identity']} | {c['severity']} |")
        lines.append("")
    if out["new"]:
        lines.append("## NEW (not automatically a vulnerability -- requires human triage)\n")
        lines.append("| Repo | File | Kind | Identity | Classification | Severity |")
        lines.append("|---|---|---|---|---|---|")
        for c in out["new"]:
            lines.append(f"| {c['repo']} | {c['file']} | {c['finding_type']} | {c['stable_identity']} | {c['classification']} | {c['severity']} |")
        lines.append("")
    if out["resolved"]:
        lines.append(f"## RESOLVED ({len(out['resolved'])} baseline findings no longer present)\n")
    if out["scope_changed"]:
        lines.append(f"## SCOPE_CHANGED ({len(out['scope_changed'])} findings in repositories outside baseline scope)\n")
    if out["unknown"]:
        lines.append(f"## UNKNOWN ({len(out['unknown'])} findings whose current state could not be established)\n")
        lines.append("| Repo | Identity | Evidence |")
        lines.append("|---|---|---|")
        for c in out["unknown"]:
            lines.append(f"| {c['repo']} | {c['stable_identity']} | {c['evidence']} |")
        lines.append("")
    lines.append("## Known Scanner V1 blind spots (unchanged)\n")
    for b in out["known_v1_blind_spots"]:
        lines.append(f"- {b}")
    lines.append("\n_JSON is authoritative; this Markdown is a presentation view of the same data._")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Scanner V1 CI observation/diff mode")
    p.add_argument("--baseline", required=True, type=Path)
    p.add_argument("--pilot-rail-baseline", type=Path)
    p.add_argument("--workspace", required=True, type=Path)
    p.add_argument("--out-json", type=Path)
    p.add_argument("--out-md", type=Path)
    p.add_argument("--only-repos", nargs="*")
    p.add_argument("--verify-baselines-only", action="store_true")
    args = p.parse_args(argv)

    if args.verify_baselines_only:
        report = verify_baselines(args.baseline, args.pilot_rail_baseline)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    with tempfile.TemporaryDirectory(prefix="secscan-ci-diff-") as tmp:
        scratch_root = Path(tmp)
        baseline, observations, diff = run_observation(
            args.baseline, args.workspace, scratch_root, only_repos=args.only_repos
        )
        out = build_output_json(args.baseline, baseline, observations, diff)

    if args.out_json:
        args.out_json.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    if args.out_md:
        args.out_md.write_text(render_markdown(out) + "\n")
    if not args.out_json and not args.out_md:
        print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
