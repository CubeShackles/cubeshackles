#!/usr/bin/env python3
"""Sync CubeShackles institutional GitHub labels and milestones across org repos.

Requires: gh auth with repo administration on CubeShackles/*.

Usage:
  python3 scripts/sync_github_taxonomy.py              # all non-archive repos
  python3 scripts/sync_github_taxonomy.py --dry-run
  python3 scripts/sync_github_taxonomy.py --repo CubeWallet
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

ORG = "CubeShackles"

ARCHIVE_SUFFIXES = ("archive", "archive1", "archive2", "archive3", "archive4")
ARCHIVE_NAMES = {
    "cubeshackles-web-archive1",
    "Backend-archive2",
    "CubeShackles-Backendarchive3",
    "cubewallet-demo-archive4",
}

LABELS: list[dict[str, str]] = [
    # type
    {"name": "type:bug", "color": "d73a4a", "description": "Correctness defect; no new product scope"},
    {"name": "type:fix", "color": "d73a4a", "description": "Repair of broken behavior"},
    {"name": "type:feat", "color": "1d76db", "description": "New capability (restricted under feature freeze)"},
    {"name": "type:docs", "color": "0075ca", "description": "Documentation / evidence / doctrine"},
    {"name": "type:security", "color": "b60205", "description": "Vulnerability, auth, trust-boundary hardening"},
    {"name": "type:compliance", "color": "5319e7", "description": "Regulatory / policy / audit evidence"},
    {"name": "type:test", "color": "0e8a16", "description": "Tests, gates, fixtures"},
    {"name": "type:infra", "color": "fbca04", "description": "CI, deploy, repo tooling"},
    {"name": "type:refactor", "color": "c5def5", "description": "Internal structure; no external contract change"},
    {"name": "type:chore", "color": "ffffff", "description": "Maintenance that is not product scope"},
    # layer
    {"name": "layer:canonical", "color": "000000", "description": "Umbrella doctrine"},
    {"name": "layer:contracts", "color": "5319e7", "description": "Interoperability contracts"},
    {"name": "layer:foundation", "color": "1d76db", "description": "CIEL / ontology / TFE / portal / agent"},
    {"name": "layer:protocol", "color": "b60205", "description": "Consensus / settlement / runtime"},
    {"name": "layer:api", "color": "fbca04", "description": "Node API / orchestrator / integration"},
    {"name": "layer:institutional", "color": "e99695", "description": "Gateway / compliance / clearing / ledger / custody"},
    {"name": "layer:access", "color": "0e8a16", "description": "Wallets / web / phone / transit apps"},
    {"name": "layer:intelligence", "color": "d93f0b", "description": "Advisory AI only — never consensus"},
    {"name": "layer:sovereign", "color": "6f42c1", "description": "Private sovereign compute / hardware"},
    {"name": "layer:ops", "color": "c2e0c6", "description": "Ops / security / chaos / observability"},
    {"name": "layer:os", "color": "a2eeef", "description": "cubeshackles-os (CubeKernel) / platform-specs"},
    {"name": "layer:control-plane", "color": "0052cc", "description": "Control plane — cross-cutting request governance"},
    # risk
    {"name": "risk:consensus-critical", "color": "b60205", "description": "May affect settlement / ledger / validator / finality"},
    {"name": "risk:public-surface", "color": "fbca04", "description": "External API / UX / public docs"},
    {"name": "risk:advisory-only", "color": "0e8a16", "description": "AI/advisory; must not mutate consensus"},
    {"name": "risk:ops-only", "color": "c5def5", "description": "Internal ops/CI only"},
    {"name": "risk:secrets-sensitive", "color": "000000", "description": "Credentials / keys / custody / private material"},
    # audience
    {"name": "audience:regulator", "color": "5319e7", "description": "Regulator / supervisory evidence"},
    {"name": "audience:institutional", "color": "1d76db", "description": "Exchange / bank / fund readiness"},
    {"name": "audience:developer", "color": "0075ca", "description": "Developer experience / contracts / SDK"},
    {"name": "audience:ops", "color": "0e8a16", "description": "Runbooks / SLO / incident"},
    # freeze
    {"name": "freeze:allowed", "color": "0e8a16", "description": "Allowed under Feature Freeze Candidate"},
    {"name": "freeze:exception-required", "color": "d93f0b", "description": "Needs formal freeze exception"},
    # governance / status
    {"name": "governance:founder-led", "color": "000000", "description": "Ownership / doctrine / authorship surface"},
    {"name": "status:blocked", "color": "b60205", "description": "Blocked on dependency"},
    {"name": "status:needs-review", "color": "fbca04", "description": "Awaiting institutional/technical review"},
]

MILESTONES: list[dict[str, Any]] = [
    {
        "title": "RC2_FREEZE",
        "state": "closed",
        "description": "Financial core freeze — settlement/ledger/validator/vault sole execution truth",
    },
    {
        "title": "AI_NATIVE_M5",
        "state": "closed",
        "description": "Native AI platform stabilized — advisory-only enforcement",
    },
    {
        "title": "PLATFORM_ALPHA_1",
        "state": "closed",
        "description": "Institutional baseline (2026-06-30) — gates green, contracts canonical",
    },
    {
        "title": "Feature Freeze Candidate",
        "state": "open",
        "description": "Maintenance/assurance mode — restricted product scope",
    },
    {
        "title": "PLATFORM_BETA_1",
        "state": "open",
        "description": "Unified OS design language across applications (target)",
    },
    {
        "title": "Angola Pilot",
        "state": "open",
        "description": "Controlled Angola deployment corridor (planned)",
    },
]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def gh_json(cmd: list[str]) -> Any:
    proc = run(cmd)
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def list_repos() -> list[str]:
    data = gh_json(["gh", "api", f"orgs/{ORG}/repos", "--paginate"])
    assert isinstance(data, list)
    names = []
    for repo in data:
        name = repo["name"]
        if name in ARCHIVE_NAMES:
            continue
        if name.endswith(ARCHIVE_SUFFIXES):
            continue
        if repo.get("archived"):
            continue
        names.append(name)
    return sorted(names)


def upsert_label(repo: str, label: dict[str, str], dry_run: bool) -> str:
    name = label["name"]
    if dry_run:
        return f"dry-run label {name}"
    # try create; on 422 update
    create = run(
        [
            "gh",
            "api",
            f"repos/{ORG}/{repo}/labels",
            "-f",
            f"name={name}",
            "-f",
            f"color={label['color']}",
            "-f",
            f"description={label['description']}",
        ],
        check=False,
    )
    if create.returncode == 0:
        return f"created label {name}"
    # update existing
    from urllib.parse import quote

    update = run(
        [
            "gh",
            "api",
            "-X",
            "PATCH",
            f"repos/{ORG}/{repo}/labels/{quote(name, safe='')}",
            "-f",
            f"new_name={name}",
            "-f",
            f"color={label['color']}",
            "-f",
            f"description={label['description']}",
        ],
        check=False,
    )
    if update.returncode == 0:
        return f"updated label {name}"
    return f"FAILED label {name}: {create.stderr or update.stderr}"


def upsert_milestone(repo: str, ms: dict[str, Any], dry_run: bool) -> str:
    title = ms["title"]
    if dry_run:
        return f"dry-run milestone {title}"
    existing = gh_json(
        [
            "gh",
            "api",
            f"repos/{ORG}/{repo}/milestones?state=all&per_page=100",
            "--paginate",
        ]
    ) or []
    found = next((m for m in existing if m.get("title") == title), None)
    if found is None:
        # GitHub rejects creating milestones already closed; create open then close.
        create = run(
            [
                "gh",
                "api",
                f"repos/{ORG}/{repo}/milestones",
                "-f",
                f"title={title}",
                "-f",
                "state=open",
                "-f",
                f"description={ms['description']}",
            ],
            check=False,
        )
        if create.returncode != 0:
            return f"FAILED milestone create {title}: {create.stderr}"
        created = json.loads(create.stdout)
        number = created["number"]
        if ms["state"] == "closed":
            close = run(
                [
                    "gh",
                    "api",
                    "-X",
                    "PATCH",
                    f"repos/{ORG}/{repo}/milestones/{number}",
                    "-f",
                    "state=closed",
                    "-f",
                    f"description={ms['description']}",
                ],
                check=False,
            )
            if close.returncode != 0:
                return f"FAILED milestone close {title}: {close.stderr}"
            return f"created+closed milestone {title}"
        return f"created milestone {title}"
    number = found["number"]
    update = run(
        [
            "gh",
            "api",
            "-X",
            "PATCH",
            f"repos/{ORG}/{repo}/milestones/{number}",
            "-f",
            f"title={title}",
            "-f",
            f"state={ms['state']}",
            "-f",
            f"description={ms['description']}",
        ],
        check=False,
    )
    if update.returncode == 0:
        return f"updated milestone {title}"
    return f"FAILED milestone update {title}: {update.stderr}"


def sync_repo(repo: str, dry_run: bool) -> list[str]:
    notes = [f"## {repo}"]
    for label in LABELS:
        notes.append(upsert_label(repo, label, dry_run))
    for ms in MILESTONES:
        notes.append(upsert_milestone(repo, ms, dry_run))
    return notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo", action="append", default=[], help="Limit to one or more repos")
    args = parser.parse_args()

    repos = args.repo or list_repos()
    # always include .github org profile repo when syncing all
    if not args.repo and ".github" not in repos:
        repos.append(".github")

    failures = 0
    for repo in repos:
        print(f"\n=== syncing {ORG}/{repo} ===", flush=True)
        try:
            for line in sync_repo(repo, args.dry_run):
                print(line, flush=True)
                if line.startswith("FAILED"):
                    failures += 1
        except Exception as exc:  # noqa: BLE001
            print(f"FAILED repo {repo}: {exc}", flush=True)
            failures += 1

    print(f"\nDone. failures={failures} repos={len(repos)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
