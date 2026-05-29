# Protocol Overview

**A developer-facing description of the CubeShackles protocol.**

This document explains the protocol concepts at a level useful for engineers and
technical reviewers. It describes design and intent; where mechanisms are planned
rather than implemented, that is marked. Protocol logic itself lives in
`cubeshackles-core`.

---

## 1. What the protocol is for

The CubeShackles protocol provides **deterministic settlement and coordination**
for identity-aware economic activity, designed to work in low-connectivity,
sovereign environments. It is not a general-purpose smart-contract chain and not a
cryptocurrency clone. Its job is to settle and audit value and identity-bound
transactions reliably.

## 2. Core primitives

### Cube
A **Cube** is the canonical unit of state: a deterministic, hash-addressed record of
an economic and/or identity-aware event. Properties:

- **Deterministic** — its contents fully determine its hash/identity.
- **Immutable** — once committed, a Cube is never edited; new state is new Cubes.
- **Causal** — a Cube references its predecessors, establishing order.
- **Replayable** — applying Cubes in order reconstructs state exactly.

### Shackle
A **Shackle** is the constraint logic a Cube must satisfy to be valid. Shackles
express:

- settlement preconditions (e.g. balance, authorization),
- identity attestations (who may act),
- validator obligations,
- policy hooks.

Shackles are deterministic. Where policy involves AI (e.g. a fraud signal), the AI
decision is supplied as a **recorded input** to the Shackle — never executed inside
consensus. The Shackle's evaluation of that recorded input is deterministic.

### SmartShackle *(planned)*
A programmable Shackle that may reference AI hooks, model-execution triggers, GPU
compute references, and inference receipts. SmartShackles are intended to remain
advisory and verifiable, with a long-term path to **zk-verifiable AI outputs** so
that an inference can be trusted without trusting the machine that produced it.

## 3. The settlement DAG

State is organized as a **directed acyclic graph** of Cubes rather than a linear
chain:

- Each Cube points to one or more predecessor Cubes.
- Validators converge on a **deterministic ordering** of the DAG frontier.
- Deterministic ordering + deterministic execution ⇒ identical state on all honest
  validators.

### Why a DAG
- **Offline-first.** Subgraphs can extend locally during a partition and reconcile
  deterministically on reconnection — essential for Angola's connectivity reality.
- **Throughput.** Causal (not total) ordering allows concurrent progress where
  events are independent.

DAG optimization (compaction, indexing, pruning) is a performance concern handled
above the protocol and must never change settlement semantics.

## 4. Validator coordination

Validators:

1. join via `cubeshackles-network-orchestrator`,
2. sync by replaying history to a verified frontier,
3. propose and validate Cubes, applying Shackle rules,
4. participate in deterministic ordering,
5. optionally consume advisory signals (recorded as inputs),
6. degrade gracefully under resource pressure,
7. are evicted on misbehavior — with their actions remaining in the audit record.

The full lifecycle is described in
[`../SYSTEM_ARCHITECTURE.md`](../SYSTEM_ARCHITECTURE.md).

## 5. Determinism, replay, audit

These three properties are the heart of the protocol:

- **Determinism** — no wall-clock, no unordered iteration, no vendor-specific math
  in consensus paths.
- **Replay** — genesis + ordered DAG reconstructs current state exactly.
- **Audit** — every Cube and validator action is attributable and observable through
  append-only, tamper-evident records.

## 6. Identity-aware transactions

Transactions are bound to identity attestations carried in Shackle conditions. This
supports regulator-grade auditability and compliance classification without placing
those decisions inside non-deterministic components — classification *signals* are
advisory; the *rules* applying them are deterministic.

## 7. Currency and offline support

- **African currency compatibility** is a first-class requirement (Kwanza and
  regional currencies).
- **Offline-first**: transactions can be captured without connectivity (e.g. via the
  phone wedge) and settled deterministically when the DAG reconciles.

## 8. Relationship to other layers

- The protocol does **not** contain AI. Intelligence is consumed as advisory signals
  from `kulifikila` / `ai-runtime` (planned), strictly outside consensus.
- The protocol does **not** assume specific hardware. Acceleration is provided by the
  compute/hardware layers behind an abstraction.

## 9. Status

Core primitives (Cube, Shackle), the DAG settlement model, and validator
coordination are under active development in the protocol-facing repositories.
SmartShackles, inference receipts, and zk-verifiable AI outputs are **planned**. See
[`../ROADMAP.md`](../ROADMAP.md) for sequencing.
