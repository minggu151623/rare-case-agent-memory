# E009 · Shared labels with matched graph exposures

All 48 Qwen3 calls completed, with 91,324 prompt tokens, 7,188 output
tokens, 800.1 seconds of request time, and no outer JSON failures.
Replay verified each prompt, score, and graph-level exposure match.

| Condition | Policy | Ungated | Key detour | Unreachable |
| --- | --- | ---: | ---: | ---: |
| Shared | Random | 33/36 | 10/36 | 0/36 |
| Shared | Targeted | 32/36 | 20/36 | 0/36 |
| Mixed | Random | 29/36 | 7/36 | 0/36 |
| Mixed | Targeted | 25/36 | 10/36 | 0/36 |

The key-detour policy gap was +10/36 under shared labels and +3/36
under mixed labels. Their difference was +7/36 (+19.4 percentage
points). Paired differences in correct counts out of six per seed
were +3, +6, -4, +2, -1, +1. Four seeds favored shared labels and
two favored mixed. Targeted scored 10 more correct with shared
labels, while random scored three more. The 36 instances per cell
are 18 underlying graphs shown twice. The seed remains the paired
unit. This diagnostic changes how labels are distributed across
graphs within a prompt, with each graph's exact two rendered forms
fixed. It does not resolve which cross-graph correspondences matter
or whether a smaller label advantage transfers beyond this generator.

[Full counts](results/aggregate.json) · [Raw calls](results/qwen3-8b)
