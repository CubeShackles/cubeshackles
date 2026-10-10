#!/usr/bin/env python3
"""Write a local synthetic env file. Does not read production or start Docker."""

from __future__ import annotations

import secrets
import sys
from pathlib import Path

NAMES = ("LEDGER_API_KEYS", "SETTLEMENT_API_KEYS", "PLATFORM_WRITE_TOKEN")


def main() -> None:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("synthetic.env.local")
    lines = [f"{name}=stg_{secrets.token_urlsafe(24)}" for name in NAMES]
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
