#!/usr/bin/env python3
"""Static ISO-1..ISO-7 check. Does not start containers or open a network."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPOSE = ROOT / "docker-compose.synthetic.yml"
EXAMPLE = ROOT / "synthetic.env.example"
FIXTURE = ROOT / "fixtures" / "synthetic-accounts.json"

PHONE = re.compile(r"(?:\+|00)?244\d{9}|\b\d{9,}\b")
REMOTE_URL = re.compile(r"https?://(?!ledger:|settlement-engine:|node-api:)[^/\s\"']+")
PROD_WORD = re.compile(r"\b(production|prod-|uat\.|amazonaws|azure|gcp)\b", re.I)


def fail(code: str, detail: str) -> str:
    return f"FAIL {code} {detail}"


def check() -> list[str]:
    compose = COMPOSE.read_text(encoding="utf-8")
    example = EXAMPLE.read_text(encoding="utf-8")
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    errors: list[str] = []

    if "sqlite:////data/ledger-staging.db" not in compose:
        errors.append(fail("ISO-1", "ledger database URL is not the staging sqlite path"))
    if REMOTE_URL.search(compose) or REMOTE_URL.search(example):
        errors.append(fail("ISO-1", "a remote URL is present"))
    if "external:" in compose:
        errors.append(fail("ISO-1", "an external network or volume is declared"))

    values = []
    for line in example.splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values.append((key, value))
        if value != "synthetic-local-only":
            errors.append(fail("ISO-2", f"{key} is not the committed placeholder"))
    active = "\n".join(line for line in compose.splitlines() if not line.lstrip().startswith("#"))
    if PROD_WORD.search(active):
        errors.append(fail("ISO-2", "compose names a production or cloud host"))

    for required in ("LEDGER_BASE_URL: http://ledger:8086", "SETTLEMENT_ENGINE_URL: http://settlement-engine:8087"):
        if required not in compose:
            errors.append(fail("ISO-3", f"missing in-network URL {required}"))

    for account in fixture["accounts"]:
        account_id = account["account_id"]
        if not account_id.startswith("stg_acct_"):
            errors.append(fail("ISO-4", f"{account_id} is not a synthetic account id"))
        if account.get("provenance") != "synthetic":
            errors.append(fail("ISO-6", f"{account_id} has no synthetic provenance"))
        if PHONE.search(account_id):
            errors.append(fail("ISO-4", f"{account_id} matches a phone-like pattern"))
    if PHONE.search(json.dumps(fixture)):
        errors.append(fail("ISO-4", "fixture contains a phone-like number"))

    if "internal: true" not in compose:
        errors.append(fail("ISO-5", "staging network is not internal"))
    if "127.0.0.1:" not in compose:
        errors.append(fail("ISO-5", "published ports are not bound to localhost"))

    for volume in (
        "cubeshackles-staging-ledger",
        "cubeshackles-staging-settlement",
        "cubeshackles-staging-node-api",
    ):
        if volume not in compose:
            errors.append(fail("ISO-7", f"missing namespaced volume {volume}"))
    if "profiles: [\"deployment-not-authorized\"]" not in compose:
        errors.append(fail("ISO-7", "services are not held behind the unauthorized profile"))
    return errors


def main() -> int:
    errors = check()
    if errors:
        print("\n".join(errors))
        return 1
    print("ISO-1 PASS static: staging database path only; no remote URL")
    print("ISO-2 PASS static: committed values are placeholders; production secret store was not read")
    print("ISO-3 PASS static: settlement and ledger URLs are in-network names")
    print("ISO-4 PASS static: fixture accounts are stg_acct_* with no phone pattern")
    print("ISO-5 PASS static: network internal: true; ports bound to 127.0.0.1")
    print("ISO-6 PASS static: every fixture account is provenance=synthetic")
    print("ISO-7 PASS static: volumes are cubeshackles-staging-* and services are profile-gated")
    print("RUNTIME NOT RUN: containers were not started")
    return 0


if __name__ == "__main__":
    sys.exit(main())
