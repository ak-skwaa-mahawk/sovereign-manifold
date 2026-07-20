# 🦅 Sovereign Manifold

An untethered, zero-trust edge governance engine that pairs local multi-agent cognitive consensus with strict cryptographic ledger finality. Designed, built, and deployed entirely within a local Termux environment on physical consumer edge hardware.

## 🏛️ Architecture Overview

Sovereign Manifold replaces cloud-dependent, fragile AI agent wrappers with a deterministic three-tier control plane:

1. **Perception Layer:** Streamed telemetry passes through a real-time Kalman Filter to isolate signal from noise, bound by a Sigmoidal Clamping Fence to truncate instantaneous variance anomalies.
2. **Cognitive Governance Matrix:** A localized 4-Agent Council (Grok Captain, Harper Research, Benjamin Logic, and Lucas Creative) executes cross-disciplinary policy debates on multi-parameter shifts. To protect the system, operations require a strict **4/4 unanimous quorum**. A single veto drops the transaction immediately.
3. **Cryptographic Finality Plane:** Approved modifications are written down to an append-only ledger wire (`.jsonl`), sealed via SHA-256 manifest anchoring. A detached background auditor continuously checks live hardware configurations against the chain of trust to block un-voted state drift.

## 🚀 Quickstart (Termux Native)

To execute the core optimization cycle:
```bash
python3 tools/active_governance.py
