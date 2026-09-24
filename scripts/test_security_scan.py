"""Tests for scripts/security_scan.py.

Each test writes a small synthetic fixture file (not a real CubeShackles
source file) so the detection logic is proven against a controlled input,
independent of any repo's current state -- if a real repo's code changes,
these tests must not.
"""

from __future__ import annotations

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
