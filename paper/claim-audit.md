# Claim audit for the extended manuscript

| Candidate statement | Evidence and scope |
| --- | --- |
| The verifier can remove a task family even when the family is attempted. | E001b and E002 provide the observed failed admissions and FIFO transitions. The FIFO identity and E005 give an exact stationary reference calculation. E005 does not fit the adaptive E002 trajectories. |
| Targeting improved rare-task accuracy. | E002 reports a positive mean on original inputs with six paired seeds and opposite family-level changes. E003 shows that the key-detour advantage reverses numerically under renamed or new-motif inputs. Limit the claim to E002's representation. |
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
Its targeted-memory counts (4/6, 0/6, 3/6) agree in direction with
the Qwen original, independent, and shared comparisons. That result
has six paired queries, different serving and grammar settings, and
Qwen-generated memories. Claims of replicated acquisition or
general label invariance would exceed the evidence.

The strongest contribution is the controlled policy comparison with
matched graph exposures. The result is an average from six paired
seeds, with two reversals and a specific two-map mixture. The FIFO
proposition is a transparent reference calculation based on
binomial thinning. Its algebra alone is insufficient as a claim of
substantial theoretical novelty.
