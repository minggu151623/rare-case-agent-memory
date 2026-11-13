# E013 · Diverse optimal paths with the original label convention

## Question

Does the original targeting advantage persist when no fixed path solves
most key-detour queries? E003 changed both graph motifs and vertex names.
This study keeps the E002 label convention while changing the optimal
paths in the held-out key-detour queries.

## Design

For each of the six E002 seeds, compare the original nine-query batch to a
batch that replaces only its three key-detour graphs. Keep the query IDs
and positions, ungated and unreachable queries, start A, goal B, key C,
labels A–F, six nodes, seven directed edges, shortest length four and
key necessity. Generate the replacement detours with the backbone
A→X→C→Y→B, locking the last edge, and sample three additional unlocked
directed edges without replacement. Reject candidates unless all nodes
appear, the key is required, and the backbone is the unique optimal
path. Reject structural isomorphs with E001, E002, E003 fresh graphs and
other E013 replacements.

Use each ordered pair (X,Y) from {D,E,F}² twice across the 18 replacements.
In each seed include one return detour (X=Y) and two distinct through
detours. Shuffle the three return pairs and six through pairs separately
in two blocks of three seeds, using one Random(613000) schedule generator.
Shuffle the three assignments within each seed. Sample extra edges and
their order with Random(seed + 613100). Verify exact constant-path
coverage on original and replacement detours by enumeration. This
is a controlled change in the evaluation distribution; it changes
topology and the mix of return and through routes within this family.

For each seed freeze the archived E002 random-mixture/model memory and
the two new E012 model memories. Before inference, replay both source
archives. Cross all three memories with both query batches, rerunning
the original batches in the same Qwen3 8B / Ollama 0.40.12 session.
Use six calls per seed (36 total), with call order shuffled by
Random(seed + 613200). Keep E002 batch prompts, scoring, seed, and decoding
options. Check frozen prompts against source memory records. Preserve
partial logs on transport failure and retry the entire same seed in
a new directory. Invalid or missing answers score zero.

## Analysis

Primary contrast is the change from original to varied-path batches in
the targeted-minus-mixture accuracy gap for key detours. Report both
gaps and the signed varied-minus-original change with six paired seed
differences, their mean, and exact two-sided sign-flip sensitivity.
Secondary contrast uses the matched rare-only arm in place of mixture.
Show all family counts and paired contrasts, plus constant-path
coverage. The held-out replacements test transfer from frozen
memories with the original acquisition distribution. Any change can
reflect the evaluation distribution and the interaction with these
memories. Do not infer that the model did or did not copy paths.
