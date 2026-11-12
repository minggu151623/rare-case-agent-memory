# Claim audit for the extended manuscript

| Candidate statement | Evidence and scope |
| --- | --- |
| The verifier can remove a task family even when the family is attempted. | E001b and E002 provide the observed failed admissions and FIFO transitions. The FIFO identity and E005 give an exact stationary reference calculation. E005 does not fit the adaptive E002 trajectories. |
| Targeting improved rare-task accuracy. | E002 reports a positive mean on original inputs with six paired seeds and opposite family-level changes. E003 shows that the key-detour advantage reverses numerically under renamed or new-motif inputs. Limit the claim to E002's representation. |
| The model copied the old solution string. | E007 finds no exact literal reuse among the targeted/model or random/model key-detour failures with a correct original answer. The data support sensitivity, and leave the internal mechanism open. |
| A shared labeling scheme preserves the benefit. | E004 compares this condition with independent relabeling. A shared permutation preserves role alignment and other cross-example properties, so the contrast cannot isolate one internal feature. |
| The effect generalizes to other agents. | E006 reads fixed Qwen-generated memories with Phi. This is a cross-model readout, not a replication of memory acquisition. Baseline floor effects must be reported. |

The graph-label and ground-truth-memory literatures already contain the
individual controls. The proposed empirical contribution is the change
in the *policy contrast* across representation conditions, with task
identity, exact stored solutions, and memory contents held fixed.
