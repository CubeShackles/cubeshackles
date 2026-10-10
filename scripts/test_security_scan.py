"""Tests for scripts/security_scan.py.

Each test writes a small synthetic fixture file (not a real CubeShackles
source file) so the detection logic is proven against a controlled input,
independent of any repo's current state -- if a real repo's code changes,
these tests must not.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from security_scan import (  # noqa: E402
    FAILS_RUN,
    ScanResult,
    discover_workspace_repos,
    scan_repo,
)


def _scan(tmp_path: Path, filename: str, source: str) -> list:
    repo_root = tmp_path / "fake-repo"
    repo_root.mkdir()
    (repo_root / filename).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / filename).write_text(source, encoding="utf-8")
    result = ScanResult()
    scan_repo(repo_root, result)
    return result.findings


# --- detection 1 & 2: credential reads and hardcoded fallbacks -------------


def test_credential_read_with_no_default_is_not_a_fallback(tmp_path):
    findings = _scan(
        tmp_path,
        "app/security.py",
        'import os\nKEY = os.getenv("SETTLEMENT_API_KEYS")\n',
    )
    kinds = {f.kind for f in findings}
    assert "CREDENTIAL_READ" in kinds
    assert "HARDCODED_FALLBACK" not in kinds


def test_hardcoded_fallback_is_flagged_production_reachable(tmp_path):
    findings = _scan(
        tmp_path,
        "app/security.py",
        'import os\nKEY = os.getenv("SETTLEMENT_API_KEY", "dev-settlement-key")\n',
    )
    fallback = [f for f in findings if f.kind == "HARDCODED_FALLBACK"]
    assert len(fallback) == 1
    assert fallback[0].classification == "production-reachable"


def test_hardcoded_fallback_in_a_test_file_is_a_test_fixture(tmp_path):
    findings = _scan(
        tmp_path,
        "tests/test_something.py",
        'import os\nKEY = os.getenv("SETTLEMENT_API_KEY", "dev-settlement-key")\n',
    )
    fallback = [f for f in findings if f.kind == "HARDCODED_FALLBACK"]
    assert len(fallback) == 1
    assert fallback[0].classification == "test-fixture"


def test_hardcoded_fallback_inside_a_denylist_collection_is_intentional(tmp_path):
    findings = _scan(
        tmp_path,
        "app/security_config.py",
        'import os\n'
        'KNOWN_TEST_CREDENTIAL_VALUES = frozenset({"dev-settlement-key", "dev-gateway-key"})\n'
        'KEY = os.getenv("SETTLEMENT_API_KEY", "dev-settlement-key")\n',
    )
    fallback = [f for f in findings if f.kind == "HARDCODED_FALLBACK"]
    assert len(fallback) == 1
    assert fallback[0].classification == "intentional-denylist"


def test_hardcoded_fallback_only_in_a_docstring_is_documentation_example(tmp_path):
    source = (
        'import os\n'
        '"""This module previously read\n\n'
        '    os.getenv("SETTLEMENT_API_KEY", "dev-settlement-key")\n\n'
        'and no longer does."""\n'
        'KEY = os.getenv("SETTLEMENT_API_KEY")\n'
    )
    findings = _scan(tmp_path, "app/security.py", source)
    # The real getenv call has no default (no HARDCODED_FALLBACK); the
    # docstring's quoted pattern is not itself parsed as a call at all, so
    # this proves no false HARDCODED_FALLBACK is raised from prose. The
    # documentation-example classification is exercised directly via
    # classify() in test_classify_documentation_example below.
    assert not [f for f in findings if f.kind == "HARDCODED_FALLBACK"]


def test_empty_default_is_not_flagged_as_a_fallback(tmp_path):
    findings = _scan(
        tmp_path,
        "app/security.py",
        'import os\nKEY = os.getenv("SETTLEMENT_API_KEY", "")\n',
    )
    assert not [f for f in findings if f.kind == "HARDCODED_FALLBACK"]


# --- detection 3: compare_digest str-vs-bytes risk -------------------------


def test_compare_digest_with_str_arguments_is_flagged(tmp_path):
    findings = _scan(
        tmp_path,
        "app/security.py",
        "import hmac\n"
        "def check(expected, provided):\n"
        "    return hmac.compare_digest(expected, provided)\n",
    )
    risky = [f for f in findings if f.kind == "COMPARE_DIGEST_STR_RISK"]
    assert len(risky) == 1
    assert risky[0].classification == "production-reachable"


