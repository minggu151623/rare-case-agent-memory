# E004 · Separate demonstration and query labels

Lock this follow-up before collecting new responses. The original E002
fixed labels can align semantic roles (start, goal and key) across
graphs. E003 changed both the demonstrations and the queries
simultaneously. Neither contrast identifies the source of the loss.

Use the six E002 seeds, same nine held-out graphs and two frozen
memories per seed (random/model and targeted/model). Use the exact
archived Qwen3 8B digest, Ollama version, inference seed, prompt template,
temperature, context and output cap used by E002 and E003. Reuse the
archived original/original and independently renamed/renamed cells.
Run these three new cells per arm and seed:

- Memory only: independently rename every graph in memory and its
  stored answer using the exact E003 maps. Queries retain original labels.
- Query only: keep memory labels fixed and apply the exact E003 maps
  to queries.
- Shared map: apply the same permutation to every memory and query
  graph and to stored solutions. Sample one derangement of A–F per seed
  using Python Random(seed + 410000), rejecting fixed points. Both arms
  share the map. This changes every vertex token while preserving
  cross-example label alignment.

This requires 36 new calls. These five cells preserve graph structure,
order, final memory composition and item identities. The shared-map
contrast does not isolate semantic role alignment from other properties
preserved by a common graph-wide relabeling. Report it as a diagnostic
for whether a consistent label system rescues the original advantage.
Do not infer the model's internal algorithm from behavioral scores.

The primary family is key detour because the E002 arm gap was largest
there. Report exact counts for all families, per-seed paired key-detour
scores, and the targeted-minus-random gap in each cell. Calculate the
memory main effect as half the sum of the two changes when memory is
renamed, and the query main effect analogously. Report the difference
of differences as the interaction on the accuracy scale. Use six
trajectory seeds as the units, preserving the pairing. The design was
chosen after observing E002/E003. Treat follow-up statistics as
diagnostic. Reconstruct each prompt and score from the raw response
before using any count in the manuscript.
