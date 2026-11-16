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

[E014](experiments/E014-publication-audit/analysis.md) is a post hoc
offline audit. Memories that still held a key-detour example answered
80/87 original key-detour queries and memories without one 9/39. The
frozen memory scored 16/18 and the empty memory 7/18, the same as the
reference-mixture arm, which lost the example in four of six seeds.
Most of the E002 policy gap is therefore retained coverage. Sixteen of
17 memories holding an unreachable example scored 0/3. The three
correct unreachable answers in the mixture arm come from one seed
where the model declared all six rare queries unreachable. The E009
sign-flip value over 64 assignments is 0.50. All 42 archived update
trajectories conform to the Lean FIFO characterization, and all 32
family losses occurred without a new admission from that family.

The Lean development now also proves that the reference law is
normalized, that the absence value lies in the unit interval under
valid weights, and Section 4's proposal-share threshold. Sixteen
exported statements use only the three standard axioms.

[E015](experiments/E015-confirmatory/analysis.md) is the confirmatory
experiment: 30 fresh seeds, four rounds, key-detour routes diversified
in every pool, one query per call, protocol committed first. The
primary retention contrast was not confirmed. The frozen memory scored
55/90 on key detours and the reference-mixture memory 51/90 (+4.4
points, bootstrap interval −5.6 to +13.3, exact sign-flip 0.51),
although the mixture arm kept a key-detour example in only 6 of 30
seeds. The empty memory scored 53/90. Adaptive minus balanced rare
accuracy was −1.7 points (Holm 0.51) and the label interaction −5.0
points (Holm 0.36). Descriptively, a retained example helped when it
stored the query's optimal path (29/32, against 116/208 with another
path and 129/210 with none). No unreachable answer was correct (0/450),
no unreachable attempt was admitted (0/208), and the model never
declared a task unreachable. The adaptive rule spent 84 of 120
supplements on that family. All 90 trajectories conform to the Lean
FIFO characterization.

The E002 gap is therefore best described as retention of a reusable
answer path on the original holdout. Retention as a general benefit, an
adaptive advantage over a matched rare-only budget, and the E009 label
interaction are not established.

[E016](experiments/E016-second-model/analysis.md) repeats the E015
comparison with Gemma 4 E4B as the acquisition model, on the same 30
seeds, one task per call, protocol committed first. Retention is not
confirmed for Gemma either: frozen 47/90 and reference mixture 55/90 on
key detours (−8.9 points, interval −21.1 to +3.3, exact sign-flip
0.24). Adaptive minus balanced rare accuracy is +1.7 points (0.38).
Rare-enriched updating scored below mixture updating with Gemma and
above it with Qwen3, and neither ordering is established. Gemma never
declared an asked task unreachable. With the query's path stored it
answered 25/36, against 21/36 for the empty memory on the same queries.
Comparisons with Gemma's empty memory depend on a scoring rule fixed in
the protocol. All 90 trajectories conform to the FIFO characterization,
222 in total.
