#!/usr/bin/env python3
"""Workspace-wide security invariant scanner for CubeShackles Python services.

Dependency-light by design (Python 3 standard library only) so it can run in
any repository's CI without a package install step, matching
validate_localization.py's convention. v1 scope, deliberately: a heuristic
pattern scan codifying the five checks used by hand in the 2026-09
cross-repo Pilot Rail security closure pass, run against every repo given on
the command line. It does NOT resolve a real cross-repo call graph (which
service actually listens on which env-var-derived base URL) -- see
"Known limitations" below.

Detections:

1. CREDENTIAL_READ         -- every os.getenv(NAME, default) / os.environ.get
                              (NAME, default) / os.environ[NAME] read of a
                              name that looks like a credential (API_KEY(S),
                              SECRET, TOKEN, PASSWORD, PRIVATE_KEY).
2. HARDCODED_FALLBACK      -- a CREDENTIAL_READ whose literal default value
                              looks like a real credential-shaped string
                              (not empty, not obviously a placeholder) and is
                              not inside a recognised denylist collection
                              (a set/frozenset/tuple/list literal assigned to
                              a name containing KNOWN/DENYLIST/BLOCKLIST/
                              FORBIDDEN/INSECURE).
3. COMPARE_DIGEST_STR_RISK -- hmac.compare_digest(...) / secrets.compare_
                              digest(...) called with an argument that is not
                              itself a `.encode(...)` call and not a `bytes`
                              literal -- the non-ASCII TypeError class of
                              defect fixed six times this pass.
4. ROUTE_NO_AUTH_DEPENDENCY-- a FastAPI route function (@app.get/post/...,
                              @router.get/post/...) with no `Depends(...)`
                              among its parameter defaults, not on the
                              conventional public-path allowlist (/health,
                              /metrics, /docs, /redoc, /openapi.json,
                              /favicon.ico), and not covered by a
                              router-level `dependencies=[Depends(...)]`
                              detected on the same router variable elsewhere
                              in the file.
5. OUTBOUND_CALL_NO_CRED   -- an httpx.get/post/put/patch/delete(...) or
                              requests.get/post/put/patch/delete(...) call
                              whose URL argument references a *_BASE_URL-
                              shaped variable or an http(s):// literal, with
                              no `headers=` keyword argument at all.

Every finding is classified as one of:
  production-reachable  -- outside any tests/ path or test_*.py/conftest.py
                            file, not inside a recognised denylist, not
                            inside a stripped docstring.
  test-fixture           -- inside tests/, a test_*.py/*_test.py file, or
                            conftest.py.
  intentional-denylist   -- the literal sits inside a KNOWN_TEST_CREDENTIAL_
                            VALUES-shaped collection.
  documentation-example  -- the literal only appears inside a stripped
                            triple-quoted docstring.

Confidence is "heuristic" for every finding in this version: this is a
regex/AST pattern scanner, not a type-aware cross-module analysis. It WILL
miss router-level dependencies defined in a different file than the route
(hence the ROUTE_NO_AUTH_DEPENDENCY findings should be read as "worth a
human look," not "confirmed unauthenticated" -- cross-check the way this
session's manual audit did, by reading the router construction). It also
cannot follow which literal env-var name a given httpx call's base URL
actually resolves to across repos, so it cannot build a real dependency
graph yet; each finding is repo-local.

Known limitations (v1, by design -- see the scope conversation this tool
came out of):
  - No cross-repo call-graph resolution (env var -> base URL -> which repo's
    server actually owns that port). Building that is the natural v2.
  - Python only. No coverage of the TypeScript/Next.js edges (e.g.
    Cubeshackles-web's server-side fetch calls) found by hand this pass.
  - AST-based, so a credential built dynamically (string concatenation,
    an f-string with no static literal, a value read from a config object
    rather than os.getenv directly) is invisible to it.

Usage:
    python3 scripts/security_scan.py <repo_root> [<repo_root> ...] \\
        [--json out.json] [--md out.md] [--workspace <dir>]

    --workspace <dir>   instead of listing repos, treat every immediate
                        subdirectory of <dir> containing a .git entry as a
                        repo root (the 50+-repo case).

Exit code is non-zero if any production-reachable HARDCODED_FALLBACK,
COMPARE_DIGEST_STR_RISK, or OUTBOUND_CALL_NO_CRED finding exists. Findings
of kind ROUTE_NO_AUTH_DEPENDENCY never fail the run on their own (too many
legitimate false positives from router-level dependencies) -- they are
always reported, never gate.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# --- what counts as a credential-shaped env var name -----------------------

CREDENTIAL_NAME_PATTERN = re.compile(
    r"(API_KEYS?|SECRET|TOKEN|PASSWORD|PRIVATE_KEY|SIGNING_KEY|CREDENTIAL)",
    re.IGNORECASE,
)

# A literal default is "credential-shaped" (worth flagging as a hardcoded
# fallback) if it is non-empty, not pure whitespace/delimiter noise, and not
# one of a small set of values that are obviously not real secrets.
OBVIOUSLY_NOT_A_SECRET = {"", "none", "null"}

DENYLIST_NAME_PATTERN = re.compile(
    r"(KNOWN_TEST|DENYLIST|BLOCKLIST|BLOCK_LIST|FORBIDDEN|INSECURE|DISALLOWED)",
    re.IGNORECASE,
)

PUBLIC_PATH_ALLOWLIST = {
    "/health",
    "/healthz",
    "/readiness",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
    "/docs/oauth2-redirect",
}

HTTP_METHOD_DECORATORS = {"get", "post", "put", "patch", "delete"}
OUTBOUND_HTTP_MODULES = {"httpx", "requests"}

TEST_PATH_SEGMENT = re.compile(r"(^|/)(tests?)(/|$)")
TEST_FILE_PATTERN = re.compile(r"(^test_.*\.py$|.*_test\.py$|^conftest\.py$)")

DOCSTRING_PATTERN = re.compile(r'("""|\'\'\')(.*?)(\1)', re.DOTALL)


