#!/usr/bin/env python3
"""Security Invariant Scanner V1 -- workspace-wide OBSERVATION pass.

Inventories every candidate directory under a workspace root, resolves
canonical repository identity, detects duplicate checkouts/worktrees,
runs the UNCHANGED scanner-V1 detectors read-only against every
supported (Python) unique repository, and produces a deterministic
JSON + Markdown report. It also re-checks the frozen Pilot Rail baseline.

This module changes NO detector semantics: findings come from
`security_scan.scan_repo` exactly as-is. It only enumerates, classifies
repositories, aggregates, and reports.

Guarantees / non-guarantees
  * Read-only: only `git config/rev-parse/symbolic-ref/status` are run
    (`--no-optional-locks`); nothing under the workspace is written.
  * Never stores literal credential values: findings are serialised with
    `stable_detail_key` (env var name only) for credential kinds.
  * V1 assigns NO severity (P0-P3). Every finding is reported severity
    UNCLASSIFIED. Remediation queues are a deterministic, rule-based
    triage of kind + classification + repository category; queue A/B
    membership is "strong static evidence", NOT a human-verified P0/P1.
  * "Scanned, no V1 findings" is NOT "secure". Unsupported languages,
    config formats and cross-repo edges are quantified in `coverage`.
  * The report contains no timestamps, so two runs over an unchanged
    workspace are byte-identical.

Usage
  python3 security_workspace_scan.py --workspace <root> \
      --baseline <pilot-rail baseline.json> \
      --pilot-rail-path <relpath> [... x10] \
      --json out.json --md out.md
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import security_scan as ss  # noqa: E402

REPORT_SCHEMA_VERSION = 1

# Directories pruned when censusing languages (superset of the scanner's own
# SKIP_DIR_NAMES: generated/vendored trees must not inflate language counts).
CENSUS_PRUNE = ss.SKIP_DIR_NAMES | {
    ".next", ".open-next", "dist", "build", "target", ".tox", ".mypy_cache",
    ".pytest_cache", "vendor", ".wrangler", "coverage", ".turbo", ".cache",
}
# Path segments that suggest generated/vendored code the scanner nevertheless
# DOES scan (they are not in SKIP_DIR_NAMES) -- quantified as a blind spot.
GENERATED_SEGMENTS = {"build", "dist", "vendor", ".next", "third_party", "generated", "gen", "target"}

LANG_BY_EXT = {
    ".py": "python", ".ts": "typescript", ".tsx": "typescript", ".js": "javascript",
    ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript", ".rs": "rust",
    ".go": "go", ".sol": "solidity", ".swift": "swift", ".kt": "kotlin", ".java": "java",
    ".dart": "dart", ".sh": "shell", ".rb": "ruby", ".c": "c", ".cpp": "c++", ".cs": "c#",
}
CONFIG_EXT = {".yml": "yaml", ".yaml": "yaml", ".toml": "toml", ".json": "json", ".tf": "terraform",
              ".ini": "ini", ".cfg": "ini", ".env": "dotenv"}
CONFIG_NAMES = {"Dockerfile": "dockerfile", "docker-compose.yml": "docker-compose", "docker-compose.yaml": "docker-compose"}
DOC_EXT = {".md", ".mdx", ".rst", ".txt"}

SUPPORTED_LANGUAGES = ("python",)

# Reasons a candidate is not scanned (spec vocabulary).
NOT_SCANNED_REASONS = (
    "UNSUPPORTED_LANGUAGE", "UNRESOLVED_REPO_IDENTITY", "BROKEN_GIT_STATE", "INACCESSIBLE",
    "EMPTY_REPOSITORY", "ARCHIVED_OR_NON_RUNTIME", "OTHER",
)

PRODUCTION_CATEGORIES = {"production/runtime", "sdk/library"}
NON_RUNTIME_CATEGORIES = {"test/demo/archive", "governance/tooling", "documentation"}

KEY_MATERIAL_NAME = re.compile(r"(PRIVATE_KEY|SIGNING_KEY|SIGNER_KEY|SIGNING_SEED|MNEMONIC|SEED_PHRASE)", re.I)
KNOWN_COMPAT_BASENAMES = {"sdk_http.py"}
# First path segment marking operator/dev tooling rather than a served
# runtime path: findings there need a human, they are not strong-evidence.
TOOLING_TOP_SEGMENTS = {"scripts", "tools", "tooling", "bin", "examples", "example", "seeds", "seed"}
# Names that match the credential-name pattern but denote a duration/limit,
# not a secret (e.g. ACCESS_TOKEN_EXPIRE_MINUTES).
NON_SECRET_SUFFIX = re.compile(r"(_MINUTES|_DAYS|_SECONDS|_HOURS|_TTL|_EXPIRE\w*|_ID)$", re.I)

COMPARE_DIGEST_RE = re.compile(r"\bcompare_digest\s*\(")
HTTP_CALL_RE = re.compile(r"\b(?:httpx|requests)\.(?:get|post|put|patch|delete|request|head|Client|AsyncClient|Session)\b")
OTHER_HTTP_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+(aiohttp|urllib3|urllib\.request|http\.client|grpc|websockets?|pycurl|treq)\b", re.M
)


# --- read-only git ----------------------------------------------------------


def git(path: Path, *args: str, timeout: int = 60) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(path), *args],
            capture_output=True, text=True, timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return 127, ""
    return proc.returncode, proc.stdout.strip()


_REMOTE_RE = re.compile(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$")


def remote_key(url: str) -> str:
    """Canonical owner/name (lowercased) from a remote URL, or ''."""
    m = _REMOTE_RE.search(url.strip())
    return f"{m.group(1)}/{m.group(2)}".lower() if m else ""


# --- language / category census --------------------------------------------


def census(path: Path) -> dict:
    langs: Counter = Counter()
    configs: Counter = Counter()
    docs = 0
    env_files = 0
    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in CENSUS_PRUNE)
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if fn == ".env" or fn.startswith(".env."):
                env_files += 1
                configs["dotenv"] += 1
            elif fn in CONFIG_NAMES:
                configs[CONFIG_NAMES[fn]] += 1
            elif ext in LANG_BY_EXT:
                langs[LANG_BY_EXT[ext]] += 1
            elif ext in CONFIG_EXT:
                configs[CONFIG_EXT[ext]] += 1
            elif ext in DOC_EXT:
                docs += 1
    return {"languages": dict(sorted(langs.items())), "config_files": dict(sorted(configs.items())),
            "doc_files": docs, "dotenv_files": env_files}


def _read_small(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:200_000].lower()
    except OSError:
        return ""


DEMO_KW = ("demo", "sandbox", "chaos", "vegemai", "archive")
INFRA_KW = ("infra", "disaster-recovery", "hardware", "observability", "operations")
DOCS_KW = ("platform-specs", "ontology", "security-framework", "enterprise-brain", ".github", "angola-pilot")
GOV_KW = ("security", "supervision", "integration")
SDK_KW = ("sdk", "contracts", "-ciel", "core")
FRONT_KW = ("web", "storybook", "design-system", "developer-portal", "retail", "wallet", "phone-wedge",
            "transit", "bualabuitu", "terrain", "kulifikila")


def categorize(name: str, path: Path, cen: dict) -> tuple[str, str]:
    """Deterministic heuristic (category, basis). Never authoritative --
    'unknown' is a legitimate answer and lands in the manual queue."""
    n = name.lower()
    langs = cen["languages"]
    manifest = _read_small(path / "requirements.txt") + _read_small(path / "pyproject.toml")
    has_api = any(k in manifest for k in ("fastapi", "flask", "uvicorn", "django", "starlette"))
    has_pkg_json = (path / "package.json").exists()
    if any(k in n for k in DEMO_KW):
        return "test/demo/archive", "name-rule"
    if has_api:
        return "production/runtime", "content-rule:python-web-framework"
    if any(k in n for k in INFRA_KW):
        return "infrastructure/deployment", "name-rule"
    if any(k in n for k in DOCS_KW):
        return "documentation" if not langs.get("python") else "governance/tooling", "name-rule"
    if n == "cubeshackles" or any(k in n for k in GOV_KW):
        return "governance/tooling", "name-rule"
    if has_pkg_json and (langs.get("typescript") or langs.get("javascript")):
        return "frontend/client", "content-rule:package.json"
    if any(k in n for k in FRONT_KW):
        return "frontend/client", "name-rule"
    if any(k in n for k in SDK_KW):
        return "sdk/library", "name-rule"
    if langs.get("python") and not has_pkg_json:
        return "sdk/library", "content-rule:python-no-web-framework"
    if not langs and cen["doc_files"]:
        return "documentation", "content-rule:docs-only"
    return "unknown", "no-rule-matched"


# --- inventory --------------------------------------------------------------


def inspect_candidate(path: Path, root: Path) -> dict:
    rel = os.path.relpath(path, root)
    rec: dict = {"name": path.name, "path": rel, "is_dir": path.is_dir()}
    if not path.exists() or not os.access(path, os.R_OK | os.X_OK):
        rec.update(is_git=False, status="INACCESSIBLE")
        return rec
    gitpath = path / ".git"
    rec["is_git"] = gitpath.exists()
    rec["is_worktree"] = gitpath.is_file()
    if not rec["is_git"]:
        rec["status"] = "NOT_A_GIT_REPOSITORY"
        return rec
    rc, _ = git(path, "rev-parse", "--is-inside-work-tree")
    if rc != 0:
        rec["status"] = "BROKEN_GIT_STATE"
        return rec
    _, url = git(path, "config", "--get", "remote.origin.url")
    rec["remote_origin_present"] = bool(url)
    rec["remote_key"] = remote_key(url)
    rc, branch = git(path, "symbolic-ref", "--short", "-q", "HEAD")
    rec["branch"] = branch if rc == 0 else "(detached)"
    rc, head = git(path, "rev-parse", "--verify", "-q", "HEAD")
    rec["head_sha"] = head if rc == 0 else ""
    _, porcelain = git(path, "status", "--porcelain")
    rec["dirty"] = bool(porcelain)
    rec["dirty_entries"] = len([ln for ln in porcelain.splitlines() if ln.strip()])
    cen = census(path)
    rec.update(cen)
    rec["category"], rec["category_basis"] = categorize(path.name, path, cen)
    rec["supported"] = any(cen["languages"].get(lang) for lang in SUPPORTED_LANGUAGES)
    rec["status"] = "OK"
    return rec


def discover_candidates(root: Path) -> list[Path]:
    """Every immediate child directory (hidden ones included, reported),
    plus each child's `.claude/worktrees/*` checkouts and any path named by
    `git worktree list`, de-duplicated by resolved path."""
    seen: dict[str, Path] = {}

    def add(p: Path) -> None:
        seen.setdefault(str(p.resolve()), p)

    tops = sorted(p for p in root.iterdir() if p.is_dir() and not p.is_symlink())
    for top in tops:
        add(top)
    for top in tops:
        wt_dir = top / ".claude" / "worktrees"
        if wt_dir.is_dir():
            for w in sorted(wt_dir.iterdir()):
                if w.is_dir():
                    add(w)
        if (top / ".git").exists():
            rc, out = git(top, "worktree", "list", "--porcelain")
            if rc == 0:
                for line in out.splitlines():
                    if line.startswith("worktree "):
                        p = Path(line[len("worktree "):])
                        if p.is_dir():
                            add(p)
    return sorted(seen.values(), key=lambda p: os.path.relpath(p, root))


def build_inventory(root: Path) -> dict:
    cands = [inspect_candidate(p, root) for p in discover_candidates(root)]
    by_key: dict[str, list[dict]] = defaultdict(list)
    for c in cands:
        if c.get("status") == "OK" and c.get("remote_key"):
            by_key[c["remote_key"]].append(c)

    def is_top(c: dict) -> bool:
        return "/" not in c["path"] and not c["path"].startswith("..")

    unique: list[dict] = []
    duplicates: list[dict] = []
    primary_of: dict[str, dict] = {}
    for key in sorted(by_key):
        group = sorted(by_key[key], key=lambda c: (not is_top(c), c["is_worktree"], c["path"]))
        primary = group[0]
        primary_of[key] = primary
        for dup in group[1:]:
            duplicates.append({
                "path": dup["path"], "remote_key": key, "duplicate_of": primary["path"],
                "is_worktree": dup["is_worktree"], "branch": dup["branch"], "head_sha": dup["head_sha"],
                "dirty": dup["dirty"], "kind": "worktree" if dup["is_worktree"] else "second-checkout",
            })
    # Repositories with no remote cannot be deduplicated by identity: each is
    # its own UNRESOLVED_REPO_IDENTITY entry (never merged by directory name).
    for c in cands:
        if c.get("status") == "OK" and not c.get("remote_key"):
            primary_of[f"unresolved:{c['path']}"] = c
    for key in sorted(primary_of):
        p = dict(primary_of[key])
        p["repo_key"] = key
        p["duplicate_checkouts"] = sorted(d["path"] for d in duplicates if d["duplicate_of"] == p["path"])
        unique.append(p)

    for u in unique:
        u["scan_status"], u["scan_reason"], u["scan_note"] = decide_scan(u)
    non_repo = [c for c in cands if c.get("status") != "OK"]
    return {
        "candidates_total": len(cands),
        "git_repositories_discovered": sum(1 for c in cands if c.get("status") == "OK"),
        "unique_repositories": unique,
        "duplicate_checkouts": sorted(duplicates, key=lambda d: d["path"]),
        "non_repository_candidates": sorted(non_repo, key=lambda c: c["path"]),
    }


def decide_scan(u: dict) -> tuple[str, str, str]:
    """(scan_status, reason, note). SCANNED includes repos flagged with a
    weak identity -- they are scanned, and the weakness is stated."""
    if not u["head_sha"]:
        return "NOT_SCANNED", "EMPTY_REPOSITORY", "no commit at HEAD"
    if not u["supported"]:
        return "NOT_SCANNED", "UNSUPPORTED_LANGUAGE", "no Python files; V1 inspects Python only"
    note = ""
    if not u.get("remote_key"):
        note = "UNRESOLVED_REPO_IDENTITY: no git remote; scanned, identity falls back to directory name"
    return "SCANNED", "", note


# --- scanning ---------------------------------------------------------------


COVERAGE_KEYS = (
    "py_files_visited", "py_files_parsed", "py_files_skipped_by_scanner_dirs",
    "py_files_unreadable_silently_skipped", "py_files_syntax_error_silently_skipped",
    "py_files_in_generated_or_vendor_like_dirs_but_scanned", "compare_digest_call_sites",
    "outbound_http_call_sites_httpx_requests", "files_using_outbound_libraries_v1_does_not_model",
)


def python_coverage(path: Path) -> dict:
    """Independent pass over exactly the .py files the scanner visits, to
    quantify what it cannot see. Does not influence findings."""
    stats = Counter({k: 0 for k in COVERAGE_KEYS})
    for p in path.rglob("*.py"):
        rel_parts = p.relative_to(path).parts
        if any(part in ss.SKIP_DIR_NAMES for part in rel_parts):
            stats["py_files_skipped_by_scanner_dirs"] += 1
            continue
        stats["py_files_visited"] += 1
        if any(seg in GENERATED_SEGMENTS for seg in rel_parts[:-1]):
            stats["py_files_in_generated_or_vendor_like_dirs_but_scanned"] += 1
        try:
            src = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            stats["py_files_unreadable_silently_skipped"] += 1
            continue
        try:
            ast.parse(src)
        except SyntaxError:
            stats["py_files_syntax_error_silently_skipped"] += 1
            continue
        stats["py_files_parsed"] += 1
        stats["compare_digest_call_sites"] += len(COMPARE_DIGEST_RE.findall(src))
        stats["outbound_http_call_sites_httpx_requests"] += len(HTTP_CALL_RE.findall(src))
        other = OTHER_HTTP_IMPORT_RE.findall(src)
        if other:
            stats["files_using_outbound_libraries_v1_does_not_model"] += 1
    return dict(stats)


def scan_unique(root: Path, unique: list[dict]) -> tuple[list[ss.Finding], dict]:
    findings: list[ss.Finding] = []
    coverage: dict[str, dict] = {}
    for u in unique:
        if u["scan_status"] != "SCANNED":
            continue
        path = (root / u["path"]).resolve()
        res = ss.ScanResult()
        ss.scan_repo(path, res)
        for f in res.findings:
            f.repo = u["repo_key"]
        findings.extend(res.findings)
        coverage[u["repo_key"]] = python_coverage(path)
    return findings, coverage


# --- finding records / queues ----------------------------------------------


def queue_for(kind: str, classification: str, category: str, relpath: str, stable_key: str) -> tuple[str, str]:
    if classification != "production-reachable":
        return "E", f"classification={classification}"
    if category in NON_RUNTIME_CATEGORIES:
        return "E", f"repository category={category}"
    if relpath.rsplit("/", 1)[-1] in KNOWN_COMPAT_BASENAMES:
        return "E", "known legacy compatibility shim (sdk_http.py)"
    if relpath.split("/", 1)[0] in TOOLING_TOP_SEGMENTS and "/" in relpath:
        return "D", "path is operator/dev tooling (scripts/tools/examples); needs manual classification"
    if kind == "HARDCODED_FALLBACK" and NON_SECRET_SUFFIX.search(stable_key):
        return "D", "name denotes a duration/limit/identifier, not necessarily a secret"
    if kind in ("HARDCODED_FALLBACK", "COMPARE_DIGEST_STR_RISK"):
        if category in PRODUCTION_CATEGORIES:
            if kind == "HARDCODED_FALLBACK" and KEY_MATERIAL_NAME.search(stable_key):
                return "A", "AST-proven literal default on key-material credential in production category"
            return "B", f"AST-proven {kind} in production category"
        return "D", f"{kind} in category={category}; production role unclear"
    if kind == "CREDENTIAL_READ":
        return ("C", "credential read without literal default (informational)") if category in PRODUCTION_CATEGORIES \
            else ("D", f"credential read in category={category}")
    return "D", f"{kind} is a heuristic rule with known false positives; needs human confirmation"


QUEUE_DEFS = {
    "A": "strong-static-evidence production-reachable P0 candidate (key-material literal fallback; AST-proven, not human-verified)",
    "B": "strong-static-evidence production-reachable P1 candidate (literal credential fallback / str compare_digest; AST-proven, not human-verified)",
    "C": "production-reachable P2/P3 (credential read without literal default; informational)",
    "D": "requires manual classification",
    "E": "test / demo / governance / documentation / known compatibility pattern",
}
QUEUE_CANDIDATE_SEVERITY = {"A": "P0-candidate", "B": "P1-candidate", "C": "P2/P3-candidate", "D": "unclassified", "E": "non-runtime"}


def finding_record(f: ss.Finding, repo_meta: dict, pilot_keys: set, baseline_ids: set, resolved_ids: set) -> dict:
    stable_key = ss.stable_detail_key(f.kind, f.detail)
    category = repo_meta["category"]
    queue, why = queue_for(f.kind, f.classification, category, f.file, stable_key)
    if f.canonical_repo in pilot_keys:
        if f.identity in baseline_ids:
            baseline_status = "pilot-rail:in-frozen-baseline"
        elif f.identity in resolved_ids:
            baseline_status = "pilot-rail:matches-resolved-history(this checkout lacks the fix)"
        else:
            baseline_status = "pilot-rail:not-in-frozen-baseline(checkout differs from pinned scan)"
    else:
        baseline_status = "unbaselined-repository"
    if f.classification == "test-fixture":
        runtime = "test"
    elif f.classification == "documentation-example":
        runtime = "documentation"
    elif f.classification == "intentional-denylist":
        runtime = "denylist"
    elif category in PRODUCTION_CATEGORIES:
        runtime = "runtime"
    else:
        runtime = "non-runtime-category"
    return {
        "identity": f.identity, "repo": repo_meta["repo_key"], "canonical_repo": f.canonical_repo,
        "repository_category": category, "file": f.file, "line": f.line, "kind": f.kind,
        "classification": f.classification, "runtime_context": runtime,
        "severity": "UNCLASSIFIED", "queue": queue, "queue_rationale": why,
        "confidence": f.confidence, "enclosing_scope": f.enclosing_scope,
        "evidence": stable_key, "baseline_status": baseline_status,
    }


def sort_key(r: dict) -> tuple:
    return (r["repo"], r["file"], r["line"], r["kind"], r["identity"])


# --- pattern analysis -------------------------------------------------------


def patterns(records: list[dict]) -> tuple[list[dict], list[dict]]:
    defs = [
        ("hardcoded credential fallback / credential read with unsafe default", lambda r: r["kind"] == "HARDCODED_FALLBACK"),
        ("credential read (no literal default)", lambda r: r["kind"] == "CREDENTIAL_READ"),
        ("outbound service call without visible credential propagation", lambda r: r["kind"] == "OUTBOUND_CALL_NO_CRED"),
        ("inbound route without visible auth dependency", lambda r: r["kind"] == "ROUTE_NO_AUTH_DEPENDENCY"),
        ("unsafe compare_digest input pattern", lambda r: r["kind"] == "COMPARE_DIGEST_STR_RISK"),
        ("repeated signing/private-key fallback", lambda r: r["kind"] == "HARDCODED_FALLBACK" and bool(KEY_MATERIAL_NAME.search(r["evidence"]))),
        ("legacy compatibility shim (sdk_http.py)", lambda r: r["file"].rsplit("/", 1)[-1] in KNOWN_COMPAT_BASENAMES),
    ]
    out = []
    for name, pred in defs:
        sel = [r for r in records if pred(r)]
        out.append({
            "pattern": name, "occurrences": len(sel), "unique_repositories": len({r["repo"] for r in sel}),
            "by_classification": dict(sorted(Counter(r["classification"] for r in sel).items())),
            "by_runtime_context": dict(sorted(Counter(r["runtime_context"] for r in sel).items())),
            "production_reachable_runtime": sum(1 for r in sel if r["runtime_context"] == "runtime" and r["classification"] == "production-reachable"),
        })
    env = defaultdict(lambda: {"repos": set(), "n": 0, "runtime": 0})
    for r in records:
        if r["kind"] == "HARDCODED_FALLBACK":
            e = env[r["evidence"]]
            e["repos"].add(r["repo"]); e["n"] += 1
            e["runtime"] += r["runtime_context"] == "runtime" and r["classification"] == "production-reachable"
    fallback_by_name = [
        {"credential_name": k, "occurrences": v["n"], "unique_repositories": len(v["repos"]), "production_reachable_runtime": v["runtime"]}
        for k, v in sorted(env.items(), key=lambda kv: (-kv[1]["n"], kv[0]))
    ]
    return out, fallback_by_name


# --- pilot rail integrity ---------------------------------------------------


def pilot_rail_check(root: Path, baseline_path: Path, rel_paths: list[str]) -> dict:
    try:
        baseline = ss.load_baseline(baseline_path)
    except ss.BaselineError as exc:
        return {"status": "INDETERMINATE", "reason": f"baseline unusable: {exc}"}
    res = ss.ScanResult()
    missing = []
    for rel in rel_paths:
        p = (root / rel).resolve()
        if not p.is_dir():
            missing.append(rel)
            continue
        ss.scan_repo(p, res)
    if missing:
        return {"status": "INDETERMINATE", "reason": "pinned Pilot Rail path(s) missing", "missing": sorted(missing)}
    diff = ss.compare_to_baseline(res, baseline)
    defect = lambda f: f.classification == "production-reachable" and f.kind in ss.FAILS_RUN  # noqa: E731
    new_def = [f for f in diff.new if defect(f)]
    reg_def = [f for f in diff.regressed if defect(f)]
    brief = lambda fs: [{"identity": f.identity, "repo": f.canonical_repo, "file": f.file, "kind": f.kind,  # noqa: E731
                         "classification": f.classification} for f in sorted(fs, key=lambda x: (x.canonical_repo, x.file, x.line, x.kind))]
    return {
        "status": "PASS" if not new_def and not reg_def else "FAIL",
        "baseline_path": str(baseline_path.name),
        "baseline_scanner_commit": baseline.get("scanner_commit"),
        "pinned_paths": sorted(rel_paths),
        "counts": {"new": len(diff.new), "unchanged": diff.unchanged_count, "resolved": len(diff.resolved),
                   "regressed": len(diff.regressed)},
        "new_production_reachable_defects_p0_p1_class": brief(new_def),
        "regressed_production_reachable_defects_p0_p1_class": brief(reg_def),
        "new_other": brief([f for f in diff.new if not defect(f)]),
        "regressed_other": brief([f for f in diff.regressed if not defect(f)]),
        "note": "V1 has no P-levels; 'P0/P1-class' = production-reachable finding of a FAILS_RUN kind, the same "
                "definition the frozen baseline's 'production_reachable_defects' used.",
    }


# --- assembly ---------------------------------------------------------------


def blind_spots(unique: list[dict], coverage: dict, findings: list[ss.Finding]) -> dict:
    py_repos = [u for u in unique if u["supported"]]
    lang_totals: Counter = Counter()
    cfg_totals: Counter = Counter()
    for u in unique:
        lang_totals.update(u["languages"])
        cfg_totals.update(u["config_files"])
    cov = Counter()
    for c in coverage.values():
        cov.update(c)
    ids = [f.identity for f in findings]
    return {
        "unsupported_repositories": sorted(u["repo_key"] for u in unique if not u["supported"]),
        "unsupported_repository_count": sum(1 for u in unique if not u["supported"]),
        "non_python_source_files_not_inspected": {k: v for k, v in sorted(lang_totals.items()) if k != "python"},
        "python_source_files": lang_totals.get("python", 0),
        "repos_with_non_python_source_alongside_python": sorted(
            u["repo_key"] for u in py_repos if any(k != "python" for k in u["languages"])),
        "config_formats_not_inspected": dict(sorted(cfg_totals.items())),
        "dotenv_files_present_names_only_not_read": sum(u["dotenv_files"] for u in unique),
        "python_coverage_totals": dict(sorted(cov.items())),
        "identity_collision_exposure": {
            "findings": len(ids), "distinct_identities": len(set(ids)),
            "colliding_findings": len(ids) - len(set(ids)),
        },
        "statements": [
            "Dynamic outbound-call construction (URLs/clients built from config objects, f-strings with no static "
            "literal, factories) is invisible to the AST rules; call sites cannot be enumerated statically. "
            "Measured proxies: outbound_http_call_sites_httpx_requests and files_using_outbound_libraries_v1_does_not_model "
            "(aiohttp/urllib3/http.client/grpc/websockets are not modelled at all).",
            "Cross-repo caller->callee credential propagation is not resolved (no env-var -> base-URL -> owning-repo graph). "
            "V1 flags a call site only if the credential is not visibly attached at that site.",
            "Values reaching compare_digest via intermediate variables are not traced (compare_digest_call_sites vs "
            "COMPARE_DIGEST_STR_RISK findings shows how much is unexamined).",
            "Scanner skips only " + ", ".join(sorted(ss.SKIP_DIR_NAMES)) + "; generated/vendored Python outside those "
            "(build/dist/vendor/...) IS scanned and counted in py_files_in_generated_or_vendor_like_dirs_but_scanned.",
            "Files that fail UTF-8 decoding or ast.parse are skipped SILENTLY by V1 (see *_silently_skipped counters).",
            "Identity has no per-occurrence disambiguator; see identity_collision_exposure.",
            "Non-Python repositories (TypeScript/Next.js, Rust, Swift, ...) and all config formats (YAML/TOML/JSON/"
            "Dockerfile/.env/Terraform/CI workflows) are not inspected. 'No V1 findings' there means NOT SCANNED.",
            "V1 assigns no severity; queues are rule-based triage, not human verification.",
            "Repository category is a name/manifest heuristic and may be wrong; see category_basis per repository.",
        ],
    }


def run(root: Path, baseline_path: Path, pilot_paths: list[str], continue_on_pilot_failure: bool = False) -> dict:
    inv = build_inventory(root)
    pilot = pilot_rail_check(root, baseline_path, pilot_paths)
    report: dict = {
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "scanner_commit": ss._scanner_commit(),
        "workspace_root": str(root),
        "inventory": inv,
        "pilot_rail_integrity": pilot,
    }
    if pilot["status"] != "PASS" and not continue_on_pilot_failure:
        report["expansion_analysis"] = "SKIPPED: Pilot Rail integrity invariant not PASS"
        return report
    unique = inv["unique_repositories"]
    findings, coverage = scan_unique(root, unique)
    meta = {u["repo_key"]: u for u in unique}
    pilot_keys = {ss.canonical_repo_id(root / p) for p in pilot_paths}
    baseline = ss.load_baseline(baseline_path)
    baseline_ids = {f["identity"] for f in baseline["findings"]}
    resolved_ids = {f["identity"] for f in baseline.get("resolved_history", [])}
    # finding.repo was rewritten to repo_key in scan_unique; recover the meta by it.
    records = sorted((finding_record(f, meta[f.repo], pilot_keys, baseline_ids, resolved_ids) for f in findings), key=sort_key)
    repo_counts = Counter(r["repo"] for r in records)
    scanned = [u for u in unique if u["scan_status"] == "SCANNED"]
    prod = [r for r in records if r["classification"] == "production-reachable"]
    queues = {q: [r for r in records if r["queue"] == q] for q in "ABCDE"}
    pats, fallback_names = patterns(records)
    report.update({
        "aggregate": {
            "total_candidate_directories": inv["candidates_total"],
            "git_repositories_discovered": inv["git_repositories_discovered"],
            "unique_repositories": len(unique),
            "duplicate_worktrees_or_checkouts": len(inv["duplicate_checkouts"]),
            "non_repository_candidates": len(inv["non_repository_candidates"]),
            "supported_repositories_scanned": len(scanned),
            "unsupported_or_unscanned_repositories": len(unique) - len(scanned),
            "repositories_with_zero_findings": sum(1 for u in scanned if repo_counts[u["repo_key"]] == 0),
            "repositories_with_findings": sum(1 for u in scanned if repo_counts[u["repo_key"]] > 0),
            "total_findings": len(records),
            "production_reachable": len(prod),
            "non_production": len(records) - len(prod),
            "test_fixture": sum(1 for r in records if r["classification"] == "test-fixture"),
            "severity_assigned_by_v1": {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "UNCLASSIFIED": len(records)},
            "queue_implied_candidate_severity": {QUEUE_CANDIDATE_SEVERITY[q]: len(v) for q, v in queues.items()},
            "by_classification": dict(sorted(Counter(r["classification"] for r in records).items())),
            "by_rule": dict(sorted(Counter(r["kind"] for r in records).items())),
            "production_reachable_by_rule": dict(sorted(Counter(r["kind"] for r in prod).items())),
            "by_repository_category": dict(sorted(Counter(r["repository_category"] for r in records).items())),
            "scanned_checkout_state": {
                "on_main": sum(1 for u in scanned if u["branch"] == "main"),
                "on_other_branch": sum(1 for u in scanned if u["branch"] != "main"),
                "dirty_worktree": sum(1 for u in scanned if u["dirty"]),
                "note": "Findings describe the checked-out working tree of each primary checkout, not origin/main.",
            },
        },
        "queue_ab_by_baseline_status": {
            q: dict(sorted(Counter(r["baseline_status"].split("(")[0] for r in queues[q]).items())) for q in "AB"},
        "queues": {q: {"definition": QUEUE_DEFS[q], "count": len(v),
                       "repositories": dict(sorted(Counter(r["repo"] for r in v).items()))} for q, v in queues.items()},
        "repeated_patterns": pats,
        "hardcoded_fallback_by_credential_name": fallback_names,
        "repositories_scanned": [
            {"repo": u["repo_key"], "path": u["path"], "category": u["category"], "findings": repo_counts[u["repo_key"]],
             "production_reachable": sum(1 for r in prod if r["repo"] == u["repo_key"]),
             "queue_AB": sum(1 for r in records if r["repo"] == u["repo_key"] and r["queue"] in "AB"),
             "scan_note": u["scan_note"]} for u in scanned],
        "coverage_limits": blind_spots(unique, coverage, findings),
        "findings": records,
    })
    return report


# --- markdown ---------------------------------------------------------------


def render_md(rep: dict) -> str:
    L: list[str] = ["# CubeShackles workspace security-surface observation (Scanner V1)", ""]
    L += ["> OBSERVATION ONLY. 'Scanned, no V1 findings' is **not** 'security proven'. V1 inspects Python only, assigns no "
          "severity, and cannot see cross-repo edges, config files or non-Python code. Queues are rule-based triage, not "
          "human-verified severities. No baselines were created or changed.", ""]
    L += [f"- Workspace root: `{rep['workspace_root']}`", f"- Scanner commit: `{rep['scanner_commit']}`", ""]
    pr = rep["pilot_rail_integrity"]
    L += ["## Pilot Rail integrity (frozen baseline)", "", f"**Status: {pr['status']}**"]
    if "counts" in pr:
        c = pr["counts"]
        L += [f"- NEW {c['new']} / UNCHANGED {c['unchanged']} / RESOLVED {c['resolved']} / REGRESSED {c['regressed']}",
              f"- NEW production-reachable defect-class: {len(pr['new_production_reachable_defects_p0_p1_class'])}",
              f"- REGRESSED production-reachable defect-class: {len(pr['regressed_production_reachable_defects_p0_p1_class'])}"]
    else:
        L.append(f"- {pr.get('reason')}")
    L.append("")
    if "aggregate" not in rep:
        return "\n".join(L + [rep.get("expansion_analysis", ""), ""])
    a = rep["aggregate"]
    L += ["## Aggregate", "", "| Metric | Value |", "|---|---|"]
    for k in ("total_candidate_directories", "git_repositories_discovered", "unique_repositories",
              "duplicate_worktrees_or_checkouts", "non_repository_candidates", "supported_repositories_scanned",
              "unsupported_or_unscanned_repositories", "repositories_with_zero_findings", "repositories_with_findings",
              "total_findings", "production_reachable", "non_production", "test_fixture"):
        L.append(f"| {k.replace('_', ' ')} | {a[k]} |")
    L += ["", f"Checkout state of scanned repos: {a['scanned_checkout_state']}", "",
          f"Queue A/B by baseline status: {rep['queue_ab_by_baseline_status']}", "", f"V1-assigned severity: {a['severity_assigned_by_v1']}", "",
          f"Queue-implied candidate severity (unverified): {a['queue_implied_candidate_severity']}", "",
          f"By rule: {a['by_rule']}", "", f"Production-reachable by rule: {a['production_reachable_by_rule']}", "",
          f"By classification: {a['by_classification']}", ""]
    L += ["## Remediation queues (deterministic; nothing fixed)", ""]
    for q in "ABCDE":
        d = rep["queues"][q]
        L.append(f"- **Queue {q}** ({d['count']}) -- {d['definition']}")
        for repo, n in d["repositories"].items():
            L.append(f"  - {repo}: {n}")
    L += ["", "## Repeated invariant patterns", "", "| Pattern | Unique repos | Occurrences | Runtime prod-reachable | By classification |",
          "|---|---|---|---|---|"]
    for p in rep["repeated_patterns"]:
        L.append(f"| {p['pattern']} | {p['unique_repositories']} | {p['occurrences']} | {p['production_reachable_runtime']} | {p['by_classification']} |")
    L += ["", "### HARDCODED_FALLBACK by credential name (names only, never values)", "", "| Name | Repos | Occurrences | Runtime prod-reachable |", "|---|---|---|---|"]
    for e in rep["hardcoded_fallback_by_credential_name"]:
        L.append(f"| {e['credential_name']} | {e['unique_repositories']} | {e['occurrences']} | {e['production_reachable_runtime']} |")
    inv = rep["inventory"]
    L += ["", "## Inventory", "", "### Unique repositories", "",
          "| Repo | Path | Branch | Category | Lang | Dirty | Scan | Reason |", "|---|---|---|---|---|---|---|---|"]
    for u in inv["unique_repositories"]:
        top = ",".join(list(u["languages"])[:3]) or "-"
        L.append(f"| {u['repo_key']} | {u['path']} | {u['branch']} | {u['category']} | {top} | {'yes' if u['dirty'] else 'no'} | {u['scan_status']} | {u['scan_reason'] or u['scan_note'] or ''} |")
    L += ["", "### Duplicate checkouts / worktrees (not counted as repositories)", ""]
    for d in inv["duplicate_checkouts"]:
        L.append(f"- `{d['path']}` -> duplicate of `{d['duplicate_of']}` ({d['kind']}, {d['branch']}, dirty={d['dirty']})")
    L += ["", "### Non-repository candidate directories", ""]
    for c in inv["non_repository_candidates"]:
        L.append(f"- `{c['path']}` -- {c['status']}")
    cl = rep["coverage_limits"]
    L += ["", "## V1 coverage limits (a clean scan here is NOT proof of security)", ""]
    L += [f"- Unsupported repositories ({cl['unsupported_repository_count']}): " + ", ".join(cl["unsupported_repositories"]),
          f"- Non-Python source files not inspected: {cl['non_python_source_files_not_inspected']}",
          f"- Config formats not inspected: {cl['config_formats_not_inspected']}",
          f"- .env-style files present (names only, never read): {cl['dotenv_files_present_names_only_not_read']}",
          f"- Python coverage totals: {cl['python_coverage_totals']}",
          f"- Identity collision exposure: {cl['identity_collision_exposure']}", ""]
    L += [f"- {s}" for s in cl["statements"]]
    L += ["", "## Findings", "", "Full per-finding records (identity, repo, category, file, kind, classification, queue, evidence) are in the JSON report.", ""]
    return "\n".join(L)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--baseline", required=True, help="frozen Pilot Rail baseline (never modified)")
    ap.add_argument("--pilot-rail-path", action="append", default=[], help="workspace-relative pinned Pilot Rail path")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--md", dest="md_out")
    ap.add_argument("--continue-on-pilot-failure", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.workspace).resolve()
    if not root.is_dir():
        print(f"[ERROR] workspace not a directory: {root}", file=sys.stderr)
        return 2
    rep = run(root, Path(args.baseline).resolve(), args.pilot_rail_path, args.continue_on_pilot_failure)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = render_md(rep)
    if args.md_out:
        Path(args.md_out).write_text(md, encoding="utf-8")
    else:
        print(md)
    return 0 if rep["pilot_rail_integrity"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
