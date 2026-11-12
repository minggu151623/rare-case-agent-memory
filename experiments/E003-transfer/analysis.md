# E003 · Label and motif transfer results

The pre-inference protocol and offline generator adjustment are recorded
in commits 9352195 and 0c53a6c. E003 completed 36 local calls across the
six archived E002 seeds, using 68,436 prompt tokens and 5,202 output
tokens in 467.2 seconds of request time. Every response had valid outer
JSON. Replay regenerated all test prompts and relabeled memories and
reproduced every item-level score. Separate checks confirmed the
intended path and lock invariants on all 54 new graphs.

Each cell below is exact accuracy out of 18 tasks. The first two rows for
an arm use the same graphs, with independent vertex permutations in
the second row.

| Arm | Condition | Ungated | Key detour | Unreachable |
| --- | --- | ---: | ---: | ---: |
| Random / model | Original | 18 | 7 | 3 |
| Random / model | Renamed | 9 | 2 | 0 |
| Random / model | New motifs | 9 | 10 | 0 |
| Targeted / model | Original | 18 | 18 | 0 |
| Targeted / model | Renamed | 11 | 1 | 0 |
| Targeted / model | New motifs | 11 | 9 | 0 |
| Targeted / oracle | Original | 17 | 17 | 0 |
| Targeted / oracle | Renamed | 7 | 0 | 0 |
| Targeted / oracle | New motifs | 10 | 9 | 0 |

The targeted/model minus random/model key-detour gap changed from
+11/18 to -1/18 after renaming and was also -1/18 on new motifs.
Within targeted/model, 17 of 18 originally correct key-detour answers
became incorrect after renaming. Targeted/oracle lost all 17 originally
correct key-detour answers. Random/model lost six correct answers and
gained one. These contrasts concern the displayed graphs and examples.
They do not identify whether relabeling the memory examples or the
held-out graphs contributed more. The new motifs also use a fresh test
draw, and the key-required motif removes the need to revisit a vertex.
Its score measures transfer to a different task construction.

[Aggregate and paired seed results](results/aggregate.json) ·
[Raw responses and item scores](results/qwen3-8b)
