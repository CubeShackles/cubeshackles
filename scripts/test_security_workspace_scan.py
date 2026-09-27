"""Tests for the workspace-wide observation layer (security_workspace_scan.py).

Every test builds a synthetic workspace of real `git init` repositories in
tmp_path -- no dependency on the real CubeShackles workspace."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

import security_scan as ss
import security_workspace_scan as ws

LITERAL = "hunter2-literal-secret"
FALLBACK_SRC = f'import os\nTOKEN = os.getenv("SVC_API_SECRET", "{LITERAL}")\n'


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-C", str(root), *args],
        check=True, capture_output=True,
    )


def make_repo(root: Path, remote: str | None, files: dict[str, str] | None = None, commit: bool = True) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q", "-b", "main")
    if remote:
        _git(root, "remote", "add", "origin", remote)
    for rel, text in (files or {}).items():
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8")
    if commit:
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--allow-empty", "-m", "init")
    return root


def make_baseline(tmp: Path, paths: list[Path]) -> Path:
    res = ss.ScanResult()
    for p in paths:
        ss.scan_repo(p, res)
    b = ss.build_baseline(res, repository_scope=sorted({f.canonical_repo for f in res.findings}), creation_source="test")
    out = tmp / "baseline.json"
    out.write_text(json.dumps(b, sort_keys=True), encoding="utf-8")
    return out


@pytest.fixture()
def workspace(tmp_path: Path) -> Path:
    root = tmp_path / "ws"
    root.mkdir()
    make_repo(root / "svc-a", "https://github.com/Org/svc-a.git", {"app/x.py": FALLBACK_SRC})
    make_repo(root / "svc-b", "git@github.com:Org/svc-b.git", {"app/y.py": "x = 1\n"})
    return root


def run_ws(root: Path, baseline: Path, pilot: list[str]) -> dict:
    return ws.run(root, baseline, pilot)


# --- identity / inventory ---------------------------------------------------


@pytest.mark.parametrize("url,expected", [
    ("https://github.com/Org/Repo.git", "org/repo"),
    ("git@github.com:Org/Repo.git", "org/repo"),
    ("https://github.com/Org/Repo/", "org/repo"),
    ("", ""),
])
def test_remote_key_normalisation(url, expected):
    assert ws.remote_key(url) == expected


def test_worktree_is_reported_as_duplicate_not_counted_twice(workspace, tmp_path):
    wt = workspace / "svc-a" / ".claude" / "worktrees" / "feat-x"
    _git(workspace / "svc-a", "worktree", "add", "-q", "-b", "feat-x", str(wt))
    inv = ws.build_inventory(workspace)
    keys = [u["repo_key"] for u in inv["unique_repositories"]]
    assert keys.count("org/svc-a") == 1
    assert [d["path"] for d in inv["duplicate_checkouts"]] == [os.path.join("svc-a", ".claude", "worktrees", "feat-x")]
    assert inv["duplicate_checkouts"][0]["kind"] == "worktree"
    assert inv["duplicate_checkouts"][0]["duplicate_of"] == "svc-a"


def test_second_checkout_with_same_remote_is_a_duplicate(workspace):
    make_repo(workspace / "svc-a-copy", "https://github.com/org/SVC-A", {"app/x.py": "y = 2\n"})
    inv = ws.build_inventory(workspace)
    assert len([u for u in inv["unique_repositories"] if u["repo_key"] == "org/svc-a"]) == 1
    assert {d["path"] for d in inv["duplicate_checkouts"]} == {"svc-a-copy"}
    assert inv["duplicate_checkouts"][0]["kind"] == "second-checkout"


def test_same_basename_different_remotes_are_not_merged(tmp_path):
    root = tmp_path / "ws"
    make_repo(root / "one" / "app", "https://github.com/A/app.git", {"m.py": "x=1\n"})
    make_repo(root / "two" / "app", "https://github.com/B/app.git", {"m.py": "x=1\n"})
    # candidates are immediate children only; expose both via symlink-free copies
    make_repo(root / "app-a", "https://github.com/A/app.git", {"m.py": "x=1\n"})
    make_repo(root / "app-b", "https://github.com/B/app.git", {"m.py": "x=1\n"})
    keys = {u["repo_key"] for u in ws.build_inventory(root)["unique_repositories"]}
    assert {"a/app", "b/app"} <= keys


def test_no_remote_repos_are_flagged_and_never_merged(tmp_path):
    root = tmp_path / "ws"
    make_repo(root / "local-1", None, {"a.py": "x=1\n"})
    make_repo(root / "local-2", None, {"a.py": "x=1\n"})
    inv = ws.build_inventory(root)
    assert len(inv["unique_repositories"]) == 2
    for u in inv["unique_repositories"]:
        assert u["scan_status"] == "SCANNED"
        assert "UNRESOLVED_REPO_IDENTITY" in u["scan_note"]


def test_not_scanned_reasons_are_explicit(tmp_path):
    root = tmp_path / "ws"
    make_repo(root / "ts-only", "https://github.com/o/ts-only.git", {"src/a.ts": "export const a = 1\n"})
    make_repo(root / "empty", "https://github.com/o/empty.git", commit=False)
    (root / "plain-dir").mkdir(parents=True)
    broken = root / "broken"
    broken.mkdir()
    (broken / ".git").write_text("gitdir: /nonexistent/nowhere\n")
    inv = ws.build_inventory(root)
    by = {u["repo_key"]: u for u in inv["unique_repositories"]}
    assert (by["o/ts-only"]["scan_status"], by["o/ts-only"]["scan_reason"]) == ("NOT_SCANNED", "UNSUPPORTED_LANGUAGE")
    assert (by["o/empty"]["scan_status"], by["o/empty"]["scan_reason"]) == ("NOT_SCANNED", "EMPTY_REPOSITORY")
    statuses = {c["path"]: c["status"] for c in inv["non_repository_candidates"]}
    assert statuses["plain-dir"] == "NOT_A_GIT_REPOSITORY"
    assert statuses["broken"] == "BROKEN_GIT_STATE"


def _snapshot(root: Path) -> dict:
    snap = {}
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            p = Path(dirpath) / fn
            snap[str(p.relative_to(root))] = (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
    return snap


def test_inventory_and_scan_do_not_mutate_the_workspace(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-a"])
    before = _snapshot(workspace)
    run_ws(workspace, baseline, ["svc-a"])
    assert _snapshot(workspace) == before


# --- pilot rail integrity ---------------------------------------------------


def test_pilot_rail_passes_against_its_own_baseline(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-a"])
    rep = run_ws(workspace, baseline, ["svc-a"])
    assert rep["pilot_rail_integrity"]["status"] == "PASS"
    assert rep["pilot_rail_integrity"]["counts"]["new"] == 0
    assert rep["pilot_rail_integrity"]["counts"]["regressed"] == 0


def test_new_pilot_rail_defect_fails_integrity_and_stops_expansion(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-a"])
    (workspace / "svc-a" / "app" / "z.py").write_text(
        'import os\nK = os.getenv("NEW_API_TOKEN", "another-literal")\n', encoding="utf-8")
    rep = run_ws(workspace, baseline, ["svc-a"])
    pr = rep["pilot_rail_integrity"]
    assert pr["status"] == "FAIL"
    assert len(pr["new_production_reachable_defects_p0_p1_class"]) == 1
    assert "aggregate" not in rep and rep["expansion_analysis"].startswith("SKIPPED")
    assert "another-literal" not in json.dumps(rep)


def test_missing_pinned_path_or_bad_baseline_is_indeterminate_not_pass(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-a"])
    assert run_ws(workspace, baseline, ["svc-a", "nope"])["pilot_rail_integrity"]["status"] == "INDETERMINATE"
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    assert run_ws(workspace, bad, ["svc-a"])["pilot_rail_integrity"]["status"] == "INDETERMINATE"


def test_baseline_file_is_never_modified(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-a"])
    h = hashlib.sha256(baseline.read_bytes()).hexdigest()
    run_ws(workspace, baseline, ["svc-a"])
    assert hashlib.sha256(baseline.read_bytes()).hexdigest() == h


# --- findings / report guarantees ------------------------------------------


def test_workspace_findings_equal_raw_scanner_findings_no_filtering(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-a"])
    rep = run_ws(workspace, baseline, ["svc-a"])
    raw = ss.ScanResult()
    ss.scan_repo(workspace / "svc-a", raw)
    ss.scan_repo(workspace / "svc-b", raw)
    assert sorted(f.identity for f in raw.findings) == sorted(r["identity"] for r in rep["findings"])
    assert rep["aggregate"]["total_findings"] == len(raw.findings)


def test_report_never_contains_literal_credential_values(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-b"])
    rep = run_ws(workspace, baseline, ["svc-b"])
    text = json.dumps(rep) + ws.render_md(rep)
    assert LITERAL not in text
    assert any(r["evidence"] == "SVC_API_SECRET" for r in rep["findings"])


def test_non_pilot_findings_are_unbaselined_never_new(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-b"])
    rep = run_ws(workspace, baseline, ["svc-b"])
    a = [r for r in rep["findings"] if r["repo"] == "org/svc-a"]
    assert a and all(r["baseline_status"] == "unbaselined-repository" for r in a)


def test_every_finding_is_severity_unclassified(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-b"])
    rep = run_ws(workspace, baseline, ["svc-b"])
    assert {r["severity"] for r in rep["findings"]} == {"UNCLASSIFIED"}
    assert rep["aggregate"]["severity_assigned_by_v1"]["P0"] == 0


def test_report_is_byte_deterministic(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-b"])
    a = json.dumps(run_ws(workspace, baseline, ["svc-b"]), sort_keys=True)
    b = json.dumps(run_ws(workspace, baseline, ["svc-b"]), sort_keys=True)
    assert a == b


def test_coverage_reports_silently_skipped_files(tmp_path):
    root = tmp_path / "ws"
    make_repo(root / "r", "https://github.com/o/r.git", {"ok.py": "x = 1\n", "bad.py": "def (:\n"})
    unique = ws.build_inventory(root)["unique_repositories"]
    _f, cov = ws.scan_unique(root, unique)
    c = cov["o/r"]
    assert c["py_files_syntax_error_silently_skipped"] == 1
    assert c["py_files_parsed"] == 1


# --- queue rules ------------------------------------------------------------


@pytest.mark.parametrize("args,expected", [
    (("HARDCODED_FALLBACK", "production-reachable", "production/runtime", "app/k.py", "VALIDATOR_PRIVATE_KEY"), "A"),
    (("HARDCODED_FALLBACK", "production-reachable", "sdk/library", "src/c.py", "SVC_HMAC_SECRET"), "B"),
    (("COMPARE_DIGEST_STR_RISK", "production-reachable", "production/runtime", "app/s.py", "x"), "B"),
    (("CREDENTIAL_READ", "production-reachable", "production/runtime", "app/s.py", "SVC_KEY"), "C"),
    (("ROUTE_NO_AUTH_DEPENDENCY", "production-reachable", "production/runtime", "app/r.py", "GET /x"), "D"),
    (("HARDCODED_FALLBACK", "production-reachable", "production/runtime", "scripts/seed.py", "ADMIN_PASSWORD"), "D"),
    (("HARDCODED_FALLBACK", "production-reachable", "production/runtime", "app/c.py", "ACCESS_TOKEN_EXPIRE_MINUTES"), "D"),
    (("HARDCODED_FALLBACK", "production-reachable", "frontend/client", "app/c.py", "SVC_SECRET"), "D"),
    (("HARDCODED_FALLBACK", "test-fixture", "production/runtime", "tests/t.py", "SVC_SECRET"), "E"),
    (("HARDCODED_FALLBACK", "production-reachable", "test/demo/archive", "app/c.py", "SVC_SECRET"), "E"),
    (("HARDCODED_FALLBACK", "production-reachable", "production/runtime", "app/sdk_http.py", "SVC_SECRET"), "E"),
])
def test_queue_assignment(args, expected):
    assert ws.queue_for(*args)[0] == expected


def test_main_exit_codes(workspace, tmp_path):
    baseline = make_baseline(tmp_path, [workspace / "svc-a"])
    common = ["--workspace", str(workspace), "--baseline", str(baseline), "--pilot-rail-path", "svc-a"]
    assert ws.main(common + ["--json", str(tmp_path / "o.json"), "--md", str(tmp_path / "o.md")]) == 0
    (workspace / "svc-a" / "app" / "z.py").write_text('import os\nK = os.getenv("N_TOKEN", "lit")\n')
    assert ws.main(common + ["--json", str(tmp_path / "o2.json"), "--md", str(tmp_path / "o2.md")]) == 3
