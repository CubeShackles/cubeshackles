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
  - Cannot trace a value through an intermediate variable (e.g.
    `b = x.encode(); compare_digest(b, ...)` is not recognised as safe --
    confirmed false positive found scanning network-orchestrator's own
    fixed app/core/security.py this pass).
  - ROUTE_NO_AUTH_DEPENDENCY's identity is call-site based (repo + path +
    enclosing function); it cannot yet identify a route by matching
    request method + resolved path against a live OpenAPI document the way
    this session's manual test suites did.

Baseline / diff mode (see BASELINE_SCHEMA_VERSION below): a baseline is a
repository-controlled, versioned snapshot of a scan's findings, identified
by a hash that is stable across checkout location, worktree path, and line
number movement (see `compute_identity`). It is NOT an allowlist: ordinary
`--json`/`--md` output always reports every finding regardless of any
baseline. `--baseline <path>` adds a second, additional comparison view
that classifies each current finding as NEW, UNCHANGED, or (compared
against the baseline's `resolved_history`) REGRESSED, and each baseline
finding no longer present as RESOLVED.

Usage:
    python3 scripts/security_scan.py <repo_root> [<repo_root> ...] \\
        [--json out.json] [--md out.md] [--workspace <dir>] \\
        [--write-baseline baseline.json [--creation-source TEXT] \\
         [--resolved-history resolved.json]] \\
        [--baseline baseline.json [--baseline-json diff.json] [--baseline-md diff.md]]

    --workspace <dir>       instead of listing repos, treat every immediate
                            subdirectory of <dir> containing a .git entry as
                            a repo root (the 50+-repo case).
    --write-baseline PATH   write a new baseline snapshot of the current
                            scan to PATH instead of (or in addition to)
                            comparing against one.
    --resolved-history PATH JSON list of {"identity", "repo", "kind",
                            "note"} entries for findings confirmed fixed in
                            a prior remediation pass, folded into a newly
                            written baseline's "resolved_history" so a
                            later reappearance of that exact identity is
                            reported as REGRESSED, not NEW.
    --baseline PATH         compare the current scan against this baseline
                            and print/write the NEW/UNCHANGED/RESOLVED/
                            REGRESSED classification. Malformed JSON or an
                            incompatible schema_version fails closed (a
                            clear error, non-zero exit) rather than
                            silently treating everything as NEW.

Exit code (ordinary mode, no --baseline): non-zero if any production-
reachable HARDCODED_FALLBACK, COMPARE_DIGEST_STR_RISK, or
OUTBOUND_CALL_NO_CRED finding exists. ROUTE_NO_AUTH_DEPENDENCY never fails
the run on its own (too many legitimate false positives from router-level
dependencies) -- always reported, never gates.

Exit code (--baseline mode): also non-zero if any NEW or REGRESSED finding
is itself a production-reachable HARDCODED_FALLBACK / COMPARE_DIGEST_STR_RISK
/ OUTBOUND_CALL_NO_CRED. Nothing wires this into CI yet in this version --
see the baseline's own "creation_source" and the org's decision to run an
observation period before any hard gate.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
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

KNOWN_V1_BLIND_SPOTS = [
    "No cross-repo call-graph resolution (env var -> base URL -> which repo's server owns that port).",
    "Python only -- no TypeScript/Next.js coverage.",
    "AST-based -- a dynamically built credential (string concatenation, an f-string with no static "
    "literal, a value read from a config object) is invisible to it.",
    "Cannot trace a value through an intermediate variable before it reaches compare_digest.",
    "ROUTE_NO_AUTH_DEPENDENCY identity is call-site based, not resolved-OpenAPI-path based.",
    "Repo display name (the 'repo' field) is a directory basename and can collide across different "
    "repos checked out to identically-named worktree paths; identity uses canonical_repo (git remote "
    "derived) specifically to avoid this, but the human-readable 'repo' field in ordinary output can "
    "still be ambiguous when scanning worktree paths directly.",
    "Identity has no per-occurrence disambiguator: two textually-identical statements (the exact same "
    "env var read with the exact same default, e.g. from a copy-pasted line) inside the SAME enclosing "
    "function collide onto one identity, undercounting distinct findings by one per such pair. Found "
    "in the real 263-finding baseline (4 collisions, all in test-fixture-classified files, none "
    "production-reachable, none P0/P1) while verifying an identical re-scan was 100% UNCHANGED.",
    "REGRESSED detection requires the SAME enclosing scope/structure the finding had when it was "
    "recorded resolved, not just the same literal default value reappearing. Verified against real "
    "code: fully reverting a fixed file back to its exact pre-fix shape correctly reports REGRESSED; "
    "reintroducing the same literal default value inside a since-refactored function (a different "
    "enclosing scope than the original module-level constant) reports NEW instead, because the "
    "structural fingerprint genuinely differs -- v1 does not guess that relationship rather than risk "
    "a false REGRESSED on an unrelated finding that merely shares a literal value.",
]


@dataclass
class Finding:
    repo: str
    file: str
    line: int
    kind: str
    detail: str
    classification: str
    confidence: str = "heuristic"
    canonical_repo: str = ""
    enclosing_scope: str = "<module>"
    identity: str = ""

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


# --- stable finding identity -------------------------------------------------
#
# Identity must survive: ordinary line movement, a different local checkout
# root, a different worktree path, and a directory-basename collision
# between two unrelated repos. It must NOT survive: the underlying security
# primitive actually changing (a different credential name, a different
# kind of finding, a different enclosing function).


def canonical_repo_id(repo_root: Path) -> str:
    """Stable repo identity independent of local directory basename or
    checkout location -- derived from the git remote origin URL when
    available. This is what makes identity survive worktrees and basename
    collisions: two different repos both checked out to a directory
    literally named "pilot-rail-doc" (the exact collision found scanning
    Cubeshackles-network-orchestrator and Cubeshackles-validator-node's
    worktrees side by side this pass) resolve to their real, distinct repo
    names here, even though `repo_root.name` -- kept as the separate,
    purely cosmetic `repo` display field -- would be identical for both.
    Falls back to an explicitly-marked directory-basename identity when no
    git remote is configured (e.g. a synthetic test fixture, or a bare
    local clone with no origin) -- this is deliberately NOT silently
    treated as equivalent to a real canonical id."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return f"unresolved:{repo_root.name}"
    url = proc.stdout.strip()
    if proc.returncode != 0 or not url:
        return f"unresolved:{repo_root.name}"
    name = url.rstrip("/").rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[: -len(".git")]
    return name or f"unresolved:{repo_root.name}"


def stable_detail_key(kind: str, detail: str) -> str:
    """The part of `detail` that reflects the actual security primitive,
    with anything that could vary cosmetically (there is currently nothing
    line/path-based in `detail` at all -- it is already string-only) kept,
    and -- for the two credential-related kinds -- narrowed to just the
    env var name, dropping the literal default value. This both makes
    identity independent of a default value being edited for clarity
    (e.g. quoting style) and keeps literal credential-shaped strings out of
    anything this key feeds into (the baseline file)."""
    if kind in ("CREDENTIAL_READ", "HARDCODED_FALLBACK"):
        return detail.split(" defaults to")[0].split(" (default=")[0].strip()
    return detail


def compute_identity(
    *, canonical_repo: str, relpath: str, kind: str, enclosing_scope: str, stable_key: str
) -> str:
    raw = "\x1f".join([canonical_repo, relpath, kind, enclosing_scope, stable_key])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


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
    def __init__(
        self,
        *,
        repo: str,
        canonical_repo: str,
        relpath: str,
        source: str,
        tree: ast.AST,
        result: ScanResult,
    ):
        self.repo = repo
        self.canonical_repo = canonical_repo
        self.relpath = relpath
        self.source = source
        self.result = result
        self.docstring_spans = docstring_spans(source)
        self.denylist_string_values: set[str] = set()
        self._collect_denylists(tree)
        self.router_dependency_names: set[str] = set()
        self._collect_router_level_dependencies(tree)
        self._scope_stack: list[str] = []

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

    def _current_scope(self) -> str:
        return ".".join(self._scope_stack) if self._scope_stack else "<module>"

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
        enclosing_scope = self._current_scope()
        skey = stable_detail_key(kind, detail)
        identity = compute_identity(
            canonical_repo=self.canonical_repo,
            relpath=self.relpath,
            kind=kind,
            enclosing_scope=enclosing_scope,
            stable_key=skey,
        )
        self.result.add(
            Finding(
                repo=self.repo,
                file=self.relpath,
                line=node.lineno,
                kind=kind,
                detail=detail,
                classification=classification,
                canonical_repo=self.canonical_repo,
                enclosing_scope=enclosing_scope,
                identity=identity,
            )
        )

    def visit_Call(self, node: ast.Call) -> None:
        self._check_credential_read(node)
        self._check_compare_digest(node)
        self._check_outbound_call(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Push the function's own name onto the scope stack BEFORE checking
        # its route auth, not after: an earlier version called
        # _check_route_auth() first, so `enclosing_scope` at emit time
        # reflected the PARENT scope, not this function's own name. Two
        # different route handlers both defined at module level (a real
        # case: Cubeshackles-node-api's POST and GET
        # /simulations/province-partition, two distinct functions, same
        # path) then collided onto the identical "<module>" scope and the
        # identical identity, silently merging two distinct findings into
        # one. Found by comparing a real baseline against an identical
        # re-scan, which should be 100% UNCHANGED and was not.
        self._scope_stack.append(node.name)
        self._check_route_auth(node)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._scope_stack.append(node.name)
        self._check_route_auth(node)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

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
    the right tradeoff for a heuristic tool meant to be re-run often. Note:
    a value encoded via an intermediate variable two lines earlier (a plain
    ast.Name at the call site) is NOT recognised -- see KNOWN_V1_BLIND_SPOTS."""
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


def scan_file(repo: str, canonical_repo: str, repo_root: Path, path: Path, result: ScanResult) -> None:
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return
    relpath = str(path.relative_to(repo_root))
    visitor = SecurityScanVisitor(
        repo=repo, canonical_repo=canonical_repo, relpath=relpath, source=source, tree=tree, result=result
    )
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
    canonical_repo = canonical_repo_id(repo_root)
    for path in repo_root.rglob("*.py"):
        relative_parts = path.relative_to(repo_root).parts
        if any(part in SKIP_DIR_NAMES for part in relative_parts):
            continue
        scan_file(repo, canonical_repo, repo_root, path, result)


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


# --- baseline: schema, build, load, compare ----------------------------------

BASELINE_SCHEMA_VERSION = 1


class BaselineError(Exception):
    """Raised when a baseline file is malformed or schema-incompatible.
    Callers must fail closed on this -- never fall back to treating every
    current finding as NEW, which would silently hide the distinction this
    whole mechanism exists to make."""


def _scanner_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.returncode == 0:
            return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def build_baseline(
    result: ScanResult,
    *,
    repository_scope: list[str],
    creation_source: str,
    resolved_history: list[dict] | None = None,
) -> dict:
    """A baseline never stores a finding's literal `detail` text -- for
    HARDCODED_FALLBACK/CREDENTIAL_READ that text contains the actual
    credential-shaped default value (e.g. "defaults to 'hmac-secret-local'").
    Only `stable_key` (the env var name alone, for those two kinds) is
    stored, which is what identity is computed from anyway."""
    prod = [f for f in result.findings if f.classification == "production-reachable"]
    defects = [f for f in prod if f.kind in FAILS_RUN]
    findings_out = []
    for f in result.findings:
        findings_out.append(
            {
                "identity": f.identity,
                "canonical_repo": f.canonical_repo,
                "file": f.file,
                "kind": f.kind,
                "classification": f.classification,
                "enclosing_scope": f.enclosing_scope,
                "stable_key": stable_detail_key(f.kind, f.detail),
            }
        )
    return {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "scanner_commit": _scanner_commit(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "creation_source": creation_source,
        "repository_scope": sorted(repository_scope),
        "finding_counts": {
            "total": len(result.findings),
            "production_reachable": len(prod),
            "production_reachable_defects": len(defects),
        },
        "classification_counts": dict(Counter(f.classification for f in result.findings)),
        "known_v1_blind_spots": KNOWN_V1_BLIND_SPOTS,
        "resolved_history": resolved_history or [],
        "findings": findings_out,
    }


def load_baseline(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BaselineError(f"cannot read baseline at {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BaselineError(f"malformed baseline JSON at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BaselineError(f"malformed baseline at {path}: root is not an object")
    required = {"schema_version", "findings"}
    missing = required - data.keys()
    if missing:
        raise BaselineError(f"malformed baseline at {path}: missing required keys {sorted(missing)}")
    if not isinstance(data["findings"], list):
        raise BaselineError(f"malformed baseline at {path}: 'findings' is not a list")
    version = data["schema_version"]
    if version != BASELINE_SCHEMA_VERSION:
        raise BaselineError(
            f"incompatible baseline schema_version {version!r} at {path}; "
            f"this scanner reads/writes schema_version {BASELINE_SCHEMA_VERSION}. "
            "Refusing to compare rather than guess compatibility."
        )
    return data


@dataclass
class BaselineDiff:
    new: list[Finding]
    unchanged_count: int
    resolved: list[dict]
    regressed: list[Finding]

    def to_dict(self) -> dict:
        return {
            "new": [asdict(f) for f in self.new],
            "unchanged_count": self.unchanged_count,
            "resolved": self.resolved,
            "regressed": [asdict(f) for f in self.regressed],
            "counts": {
                "new": len(self.new),
                "unchanged": self.unchanged_count,
                "resolved": len(self.resolved),
                "regressed": len(self.regressed),
            },
        }


def compare_to_baseline(result: ScanResult, baseline: dict) -> BaselineDiff:
    """REGRESSED, precisely: a current finding whose identity matches an
    entry in the baseline's `resolved_history` -- i.e. something this org
    explicitly recorded as fixed in a prior remediation pass -- and which
    is NOT present in the baseline's ordinary `findings` list (it should
    never be in both; if it somehow is, ordinary UNCHANGED wins, since the
    baseline's own current-state list is the more authoritative signal).

    A finding this scanner has simply never seen before, with no matching
    resolved_history entry, is NEW, not REGRESSED -- v1 cannot reliably
    tell "this is a brand new occurrence of an old pattern in a place we
    never checked" from "this specific thing came back," and does not
    guess: it reports NEW and lets a human decide.

    UNCHANGED: present in both the baseline's `findings` and the current
    scan. RESOLVED: present in the baseline's `findings` but absent from
    the current scan (regardless of resolved_history)."""
    baseline_ids = {f["identity"] for f in baseline["findings"]}
    resolved_history_ids = {f["identity"] for f in baseline.get("resolved_history", [])}
    current_by_id: dict[str, Finding] = {f.identity: f for f in result.findings}
    current_ids = set(current_by_id)

    regressed_ids = (current_ids & resolved_history_ids) - baseline_ids
    new_ids = current_ids - baseline_ids - resolved_history_ids
    unchanged_ids = current_ids & baseline_ids
    resolved_ids = baseline_ids - current_ids

    resolved_entries = [f for f in baseline["findings"] if f["identity"] in resolved_ids]

    return BaselineDiff(
        new=[current_by_id[i] for i in sorted(new_ids)],
        unchanged_count=len(unchanged_ids),
        resolved=resolved_entries,
        regressed=[current_by_id[i] for i in sorted(regressed_ids)],
    )


def render_baseline_markdown(diff: BaselineDiff, baseline: dict) -> str:
    lines = ["# Security Invariant Scan -- Baseline Comparison\n"]
    lines.append(
        f"Comparing against baseline created {baseline.get('created_at', 'unknown')} "
        f"(schema v{baseline.get('schema_version')}, scanner commit "
        f"`{baseline.get('scanner_commit', 'unknown')}`).\n"
    )
    c = diff.to_dict()["counts"]
    lines.append(
        f"**NEW: {c['new']}  UNCHANGED: {c['unchanged']}  "
        f"RESOLVED: {c['resolved']}  REGRESSED: {c['regressed']}**\n"
    )

    new_defects = [f for f in diff.new if f.classification == "production-reachable" and f.kind in FAILS_RUN]
    regressed_defects = [f for f in diff.regressed if f.classification == "production-reachable" and f.kind in FAILS_RUN]

    if new_defects or regressed_defects:
        lines.append("## ⚠ New or regressed production-reachable defects\n")
        lines.append("| State | Repo | File | Kind | Detail |")
        lines.append("|---|---|---|---|---|")
        for f in new_defects:
            lines.append(f"| NEW | {f.repo} | {f.file} | {f.kind} | {f.detail} |")
        for f in regressed_defects:
            lines.append(f"| REGRESSED | {f.repo} | {f.file} | {f.kind} | {f.detail} |")
        lines.append("")
    else:
        lines.append("No new or regressed production-reachable P0/P1-class defects.\n")

    if diff.regressed:
        lines.append("## All REGRESSED findings\n")
        lines.append("| Repo | File | Kind | Classification | Detail |")
        lines.append("|---|---|---|---|---|")
        for f in diff.regressed:
            lines.append(f"| {f.repo} | {f.file} | {f.kind} | {f.classification} | {f.detail} |")
        lines.append("")

    if diff.new:
        lines.append("## All NEW findings\n")
        lines.append("| Repo | File | Kind | Classification | Detail |")
        lines.append("|---|---|---|---|---|")
        for f in diff.new:
            lines.append(f"| {f.repo} | {f.file} | {f.kind} | {f.classification} | {f.detail} |")
        lines.append("")

    if diff.resolved:
        lines.append("## All RESOLVED findings (no longer detected)\n")
        lines.append("| Repo | File | Kind |")
        lines.append("|---|---|---|")
        for entry in diff.resolved:
            lines.append(f"| {entry.get('canonical_repo')} | {entry.get('file')} | {entry.get('kind')} |")
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repos", nargs="*", help="Repo root directories to scan")
    parser.add_argument("--workspace", help="Scan every .git-containing subdirectory of this path")
    parser.add_argument("--json", dest="json_out", help="Write JSON findings to this path")
    parser.add_argument("--md", dest="md_out", help="Write Markdown report to this path")
    parser.add_argument("--write-baseline", dest="write_baseline", help="Write a new baseline JSON to this path")
    parser.add_argument(
        "--creation-source", default="manual", help="Provenance note stored in a newly written baseline"
    )
    parser.add_argument(
        "--resolved-history",
        dest="resolved_history_in",
        help="JSON file: list of {identity, canonical_repo, file, kind, note} folded into a "
        "newly written baseline's resolved_history",
    )
    parser.add_argument("--baseline", dest="baseline_in", help="Compare the current scan against this baseline")
    parser.add_argument("--baseline-json", dest="baseline_json_out", help="Write the baseline diff as JSON")
    parser.add_argument("--baseline-md", dest="baseline_md_out", help="Write the baseline diff as Markdown")
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

    # Ordinary output: always produced, in full, regardless of baseline mode.
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

    exit_code = 0
    prod_defects = [
        f for f in result.findings if f.classification == "production-reachable" and f.kind in FAILS_RUN
    ]
    if prod_defects:
        exit_code = 1

    if args.write_baseline:
        resolved_history = []
        if args.resolved_history_in:
            resolved_history = json.loads(Path(args.resolved_history_in).read_text(encoding="utf-8"))
        canonical_scope = sorted({f.canonical_repo for f in result.findings} | {
            canonical_repo_id(root) for root in repo_roots if root.is_dir()
        })
        baseline = build_baseline(
            result,
            repository_scope=canonical_scope,
            creation_source=args.creation_source,
            resolved_history=resolved_history,
        )
        Path(args.write_baseline).write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"[baseline] wrote {args.write_baseline}", file=sys.stderr)

    if args.baseline_in:
        try:
            baseline = load_baseline(Path(args.baseline_in))
        except BaselineError as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            return 2
        diff = compare_to_baseline(result, baseline)
        if args.baseline_json_out:
            Path(args.baseline_json_out).write_text(
                json.dumps(diff.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        baseline_md = render_baseline_markdown(diff, baseline)
        if args.baseline_md_out:
            Path(args.baseline_md_out).write_text(baseline_md, encoding="utf-8")
        else:
            print(baseline_md)
        new_or_regressed_defects = [
            f
            for f in diff.new + diff.regressed
            if f.classification == "production-reachable" and f.kind in FAILS_RUN
        ]
        if new_or_regressed_defects:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