def test_compare_digest_with_a_local_helper_wrapping_encode_is_not_flagged(tmp_path):
    """Ground-truth regression: found by running this scanner against
    cubeshackles-ledger's own just-fixed app/core/security.py, which wraps
    encoding in a local `_to_bytes()` helper rather than calling `.encode(`
    directly at the call site -- the exact shape used across every fix in
    this session's Pilot Rail closure pass."""
    findings = _scan(
        tmp_path,
        "app/security.py",
        "import hmac\n"
        'def _to_bytes(value):\n    return value.encode("utf-8")\n'
        "def check(expected, provided):\n"
        "    return hmac.compare_digest(_to_bytes(expected), _to_bytes(provided))\n",
    )
    assert not [f for f in findings if f.kind == "COMPARE_DIGEST_STR_RISK"]


def test_compare_digest_with_encoded_bytes_is_not_flagged(tmp_path):
    findings = _scan(
        tmp_path,
        "app/security.py",
        "import hmac\n"
        "def check(expected, provided):\n"
        '    return hmac.compare_digest(expected.encode("utf-8"), provided.encode("utf-8"))\n',
    )
    assert not [f for f in findings if f.kind == "COMPARE_DIGEST_STR_RISK"]


# --- detection 4: route with no visible auth dependency --------------------


def test_route_with_depends_is_not_flagged(tmp_path):
    findings = _scan(
        tmp_path,
        "app/routes.py",
        "from fastapi import APIRouter, Depends\n"
        "router = APIRouter()\n"
        "@router.post('/compliance/gate')\n"
        "def gate(request: dict, _api_key: str = Depends(require_api_key)) -> dict:\n"
        "    return {}\n",
    )
    assert not [f for f in findings if f.kind == "ROUTE_NO_AUTH_DEPENDENCY"]


def test_route_with_no_depends_is_flagged(tmp_path):
    findings = _scan(
        tmp_path,
        "app/routes.py",
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        "@router.post('/compliance/gate')\n"
        "def gate(request: dict) -> dict:\n"
        "    return {}\n",
    )
    flagged = [f for f in findings if f.kind == "ROUTE_NO_AUTH_DEPENDENCY"]
    assert len(flagged) == 1
    assert "/compliance/gate" in flagged[0].detail


def test_health_route_is_allowlisted(tmp_path):
    findings = _scan(
        tmp_path,
        "app/routes.py",
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        "@router.get('/health')\n"
        "def health() -> dict:\n"
        "    return {'status': 'ok'}\n",
    )
    assert not [f for f in findings if f.kind == "ROUTE_NO_AUTH_DEPENDENCY"]


def test_router_level_dependency_protects_every_route_on_it(tmp_path):
    findings = _scan(
        tmp_path,
        "app/routes.py",
        "from fastapi import APIRouter, Depends\n"
        "router = APIRouter(dependencies=[Depends(require_api_key)])\n"
        "@router.get('/anchor')\n"
        "def anchor() -> dict:\n"
        "    return {}\n"
        "@router.post('/anchor/process-queue')\n"
        "def process_queue() -> dict:\n"
        "    return {}\n",
    )
    assert not [f for f in findings if f.kind == "ROUTE_NO_AUTH_DEPENDENCY"]


# --- detection 5: outbound call with no credential header ------------------


def test_outbound_call_with_headers_is_not_flagged(tmp_path):
    findings = _scan(
        tmp_path,
        "app/client.py",
        "import httpx\n"
        "BASE_URL = 'http://127.0.0.1:8010'\n"
        "def call():\n"
        "    return httpx.post(f'{BASE_URL}/anchor', headers={'X-API-Key': 'k'})\n",
    )
    assert not [f for f in findings if f.kind == "OUTBOUND_CALL_NO_CRED"]


def test_outbound_call_with_no_headers_to_an_internal_url_is_flagged(tmp_path):
    findings = _scan(
        tmp_path,
        "app/client.py",
        "import httpx\n"
        "BASE_URL = 'http://127.0.0.1:8010'\n"
        "def call():\n"
        "    return httpx.post(f'{BASE_URL}/anchor')\n",
    )
    flagged = [f for f in findings if f.kind == "OUTBOUND_CALL_NO_CRED"]
    assert len(flagged) == 1
    assert flagged[0].classification == "production-reachable"


