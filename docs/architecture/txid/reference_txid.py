#!/usr/bin/env python3
"""Investigation-only tx1 encoder.

This is not a service module and it is not wired into node-api, settlement,
or the ledger. Gate 3 implementation is not authorized.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path

ENCODING_ID = "cs-txid-v1-length-prefix"
PREIMAGE_LABEL = b"CS-TXID-v1\x00"
NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
PRINCIPAL_RE = re.compile(r"^(citizen|institution):[A-Za-z0-9._:-]{1,128}$")
KEY_RE = re.compile(r"^[A-Za-z0-9._:-]{22,128}$")
TX1_RE = re.compile(r"^tx1\.[a-z][a-z0-9_-]{0,31}\.[a-z2-7]{32}$")
V0_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
FUTURE_RE = re.compile(r"^tx([2-9]|[1-9][0-9]+)\.")


class TxIdRejection(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _field(value: str) -> bytes:
    raw = _nfc(value).encode("utf-8")
    return len(raw).to_bytes(4, "big") + raw


def preimage(namespace: str, principal: str, idempotency_key: str) -> bytes:
    return PREIMAGE_LABEL + _field(namespace) + _field(principal) + _field(idempotency_key)


def base32_lower(digest: bytes) -> str:
    return base64.b32encode(digest).decode("ascii").rstrip("=").lower()


def derive(namespace: str, principal: str, idempotency_key: str) -> str:
    namespace = _nfc(namespace)
    principal = _nfc(principal)
    idempotency_key = _nfc(idempotency_key)
    if not NAMESPACE_RE.fullmatch(namespace):
        raise TxIdRejection("namespace_rejected")
    if not PRINCIPAL_RE.fullmatch(principal):
        raise TxIdRejection("principal_rejected")
    if not KEY_RE.fullmatch(idempotency_key):
        raise TxIdRejection("idempotency_key_rejected")
    digest = hashlib.sha256(preimage(namespace, principal, idempotency_key)).digest()
    return f"tx1.{namespace}.{base32_lower(digest)[:32]}"


def classify(value: str) -> str:
    if TX1_RE.fullmatch(value):
        return "tx1"
    if FUTURE_RE.match(value):
        return "future-version"
    if value.startswith("tx1.") or value.startswith("tx2."):
        return "ambiguous"
    if V0_RE.fullmatch(value):
        return "rc2a-v0"
    return "unknown"


def birthday_bound(transactions: int, bits: int = 160) -> str:
    """Approximate collision probability n(n-1)/2^(bits+1)."""
    if transactions < 2:
        return "0"
    log10_p = (
        math.log10(transactions)
        + math.log10(transactions - 1)
        - math.log10(2) * (bits + 1)
    )
    return f"1e{log10_p:.1f}"


def vector_cases() -> list[dict[str, str]]:
    key = "stg-idem-key-0001-aaaa"
    return [
        {
            "name": "c1-canonical",
            "namespace": "retail",
            "principal": "citizen:stg_acct_payer_001",
            "idempotency_key": key,
        },
        {
            "name": "c2-domain-a",
            "namespace": "ab",
            "principal": "citizen:c",
            "idempotency_key": "stg-idem-key-0002-bbbb",
        },
        {
            "name": "c2-domain-b",
            "namespace": "a",
            "principal": "citizen:bc",
            "idempotency_key": "stg-idem-key-0002-bbbb",
        },
        {
            "name": "c3-institution",
            "namespace": "institutional",
            "principal": "institution:stg_inst_001",
            "idempotency_key": "stg-idem-key-0003-cccc",
        },
    ]


def rejection_cases() -> list[dict[str, str]]:
    return [
        {
            "name": "c3-display-name",
            "namespace": "retail",
            "principal": "citizen:Ada Lovelace",
            "idempotency_key": "stg-idem-key-0001-aaaa",
            "error": "principal_rejected",
        },
        {
            "name": "c3-phone",
            "namespace": "retail",
            "principal": "citizen:+244923000000",
            "idempotency_key": "stg-idem-key-0001-aaaa",
            "error": "principal_rejected",
        },
        {
            "name": "c4-low-entropy",
            "namespace": "retail",
            "principal": "citizen:stg_acct_payer_001",
            "idempotency_key": "short-key",
            "error": "idempotency_key_rejected",
        },
        {
            "name": "c2-separator-in-field",
            "namespace": "retail",
            "principal": "citizen:a|b",
            "idempotency_key": "stg-idem-key-0001-aaaa",
            "error": "principal_rejected",
        },
        {
            "name": "c3-non-ascii",
            "namespace": "retail",
            "principal": "citizen:acct\u00e9",
            "idempotency_key": "stg-idem-key-0001-aaaa",
            "error": "principal_rejected",
        },
    ]


def build_document() -> dict:
    vectors = []
    for case in vector_cases():
        vectors.append({**case, "transaction_id": derive(case["namespace"], case["principal"], case["idempotency_key"])})
    domain = [item for item in vectors if item["name"].startswith("c2-domain")]
    if domain[0]["transaction_id"] == domain[1]["transaction_id"]:
        raise SystemExit("domain-separation pair collided")
    return {
        "encoding_id": ENCODING_ID,
        "status": "RECOMMENDED — not founder-finalized and not implemented",
        "wire": "tx1.<namespace>.<base32rfc4648-nopad-lower(sha256(preimage))[:32]>",
        "preimage": "CS-TXID-v1 NUL, then u32be length and UTF-8 NFC bytes for namespace, principal, idempotency_key",
        "truncation_bits": 160,
        "birthday_approximation": {
            "1e9": birthday_bound(10**9),
            "1e12": birthday_bound(10**12),
        },
        "vectors": vectors,
        "rejections": rejection_cases(),
        "recognition": [
            {"id": vectors[0]["transaction_id"], "class": "tx1"},
            {"id": "idem-rc2a-example-key-0001", "class": "rc2a-v0"},
            {"id": "tx2.retail.abcdefghijklmnopqrstuvwxyz234567", "class": "future-version"},
        ],
    }


def main() -> None:
    document = build_document()
    destination = Path(__file__).with_name("vectors.json")
    destination.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    for case in document["rejections"]:
        try:
            derive(case["namespace"], case["principal"], case["idempotency_key"])
        except TxIdRejection as error:
            if error.code != case["error"]:
                raise SystemExit(f"{case['name']} expected {case['error']} got {error.code}")
        else:
            raise SystemExit(f"{case['name']} was accepted")
    for item in document["recognition"]:
        seen = classify(item["id"])
        if seen != item["class"]:
            raise SystemExit(f"{item['id']} class {seen} != {item['class']}")
    legacy = "idem-rc2a-example-key-0001"
    if legacy != legacy:
        raise SystemExit("re-key")
    print(destination)


if __name__ == "__main__":
    main()
