# E014 · Publication audit of the archived evidence

Date locked: 2026-11-15. Offline reanalysis. No model inference, no new
graphs, and no change to any archived trace or aggregate.

## Why this exists

The 2026-11-15 readiness review asked for three things before release:
an explicit uncertainty statement for E009, a clearer account of what
the memory updates changed relative to not updating at all, and a
machine check that the manuscript's numbers trace to the archives.
While cross-checking the E002 aggregate for this audit, we noticed that
the reference-mixture arm's key-detour score (7/18) equals the
empty-memory score and that its seed-level scores appear to track
whether a key-detour example is still in the final memory. Part B below
was therefore designed **after** seeing the E002 aggregate. It is a post
hoc description and is labeled as such wherever it is reported.

## Part A · E009 sign-flip sensitivity value

Input: the six seed-level differences in the policy gap (shared minus
mixed), in correct key-detour answers out of six, recomputed from the
E009 traces by `src.matched_labels.report`.

Compute the exact two-sided sign-flip value over all 64 sign
assignments with the absolute mean as the statistic, using the same
`sign_flip_p` function as E002, E012, and E013. Report it as a post hoc
sensitivity value under sign exchangeability. It is not a
design-based randomization test and a large value is not evidence of no
effect.

## Part B · Retained family coverage and held-out readout

Unit: one evaluated memory for one seed. Memories:

- E002: four arms, plus the frozen initial memory and the empty memory.
- E012: the balanced rare-only arm. The E012 adaptive arm repeats the
  E002 targeted/model prompts and responses and is counted once.

For each unit record the number of key-detour and unreachable examples
in the evaluated memory (from the replayed final `retained` counts; the
frozen memory holds one of each and the empty memory none) and the
correct answers out of three for that family on the original holdout.

Report, for each family:

1. pooled correct/total split by presence (at least one example of the
   family in memory) versus absence;
2. the same split per memory condition;
3. the number of units with a perfect 3/3 and with 0/3 in each group;
4. for key detours only, the same split on the E013 varied-path batch
   for the three memories that E013 evaluated.

No test is attached. Presence is not randomized: it is determined by
policy, seed, model answers, and FIFO order, and units within a seed
share the holdout. The original key-detour holdout admits a single
fixed optimal path (E011), so an association on that batch cannot
separate use of the retained example from reuse of its path.

## Part C · Manuscript number check

`check.py` recomputes the quantities above and asserts a fixed list of
manuscript statements against the archived aggregates and replayed
reports (E002–E013). A failed assertion stops the script. The list is in
the script and is extended when the manuscript adds a number.

## Amendment 1 · added before any reported output

A first run of the Part B split (no file written) showed that all three
correct unreachable answers in the reference-mixture arm come from one
unit. Two additions follow. Both were specified after seeing that split.

**Part B, item 5.** For every unit with a correct unreachable answer,
classify the answers to its three key-detour queries with
`src.path_errors.classify` and report how many are false unreachable
claims. This shows whether the correct answers reflect discrimination
between the two rare families or one response applied to both.

**Part D · FIFO conformance on realized trajectories.** The Lean lemma
`foldl_admit_absent_iff` states, for any admission history, that a
family is absent from a full FIFO memory exactly when its last initial
position `r` is at most the number of admissions `n` and none of the
last `K` admissions belongs to it. Check that statement against every
archived update trajectory: E002 (four arms), the E012 balanced
rare-only arm, and E008 (two arms), six seeds each, 42 trajectories.

For each trajectory read the ordered memory identifiers from the three
archived prompts (round-1 solve, round-2 solve, final evaluation) and
recover the ordered admissions as the entries that appear after each
round. Then check (i) the final memory equals the last `K = 6` entries
of the initial list followed by the admissions, which is the Lean
`retain` form of the update, and (ii) for each of the three families,
the predicted absence equals the observed absence. Report the number of
family-trajectory checks, and per experiment, arm, and family the
number of trajectories in which the family ended absent and how many of
those had no admission from that family. A mismatch stops the script.

This is a consistency check between the archived implementation and
the formal model on 42 short trajectories. It is not a statistical test
and does not validate the i.i.d. probability law on these data.

## Outputs and replay

```sh
python3 -m experiments.E014-publication-audit.check > /tmp/e014.json
cmp /tmp/e014.json experiments/E014-publication-audit/results.json
```

Record the results in `analysis.md`, including any outcome that does not
support the manuscript's framing.