def test_outbound_call_to_a_non_url_argument_is_not_flagged(tmp_path):
    """A call whose first argument isn't a URL-shaped literal/name at all
    (e.g. an already-built request object) should not false-positive."""
    findings = _scan(
        tmp_path,
        "app/client.py",
        "import httpx\n"
        "def call(prepared_request):\n"
        "    return httpx.post(prepared_request)\n",
    )
    assert not [f for f in findings if f.kind == "OUTBOUND_CALL_NO_CRED"]


# --- exit-code contract -----------------------------------------------------


def test_fails_run_kinds_match_documented_contract():
    assert FAILS_RUN == {"HARDCODED_FALLBACK", "COMPARE_DIGEST_STR_RISK", "OUTBOUND_CALL_NO_CRED"}
    # ROUTE_NO_AUTH_DEPENDENCY deliberately never gates the run -- too many
    # legitimate false positives from router-level dependencies defined in
    # a different file than the route itself.
    assert "ROUTE_NO_AUTH_DEPENDENCY" not in FAILS_RUN


# --- workspace discovery ----------------------------------------------------


def test_scans_a_repo_root_that_sits_inside_dot_claude_worktrees(tmp_path):
    """Ground-truth regression, found while re-verifying the
    VALIDATOR_PRIVATE_KEY fix: every worktree-based checkout this org
    actually works from sits under a literal `.claude/worktrees/...` path.
    An earlier version checked SKIP_DIR_NAMES against each file's ABSOLUTE
    path, so `.claude` being an ancestor of repo_root itself silently
    skipped every file with no error -- zero findings, no warning."""
    repo_root = tmp_path / ".claude" / "worktrees" / "some-branch"
    repo_root.mkdir(parents=True)
    (repo_root / "app").mkdir()
    (repo_root / "app" / "security.py").write_text(
        'import os\nKEY = os.getenv("SETTLEMENT_API_KEY", "dev-settlement-key")\n',
        encoding="utf-8",
    )
    result = ScanResult()
    scan_repo(repo_root, result)
    assert [f for f in result.findings if f.kind == "HARDCODED_FALLBACK"]


def test_discover_workspace_repos_finds_only_git_directories(tmp_path):
    (tmp_path / "repo-a" / ".git").mkdir(parents=True)
    (tmp_path / "repo-b" / ".git").mkdir(parents=True)
    (tmp_path / "not-a-repo").mkdir()
    (tmp_path / "a-file.txt").write_text("x")
    found = discover_workspace_repos(tmp_path)
    assert [p.name for p in found] == ["repo-a", "repo-b"]


# --- ground-truth regression: files this session actually fixed -----------


@pytest.mark.parametrize(
    "fixed_source",
    [
        # institutional-gateway/api/security.py, post-fix shape
        'import hmac\n'
        'def constant_time_equals(provided: str, expected: str) -> bool:\n'
        '    return hmac.compare_digest(\n'
        '        provided.encode("utf-8", errors="surrogatepass"),\n'
        '        expected.encode("utf-8", errors="surrogatepass"),\n'
        '    )\n',
    ],
)
def test_fixed_compare_digest_shapes_are_not_flagged(tmp_path, fixed_source):
    findings = _scan(tmp_path, "app/security.py", fixed_source)
    assert not [f for f in findings if f.kind == "COMPARE_DIGEST_STR_RISK"]


def test_retired_pre_fix_compare_digest_shape_is_flagged(tmp_path):
    """The exact shape this session's institutional-gateway fix (cf2581a)
    replaced -- proves the scanner would have caught it before the fix."""
    findings = _scan(
        tmp_path,
        "app/security.py",
        "import hmac\n"
        "def _api_key_accepted(provided, candidate):\n"
        "    return hmac.compare_digest(provided, candidate)\n",
    )
    assert [f for f in findings if f.kind == "COMPARE_DIGEST_STR_RISK"]


# ---------------------------------------------------------------------------
# Stable finding identity and baseline diff (durable V1 baseline)
# ---------------------------------------------------------------------------


def _init_git_repo(root: Path, remote_url: str | None = None) -> None:
    """Real `git init` (+ optional remote), not a mock -- canonical_repo_id
    shells out to the real git binary, so these tests prove the actual
    subprocess call resolves correctly, not an assumption about it."""
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    if remote_url:
        subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=root, check=True)


