# E008 · Independent labels throughout memory acquisition

E003/E004 relabel the completed memory and held-out queries. E008 tests
whether independently relabeling inputs from the start of acquisition
changes the result. It is a follow-up to the observed E003 failure.

Use all six E002 seeds and exactly the same original graph pools.
Apply the E003 per-case permutation to every graph in every pool,
including initial examples, backgrounds, supplements, and holdouts.
Preserve graph identities, roles, graph ordering, family tags, seed,
and budget. Initial examples use exact solutions to the renamed
graphs. The model generates its own answers to each renamed attempted
task. Run only the random/model and targeted/model arms, in the same
relative order as E002, with two solve calls and one held-out call each.
Use the pinned Qwen3 8B digest and settings. This gives 36 live calls.

Compare final scores by family and the targeted-minus-random policy
contrast with the original-label E002 cells and frozen-memory,
independent-both E004 cells. The comparison estimates the policy
effect when representation changes throughout the pipeline. Because
admitted cases can differ, it is not a fixed-memory label effect.
Report six per-seed scores and the family-level attempts, admissions,
evictions and final memories. Reconstruct all inputs and scores from
the trace before interpreting results. This check remains conditional
on the original graph motifs and on Qwen3 8B.
