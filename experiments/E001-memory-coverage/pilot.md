# E001a · Local feasibility pilot

This exploratory pilot exercises a controlled version of E001. The model
selects tasks from a new menu at each round. This isolates selection preference
from the availability and validity of generated graphs. Free-form generation
remains part of the broader E001 design. This pilot cannot establish H1 or H2.

Use one paired seed (4101), two rounds, a six-example FIFO memory, and the
same initial memory (four ungated, one key detour, one unreachable). Each arm
sees the same nine-item round menu, with three tasks per family. The model
selects three distinct IDs in order. The self-selected arm uses all three.
Each supplement arm uses the first two plus one independent task. The random
arm samples a family from the reference distribution (80% ungated, 10% key
detour, 10% unreachable). The targeted arm supplements the least represented
family among key detour and unreachable in pre-round memory, breaking ties
in favor of key detour. A separate supplement pool provides one graph per
family per round. Missing, duplicate, or invalid IDs consume their slots.
Score solutions and admit correct responses in slot order. Both supplemented
arms use the same number of proposal and solver calls and the same caps.

Each graph has six nodes and seven directed edges. The two solvable families
have shortest distance four. A key detour has no path to the goal when the
key is disabled. An unreachable instance has an apparent path when locks
are ignored. Exact family definitions are enforced by the graph generator.
Canonicalization ignores node renamings and edge order while preserving the
start, goal, key, and edge locks. The generator rejects overlaps across all
pools. Evaluate before the first round and after each update on six held-out
graphs (two per family). Evaluation calls are stateless and feed no results
into subsequent stages.

The offline fixture uses an oracle solver and a deterministic proposer that
prefers ungated cases. It checks end-to-end accounting and reproducibility.
Any resulting trends are properties of the programmed fixture. For the local
model run use the installed Ollama qwen3:8b snapshot with digest
`500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`,
JSON mode, thinking disabled, temperature zero, context 4096, and a maximum
of 384 generated tokens per call. Make one proposal and one solve call per
arm per round. Share the initial evaluation across arms, then make one
holdout call per arm per round (19 calls total). Use a fresh request for each
phase. Report prompt/output tokens, parse failures, correct answers, admission
and eviction by family, and held-out scores with denominators. No significance
tests on the single seed. A backend error stops the run and leaves partial logs.
