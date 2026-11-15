# E015 · Confirmatory experiment results

Thirty fresh seeds (7101–7130), run under the [locked protocol](protocol.md)
and its Amendment 1. All 2,790 calls completed in one pass on Qwen3 8B,
Ollama 0.40.16, in 2.84 hours of request time. The aggregate replays
offline:

```sh
root=experiments/E015-confirmatory/results/qwen3-8b
python3 -m src.confirmatory "$root" --audit | cmp - "$root/aggregate.json"
```

**Summary.** The primary retention hypothesis was not confirmed. Neither
secondary contrast was established. Memory coverage changed as the FIFO
model predicts, and held-out accuracy did not follow it.

## Scores

Correct answers out of 90 per family (30 seeds, three queries each, one
query per call, original labels).

| Evaluated memory | Rare supplements | Seeds retaining a key-detour example | Ungated | Key detour | Unreachable |
| --- | ---: | ---: | ---: | ---: | ---: |
| Empty | – | 0/30 | 62 | 53 | 0 |
| Frozen initial memory | – | 30/30 | 87 | 55 | 0 |
| Reference-mixture updates | 26/120 | 6/30 | 88 | 51 | 0 |
| Balanced rare-only updates | 120/120 | 24/30 | 88 | 59 | 0 |
| Adaptive updates | 120/120 | 20/30 | 88 | 56 | 0 |

All 1,350 requested readout answers were returned. No single path solves
more than 10 of the 90 key-detour queries.

## Primary contrast (confirmatory): frozen minus reference mixture

Correct key-detour answers out of three, per seed, in seed order:

`+1 −1 0 0 −1 0 +1 0 0 +1 0 0 +1 −1 0 0 +1 −2 +1 −1 +1 +1 −1 +1 0 +1 0 0 +1 0`

- Mean +0.133 of three (+4.4 percentage points), standard deviation 0.819.
- Positive in 11 seeds, zero in 13, negative in 6.
- Percentile bootstrap interval: −5.6 to +13.3 points.
- Exact two-sided sign-flip value over all 2^30 assignments: **0.507**.

The protocol's criterion (positive mean and a value at most 0.05) is not
met. **The retention reading is not confirmed under these conditions.**
The mixture arm did lose coverage: it kept a key-detour example in 6 of
30 seeds, against 30 of 30 for the frozen memory. The lost coverage did
not cost accuracy. The frozen memory was also only two answers ahead of
the empty memory (55 against 53; mean +2.2 points, interval −10.0 to
+14.4).

The interval excludes a gap of the size seen in E002, where the frozen
memory led the mixture arm by 9 of 18 answers (50 points) on the
original holdout. It does not exclude a gap of up to about 13 points.

## Secondary contrasts (Holm-adjusted over the two)

| Contrast | Mean | 95% bootstrap | +/0/− seeds | Sign-flip | Holm |
| --- | ---: | ---: | ---: | ---: | ---: |
| Q2 adaptive − balanced, rare answers of six | −1.7 points | −5.0 to +1.7 | 3/21/6 | 0.508 | 0.508 |
| Q3 label interaction, (adaptive − balanced) shared − mixed | −5.0 points | −11.7 to +1.1 | 5/15/10 | 0.180 | 0.360 |

Neither is established. The point estimate of Q2 is negative. A value
above the threshold is not evidence of equivalence. For Q2 the interval
bounds an adaptive advantage at under two points of rare accuracy in
this setting.

**Why adaptation did not help here.** No model answer to an unreachable
task was admitted in any arm (0 of 208 attempts). The initial
unreachable example was therefore evicted in every update trajectory,
and unreachable became the least-covered family. The adaptive rule then
sent 84 of its 120 supplements to unreachable tasks and 36 to key
detours. The balanced rule sent 60 to each. Adaptive admitted 27
key-detour examples and balanced 45, and adaptive retained a key-detour
example in 20 seeds against 24. Targeting the least-covered family
spends the budget on a family the model cannot add.

## Descriptive results

No test here is confirmatory. Eight sign-flip values were computed in
this block without correction.

**Key detours against the mixture arm.** Balanced minus mixture: +8.9
points (interval 0.0 to +17.8, sign-flip 0.096). Adaptive minus mixture:
+5.6 points (−1.1 to +12.2, 0.227).

**Retained coverage split.** As in E014 Part B, by whether the evaluated
memory holds an example of the queried family (150 memories).

| Family | Example retained | Memories | Correct | At 3/3 | At 0/3 |
| --- | --- | ---: | ---: | ---: | ---: |
| Key detour | yes | 80 | 145/240 | 17 | 2 |
| Key detour | no | 70 | 129/210 | 15 | 5 |
| Unreachable | yes | 30 | 0/90 | 0 | 30 |
| Unreachable | no | 120 | 0/360 | 0 | 120 |

The E014 association (80/87 with an example, 9/39 without) does not
appear: 60.4% with an example and 61.4% without. Within the mixture
arm, the six seeds that kept an example scored 7/18 and the 24 that
lost it 44/72.

