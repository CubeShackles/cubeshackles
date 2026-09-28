"""Tests for scripts/security_ci_diff.py's classification logic.

These are synthetic, offline unit tests of `build_diff` -- no git, no
network, no real repository. They exist to lock in the observation-mode
semantics this task requires without depending on the private canonical
baseline file (which is deliberately not committed to this public repo)
or on any live repository state. The mutation-testing protocol against
real repository content (Phase 6 of the CI Observation task) was run
separately, by hand, against isolated temporary worktrees -- see the
task's completion report; it is not repeated here because it must never
touch a tracked repository, including this one's CI.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from security_ci_diff import RepoObservation, build_diff, derive_severity  # noqa: E402
from security_scan import Finding  # noqa: E402


def _baseline(findings: list[dict], resolved_history: list[dict]) -> dict:
    return {
        "repository_scope": ["repo-a"],
        "findings": findings,
        "resolved_history": resolved_history,
    }


def _finding(identity: str, **kwargs) -> Finding:
    base = dict(
        repo="repo-a", file="app.py", line=1, kind="HARDCODED_FALLBACK",
        detail="X defaults to 'y'", classification="production-reachable",
        confidence="heuristic", canonical_repo="repo-a", enclosing_scope="<module>",
        identity=identity,
    )
    base.update(kwargs)
    return Finding(**base)


def _scanned_obs(findings: list[Finding], canonical_repo: str = "repo-a") -> RepoObservation:
    obs = RepoObservation(
        canonical_repo=canonical_repo, baseline_name=canonical_repo,
        baseline_head_sha="sha1", baseline_supported=True, local_clone=None,
    )
    obs.scan_status = "SCANNED"
    obs.current_head_sha = "sha2"
    obs.findings = findings
    return obs


def test_unchanged_identity_present_in_both():
    baseline = _baseline([{"identity": "id1", "canonical_repo": "repo-a", "file": "app.py", "kind": "K", "classification": "production-reachable"}], [])
    obs = _scanned_obs([_finding("id1")])
    diff = build_diff(baseline, [obs], {"repo-a"})
    assert len(diff["unchanged"]) == 1
    assert not diff["new"] and not diff["regressed"] and not diff["resolved"]


def test_new_identity_absent_from_baseline_and_resolved_history():
    baseline = _baseline([], [])
    obs = _scanned_obs([_finding("id-new")])
    diff = build_diff(baseline, [obs], {"repo-a"})
    assert len(diff["new"]) == 1
    assert diff["new"][0].stable_identity == "id-new"


def test_regressed_requires_resolved_history_membership():
    baseline = _baseline([], [{"identity": "id-resolved", "canonical_repo": "repo-a", "file": "app.py", "kind": "K", "note": "fixed"}])
    obs = _scanned_obs([_finding("id-resolved")])
    diff = build_diff(baseline, [obs], {"repo-a"})
    assert len(diff["regressed"]) == 1
    assert not diff["new"]


def test_resolved_when_baseline_identity_missing_from_current_scan():
    baseline = _baseline([{"identity": "id-gone", "canonical_repo": "repo-a", "file": "app.py", "kind": "K", "classification": "production-reachable"}], [])
    obs = _scanned_obs([])  # nothing found this scan
    diff = build_diff(baseline, [obs], {"repo-a"})
    assert len(diff["resolved"]) == 1
    assert diff["resolved"][0].stable_identity == "id-gone"


def test_scope_changed_for_repo_outside_baseline_scope():
    baseline = _baseline([], [])
    obs = _scanned_obs([_finding("id-x", canonical_repo="repo-b")], canonical_repo="repo-b")
    diff = build_diff(baseline, [obs], {"repo-a"})  # repo-b not in scope
    assert len(diff["scope_changed"]) == 1
    assert not diff["new"]


def test_failed_scan_reports_baseline_findings_as_unknown_not_resolved():
    baseline = _baseline([{"identity": "id-unknown", "canonical_repo": "repo-a", "file": "app.py", "kind": "K", "classification": "production-reachable"}], [])
    obs = RepoObservation(
        canonical_repo="repo-a", baseline_name="repo-a", baseline_head_sha="sha1",
        baseline_supported=True, local_clone=None,
    )
    obs.scan_status = "FAILED"
    obs.note = "git fetch failed"
    diff = build_diff(baseline, [obs], {"repo-a"})
    assert len(diff["unknown"]) == 1
    assert not diff["resolved"]  # a scan failure must never be silently reported RESOLVED


def test_line_number_change_alone_does_not_change_classification():
    """Identity does not include line number -- moving a finding's line
    (e.g. code above it grew) must keep it UNCHANGED, never NEW/REGRESSED."""
    baseline = _baseline([{"identity": "id-moved", "canonical_repo": "repo-a", "file": "app.py", "kind": "K", "classification": "production-reachable"}], [])
    obs = _scanned_obs([_finding("id-moved", line=99)])
    diff = build_diff(baseline, [obs], {"repo-a"})
    assert len(diff["unchanged"]) == 1
    assert diff["unchanged"][0].line == 99


def test_derive_severity_non_production_is_info():
    assert derive_severity("HARDCODED_FALLBACK", "test-fixture") == "info"
    assert derive_severity("HARDCODED_FALLBACK", "production-reachable") == "high"
    assert derive_severity("CREDENTIAL_READ", "production-reachable") == "medium"


if __name__ == "__main__":
    import inspect
    mod = sys.modules[__name__]
    failures = 0
    for name, fn in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    print(f"\n{'ALL PASSED' if not failures else f'{failures} FAILED'}")
    raise SystemExit(1 if failures else 0)
