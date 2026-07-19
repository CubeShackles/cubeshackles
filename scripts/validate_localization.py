#!/usr/bin/env python3
"""Deterministic validator for CubeShackles bilingual documentation.

Dependency-light by design (Python 3 standard library only) so it can run in
any repository's CI without a package install step. See
docs/LOCALIZATION_POLICY.md section 8.

Usage:
    python3 scripts/validate_localization.py [repo_root] [--pt-file NAME]...

Discovers every `*.md` file in repo_root (default: current directory) that
has a sibling `<name>.pt.md`, and validates the pair. English partners may be
untagged (`FOO.md`) or tagged (`FOO.en.md`). Also validates the top-level
README.md/README.pt.md pair explicitly, even if README.md has no Portuguese
sibling yet (reported as a MISSING_TRANSLATION finding rather than silently
skipped).

Exit code is non-zero if any ERROR-level finding was produced. WARNING-level
findings do not fail the run but are always printed.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROHIBITED_TERMS = [
    "production ready",
    "fully operational",
    "guaranteed uptime",
    "unbreakable",
    "pronto para produção",
    "totalmente operacional",
    "tempo de atividade garantido",
    "inquebrável",
]

PROHIBITED_ALLOWLIST_FILES = {
    "PRODUCTION_PRINCIPLES.md",
    "sovereign-infrastructure-thesis.md",
}

# Uppercase-only: a case-insensitive match would false-positive on the
# ordinary Portuguese word "todo" ("every"/"all", e.g. "todo o histórico").
PLACEHOLDER_PATTERN = re.compile(r"\bTODO\b|\bTBD\b")

# Files that document the *shape* of a bilingual README (not a README
# themselves) — their body is a template skeleton inside a fenced code
# block, so the byte-identity and top-of-file nav checks don't apply.
TEMPLATE_FILE_MARKER = "TEMPLATE"

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
]

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
NUMBER_PATTERN = re.compile(r"(?<![\w.])\d[\d,.]*%?(?![\w])")
# Captures the optional language tag (group 1) and body (group 2) of a
# fenced block. Tagged blocks (```bash, ```yaml, ...) are treated as real
# commands/config and must be byte-identical across languages. Untagged
# blocks (bare ```) are treated as prose diagrams — same convention already
# used for the pipeline-arrow diagrams in several READMEs — and are allowed
# to carry translated labels, checked only for line-count correspondence.
CODE_BLOCK_PATTERN = re.compile(r"```([^\n`]*)\n(.*?)```", re.DOTALL)
# Accepts either nav convention: both languages linked
# ([English](url) | [Português](url)), or the current page's language bolded
# instead of self-linked (**English** | [Português](url), and the mirror on
# the Portuguese file) — the bolded form avoids a dead self-link and is the
# convention already in use on the org profile README.
NAV_PATTERN = re.compile(
    r"(?:\[English\]\([^)]+\)|\*\*English\*\*)\s*\|\s*"
    r"(?:\[Português\]\([^)]+\)|\*\*Português\*\*)"
)
METADATA_PATTERN = re.compile(
    r"<!--\s*localization:\s*(.*?)-->", re.DOTALL
)
REQUIRED_METADATA_KEYS = [
    "canonical_file",
    "locale",
    "translation_status",
    "last_synchronized",
]
VALID_TRANSLATION_STATUS = {"reviewed", "machine-assisted", "pending-review"}


@dataclass
class Finding:
    level: str  # "ERROR" | "WARNING"
    file: str
    message: str


@dataclass
class Report:
    findings: list = field(default_factory=list)

    def error(self, file: str, message: str) -> None:
        self.findings.append(Finding("ERROR", file, message))

    def warn(self, file: str, message: str) -> None:
        self.findings.append(Finding("WARNING", file, message))

    @property
    def has_errors(self) -> bool:
        return any(f.level == "ERROR" for f in self.findings)


def strip_code_blocks(text: str) -> str:
    return CODE_BLOCK_PATTERN.sub("", text)


def strip_localization_metadata(text: str) -> str:
    """Remove PT translation metadata footers before prose comparisons.

    The `last_synchronized: YYYY-MM-DD` date is PT-only bookkeeping and must
    not drive numeric-parity warnings against the English canonical file.
    """
    return METADATA_PATTERN.sub("", text)


def extract_code_blocks(text: str) -> list:
    """Returns [(language_tag, body), ...] for every fenced block."""
    return [(tag.strip(), body) for tag, body in CODE_BLOCK_PATTERN.findall(text)]


def extract_headings(text: str) -> list:
    return [(len(h), t.strip()) for h, t in HEADING_PATTERN.findall(strip_code_blocks(text))]


def extract_numbers(text: str) -> set:
    prose = strip_localization_metadata(strip_code_blocks(text))
    return set(NUMBER_PATTERN.findall(prose))


def check_prohibited_terms(report: Report, relpath: str, text: str) -> None:
    if Path(relpath).name in PROHIBITED_ALLOWLIST_FILES:
        return
    lowered = text.lower()
    for term in PROHIBITED_TERMS:
        if term in lowered:
            report.error(relpath, f'prohibited claim language found: "{term}"')


def check_placeholders(report: Report, relpath: str, text: str) -> None:
    # Match against the original text so reported line numbers stay accurate,
    # then skip hits that fall inside fenced code blocks (same exclusion as
    # strip_code_blocks, without shifting offsets).
    code_spans = [(m.start(), m.end()) for m in CODE_BLOCK_PATTERN.finditer(text)]

    def in_code_block(pos: int) -> bool:
        return any(start <= pos < end for start, end in code_spans)

    for m in PLACEHOLDER_PATTERN.finditer(text):
        if in_code_block(m.start()):
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        report.error(
            relpath,
            f"line {line_no}: TODO/TBD placeholder without an explicit status "
            "label (use planned/proposed/under evaluation instead)",
        )


def check_secrets(report: Report, relpath: str, text: str) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            report.error(relpath, "possible secret/credential pattern found")


def check_duplicate_headings(report: Report, relpath: str, text: str) -> None:
    headings = extract_headings(text)
    seen = {}
    for level, title in headings:
        key = (level, title.lower())
        seen[key] = seen.get(key, 0) + 1
    for (level, title), count in seen.items():
        if count > 1:
            report.warn(relpath, f'duplicate heading "{"#" * level} {title}" appears {count} times')


def check_metadata(report: Report, pt_relpath: str, pt_text: str) -> None:
    m = METADATA_PATTERN.search(pt_text)
    if not m:
        report.error(pt_relpath, "missing <!-- localization: ... --> metadata block")
        return
    body = m.group(1)
    # [ \t]* (not \s*) so the separator can't swallow the newline into the
    # next key's line — \s* would eat across lines whenever a value is empty.
    found_keys = dict(re.findall(r"^[ \t]*(\w+):[ \t]*(.*)$", body, re.MULTILINE))
    for key in REQUIRED_METADATA_KEYS:
        if key not in found_keys or not found_keys[key].strip():
            report.error(pt_relpath, f"localization metadata missing required key: {key}")
    status = found_keys.get("translation_status", "").strip()
    if status and status not in VALID_TRANSLATION_STATUS:
        report.error(
            pt_relpath,
            f'translation_status "{status}" is not one of {sorted(VALID_TRANSLATION_STATUS)}',
        )
    if status == "reviewed" and "reviewer" not in found_keys:
        report.warn(
            pt_relpath,
            "translation_status is 'reviewed' but no reviewer is recorded — "
            "see docs/TRANSLATION_REVIEW_CHECKLIST.md",
        )


def check_nav(report: Report, relpath: str, text: str, is_pt: bool) -> None:
    lines = text.strip().splitlines()
    head = "\n".join(lines[:3])
    if not NAV_PATTERN.search(head):
        report.error(
            relpath,
            "missing '[English](...) | [Português](...)' navigation line "
            "near the top of the file",
        )


def check_heading_parity(report: Report, en_relpath: str, en_text: str, pt_relpath: str, pt_text: str) -> None:
    en_headings = extract_headings(en_text)
    pt_headings = extract_headings(pt_text)
    if len(en_headings) != len(pt_headings):
        report.error(
            pt_relpath,
            f"heading count mismatch: {en_relpath} has {len(en_headings)} "
            f"headings, {pt_relpath} has {len(pt_headings)}",
        )
        return
    for i, ((el, _), (pl, _)) in enumerate(zip(en_headings, pt_headings)):
        if el != pl:
            report.error(
                pt_relpath,
                f"heading #{i + 1} level mismatch: English is h{el}, "
                f"Portuguese is h{pl} — structure must correspond",
            )


def check_code_blocks(report: Report, en_relpath: str, en_text: str, pt_relpath: str, pt_text: str) -> None:
    en_blocks = extract_code_blocks(en_text)
    pt_blocks = extract_code_blocks(pt_text)
    if len(en_blocks) != len(pt_blocks):
        report.error(
            pt_relpath,
            f"code block count mismatch: {en_relpath} has {len(en_blocks)}, "
            f"{pt_relpath} has {len(pt_blocks)}",
        )
        return
    for i, ((etag, ebody), (ptag, pbody)) in enumerate(zip(en_blocks, pt_blocks)):
        if etag:
            # Tagged block (```bash, ```yaml, ...): a real command/config
            # example. Must be byte-identical — copy-paste safety.
            if ebody != pbody:
                report.error(
                    pt_relpath,
                    f"code block #{i + 1} (```{etag}) differs between English "
                    "and Portuguese — commands/filenames/identifiers must be "
                    "byte-identical",
                )
        else:
            # Untagged block: treated as a prose diagram. Labels may be
            # translated; only line-count correspondence is checked.
            if ebody.count("\n") != pbody.count("\n"):
                report.warn(
                    pt_relpath,
                    f"untagged code block #{i + 1} line-count differs between "
                    "English and Portuguese — confirm it's still the same "
                    "diagram, just with translated labels",
                )


def check_numeric_parity(report: Report, en_relpath: str, en_text: str, pt_relpath: str, pt_text: str) -> None:
    en_numbers = extract_numbers(en_text)
    pt_numbers = extract_numbers(pt_text)
    missing_in_pt = en_numbers - pt_numbers
    missing_in_en = pt_numbers - en_numbers
    if missing_in_pt:
        report.warn(
            pt_relpath,
            f"numeric values present in English but not found in Portuguese: {sorted(missing_in_pt)}",
        )
    if missing_in_en:
        report.warn(
            pt_relpath,
            f"numeric values present in Portuguese but not found in English: {sorted(missing_in_en)}",
        )


def check_links_resolve(report: Report, relpath: str, text: str, base: Path) -> None:
    for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", strip_code_blocks(text)):
        target = m.group(1).split("#")[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("/"):
            continue
        resolved = (base.parent / target).resolve()
        if not resolved.exists():
            report.error(relpath, f"relative link target does not resolve: {target}")


def validate_pair(report: Report, repo_root: Path, en_path: Path, pt_path: Path) -> None:
    en_rel = str(en_path.relative_to(repo_root))
    pt_rel = str(pt_path.relative_to(repo_root))

    if not pt_path.exists():
        report.error(pt_rel, "required Portuguese translation is missing")
        return

    en_text = en_path.read_text(encoding="utf-8")
    pt_text = pt_path.read_text(encoding="utf-8")
    is_template = TEMPLATE_FILE_MARKER in en_path.name.upper()

    if not is_template:
        check_nav(report, en_rel, en_text, is_pt=False)
        check_nav(report, pt_rel, pt_text, is_pt=True)
        check_code_blocks(report, en_rel, en_text, pt_rel, pt_text)
    check_metadata(report, pt_rel, pt_text)
    check_heading_parity(report, en_rel, en_text, pt_rel, pt_text)
    check_numeric_parity(report, en_rel, en_text, pt_rel, pt_text)
    check_duplicate_headings(report, en_rel, en_text)
    check_duplicate_headings(report, pt_rel, pt_text)
    check_placeholders(report, en_rel, en_text)
    check_placeholders(report, pt_rel, pt_text)
    check_prohibited_terms(report, en_rel, en_text)
    check_prohibited_terms(report, pt_rel, pt_text)
    check_secrets(report, en_rel, en_text)
    check_secrets(report, pt_rel, pt_text)
    check_links_resolve(report, en_rel, en_text, en_path)
    check_links_resolve(report, pt_rel, pt_text, pt_path)


def english_sibling_for_pt(pt_path: Path) -> Path | None:
    """Resolve the English partner for a `*.pt.md` file.

    Supports both untagged English names (`FOO.md` ↔ `FOO.pt.md`) and the
    tagged style-guide convention (`FOO.en.md` ↔ `FOO.pt.md`). Prefers the
    untagged form when both exist.
    """
    stem = pt_path.name[: -len(".pt.md")]
    untagged = pt_path.with_name(stem + ".md")
    if untagged.exists():
        return untagged
    tagged = pt_path.with_name(stem + ".en.md")
    if tagged.exists():
        return tagged
    return None


def discover_pairs(repo_root: Path) -> list:
    pairs = []
    for pt_path in repo_root.rglob("*.pt.md"):
        if any(part in (".git", "node_modules", ".venv") for part in pt_path.parts):
            continue
        en_path = english_sibling_for_pt(pt_path)
        if en_path is not None:
            pairs.append((en_path, pt_path))
    readme_en = repo_root / "README.md"
    readme_pt = repo_root / "README.pt.md"
    if readme_en.exists() and (readme_en, readme_pt) not in pairs:
        pairs.append((readme_en, readme_pt))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_root", nargs="?", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    report = Report()

    pairs = discover_pairs(repo_root)
    if not pairs:
        print(f"No README.md found under {repo_root} — nothing to validate.")
        return 0

    for en_path, pt_path in pairs:
        validate_pair(report, repo_root, en_path, pt_path)

    errors = [f for f in report.findings if f.level == "ERROR"]
    warnings = [f for f in report.findings if f.level == "WARNING"]

    for f in report.findings:
        print(f"[{f.level}] {f.file}: {f.message}")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
