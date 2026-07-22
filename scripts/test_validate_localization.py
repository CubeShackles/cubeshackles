#!/usr/bin/env python3
"""Permanent regression fixtures for validate_localization.py's prohibited-
claims check, specifically its negation-awareness.

Dependency-light (stdlib only), run directly:
    python3 scripts/test_validate_localization.py

Exercises both directions on every controlled phrase pair, per founder
review of Batch 3 (2026-07-19): the positive (unqualified) form of a claim
must still be caught, and the negated (honest disclosure) form of the same
claim must not be — a negation-aware check can easily become too
permissive, so both sides are tested for every phrase, not just the
negated one.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "validate_localization.py"

VALID_METADATA = """
<!--
localization:
  canonical_file: README.md
  locale: pt-AO
  translation_status: machine-assisted
  canonical_commit: abc123
  last_synchronized: 2026-07-19
-->
"""

# (label, english_sentence, portuguese_sentence, should_flag)
CASES = [
    # --- "production ready" / "production-ready" ---
    ("en: unqualified 'production ready'", "This system is production ready.", "Este sistema.", True),
    ("en: negated 'not production-ready'", "This system is not production-ready.", "Este sistema.", False),
    ("pt: unqualified 'pronto para produção'", "This system.", "Este sistema está pronto para produção.", True),
    ("pt: negated 'não está pronto para produção'", "This system.", "Este sistema não está pronto para produção.", False),
    # --- "approved by {a,the} regulator" ---
    ("en: unqualified 'approved by the regulator'", "This product was approved by the regulator.", "Este produto.", True),
    ("en: negated 'not approved by a regulator'", "This product has not approved by a regulator status.", "Este produto.", False),
    ("pt: unqualified 'aprovado pelo regulador'", "This product.", "Este produto foi aprovado pelo regulador.", True),
    ("pt: negated 'não foi aprovado por qualquer regulador'", "This product.", "Este produto não foi aprovado por qualquer regulador.", False),
    # --- "guaranteed settlement finality" / "assegura finalidade de liquidação" ---
    ("en: unqualified 'provides guaranteed settlement finality'", "This engine provides guaranteed settlement finality.", "Este motor.", True),
    ("en: benign 'does not provide settlement finality' (different phrase, must not false-positive)", "This engine does not provide settlement finality.", "Este motor.", False),
    ("pt: unqualified 'assegura finalidade de liquidação'", "This engine.", "Este motor assegura finalidade de liquidação.", True),
    ("pt: negated 'não assegura finalidade de liquidação'", "This engine.", "Este motor não assegura finalidade de liquidação.", False),
]


def run_case(label: str, en_sentence: str, pt_sentence: str, should_flag: bool) -> str | None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "README.md").write_text(
            f"[English](./README.md) | [Português](./README.pt.md)\n\n# Test\n\n{en_sentence}\n",
            encoding="utf-8",
        )
        (root / "README.pt.md").write_text(
            f"[English](./README.md) | [Português](./README.pt.md)\n\n# Teste\n\n{pt_sentence}\n{VALID_METADATA}",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(root), "--repo-name", "test-fixture", "--claims-register", "/dev/null"],
            capture_output=True,
            text=True,
        )
        flagged = "prohibited claim language found" in result.stdout
        if flagged != should_flag:
            return (
                f"expected flagged={should_flag}, got flagged={flagged}\n"
                f"--- stdout ---\n{result.stdout}"
            )
        return None


def main() -> int:
    failures = 0
    for label, en, pt, should_flag in CASES:
        error = run_case(label, en, pt, should_flag)
        if error:
            failures += 1
            print(f"[FAIL] {label}\n  {error}")
        else:
            print(f"[PASS] {label}")
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
