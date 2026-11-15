# Claim audit for the extended manuscript

| Candidate statement | Evidence and scope |
| --- | --- |
| The verifier can remove a task family even when the family is attempted. | E001b and E002 provide the observed failed admissions and FIFO transitions. The FIFO identity and E005 give an exact stationary reference calculation. E005 does not fit the adaptive E002 trajectories. |
| Targeting improved rare-task accuracy. | E002 shows a positive mean on the original inputs against a reference-mixture baseline. E012 compares adaptation with a matched rare budget and finds a 5.6-point rare macro gap driven by one seed. E003 shows a numerical reversal under renamed or fresh-motif inputs. |
| The model copied the old solution string. | E007 finds no exact literal reuse among the targeted/model or random/model key-detour failures with a correct original answer. The data support sensitivity, and leave the internal mechanism open. |
| A shared labeling scheme preserves the benefit. | E004 compares this condition with independent relabeling. A shared permutation preserves role alignment and other cross-example properties, so the contrast cannot isolate one internal feature. |
| The effect generalizes to other agents. | E006 reads fixed Qwen-generated memories with the cached Gemma 4 E4B snapshot after the Phi download failed. This is a cross-model readout, not a replication of memory acquisition. Baseline floor effects must be reported. |

The graph-label and ground-truth-memory literatures already contain the
individual controls. The proposed empirical contribution is the change
in the *policy contrast* across representation conditions, with task
identity, exact stored solutions, and memory contents held fixed.

## Challenges raised during the extension

- **Both sides were perturbed together.** E004 changes demonstration
  and query labels separately. The large accuracy loss appears under
  either one-sided change, and the accuracy interaction is influenced
  by the floor.
- **A shared permutation could simply be an easier random draw.**
  E009 matches each graph's two rendered forms exactly across
  conditions. The targeted-minus-random gap is 19.4 points larger
  under shared labels, with reversals in two seeds. The experiment
  controls individual representations while changing their joint
  arrangement in the prompt.
- **Changing labels only at evaluation may explain the drop.**
  E008 changes the representation during acquisition as well.
  It finds no recovery of the targeted advantage on these graphs.
- **Verification explains everything.** E005 is exact under i.i.d.
  attempts and gives an interpretable limiting reference. It does
  not identify an admission process for the adaptive experiments or
  predict held-out accuracy.
- **Valid JSON means the model answered.** E006 requests nine
  answers per call and tracks the actual returned IDs. E010
  probes the first key-detour item from each seed separately.
  These readouts change model, backend, and output grammar together.

## Final cross-model judgment

E006 is a failed batch comparison for key detours. Gemma answered
only the first query in every call, and no cell scored a key-detour
success. E010 restores answer completeness with one query per call.
On the same six key-detour queries, Qwen's targeted-minus-random
gaps are +3, 0, and +3, and Gemma's are +3, -1, and +2 under the
original, independent, and shared comparisons. The model, serving
and grammar settings differ and the memories all come from Qwen. Claims of replicated acquisition or
general label invariance would exceed the evidence.

The strongest contribution is the controlled policy comparison with
matched graph exposures. The result is an average from six paired
seeds, with two reversals and a specific two-map mixture. The FIFO
proposition is a transparent reference calculation based on
binomial thinning. Its algebra alone is insufficient as a claim of
substantial theoretical novelty.

## November 13 audit

[E011](../experiments/E011-manuscript-audit/analysis.md) finds a fixed-path
shortcut that ties the 18/18 Qwen result on the original key-detour family.
It also matches the Gemma diagnostic's six item IDs in the archived Qwen
responses and finds a Qwen tie under independent relabeling. The revised
manuscript reports both findings, the E009 leave-one-seed-out range, and the
need for a matched nonadaptive rare-only comparison, now tested in E012.

## Matched-budget and varied-path controls

- E012 reduces the observed rare macro gap from the 22.2-point E002
  comparison to 5.6 points against the matched rare-only control. This
  compares two different baselines and does not give an additive
  decomposition. The 5.6-point gap comes from one seed.