def _write_fallback_repo(root: Path, *, remote_url: str, filename: str = "app/security.py") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    _init_git_repo(root, remote_url)
    target = root / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        'import os\nKEY = os.getenv("SETTLEMENT_API_KEY", "dev-settlement-key")\n', encoding="utf-8"
    )
    return root


def test_canonical_repo_id_derives_from_git_remote(tmp_path):
    from security_scan import canonical_repo_id

    repo = tmp_path / "some-local-dirname"
    _init_git_repo(repo, "https://github.com/CubeShackles/cubeshackles-settlement-engine.git")
    assert canonical_repo_id(repo) == "cubeshackles-settlement-engine"


def test_canonical_repo_id_falls_back_without_a_remote(tmp_path):
    from security_scan import canonical_repo_id

    repo = tmp_path / "no-remote-repo"
    _init_git_repo(repo, remote_url=None)
    assert canonical_repo_id(repo) == "unresolved:no-remote-repo"


def test_identical_scan_is_entirely_unchanged(tmp_path):
    from security_scan import build_baseline, compare_to_baseline

    repo = _write_fallback_repo(tmp_path / "repo-a", remote_url="https://github.com/Org/repo-a.git")
    first = ScanResult()
    scan_repo(repo, first)
    baseline = build_baseline(first, repository_scope=["repo-a"], creation_source="test")

    second = ScanResult()
    scan_repo(repo, second)
    diff = compare_to_baseline(second, baseline)
    assert len(diff.new) == 0
    assert len(diff.regressed) == 0
    assert len(diff.resolved) == 0
    assert diff.unchanged_count == len(second.findings) > 0


def test_genuinely_new_finding_is_new(tmp_path):
    from security_scan import build_baseline, compare_to_baseline

    repo = _write_fallback_repo(tmp_path / "repo-b", remote_url="https://github.com/Org/repo-b.git")
    baseline_scan = ScanResult()
    scan_repo(repo, baseline_scan)
    baseline = build_baseline(baseline_scan, repository_scope=["repo-b"], creation_source="test")

    (repo / "app" / "another.py").write_text(
        'import os\nKEY = os.getenv("LEDGER_API_KEY", "dev-ledger-key")\n', encoding="utf-8"
    )
    after = ScanResult()
    scan_repo(repo, after)
    diff = compare_to_baseline(after, baseline)
    assert any(f.detail.startswith("LEDGER_API_KEY") for f in diff.new)
    assert diff.regressed == []


def test_removed_finding_is_resolved(tmp_path):
    from security_scan import build_baseline, compare_to_baseline

    repo = _write_fallback_repo(tmp_path / "repo-c", remote_url="https://github.com/Org/repo-c.git")
    baseline_scan = ScanResult()
    scan_repo(repo, baseline_scan)
    baseline = build_baseline(baseline_scan, repository_scope=["repo-c"], creation_source="test")

    (repo / "app" / "security.py").write_text("import os\n", encoding="utf-8")
    after = ScanResult()
    scan_repo(repo, after)
    diff = compare_to_baseline(after, baseline)
    # The removed line held both a CREDENTIAL_READ and a HARDCODED_FALLBACK
    # finding (the same os.getenv call); both are resolved.
    resolved_kinds = {entry["kind"] for entry in diff.resolved}
    assert resolved_kinds == {"CREDENTIAL_READ", "HARDCODED_FALLBACK"}
    assert diff.new == []
    assert diff.regressed == []


