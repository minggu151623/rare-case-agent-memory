# E009 · Match each graph's label exposure across conditions

E004's shared and independent conditions differ in which permutations
were sampled for each graph as well as their consistency across graphs.
E009 controls the marginal permutations exactly.

Use the two archived E002 final model-answer memories and the same nine
queries per seed across all six seeds. With Random(seed + 510000),
choose two derangements of A-F. Reject the second unless its image
differs from the first at every vertex. Keep the two maps fixed within
a seed, for both arms and both conditions.

- Shared: apply map r to every graph in the memory and query list in
  repetition r, for r=0,1.
- Mixed: apply map (r+i) mod 2 to the graph at zero-based index i in
  each list, and map any stored answer with its graph. Thus every
  individual graph sees both maps once in each condition. Across
  graphs, shared prompts use a single map and mixed prompts alternate
  maps. This is a structured mixture of two mappings, rather than
  fully independent relabeling.

Use the same pinned Qwen3 8B snapshot and inference settings as E004.
The sample is six seeds x two arms x two conditions x two repetitions,
or 48 new calls. Use one fresh request per cell and preserve list
order, graph IDs, and exact memory composition. Audit the marginal
permutation match and replay every answer before comparing scores.

Primary outcome: on key-detour tasks, report the difference between
the targeted-minus-random gaps in shared and mixed conditions, in
percentage points. Also report each policy's shared-minus-mixed
contrast and all family counts. Average within each seed before
averaging across seeds. This protocol was motivated by E004, so it
is a diagnostic follow-up on the same tasks and memories.
