#!/usr/bin/env python3
"""General-purpose internal-documentation-link checker.

Unlike `validate_localization.py`'s `check_links_resolve` (which only runs
on README.md/README.pt.md and other bilingual pairs), this scans **every**
Markdown file in a repository for relative links and fails if the target
doesn't exist on disk. Added 2026-07-19 per founder review of Batch 3:
"CI should fail on future dead internal documentation links" — the trigger
was `Cubeshackles-node-api`'s README linking to four docs that didn't
exist, but the check applies repo-wide, not just to that one file.

Usage:
    python3 scripts/check_doc_links.py [repo_root]

Skips external links (http/https/mailto), in-page anchors (#foo), and
absolute paths (leading /, which usually mean "resolve from a different
repo's root" in this org's cross-repo companion-doc tables and can't be
checked locally). Exit code is non-zero if any relative link fails to
resolve.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`[^`\n]+`")

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__"}


def strip_code(text: str) -> str:
    return INLINE_CODE_PATTERN.sub("", CODE_BLOCK_PATTERN.sub("", text))


def check_file(md_path: Path, repo_root: Path) -> list:
    findings = []
    text = md_path.read_text(encoding="utf-8", errors="replace")
    for m in LINK_PATTERN.finditer(strip_code(text)):
        target = m.group(1).strip()
        target = target.split("#", 1)[0]
        if not target:
            continue
        if target.startswith(("http://", "https://", "mailto:", "/")):
            continue
        resolved = (md_path.parent / target).resolve()
        if not resolved.exists():
            line_no = text.count("\n", 0, m.start()) + 1
            findings.append(
                f"{md_path.relative_to(repo_root)}:{line_no}: dead relative link -> {target}"
            )
    return findings


def main() -> int:
    repo_root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    all_findings = []
    for md_path in repo_root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in md_path.parts):
            continue
        all_findings.extend(check_file(md_path, repo_root))

    for f in all_findings:
        print(f"[ERROR] {f}")
    print(f"\n{len(all_findings)} dead internal link(s) found.")
    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
