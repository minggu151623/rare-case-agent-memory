# Findings

[E000](experiments/E000-oracle-smoke/analysis.md) passed nine local checks
of the exact planning oracle and scorer.

[E001a and E001b](experiments/E001-memory-coverage/analysis.md) completed 19
local Qwen3 8B calls each. E001a exposed invalid proposal IDs. With a clearer
prompt and a menu-constrained output schema, E001b exercised all three
memory policies. Across those trajectories, unreachable tasks were
attempted seven times and never admitted. FIFO evicted the initial example
of that family in every arm. Total rare coverage still increased, driven by
key-detour examples. All three arms ended at 2/4 on the rare holdout.

The runs establish feasibility and motivate per-family auditing.
H1 (coverage drift) and H2 (targeted supplementation) remain pending.

[E002](experiments/E002-admission/analysis.md) completed and replayed all
84 model calls over six paired seeds. Supplying an exact supplement
answer increased targeted final unreachable coverage by 0.67 examples
on average. Both targeted arms scored 0/18 on held-out unreachable
tasks. Targeted model exceeded random model by 22.2 percentage points
in rare macro accuracy through key-detour gains, alongside an
unreachable accuracy decrease. The inference is restricted to the
tested model and graph templates. The report preserves both locked
contrasts and all seed-level evidence.

[E003](experiments/E003-transfer/analysis.md) replayed 36 calls on three
frozen memories per seed. Targeted/model key-detour accuracy went from
18/18 on the original graphs to 1/18 after vertex renaming. It scored
9/18 on fresh motifs compared with 10/18 for random/model. The paper
reports the gain in the original representation together with this
transfer failure. The free-form H1 question remains outside the study.

The extended [E004](experiments/E004-representation/analysis.md) study
shows losses after either one-sided label change, and partial recovery
under a shared derangement (12/18 targeted, 2/18 random).
[E005](experiments/E005-fifo-null/analysis.md) gives an exact FIFO
absence probability under stationary independent attempts.
[E007](experiments/E007-error-audit/analysis.md) finds zero exact
literal path repeats among the 17 lost targeted key-detour answers.

[E008](experiments/E008-end-to-end/analysis.md) varied labels throughout
acquisition and evaluation. Key-detour accuracy was 3/18 random and
2/18 targeted. Starting acquisition with independently labeled
graphs did not restore the targeted advantage observed under E002's
original labels.

[E009](experiments/E009-matched-labels/analysis.md) matched each graph's
exact rendered forms across conditions. Shared labeling increased the
targeted-minus-random gap by 19.4 points on average, with reversals
in two of six seeds. [E006](experiments/E006-cross-model/analysis.md)
showed that Gemma answered only the first query in all 60 batch calls.
In [E010](experiments/E010-single-query/analysis.md) it answered all
single queries. On those same six cases, the Qwen batch and Gemma
single-query policy gaps were positive under original and shared labels.
Under independent labels Qwen tied and Gemma favored random. This is
a qualitative readout check with frozen Qwen memories.

[E011](experiments/E011-manuscript-audit/analysis.md) found that a
generator-aware constant path solved all 18 original detours and none of
the 18 fresh E003 key-required graphs before vertex renaming. E002
attempted 12 rare supplements with targeted allocation versus three
under the reference-mixture control. E012 locks a matched rare-only
budget, and E013 locks a fixed-label holdout with varied optimal paths.

[E012](experiments/E012-rare-only/analysis.md) reran both model-answer
policies with 12 rare supplements each. Adaptive scored 18/18 key detours
and balanced rare-only random scored 16/18, with both at 0/18 unreachable.
The +5.6-point rare macro gap came from a single seed. This is limited
evidence for an adaptive advantage over the matched control.

[E013](experiments/E013-diverse-paths/analysis.md) kept the original
vertex convention and replaced 18 detours with graphs requiring nine
distinct optimal paths. The best fixed path dropped from 18/18 to
2/18. With frozen memories, adaptive scores went from 18/18 to 7/18,
balanced rare-only from 16/18 to 5/18, and reference-mixture random
from 7/18 to 3/18. The adaptive gap against mixture narrowed by 38.9
points, while the two-answer gap against the matched control came from
the same one seed on both batches. This is a readout study at fixed
labels, with acquisition on the original graph distribution.

The [Lean 4 formalization](formal/README.md) proves the FIFO absence
threshold, the finite i.i.d. law, the zero-admission case, and the
positive-rate limit. The list-level FIFO characterization holds
for any admission history. The probability result applies to E005's
reference law with independent attempts and constant weights.