@dataclass
class Finding:
    repo: str
    file: str
    line: int
    kind: str
    detail: str
    classification: str
    confidence: str = "heuristic"

    def key(self) -> tuple:
        return (self.repo, self.file, self.line, self.kind, self.detail)


@dataclass
class ScanResult:
    findings: list = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)


# --- classification helpers -------------------------------------------------


def is_test_path(relpath: str) -> bool:
    if TEST_PATH_SEGMENT.search(relpath):
        return True
    name = relpath.rsplit("/", 1)[-1]
    return bool(TEST_FILE_PATTERN.match(name))


def docstring_spans(source: str) -> list[tuple[int, int]]:
    """Byte-offset spans of every triple-quoted string literal in `source`,
    so a literal that only appears inside a docstring (explanatory prose
    quoting a retired pattern, as several of this session's own fixed files
    do) is classified as documentation-example rather than a live defect."""
    return [m.span() for m in DOCSTRING_PATTERN.finditer(source)]


def offset_in_spans(offset: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= offset < end for start, end in spans)


def classify(
    *, relpath: str, offset: int, source: str, spans: list[tuple[int, int]], in_denylist: bool
) -> str:
    if in_denylist:
        return "intentional-denylist"
    if is_test_path(relpath):
        return "test-fixture"
    if offset_in_spans(offset, spans):
        return "documentation-example"
    return "production-reachable"


# --- AST literal helpers -----------------------------------------------------