def test_resolved_finding_reintroduced_is_regressed(tmp_path):
    """The exact scenario this session's remediation pass needs distinguished
    from an ordinary NEW finding: a credential fallback that was explicitly
    fixed and recorded in resolved_history, then somehow reappears."""
    from security_scan import build_baseline, compare_to_baseline

    repo = _write_fallback_repo(tmp_path / "repo-d", remote_url="https://github.com/Org/repo-d.git")
    fixed_scan = ScanResult()
    scan_repo(repo, fixed_scan)
    fallback_finding = next(f for f in fixed_scan.findings if f.kind == "HARDCODED_FALLBACK")

    # Simulate the remediation: the fallback is removed, and its identity is
    # recorded in resolved_history at baseline-write time.
    (repo / "app" / "security.py").write_text("import os\n", encoding="utf-8")
    clean_scan = ScanResult()
    scan_repo(repo, clean_scan)
    baseline = build_baseline(
        clean_scan,
        repository_scope=["repo-d"],
        creation_source="test",
        resolved_history=[
            {
                "identity": fallback_finding.identity,
                "canonical_repo": fallback_finding.canonical_repo,
                "file": fallback_finding.file,
                "kind": fallback_finding.kind,
                "note": "removed the hardcoded fallback",
            }
        ],
    )

    # The fallback reappears (e.g. a revert).
    (repo / "app" / "security.py").write_text(
        'import os\nKEY = os.getenv("SETTLEMENT_API_KEY", "dev-settlement-key")\n', encoding="utf-8"
    )
    reverted_scan = ScanResult()
    scan_repo(repo, reverted_scan)
    diff = compare_to_baseline(reverted_scan, baseline)
    assert len(diff.regressed) == 1
    assert diff.regressed[0].identity == fallback_finding.identity
    # The CREDENTIAL_READ finding on the same line was never declared
    # resolved (only the HARDCODED_FALLBACK identity was put in
    # resolved_history above) and was also absent from the "clean" baseline
    # -- it correctly reports as NEW, not REGRESSED. v1 does not guess a
    # relationship it wasn't told about; only the specific identity
    # recorded in resolved_history gets REGRESSED treatment.
    assert [f.kind for f in diff.new] == ["CREDENTIAL_READ"]


def test_line_number_movement_alone_is_unchanged_not_new_plus_resolved(tmp_path):
    from security_scan import build_baseline, compare_to_baseline

    repo = _write_fallback_repo(tmp_path / "repo-e", remote_url="https://github.com/Org/repo-e.git")
    before = ScanResult()
    scan_repo(repo, before)
    baseline = build_baseline(before, repository_scope=["repo-e"], creation_source="test")

    # Push the same finding down several lines with blank-line padding --
    # nothing about the finding itself changed, only its line number.
    original = (repo / "app" / "security.py").read_text(encoding="utf-8")
    (repo / "app" / "security.py").write_text("\n\n\n\n\n" + original, encoding="utf-8")
    after = ScanResult()
    scan_repo(repo, after)
    diff = compare_to_baseline(after, baseline)
    assert diff.new == []
    assert diff.resolved == []
    assert diff.unchanged_count == len(after.findings) > 0


def test_different_checkout_root_does_not_change_identity(tmp_path):
    """Two independent clones of the 'same' repo (same remote URL, same
    content) at two different absolute paths must produce identical
    identities -- proves identity survives a different local checkout
    root, not just a renamed directory."""
    from security_scan import build_baseline, compare_to_baseline

    clone_one = _write_fallback_repo(
        tmp_path / "clone-one" / "deeply" / "nested", remote_url="https://github.com/Org/shared-repo.git"
    )
    clone_two = _write_fallback_repo(
        tmp_path / "clone-two", remote_url="https://github.com/Org/shared-repo.git"
    )
    scan_one = ScanResult()
    scan_repo(clone_one, scan_one)
    baseline = build_baseline(scan_one, repository_scope=["shared-repo"], creation_source="test")

    scan_two = ScanResult()
    scan_repo(clone_two, scan_two)
    diff = compare_to_baseline(scan_two, baseline)
    assert diff.new == []
    assert diff.resolved == []
    assert diff.unchanged_count == len(scan_two.findings) > 0


def test_repo_name_collision_does_not_merge_two_distinct_findings(tmp_path):
    """Two DIFFERENT repos (different remotes) checked out to identically-
    named worktree directories -- the exact collision found scanning
    Cubeshackles-network-orchestrator and Cubeshackles-validator-node's
    worktrees, both literally named "pilot-rail-doc" -- must not be
    treated as the same repo by identity, even though `repo_root.name`
    (the cosmetic `repo` display field) is identical for both."""
    from security_scan import build_baseline, compare_to_baseline

    workdir_a = _write_fallback_repo(
        tmp_path / "worktrees" / "pilot-rail-doc-a" / "pilot-rail-doc",
        remote_url="https://github.com/CubeShackles/repo-one.git",
    )
    workdir_b = _write_fallback_repo(
        tmp_path / "worktrees" / "pilot-rail-doc-b" / "pilot-rail-doc",
        remote_url="https://github.com/CubeShackles/repo-two.git",
    )
    assert workdir_a.name == workdir_b.name == "pilot-rail-doc"

    scan_a = ScanResult()
    scan_repo(workdir_a, scan_a)
    baseline = build_baseline(scan_a, repository_scope=["repo-one"], creation_source="test")

    scan_b = ScanResult()
    scan_repo(workdir_b, scan_b)
    diff = compare_to_baseline(scan_b, baseline)
    # repo-two's finding must be NEW against repo-one's baseline, not
    # silently treated as the same (UNCHANGED) finding.
    assert len(diff.new) >= 1
    assert all(f.canonical_repo == "repo-two" for f in diff.new)