- E013 holds vertex roles fixed and changes the detour distribution.
  Both rare-only policies lose 11 correct detours. The remaining
  two-answer adaptive gap again comes from one seed. The reference
  mixture scores 3/18 on the varied queries, below both rare-only
  policies. Unchanged queries in the same mixture batches also change
  scores, so the transfer result concerns batched readout.

## November 15 publication audit

Changes to claims in this revision, with the evidence for each.

| Claim | Change | Reason |
| --- | --- | --- |
| Adaptive allocation improved rare-task accuracy over the reference mixture. | Reframed as mostly retained coverage. | The frozen memory scored 16/18 and the empty memory 7/18 on key detours. The mixture arm lost the key-detour example in four of six seeds and scored 7/18. E014 Part B: 80/87 with a retained example, 9/39 without. |
| Targeting lowered unreachable accuracy from 3/18 to 0/18. | Attributed to one seed. | In seed 6204 the mixture memory held an unreachable example and no key-detour example, and the model declared all six rare queries unreachable. E014 Part B, item 5. |
| Shared labels widen the policy gap by 19.4 points. | Marked exploratory, with the post hoc value. | Sign-flip value 0.50 over 64 assignments. The protocol named the outcome and no uncertainty calculation. |
| The controls bound the policy gap. | Added that they were not combined. | E009 used the mixture baseline and original generator, E012 the shortcut holdout, E013 memories from the original generator. |
| The Lean artifact verifies the proposition. | Scope stated on both sides. | Sixteen statements, including normalization and the proposal-share threshold. The proofs do not cover the generator, scorer, or any model output. E014 Part D replays the list-level lemma on 42 trajectories. |
| Ground-truth memory, matched budgets, and label permutations are contributions. | Disclaimed as prior work. | Xiong et al., Liu and Ding, Herbst et al. The contribution is the audit of a policy contrast. |

Statements the evidence does not support and the manuscript does not
make: that adaptive allocation outperforms a matched rare-only budget,
that the retention split is causal, that the label effect is confirmed,
that the acquisition result replicates on a second model, or that the
Lean proofs validate the empirical scores.

The split by retained coverage is post hoc and unrandomized. On the
original holdout one fixed path answers every key-detour query, so the
split cannot separate use of the retained example from reuse of its
answer path. On the varied-path batch the same split gives 15/42
against 0/12.

## November 15 confirmatory experiment

E015 was locked before its results and changes the following claims.

| Claim | Change | Reason |
| --- | --- | --- |
| The E002 policy gap is mostly retained coverage. | Narrowed to the original holdout and described as retention of a reusable answer. | E015 primary contrast, frozen minus mixture on key detours: 55/90 against 51/90, +4.4 points, interval −5.6 to +13.3, exact sign-flip 0.51. The mixture arm kept a key-detour example in 6 of 30 seeds. The empty memory scored 53/90. |
| Memories holding a key-detour example answer more key-detour queries. | Stated as specific to the original holdout. | E015: 145/240 with an example, 129/210 without. With the query's optimal path stored 29/32, with another path 116/208. |
| Adaptive allocation may beat a matched rare-only budget. | Still unestablished, now with a negative point estimate. | E015 Q2: −1.7 points, interval −5.0 to +1.7, Holm-adjusted 0.51. Adaptive spent 84 of 120 supplements on unreachable tasks, none admitted. |
| Shared labels widen the policy gap. | Stated as not replicated. | E015 Q3: −5.0 points, Holm-adjusted 0.36. The adaptive-minus-mixture interaction was −10.0 points, descriptive and uncorrected. |
| Retained unreachable examples do not help. | Kept, with more data. | E015: 0/450 readout answers correct, 0 of 208 attempts admitted, no unreachable declaration in 3,510 requested answers. |
| The FIFO model describes the update trajectories. | Extended to 132 trajectories. | E015: 90 trajectories, 270 checks, no disagreement. |

Statements the manuscript does not make after E015: that retention has
no effect (the interval allows up to about 13 points), that the E002
counts were wrong, that labels reverse the policy gap, or which of the
three design changes removed the gap. E015 changed the generator, the
number of rounds, and the readout format together.

All 44 E015 statements in the manuscript are asserted by
`experiments/E015-confirmatory/check_manuscript.py`.