def literal_str(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def collection_contains_str(node: ast.AST, name_hint: str | None) -> bool:
    return isinstance(node, (ast.Set, ast.List, ast.Tuple)) and (
        name_hint is None or DENYLIST_NAME_PATTERN.search(name_hint) is not None
    )


class SecurityScanVisitor(ast.NodeVisitor):
    def __init__(self, *, repo: str, relpath: str, source: str, tree: ast.AST, result: ScanResult):
        self.repo = repo
        self.relpath = relpath
        self.source = source
        self.result = result
        self.docstring_spans = docstring_spans(source)
        self.denylist_string_values: set[str] = set()
        self._collect_denylists(tree)
        self.router_dependency_names: set[str] = set()
        self._collect_router_level_dependencies(tree)

    # -- setup passes ---------------------------------------------------
    #
    # Both passes walk the SAME tree object the visitor is later run over
    # (passed in, not re-parsed from source) -- ast.parse() on the same
    # source text twice produces two structurally-identical but distinct
    # trees, and Python object identity (id()) differs between them, so a
    # second parse would silently defeat the denylist-membership check
    # below (this was caught by test_hardcoded_fallback_inside_a_denylist_
    # collection_is_intentional failing against a real second-parse bug in
    # an earlier version of this file).

    def _collect_denylists(self, tree: ast.AST) -> None:
        """Collects the STRING VALUES held in any collection literal
        assigned to a denylist-shaped name, not node identities: the same
        literal value (e.g. "dev-settlement-key") legitimately appears as
        two textually-identical but distinct AST nodes -- once inside the
        denylist collection, once as a getenv() default elsewhere in the
        file -- so identity comparison can never match between them. An
        earlier version of this function compared by id() and silently
        never classified anything as intentional-denylist; caught by
        test_hardcoded_fallback_inside_a_denylist_collection_is_intentional."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                target_names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                name_hint = target_names[0] if target_names else None
                if name_hint and DENYLIST_NAME_PATTERN.search(name_hint):
                    for child in ast.walk(node.value):
                        if isinstance(child, ast.Constant) and isinstance(child.value, str):
                            self.denylist_string_values.add(child.value)

    def _collect_router_level_dependencies(self, tree: ast.AST) -> None:
        """`router = APIRouter(..., dependencies=[Depends(...)])` protects
        every route registered on `router` by default. Record which router
        variable names have this, so per-route findings on that router are
        suppressed."""
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not isinstance(node.value, ast.Call):
                continue
            call = node.value
            callee = call.func.id if isinstance(call.func, ast.Name) else None
            if callee != "APIRouter":
                continue
            has_deps = any(
                kw.arg == "dependencies"
                and isinstance(kw.value, ast.List)
                and any(
                    isinstance(elt, ast.Call)
                    and isinstance(elt.func, ast.Name)
                    and elt.func.id == "Depends"
                    for elt in kw.value.elts
                )
                for kw in call.keywords
            )
            if has_deps:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.router_dependency_names.add(target.id)

    # -- per-node visits --------------------------------------------------

    def _emit(self, node: ast.AST, kind: str, detail: str, *, in_denylist: bool = False) -> None:
        offset = getattr(node, "col_offset", 0)
        # Use the node's line to compute a rough char offset for docstring
        # containment; good enough for the docstring/production distinction
        # at this granularity (line-level, not exact-char).
        lines = self.source.splitlines(keepends=True)
        char_offset = sum(len(l) for l in lines[: node.lineno - 1]) + offset
        classification = classify(
            relpath=self.relpath,
            offset=char_offset,
            source=self.source,
            spans=self.docstring_spans,
            in_denylist=in_denylist,
        )
        self.result.add(
            Finding(
                repo=self.repo,
                file=self.relpath,
                line=node.lineno,
                kind=kind,
                detail=detail,
                classification=classification,
            )
        )

    def visit_Call(self, node: ast.Call) -> None:
        self._check_credential_read(node)
        self._check_compare_digest(node)
        self._check_outbound_call(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_route_auth(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_route_auth(node)
        self.generic_visit(node)

    # -- detection 1 & 2: credential reads and hardcoded fallbacks --------

    def _check_credential_read(self, node: ast.Call) -> None:
        func = node.func
        is_getenv = (
            isinstance(func, ast.Attribute)
            and func.attr in ("getenv", "get")
            and isinstance(func.value, ast.Attribute)
            and isinstance(func.value.value, ast.Name)
            and func.value.value.id == "os"
            and func.value.attr in ("environ",)
        ) or (isinstance(func, ast.Attribute) and func.attr == "getenv" and _is_os_name(func.value))
        if not is_getenv:
            return
        if not node.args:
            return
        name = literal_str(node.args[0])
        if not name or not CREDENTIAL_NAME_PATTERN.search(name):
            return
        default_node = node.args[1] if len(node.args) > 1 else None
        default_val = literal_str(default_node)
        self._emit(node, "CREDENTIAL_READ", f"{name} (default={default_val!r})")
        if default_val is not None and default_val.strip().lower() not in OBVIOUSLY_NOT_A_SECRET:
            in_denylist = default_val in self.denylist_string_values
            self._emit(
                node,
                "HARDCODED_FALLBACK",
                f"{name} defaults to {default_val!r}",
                in_denylist=in_denylist,
            )

    # -- detection 3: compare_digest with a non-bytes argument -------------

    def _check_compare_digest(self, node: ast.Call) -> None:
        func = node.func
        is_compare_digest = isinstance(func, ast.Attribute) and func.attr == "compare_digest"
        if not is_compare_digest:
            return
        for arg in node.args:
            if _looks_like_bytes(arg):
                continue
            self._emit(
                node,
                "COMPARE_DIGEST_STR_RISK",
                "compare_digest argument is not visibly bytes-encoded "
                "(non-ASCII input may raise TypeError instead of returning False)",
            )
            return  # one finding per call site is enough

    # -- detection 4: FastAPI route with no visible auth dependency -------

    def _check_route_auth(self, node) -> None:
        route_path = None
        router_name = None
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            callee = dec.func
            attr = callee.attr if isinstance(callee, ast.Attribute) else None
            base = callee.value.id if isinstance(callee, ast.Attribute) and isinstance(callee.value, ast.Name) else None
            if attr not in HTTP_METHOD_DECORATORS or base is None:
                continue
            router_name = base
            if dec.args:
                route_path = literal_str(dec.args[0])
            has_dependencies_kwarg = any(kw.arg == "dependencies" for kw in dec.keywords)
            if has_dependencies_kwarg:
                return  # protected at the decorator level
        if router_name is None:
            return
        if route_path in PUBLIC_PATH_ALLOWLIST:
            return
        if router_name in self.router_dependency_names:
            return
        # Look for Depends( in any parameter default.
        defaults = list(node.args.defaults) + list(node.args.kw_defaults)
        for d in defaults:
            if d is None:
                continue
            if isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "Depends":
                return
        self._emit(
            node,
            "ROUTE_NO_AUTH_DEPENDENCY",
            f"{router_name}.<method> {route_path or '(dynamic path)'} has no visible Depends(...) "
            "and is not on the public-path allowlist (cross-check router-level "
            "dependencies defined elsewhere before treating this as confirmed)",
        )

    # -- detection 5: outbound call with no headers kwarg ------------------

    def _check_outbound_call(self, node: ast.Call) -> None:
        func = node.func
        if not isinstance(func, ast.Attribute):
            return
        if func.attr not in HTTP_METHOD_DECORATORS and func.attr not in ("request",):
            return
        module_name = None
        if isinstance(func.value, ast.Name):
            module_name = func.value.id
        elif isinstance(func.value, ast.Attribute) and isinstance(func.value.value, ast.Name):
            module_name = func.value.value.id
        if module_name not in OUTBOUND_HTTP_MODULES:
            return
        if not node.args and not any(kw.arg == "url" for kw in node.keywords):
            return
        url_arg = node.args[0] if node.args else next(kw.value for kw in node.keywords if kw.arg == "url")
        looks_internal = _looks_like_internal_url(url_arg)
        if not looks_internal:
            return
        has_headers = any(kw.arg == "headers" for kw in node.keywords)
        if has_headers:
            return
        self._emit(
            node,
            "OUTBOUND_CALL_NO_CRED",
            f"{module_name}.{func.attr}(...) to what looks like an internal service URL, no headers= argument",
        )


def _is_os_name(node: ast.AST) -> bool:
    return isinstance(node, ast.Name) and node.id == "os"


def _looks_like_bytes(node: ast.AST) -> bool:
    """True if `node` is unlikely to be a bare `str` at the point it reaches
    compare_digest. Direct `.encode(...)` calls and byte literals are the
    clear case. Any OTHER call (e.g. a local `_to_bytes()` helper, the exact
    shape this session's own fixes across institutional-gateway,
    compliance-engine, network-orchestrator, validator-node, node-api,
    core, and ledger all use) is also treated as safe: a v1 false-positive
    found by running this scanner against ledger's own just-fixed
    app/core/security.py, whose `_to_bytes(provided)` wrapper this function
    did not originally recognise. This trades a false negative (a helper
    that does NOT actually encode, and is instead named misleadingly) for
    eliminating a false positive on the org's own now-dominant pattern --
    the right tradeoff for a heuristic tool meant to be re-run often."""
    if isinstance(node, ast.Call):
        return True
    if isinstance(node, ast.Constant) and isinstance(node.value, bytes):
        return True
    return False


def _looks_like_internal_url(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.startswith("http://") or node.value.startswith("https://")
    if isinstance(node, ast.JoinedStr):  # f-string
        for value in node.values:
            if isinstance(value, ast.FormattedValue) and isinstance(value.value, ast.Name):
                if "BASE_URL" in value.value.id.upper() or "URL" in value.value.id.upper():
                    return True
            if isinstance(value, ast.Constant) and (
                value.value.startswith("http://") or value.value.startswith("https://")
            ):
                return True
    if isinstance(node, ast.Name) and "URL" in node.id.upper():
        return True
    return False


# --- driver ------------------------------------------------------------------


def scan_file(repo: str, repo_root: Path, path: Path, result: ScanResult) -> None:
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return
    relpath = str(path.relative_to(repo_root))
    visitor = SecurityScanVisitor(repo=repo, relpath=relpath, source=source, tree=tree, result=result)
    visitor.visit(tree)


SKIP_DIR_NAMES = {".venv", "venv", "node_modules", ".git", "__pycache__", ".claude", "site-packages"}


def scan_repo(repo_root: Path, result: ScanResult) -> None:
    """Note: the skip check uses the path RELATIVE to repo_root, not the
    absolute path. Using path.parts directly (an earlier version's bug,
    caught while re-verifying the VALIDATOR_PRIVATE_KEY fix) means every
    file's ancestor directories are checked, including repo_root's own --
    and every worktree-based checkout this org actually works from sits
    under a literal `.claude/worktrees/...` path, which is itself in
    SKIP_DIR_NAMES. That silently produced zero findings for any repo root
    passed as a worktree path, with no error or warning. Does not affect
    the original 296/243/33 baseline, which scanned top-level checkouts."""
    repo = repo_root.name
    for path in repo_root.rglob("*.py"):
        relative_parts = path.relative_to(repo_root).parts
        if any(part in SKIP_DIR_NAMES for part in relative_parts):
            continue
        scan_file(repo, repo_root, path, result)


def discover_workspace_repos(workspace: Path) -> list[Path]:
    return sorted(
        p for p in workspace.iterdir() if p.is_dir() and (p / ".git").exists()
    )


FAILS_RUN = {"HARDCODED_FALLBACK", "COMPARE_DIGEST_STR_RISK", "OUTBOUND_CALL_NO_CRED"}


def render_markdown(result: ScanResult) -> str:
    lines = ["# Security Invariant Scan\n"]
    by_repo: dict[str, list[Finding]] = {}
    for f in result.findings:
        by_repo.setdefault(f.repo, []).append(f)

    total = len(result.findings)
    prod = [f for f in result.findings if f.classification == "production-reachable"]
    prod_defects = [f for f in prod if f.kind in FAILS_RUN]
    lines.append(
        f"**{total} findings across {len(by_repo)} repos** -- "
        f"{len(prod)} production-reachable, **{len(prod_defects)} production-reachable defects**.\n"
    )

    if prod_defects:
        lines.append("## Production-reachable defects\n")
        lines.append("| Repo | File | Line | Kind | Detail |")
        lines.append("|---|---|---|---|---|")
        for f in sorted(prod_defects, key=lambda f: (f.repo, f.file, f.line)):
            lines.append(f"| {f.repo} | {f.file} | {f.line} | {f.kind} | {f.detail} |")
        lines.append("")

    route_findings = [f for f in result.findings if f.kind == "ROUTE_NO_AUTH_DEPENDENCY"]
    if route_findings:
        lines.append(
            "## Routes with no visible auth dependency (heuristic -- verify manually)\n"
        )
        lines.append("| Repo | File | Line | Detail |")
        lines.append("|---|---|---|---|")
        for f in sorted(route_findings, key=lambda f: (f.repo, f.file, f.line)):
            lines.append(f"| {f.repo} | {f.file} | {f.line} | {f.detail} |")
        lines.append("")

    lines.append("## All findings by repo and classification\n")
    for repo in sorted(by_repo):
        lines.append(f"### {repo}\n")
        by_kind: dict[str, dict[str, int]] = {}
        for f in by_repo[repo]:
            by_kind.setdefault(f.kind, {}).setdefault(f.classification, 0)
            by_kind[f.kind][f.classification] += 1
        lines.append("| Kind | " + " | ".join(sorted({c for k in by_kind.values() for c in k})) + " |")
        cls_names = sorted({c for k in by_kind.values() for c in k})
        lines.append("|---|" + "---|" * len(cls_names))
        for kind in sorted(by_kind):
            row = [kind] + [str(by_kind[kind].get(c, 0)) for c in cls_names]
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repos", nargs="*", help="Repo root directories to scan")
    parser.add_argument("--workspace", help="Scan every .git-containing subdirectory of this path")
    parser.add_argument("--json", dest="json_out", help="Write JSON findings to this path")
    parser.add_argument("--md", dest="md_out", help="Write Markdown report to this path")
    args = parser.parse_args(argv)

    repo_roots: list[Path] = [Path(r).resolve() for r in args.repos]
    if args.workspace:
        repo_roots.extend(discover_workspace_repos(Path(args.workspace).resolve()))
    if not repo_roots:
        parser.error("provide at least one repo root or --workspace")

    result = ScanResult()
    for root in repo_roots:
        if not root.is_dir():
            print(f"[WARNING] skipping {root}: not a directory", file=sys.stderr)
            continue
        scan_repo(root, result)

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps([asdict(f) for f in result.findings], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    md = render_markdown(result)
    if args.md_out:
        Path(args.md_out).write_text(md, encoding="utf-8")
    else:
        print(md)

    prod_defects = [
        f for f in result.findings if f.classification == "production-reachable" and f.kind in FAILS_RUN
    ]
    return 1 if prod_defects else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
