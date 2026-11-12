# E010 · Single-query Gemma readout

All 36 local calls completed in 104.4 seconds of request time. All
responses had the expected outer format and included the requested
query ID. No separate reasoning content was returned. Offline replay
reconstructed the exact prompts and reproduced every score.

| Labels | Random memory | Targeted memory |
| --- | ---: | ---: |
| Original | 1/6 | 4/6 |
| Independent memory and query | 1/6 | 0/6 |
| Shared derangement | 1/6 | 3/6 |

The targeted-minus-random gap was +3/6 with the original labels,
-1/6 under independent relabeling, and +2/6 under the shared
derangement. The direction agrees with the Qwen batched readout
in these three conditions. Gemma read the same frozen Qwen-generated
examples and only the first key-detour item from each seed. E010
changes the task count per call after E006 exposed omissions. It
supports a directional comparison for this subset. It does not
replicate acquisition, the five-cell factorial effects, or E009's
matched-marginal control on a second model.

[Per-seed scores](results/aggregate.json) · [Raw responses](results/gemma-e4b)
