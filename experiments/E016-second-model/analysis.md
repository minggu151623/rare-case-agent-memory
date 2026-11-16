# E016 · Second acquisition model, results

Thirty seeds (7101–7130) with Gemma 4 E4B, run under the
[locked protocol](protocol.md). All 2,430 calls completed in one pass in
1.15 hours of request time, with no format failure, no rerun, and no
change of runtime. The aggregate replays offline:

```sh
root=experiments/E016-second-model/results/gemma-e4b
python3 -m src.second_model "$root" --audit | cmp - "$root/aggregate.json"
```

**Summary.** The retention reading is not confirmed for Gemma either.
The point estimate has the opposite sign. The adaptive contrast is not
established. The E015 null results are therefore not specific to Qwen3.

## Scores

Correct answers out of 90 per family, with E015 (Qwen3 8B) beside them.
Both models answered the same 270 held-out queries.

| Evaluated memory | Seeds retaining a key-detour example | Ungated | Key detour | Unreachable | Qwen3 key detour |
| --- | ---: | ---: | ---: | ---: | ---: |
| Empty | 0/30 | 86 | 48 | 0 | 53 |
| Frozen initial memory | 30/30 | 87 | 47 | 0 | 55 |
| Reference-mixture updates | 6/30 | 87 | 55 | 0 | 51 |
| Balanced rare-only updates | 29/30 | 88 | 49 | 0 | 59 |
| Adaptive updates | 21/30 | 88 | 52 | 0 | 56 |

## Primary contrast: frozen minus reference mixture, key detours

Per seed, in seed order:

`0 −1 +1 −1 −3 −3 0 0 0 0 −1 +1 0 +1 +1 0 −1 −1 −1 0 0 0 0 0 +2 0 −1 0 −1 0`

- Mean −0.267 of three (−8.9 percentage points), standard deviation 1.05.
- Positive in 5 seeds, zero in 15, negative in 10.
- Percentile bootstrap interval: −21.1 to +3.3 points.
- Exact two-sided sign-flip value: **0.240**.

The criterion (positive mean and a value at most 0.05) is not met.
**The retention reading is not confirmed for this model.** The mixture
memory kept a key-detour example in 6 of 30 seeds and answered more
key-detour queries than the frozen memory, 55 against 47. The frozen
memory was one answer behind the empty memory (47 against 48; interval
−16.7 to +13.3 points).

When the readout is rescored under the strict E015 rule the primary
contrast is identical. That rescoring keeps the trajectories acquired
under the locked rule. See "Where the scoring rule acted" below for the
one seed in which the rule changed an admission.

## Secondary contrast: adaptive minus balanced, rare answers

+1.7 points (interval −0.6 to +3.9), positive in 4 seeds, zero in 25,
negative in 1, sign-flip 0.375. Not established. Unreachable accuracy
is zero in every memory, so this is the key-detour difference, 52
against 49, +3.3 points. In E015 the same contrast was −3.3 points.

As in E015, no unreachable attempt was admitted (0 of 210), every
trajectory lost the unreachable example, and the adaptive rule sent 86
of its 120 supplements to unreachable tasks. It admitted 34 key-detour
examples against 51 for the balanced rule and retained one in 21 seeds
against 29.

## Descriptive results

Three sign-flip values in this block are uncorrected.

- Balanced minus mixture on key detours: −6.7 points (−16.7 to +3.3,
  0.313). Adaptive minus mixture: −3.3 points (−12.2 to +4.4, 0.613).
  Both rare-enriched policies scored below the mixture policy, the
  opposite order from E015.
- **Retained coverage.** Memories holding a key-detour example answered
  140/258 key-detour queries (54.3%) and memories without one 111/192
  (57.8%).
- **Path availability.** Optimal path stored in memory: 25/36 (69.4%).
  Key-detour example with another path: 115/222 (51.8%). No key-detour
  example: 111/192 (57.8%).
- **Ungated.** 86/90 with the empty memory and 87 or 88 with a memory.
  Gemma does not need an example for ungated tasks, where Qwen3 rose
  from 62 to 87.
