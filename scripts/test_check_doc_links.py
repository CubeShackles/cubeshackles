#!/usr/bin/env python3
"""Regression fixtures for check_doc_links.py line-number accuracy.

Matches must be found on the original file text so reported line numbers
point at the real Markdown location. Matching against a code-stripped copy
shifts offsets whenever fenced/inline code precedes a link (Bugbot review
on CubeShackles/cubeshackles#5).
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check_doc_links.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_doc_links", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class CheckDocLinksLineNumbers(unittest.TestCase):
    def test_line_number_survives_preceding_code_block(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            md = root / "demo.md"
            md.write_text(
                "# Title\n"
                "\n"
                "Prose before code.\n"
                "\n"
                "```md\n"
                "[example](./missing-in-code.md)\n"
                "```\n"
                "\n"
                "See [CONTRACTS](./does-not-exist.md) for details.\n",
                encoding="utf-8",
            )
            findings = mod.check_file(md, root)
            self.assertEqual(len(findings), 1, findings)
            self.assertIn("demo.md:9:", findings[0], findings[0])
            self.assertIn("does-not-exist.md", findings[0])

    def test_skips_links_inside_fenced_and_inline_code(self) -> None:
        mod = _load()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            md = root / "skip.md"
            md.write_text(
                "```\n[dead](./a.md)\n```\n"
                "Inline `[dead](./b.md)` stays ignored.\n",
                encoding="utf-8",
            )
            self.assertEqual(mod.check_file(md, root), [])


if __name__ == "__main__":
    unittest.main()
