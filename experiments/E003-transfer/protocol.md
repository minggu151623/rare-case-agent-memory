# E003 · Transfer after renaming vertices and changing motifs

E002 used structurally distinct graphs with fixed node labels and
generator backbones. E003 is a post-E002 robustness check on frozen
final memories. It does not rerun memory acquisition.

Use all six E002 seeds, the same installed Qwen3 8B digest and inference
settings, and three frozen memories per seed: random/model,
targeted/model and targeted/oracle. Recover each memory directly from
its archived final-evaluation prompt. For each memory make two calls:

1. Rename each graph's six vertices independently using a seeded
   bijection of A–F, including graphs and paths in memory. Rename
   the original nine held-out graphs by independent bijections.
   Keep graph identities, answer semantics, order and model seed.
   Use the same renamed test instances across arms.
2. Use the same renamed memory and nine new, renamed graphs (three
   per family). The ungated backbone branches through two
   equal-length routes of length four. The key-required solvable
   backbone has a shortest path of length four that collects the
   key without revisiting a node. The unreachable backbone puts
   the key beyond a lock. All graphs have six nodes and seven edges.
   Require no repeated structural key across E001, E002 and the new
   graphs. Share new test instances across arms within a seed.

Use independent data RNG streams with seed offsets 210000 for
renaming and 310000 for new-graph generation. Draw no data-dependent
samples. Complete exactly 36 evaluation calls (no memory updates).
Set context 4096, output cap 384 and use the E002 final-evaluation
sampling seed (trajectory seed + 2). Check matched original and
renamed tasks with the same verifier and record raw response,
token counts and correctness per instance.

Primary robustness quantities are the three arms' changes in
key-detour accuracy under the renaming contrast and the targeted/model
minus random/model key-detour gap under each condition. Also report
unreachable counts and the three-family scores with denominators. A
large loss under renaming would establish prompt sensitivity in this
setup. The new-motif contrast combines an independent test draw and a
topology change, and should be described as transfer rather than a
causal effect of topology alone. Treat all results as a diagnostic for
this model and the archived memories.

Offline feasibility adjustment before inference. The first ungated
backbone exhausted structurally unique draws after three seeds. The
ungated generator now samples one of three equivalent-length branch
positions before adding a distractor. This preserves graph size,
two shortest routes, and the locked transfer estimands.
