#!/usr/bin/env python3
"""Inspect the rendered Compose config. Does not start containers.

A passing result is STATIC / RENDERED only. It is not a runtime isolation pass.
The deployment-not-authorized profile is a startup safeguard, not the boundary.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPOSE = ROOT / "docker-compose.synthetic.yml"
ENV_FILE = ROOT / "synthetic.env.example"
REVIEW = ROOT / "rendered-config-review.json"

ALLOWED_ENV = {
    "synthetic-local-only",
    "sqlite:////data/ledger-staging.db",
    "/data/node-api-staging.db",
    "/data/settlement-store.db",
    "/data/settlement-security.db",
    "/data/ciel-staging.key",
    "http://ledger:8086",
    "http://settlement-engine:8087",
    "true",
}
EXPECTED = {
    "ledger": {"port": "8086", "volume_suffix": "cubeshackles-staging-ledger"},
    "settlement-engine": {"port": "8087", "volume_suffix": "cubeshackles-staging-settlement"},
    "node-api": {"port": "8000", "volume_suffix": "cubeshackles-staging-node-api"},
}


def compose_config(profile: bool) -> dict:
    command = [
        "docker",
        "compose",
        "--env-file",
        str(ENV_FILE),
        "-f",
        str(COMPOSE),
        "--project-directory",
        str(ROOT),
    ]
    if profile:
        command.extend(["--profile", "deployment-not-authorized"])
    command.extend(["config", "--format", "json"])
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "docker compose config failed")
    return json.loads(completed.stdout)


def review_service(name: str, service: dict) -> dict:
    environment = service.get("environment") or {}
    unexpected = sorted(key for key, value in environment.items() if value not in ALLOWED_ENV)
    ports = service.get("ports") or []
    volumes = service.get("volumes") or []
    networks = list((service.get("networks") or {}).keys())
    expected = EXPECTED[name]
    problems: list[str] = []
    if unexpected:
        problems.append(f"unexpected env values: {unexpected}")
    if service.get("extra_hosts"):
        problems.append("extra_hosts is set")
    if networks != ["cubeshackles-staging"]:
        problems.append(f"networks {networks}")
    if len(ports) != 1 or ports[0].get("host_ip") != "127.0.0.1" or str(ports[0].get("published")) != expected["port"]:
        problems.append(f"ports {ports}")
    if len(volumes) != 1 or volumes[0].get("type") != "volume" or volumes[0].get("target") != "/data":
        problems.append(f"volumes {volumes}")
    source = str(volumes[0].get("source", "")) if volumes else ""
    if not source.endswith(expected["volume_suffix"]):
        problems.append(f"volume source {source}")
    context = str((service.get("build") or {}).get("context", ""))
    if not context.endswith("synthetic-local-only"):
        problems.append("build context is not the placeholder")
    return {
        "environment_keys": sorted(environment),
        "host_ip": ports[0].get("host_ip") if ports else None,
        "published_port": str(ports[0].get("published")) if ports else None,
        "volume_type": volumes[0].get("type") if volumes else None,
        "volume_target": volumes[0].get("target") if volumes else None,
        "named_volume": source.endswith(expected["volume_suffix"]),
        "network": networks,
        "profiles": service.get("profiles") or [],
        "inherited_dockerfile": (service.get("build") or {}).get("dockerfile"),
        "build_context_published": False,
        "problems": problems,
    }


def main() -> int:
    overrides = sorted(
        path.name
        for path in ROOT.iterdir()
        if path.name.startswith(("docker-compose", "compose.")) and path.suffix in {".yml", ".yaml"}
    )
    try:
        default = compose_config(profile=False)
        rendered = compose_config(profile=True)
    except (RuntimeError, FileNotFoundError) as error:
        print(f"RENDERED_CONFIG = NOT PRODUCED ({error})")
        print("RUNTIME_ISOLATION = NOT VERIFIED")
        return 2
    services = rendered.get("services") or {}
    reviewed = {name: review_service(name, services[name]) for name in EXPECTED if name in services}
    missing = sorted(set(EXPECTED) - set(services))
    network = (rendered.get("networks") or {}).get("cubeshackles-staging") or {}
    problems = [item for spec in reviewed.values() for item in spec["problems"]]
    if missing:
        problems.append(f"missing services {missing}")
    if list(default.get("services") or {}) != []:
        problems.append("default config renders services; the profile is not holding them")
    if network.get("internal") is not True:
        problems.append("staging network is not internal")
    if network.get("external"):
        problems.append("staging network is external")
    document = {
        "status": "RENDERED_CONFIG = PASS (REPORTED)" if not problems else "RENDERED_CONFIG = FAIL",
        "runtime_isolation": "NOT VERIFIED",
        "containers_started": False,
        "profile_is_a_safeguard_not_a_boundary": True,
        "override_files_in_directory": overrides,
        "default_config_services": sorted((default.get("services") or {}).keys()),
        "network_internal": network.get("internal") is True,
        "network_external": bool(network.get("external")),
        "services": reviewed,
        "problems": problems,
    }
    REVIEW.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(document["status"])
    print("RUNTIME_ISOLATION = NOT VERIFIED")
    print(f"default services: {document['default_config_services']}")
    print(f"override files: {overrides}")
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