- **FIFO conformance.** 90 trajectories, 270 checks, no disagreement.
  A rare family ended absent in 124 checks, 113 without an admission.

## Response format

- 1,077 of 1,080 solve calls and 1,176 of 1,350 readout calls returned
  the requested ID. Of the 174 readout calls that did not, 169 are
  empty-memory calls with one answer under the key `"id"`. The
  single-entry rule fixed in the protocol scores these.
- Under the strict rule the empty memory would score 4/90 on key
  detours, against 48/90 under the locked rule. Every comparison with
  the empty memory depends on this rule. The primary and secondary
  contrasts do not involve the empty memory.

## Readings added after the locked aggregate

[exploratory.py](exploratory.py) writes [exploratory.json](exploratory.json).

- **Same-query control for the path split.** On the 36 answers whose
  query path was stored, the empty memory gave 21/36 on the same
  queries (7 gained with the memory, 3 lost). On the 222 answers with
  another stored path the empty memory gave 118/222. The matched gain
  is 4 of 36 answers, smaller than the 9 of 32 seen with Qwen3.
- **Unreachable declarations.** The aggregate counts two responses that
  contain an unreachable declaration. Both come from one frozen memory
  (seed 7130) and both attach the declaration to the memory's own
  unreachable example `i03`, which the model repeated in its answer.
  Gemma never declared an asked task unreachable, in 660 unreachable
  tasks across acquisition and readout. The family is at a response
  floor for this model too.
- **Echoed memory IDs.** Three frozen-memory readout calls returned a
  single answer keyed by a memory example ID. The locked rule scores
  that answer for the asked task.

## Where the scoring rule acted (added after the fourth-round review)

[strict_rule.py](strict_rule.py) writes [strict_rule.json](strict_rule.json).
An independent reviewer found that the rule had also acted in
acquisition, which the first version of this analysis did not say.

- Correct answers scored only because of the rule: 44 key-detour and 7
  ungated answers of the empty memory, 2 ungated answers of the frozen
  memory, and 3 solve answers.
- The 3 solve answers are one task: ungated background task `b000` in
  round 1 of seed 7125, once per updating arm. The rule admitted it in
  all three arms. No other seed has a solve rescue.
- **Strict rerun of seed 7125.** We reran this seed with the rule off
  in acquisition and readout (81 new calls,
  `sensitivity-strict-rule/7125`). Key-detour scores were unchanged for
  the frozen and updated memories (3, 1, 2, 2), the primary difference
  stayed at +2, and the secondary difference stayed at 0. The empty
  memory went from 1 to 0. Both contrasts are therefore the same under
  either rule.

- **Repeatability.** A reviewer compared the rerun with the locked run:
  57 of its prompts are byte-identical to prompts of the locked run, and
  one of them, ungated query `h00` under the same memory, received a
  different answer. Gemma's temperature-zero answers in LM Studio are
  therefore not exactly repeatable, although the two development runs
  returned identical responses. The rerun mixes the rule change with
  this run-to-run variation. No contrast is affected.

## Deviations and observations

- None from the locked protocol. No amendment was needed.
- The model was loaded once as `rare-case-gemma-e4b` and stayed loaded.
  File hashes were verified at every seed.
- Readout format and scoring differ from E006, which used nine-query
  batches. Scores are not comparable with E006 or E010.

## What this changes

1. Retention is not confirmed on either model. With Gemma the frozen
   memory was 8.9 points below the mixture memory.
2. The policy ordering differs between models. Rare-enriched updating
   was above mixture updating with Qwen3 (+8.9 and +5.6 points) and
   below it with Gemma (−6.7 and −3.3). Neither ordering is
   established.
3. The path-reuse pattern has the same direction with Gemma and is
   weaker (matched gain 4/36 against 9/32). It remains a hypothesis.
4. Neither model ever declared an asked task unreachable. The
   unreachable family carries no information about memory policy in
   this study.
5. A stored example is not needed by Gemma for ungated tasks. The
   benefit of memory depends on the reader.
6. The FIFO characterization holds in all 90 new trajectories.
