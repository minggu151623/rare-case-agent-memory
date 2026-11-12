# E002 · Paired admission mechanism results

Protocol commit a10427f. Inference runner commit f8957be. Ollama 0.40.12,
qwen3:8b digest
500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41.
Six seeds ran all 84 calls locally, totaling 122,297 prompt tokens and
8,193 output tokens over 714.6 seconds of request time. All responses
had valid outer JSON. The trace audit replayed all calls, verified the
split boundaries and checked the stage counts and held-out scores.
An independent graph-relaxation check agreed with BFS on all 150 E002
graphs. The 36 earlier graphs and 150 E002 graphs have distinct structural
keys.

## Locked primary contrasts

| Contrast | Paired differences in seed order | Mean | Two-sided sign-flip sensitivity |
| --- | --- | ---: | ---: |
| Final unreachable examples, targeted oracle minus targeted model | 1, 1, 1, 0, 1, 0 | +0.667 examples | 0.125 |
| Final rare macro accuracy, targeted model minus random model | 1/2, 0, 0, 0, 1/2, 1/3 | +22.22 percentage points | 0.250 |

The sign-flip calculation assumes sign exchangeability and uses six
paired trajectories, not the number of individual tasks. With four
nonzero differences in the first contrast and three in the second, the
sensitivity values are coarse. Report both effects as observations in
this controlled setting.

## Where coverage and accuracy diverged

No unreachable attempt passed the model-answer verifier in any arm
(0/17 attempt records across arms and rounds, with tasks shared across
conditions). The targeted oracle condition admitted four unreachable
supplements and retained five unreachable examples across the six final
memories, versus one in targeted model. The two conditions both scored
0/18 on held-out unreachable tasks. Random/model achieved 3/18, so this
study does not show the model was uniformly incapable of that family.
Targeted/model improved key-detour accuracy from 7/18 under random/model
to 18/18. Its rare macro gain therefore coexisted with an unreachable
accuracy decrease from 3/18 to 0/18. Frozen memory achieved 16/18 on
key detour and 0/18 on unreachable. Empty memory achieved 7/18 and 0/18.

This study isolates access to exact supplement answers and tests a
matched allocation contrast with fixed background tasks. It does not
estimate drift under free-form model generation. The generator rejects
isomorphic repeats but uses fixed node roles and shared path templates.
An independent node-label robustness check is needed before framing
the key-detour result as generalization beyond these templates. The
coverage contrast is a policy effect because adaptive targeted choices
can change after an earlier admission.

[Aggregate report](results/aggregate.json) · [Seed-level evidence](results/qwen3-8b)
