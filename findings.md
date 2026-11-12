# Findings

[E000](experiments/E000-oracle-smoke/analysis.md) passed nine local checks
of the exact planning oracle and scorer.

[E001a and E001b](experiments/E001-memory-coverage/analysis.md) completed 19
local Qwen3 8B calls each. E001a exposed invalid proposal IDs. With a clearer
prompt and a menu-constrained output schema, E001b exercised all three
memory policies. Across those trajectories, unreachable tasks were
attempted seven times and never admitted. FIFO evicted the initial example
of that family in every arm. Total rare coverage still increased, driven by
key-detour examples. All three arms ended at 2/4 on the rare holdout.

The runs establish feasibility and motivate per-family auditing.
H1 (coverage drift) and H2 (targeted supplementation) remain pending.
