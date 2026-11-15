# E014 · Publication audit results

Offline reanalysis of the archived traces under the
[locked protocol](protocol.md) and its Amendment 1. No model was run.
[results.json](results.json) is reproduced by

```sh
python3 -m experiments.E014-publication-audit.check | cmp - experiments/E014-publication-audit/results.json
```

Everything below is post hoc. Parts B and D were designed after looking
at the E002 aggregate, and Amendment 1 after a first look at the Part B
split.

## Part A · E009 sign-flip sensitivity value

The six seed-level differences in the policy gap (shared minus mixed)
are `(+3, +6, -4, +2, -1, +1)` correct key-detour answers out of six,
a mean of +19.4 percentage points. Over all 64 sign assignments the
exact two-sided sign-flip value is **0.50**. Under sign exchangeability
the observed mean is unremarkable. The value does not show that the
effect is zero. E009 stays a descriptive result.

## Part B · Retained coverage and held-out readout

42 evaluated memories (seven per seed) on the original holdout.

| Family | Example retained | Units | Correct | Units at 3/3 | Units at 0/3 |
| --- | --- | ---: | ---: | ---: | ---: |
| Key detour | yes | 29 | 80/87 | 25 | 0 |
| Key detour | no | 13 | 9/39 | 1 | 8 |
| Unreachable | yes | 17 | 3/51 | 1 | 16 |
| Unreachable | no | 25 | 0/75 | 0 | 25 |

**Key detours.** Accuracy tracked whether the evaluated memory still
held a key-detour example. In the reference-mixture arm the two seeds
that kept one scored 6/6 and the four that lost it scored 1/12. The
frozen initial memory (one example) scored 16/18 and the empty memory
7/18, the same total as the mixture arm. Within seeds, accuracy was
higher with a retained example in five of six seeds. Seed 6203 is the
exception: its empty memory already scored 3/3. Seed 6202's empty memory
scored 2/3, and seed 6206 is mixed (8/12 with, 4/9 without).

This reframes the E002 policy gap. Relative to not updating at all, the
rare-enriched policies added two correct answers (18/18 against 16/18).
The reference-mixture policy lost nine (7/18). Most of the measured
"gain" from targeting is coverage that mixture updates evicted.

**Varied-path batch (E013).** With a retained key-detour example the
three evaluated memories scored 15/42, and without one 0/12. The
association is weaker but in the same direction when no single path
solves the batch.

**Unreachable.** Retained examples did not help. Sixteen of the
seventeen memories that held an unreachable example scored 0/3,
including all six frozen memories and all four targeted-oracle
memories that held one or two.

**The one exception is not discrimination.** All three correct
unreachable answers come from seed 6204 of the reference-mixture arm.
That memory held an unreachable example and no key-detour example, and
the model declared all six rare queries unreachable: three correct
answers and three false unreachable claims on key detours. The
manuscript's "unreachable performance fell from 3/18 to 0/18" under
targeting therefore reflects one seed's blanket response. It is not
evidence that mixture sampling preserved an unreachable skill.

**Limits.** Presence was not randomized. It depends on policy, seed,
model answers, and FIFO order, and the seven units of a seed share one
holdout. E011 showed that one fixed path solves every original
key-detour query, so on that batch the association cannot separate use
of the retained example from reuse of its answer path. No test is
attached.

## Part D · FIFO conformance on realized trajectories

All 42 archived update trajectories (E002 four arms, E012 balanced
rare-only, E008 two arms; six seeds each) satisfy both checks: the
final memory is the last six entries of the initial list followed by
the ordered admissions, and for each family the absence predicted by
the Lean lemma `foldl_admit_absent_iff` equals the observed absence.
126 family-trajectory checks, 0 mismatches.

| Study and arm | Key detour lost | Unreachable lost |
| --- | ---: | ---: |
| E002 random / model | 4 of 6 | 5 of 6 |
| E002 random / oracle | 3 of 6 | 4 of 6 |
| E002 targeted / model | 0 of 6 | 5 of 6 |
| E002 targeted / oracle | 0 of 6 | 2 of 6 |
| E012 balanced rare-only | 0 of 6 | 3 of 6 |
| E008 random / model | 3 of 6 | 1 of 6 |
| E008 targeted / model | 1 of 6 | 1 of 6 |

A rare family ended absent in 32 family-trajectories. In all 32 no
example of that family had been admitted, so each loss is an instance
of the no-replenishment case: the family left when the number of
admissions reached the position of its last initial example. The
ungated family was never lost.

This check ties the archived Python update to the formal model. It
covers 42 two-round trajectories and says nothing about the i.i.d.
probability law, which these adaptive runs do not follow.

## Part C · Manuscript number check

72 manuscript statements are asserted against the archives and replayed
reports, including the Part A, B, and D numbers above. All pass.

## What changed in the manuscript

- The abstract and Section 6 now report the frozen (16/18) and empty
  (7/18) baselines next to the policy scores and state the Part B
  split as post hoc.
- The unreachable "decrease" under targeting is attributed to the
  single blanket-response seed.
- E009 carries the 0.50 sensitivity value and the word exploratory.
- Section 4 cites the Part D conformance check as the link between the
  Lean model and the experiment code.
