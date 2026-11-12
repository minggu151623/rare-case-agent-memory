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
