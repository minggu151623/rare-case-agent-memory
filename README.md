# Auditing Rare-Case Coverage in LLM Agents with Iterative Example Memory

We study whether an LLM agent's example memory loses coverage of rare planning
tasks over successive updates, where losses occur, and whether targeted
supplementation improves rare-case accuracy at the same budget as random
supplementation. The agent's model weights are fixed.

- [Research state](research-state.yaml), [decision log](research-log.md), and
  [findings](findings.md)
- [Related work and positioning](literature/survey.md)
- [E000 CPU oracle check](experiments/E000-oracle-smoke/protocol.md)
- [E001 LLM pilot design](experiments/E001-memory-coverage/protocol.md)

Run the oracle check from the repository root with Python 3.10 or later.
It uses the standard library and runs locally.

```sh
python3 -m unittest discover -s experiments/E000-oracle-smoke -v
```

The LLM pilot remains planned. The CPU check validates benchmark mechanics.

## E001 feasibility pilots

Run the fixed offline fixture and its regression checks from the repo root.

```sh
python3 -m unittest discover -s experiments/E001-memory-coverage -v
python3 -m src.pilot --output local-runs/fixture
```

For local model inference, point the same runner at a loopback Ollama server
with the pinned qwen3:8b digest specified in the
[E001a protocol](experiments/E001-memory-coverage/pilot.md). The current runner uses
the proposal schema from [E001b](experiments/E001-memory-coverage/pilot-b.md).

```sh
python3 -m src.pilot --ollama-port 11434 --output local-runs/qwen3-8b
```

Each run needs a fresh output directory. The runner writes a per-call JSONL
trace and a summary with per-family counts. Keep the trace and holdout cases
away from future agent memory. Both pilots use a controlled proposal menu.
See [feasibility results](experiments/E001-memory-coverage/analysis.md).