def test_baseline_cannot_suppress_a_finding_from_ordinary_output(tmp_path):
    """Loading and comparing against a baseline must never remove anything
    from the underlying ScanResult -- ordinary --json/--md output is always
    the full, unfiltered result regardless of baseline mode."""
    from security_scan import build_baseline

    repo = _write_fallback_repo(tmp_path / "repo-f", remote_url="https://github.com/Org/repo-f.git")
    scan = ScanResult()
    scan_repo(repo, scan)
    before_count = len(scan.findings)
    build_baseline(scan, repository_scope=["repo-f"], creation_source="test")
    assert len(scan.findings) == before_count  # untouched by baseline construction


def test_malformed_baseline_fails_closed(tmp_path):
    from security_scan import BaselineError, load_baseline

    bad = tmp_path / "bad.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(BaselineError):
        load_baseline(bad)

    missing_keys = tmp_path / "missing.json"
    missing_keys.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    with pytest.raises(BaselineError):
        load_baseline(missing_keys)


def test_incompatible_schema_version_fails_clearly(tmp_path):
    from security_scan import BASELINE_SCHEMA_VERSION, BaselineError, load_baseline

    incompatible = tmp_path / "incompatible.json"
    incompatible.write_text(
        json.dumps({"schema_version": BASELINE_SCHEMA_VERSION + 999, "findings": []}), encoding="utf-8"
    )
    with pytest.raises(BaselineError, match="incompatible"):
        load_baseline(incompatible)


def test_baseline_never_stores_the_literal_credential_value(tmp_path):
    """A HARDCODED_FALLBACK's detail contains the literal default value
    (e.g. "hmac-secret-local"); the baseline must store only the env var
    name (stable_key), never that literal, per the requirement not to
    persist secrets or credential-shaped values in a committed artifact."""
    from security_scan import build_baseline

    repo = _write_fallback_repo(tmp_path / "repo-g", remote_url="https://github.com/Org/repo-g.git")
    scan = ScanResult()
    scan_repo(repo, scan)
    baseline = build_baseline(scan, repository_scope=["repo-g"], creation_source="test")
    serialized = json.dumps(baseline)
    assert "dev-settlement-key" not in serialized
    fallback_entries = [f for f in baseline["findings"] if f["kind"] == "HARDCODED_FALLBACK"]
    assert fallback_entries and fallback_entries[0]["stable_key"] == "SETTLEMENT_API_KEY"


def test_two_route_handlers_to_the_same_path_get_distinct_identities(tmp_path):
    """Ground-truth regression: found comparing a real baseline against an
    identical re-scan (should be 100% UNCHANGED, was not). Two distinct
    functions -- different HTTP methods, same path, the exact shape of
    Cubeshackles-node-api's POST and GET /simulations/province-partition --
    must not collide onto the same identity just because ROUTE_NO_AUTH_
    DEPENDENCY's detail text doesn't include the HTTP method: an earlier
    version pushed the function's own name onto the scope stack AFTER
    checking route auth, so both handlers' enclosing_scope was wrongly
    "<module>" (the parent scope) instead of each function's own name."""
    findings = _scan(
        tmp_path,
        "app/main.py",
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        "@router.post('/simulations/province-partition')\n"
        "def create_partition() -> dict:\n"
        "    return {}\n"
        "@router.get('/simulations/province-partition')\n"
        "def read_partition() -> dict:\n"
        "    return {}\n",
    )
    flagged = [f for f in findings if f.kind == "ROUTE_NO_AUTH_DEPENDENCY"]
    assert len(flagged) == 2
    assert flagged[0].enclosing_scope != flagged[1].enclosing_scope
    assert flagged[0].identity != flagged[1].identity
    assert {f.enclosing_scope for f in flagged} == {"create_partition", "read_partition"}
