#!/usr/bin/env node
/**
 * Second implementation of the investigation encoder.
 * Reads vectors.json and checks every id. Does not write identity state.
 */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ALPHABET = "abcdefghijklmnopqrstuvwxyz234567";

function base32Lower(bytes) {
  let bits = 0;
  let value = 0;
  let out = "";
  for (const byte of bytes) {
    value = (value << 8) | byte;
    bits += 8;
    while (bits >= 5) {
      out += ALPHABET[(value >>> (bits - 5)) & 31];
      bits -= 5;
    }
  }
  if (bits > 0) out += ALPHABET[(value << (5 - bits)) & 31];
  return out;
}

function nfc(value) {
  return value.normalize("NFC");
}

function field(value) {
  const raw = Buffer.from(nfc(value), "utf8");
  const header = Buffer.alloc(4);
  header.writeUInt32BE(raw.length, 0);
  return Buffer.concat([header, raw]);
}

function derive(namespace, principal, idempotencyKey) {
  const preimage = Buffer.concat([
    Buffer.from("CS-TXID-v1\u0000", "utf8"),
    field(namespace),
    field(principal),
    field(idempotencyKey),
  ]);
  const digest = createHash("sha256").update(preimage).digest();
  return `tx1.${nfc(namespace)}.${base32Lower(digest).slice(0, 32)}`;
}

const document = JSON.parse(
  readFileSync(join(dirname(fileURLToPath(import.meta.url)), "vectors.json"), "utf8"),
);
for (const vector of document.vectors) {
  const got = derive(vector.namespace, vector.principal, vector.idempotency_key);
  if (got !== vector.transaction_id) {
    console.error(`${vector.name}\n expected ${vector.transaction_id}\n got      ${got}`);
    process.exit(1);
  }
}
console.log(`node verified ${document.vectors.length} vectors`);
