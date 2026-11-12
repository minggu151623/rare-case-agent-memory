# E004 · Which labels matter?

The runner completed 36 local calls using 68,493 prompt and 5,081
output tokens, with 555.1 seconds of request time and no outer-JSON
failures. Replay validated all 60 cells, including the 24 archived
responses from E002 and E003. Every prompt matched the reconstructed
graph and memory transformations.

| Labels | Random / model | Targeted / model | Targeted minus random |
| --- | ---: | ---: | ---: |
| Original memory and queries | 7/18 | 18/18 | +11/18 |
| Independently rename memory only | 3/18 | 3/18 | 0/18 |
| Independently rename queries only | 1/18 | 2/18 | +1/18 |
| Independently rename both | 2/18 | 1/18 | −1/18 |
| One shared derangement | 2/18 | 12/18 | +10/18 |

For targeted/model, the averaged memory and query main effects were
−44.4 and −50.0 percentage points, respectively. The interaction on
the accuracy scale was +77.8 points. Single-side changes already
took accuracy near the floor, so this positive interaction does not
show that independent changes are beneficial. For random/model,
the corresponding effects were −8.3, −19.4, and +27.8 points from
a lower original baseline.

Changing either side independently was sufficient to erase nearly
all of the original targeted advantage. A shared derangement
recovered most of the policy gap and some of the absolute targeted
accuracy. This contrast preserves the consistency of cross-graph
labels while removing the original tokens from each vertex. It
cannot distinguish role alignment from all other properties of a
shared mapping. The archived and newly collected responses are
distinct runs using the same pinned settings, not randomized
reruns of the original conditions.

[All families, per-seed counts and contrasts](results/aggregate.json)
· [Archived responses](results/qwen3-8b)