**Path availability.** Split of the 450 key-detour readout answers by
whether a retained key-detour example has the query's optimal path as
its own stored path.

| Group | Correct |
| --- | ---: |
| Optimal path present in memory | 29/32 (90.6%) |
| Key-detour example present, other path | 116/208 (55.8%) |
| No key-detour example | 129/210 (61.4%) |

The frozen memory alone gives 12/13 and 43/77. This is the pattern
expected if a stored example helps mainly when its answer can be reused.
It is an observational split with 32 answers in the first group.
Presence of a matching path was not randomized.

**Label sub-study.** Correct key-detour answers out of 180 per cell.

| Memory | Shared | Mixed | Shared − mixed | Interval | Sign-flip |
| --- | ---: | ---: | ---: | ---: | ---: |
| Reference mixture | 101 | 93 | +4.4 points | −1.7 to +11.1 | 0.265 |
| Balanced rare-only | 99 | 100 | −0.6 | −7.2 to +6.7 | 1.000 |
| Adaptive | 91 | 101 | −5.6 | −10.0 to −1.1 | 0.030 |

The adaptive-minus-mixture interaction, the contrast that E009 reported
as +19.4 points on six seeds, is −10.0 points here (interval −17.8 to
−2.2, sign-flip 0.031). The sign is opposite to E009. The value is
uncorrected and one of eight, so we do not read it as an effect in the
opposite direction. E009's direction did not replicate.

**Unreachable tasks.** Zero of 450 readout answers were correct,
including the 90 from frozen memories that held an unreachable example.

**Ungated tasks.** 62/90 with the empty memory and 87 or 88 of 90 with
every nonempty memory. Ungated tasks still share one backbone (see the
protocol), so this gain is compatible with path reuse.

**FIFO conformance.** All 90 update trajectories equal the newest six
entries of the initial memory followed by the admissions. Predicted and
observed family absence agree in all 270 checks. A rare family ended
absent in 130 of 180 rare checks, 121 of them with no admission from
that family during the run.

**Admissions.** Attempted, admitted, and evicted examples by arm.

| Arm | Family | Attempted | Admitted | Evicted |
| --- | --- | ---: | ---: | ---: |
| Mixture | ungated | 297 | 292 | 240 |
| Mixture | key detour | 33 | 15 | 37 |
| Mixture | unreachable | 30 | 0 | 30 |
| Balanced | ungated | 203 | 198 | 173 |
| Balanced | key detour | 80 | 45 | 40 |
| Balanced | unreachable | 77 | 0 | 30 |
| Adaptive | ungated | 203 | 194 | 158 |
| Adaptive | key detour | 56 | 27 | 33 |
| Adaptive | unreachable | 101 | 0 | 30 |

## Exploratory readings added after the locked analysis

[exploratory.py](exploratory.py) was written after `aggregate.json` was
archived. Its output is [exploratory.json](exploratory.json).

- The model never returned an unreachable declaration: 0 of 3,510
  requested answers across acquisition, readout, and the label
  sub-study, including 658 answers to unreachable tasks. On the 450
  unreachable readout queries the first detectable error was a
  nonexistent edge (268), a locked edge before the key (147), or a
  wrong endpoint (35). In this run the unreachable family measures a
  response the model does not produce, with or without an example.
- The path-availability split by memory is in the JSON file.

## Deviations and observations

- **Runtime.** Ollama updated itself from 0.40.12 to 0.40.16 before the
  first confirmatory call. Amendment 1 records it. All 30 seeds ran on
  0.40.16 with the pinned digest.
- **One format failure.** Seed 7126, label sub-study, mixture memory,
  mixed condition, repetition 0, query `h04`: the response reached the
  384-token limit and was not valid JSON. It is scored as incorrect, as
  the protocol requires. It does not touch the primary contrast or Q2.
- **No reruns.** No transport failure occurred and no partial directory
  exists. The empty directory left by the version check before
  Amendment 1 contained no call.
- **Readout format.** E015 asks one query per call. E002–E013 asked nine
  per call. Absolute scores are not comparable across the two. The
  empty memory scored 53/90 on key detours here.
- **Sample size.** The protocol sized 30 seeds for a standardized effect
  near 0.55. The observed standardized primary effect is 0.16.

## What this changes

1. The manuscript's main reading of E002, that the policy gap was mostly
   retained coverage, was a post hoc reading on a holdout where one path
   answers every key-detour query. With routes diversified in memory,
   supplements, and holdout, on fresh seeds, losing the key-detour
   example did not reduce accuracy. The reading is narrowed to the
   original holdout.
2. The E015 path split and the E011 fixed-path diagnostic point the same
   way: the E002 retention effect is best explained by reuse of a stored
   answer path. This explanation is descriptive.
3. An adaptive advantage over a matched rare budget remains
   unestablished, now with a negative point estimate on 30 seeds.
4. The E009 label interaction did not replicate.
5. The FIFO reference model describes coverage in all 90 new
   trajectories. Coverage did not predict accuracy.
