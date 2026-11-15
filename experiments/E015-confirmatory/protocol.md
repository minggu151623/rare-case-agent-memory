# E015 · Confirmatory experiment on fresh seeds

Locked on 2026-11-15, before any model call on the 30 confirmatory
seeds. It replaces the earlier [design draft](protocol-draft.md), which
is kept unchanged for comparison.

## Decisions

The author delegated the three open decisions of the draft.

1. **Primary question: retention.** It is the main reading of the
   released manuscript and rests on post hoc evidence (E014 Part B).
   The label interaction that the handoff proposed as primary becomes
   a secondary question, because E009 gave it a sign-flip value of 0.50.
2. **Four update rounds.** With two rounds the shuffled initial order
   decides most evictions. Four rounds allow up to twelve admissions
   into six slots, so retention depends on what each policy admits.
3. **One model, Qwen3 8B.** The acquisition and readout model of E002.
   A second acquisition model stays an open limitation.

## Questions

- **Primary (Q1, retention).** Is held-out key-detour accuracy lower
  after reference-mixture updates than with the frozen initial memory?
- **Secondary (Q2, adaptation).** Does adaptive allocation exceed
  balanced rare-only allocation in rare accuracy?
- **Secondary (Q3, labels).** Is the adaptive-minus-balanced
  key-detour gap different under shared and mixed label assignments?

## Tasks

Thirty confirmatory seeds, 7101–7130, and two development seeds, 7001
and 7002. None was used in E001–E013. Per seed: an initial memory of
four ungated, one key-detour and one unreachable example; four rounds
with two background tasks drawn from the reference mixture (0.8, 0.1,
0.1) and one supplement of each family; a holdout of three tasks per
family. All graphs have six nodes and seven edges, start A, goal B, and
key C where a key exists.

Every key-detour task, in every pool, uses the E013 generator: backbone
`A→X→C→Y→B` with `X, Y ∈ {D, E, F}`, last edge locked, and a unique
optimal path. Holdout routes follow the E013 balance: one return route
and two through routes per seed, and each of the nine routes ten times
over the 30 seeds. Routes in the initial memory, backgrounds, and
supplements are drawn uniformly. Ungated and unreachable tasks use the
original generator. Ungated tasks therefore still share one backbone.
The unreachable family has one correct answer by definition.

Graphs are deduplicated up to relabeling against each other and
against every graph of E001–E013 (`src.confirmatory.prior_keys`).

## Arms

Five evaluated memories per seed: empty, frozen initial memory, and the
final memories of three update policies. All policies share the initial
memory, backgrounds, supplement pools, capacity six, FIFO eviction, and
exact verification of the model's own answers. No oracle answers enter
after the initial memory.

- **Reference mixture.** The supplement family is drawn from the
  reference mixture each round.
- **Balanced rare-only.** Two key-detour and two unreachable
  supplements in a seed-specific random order.
- **Adaptive.** The supplement comes from the rare family with the
  fewest examples in the current memory, with a seed-specific tie order.

Each round is one solve call with three candidates, as in E002. The
order of arms is shuffled per seed.

## Readout

One query per call. Each of the five memories answers the nine holdout
queries under the original labels: 45 calls per seed. Memories are
visited in a seed-shuffled order and queries in holdout order within a
memory. A missing or invalid answer scores zero.

**Label sub-study.** For the three updated memories and the three
key-detour queries, two derangements per seed that disagree at every
vertex (`maps_for_seed`). In the shared condition every memory graph
and the query use map `r` in repetition `r`. In the mixed condition the
query uses map `r` and the memory graph at position `i` uses map
`(r + i) mod 2`. Across the two repetitions every query and every memory
graph is therefore shown once under each map in both conditions. The
conditions differ only in which renderings share a prompt. 36 calls per
seed, in a seed-shuffled order of memory, condition, and repetition.

Model and settings: Qwen3 8B at digest `500a1f06…8b41`, Ollama 0.40.12,
thinking disabled, temperature zero, 4096-token context, 384 output
tokens, the E002 system instruction. 93 calls per seed, 2,790 in total.

## Checks before inference

`python3 -m unittest discover -s experiments/E015-confirmatory` and
`python3 -m src.confirmatory --preflight` must pass. They cover:

- an independent relaxation solver agreeing with the production solver
  on all 1,120 graphs, and family validity of each graph;
- no duplicate graph within E015 and none shared with E001–E013;
- holdout routes: 90 key-detour queries, nine optimal paths, the best
  fixed path correct on 10 of 90;
- acquisition routes: 170 key-detour tasks, nine optimal paths, the
  most frequent on 26 of 170 (reported, not constrained);
- matched rendered exposures between the shared and mixed conditions;
- a fixture run that replays and detects a tampered summary.

## Development seeds

Seeds 7001 and 7002 were run once on the model before locking, with the
final code. Their traces are archived under `development/` and never
enter the analysis. Before locking we looked only at the interface:
all 186 calls returned valid outer JSON and stopped normally, all 90
readout queries returned the requested ID, the longest response had 60
output tokens, the largest prompt plus response had 1,288 tokens, and
mean request times were 7.4 s per solve call, 2.1 s per readout call,
and 3.5 s per label call.

No prompt, schema, generator, or scoring change followed. We did not
compare memories on these seeds.

## Analysis

Unit: seed. All contrasts are paired differences in correct answers.

**Primary, confirmatory.** `D = frozen − reference mixture`, correct
key-detour answers out of three, original labels. Report the 30
differences, their mean and standard deviation, the counts of positive,
zero, and negative seeds, a percentile bootstrap interval over seeds
(10,000 resamples, generator seed 715200), and the exact two-sided
sign-flip value computed by convolution over all `2^30` assignments.
The retention reading is confirmed if the mean is positive and the
value is at most 0.05. Otherwise it is not confirmed under these
conditions, and the manuscript is narrowed to say so.

**Secondary, Holm-adjusted over the two at 0.05.**

- Q2: adaptive minus balanced rare-only, correct rare answers out of six
  (key detour plus unreachable).
- Q3: (adaptive − balanced) under shared labels minus the same gap
  under mixed labels, correct key-detour answers out of six per memory
  and condition.

A value above the threshold is not evidence of equivalence. Thirty
seeds were sized for a standardized effect near 0.55. The archived
adaptive-versus-balanced effect was about 0.4, which this sample can
bound and is unlikely to confirm.

**Descriptive, no test interpreted as confirmatory.** Family scores for
all five memories; balanced minus mixture, adaptive minus mixture, and
frozen minus empty on key detours; shared minus mixed within each
memory and the adaptive-minus-mixture label interaction; the E014 split
by retained coverage; key-detour accuracy by whether a retained
example's path is optimal for the query; seeds retaining each rare
family per memory; attempts, admissions, and evictions by family;
supplement families; answers returned; tokens and seconds by stage.

**Conformance.** Every update trajectory is checked against the Lean
FIFO characterization, as in E014 Part D.

## Rules

- All 30 seeds are run. No interim analysis, no early stop, no added
  seeds. `--audit` is not run on the confirmatory seeds before the last
  seed completes.
- A transport failure reruns the whole seed. The partial directory is
  kept as `<seed>.partial-N`. Content errors are never retried.
- Every score is recomputed from the stored prompts and responses by
  `replay_seed`, which also rebuilds every prompt from the task pools.
- Holdout tasks and their answers never enter a memory.
- Deviations and unexpected observations go in `analysis.md`.

## Amendment 1 · runtime version, before any confirmatory call

Between the development run and the first confirmatory seed the local
Ollama application updated itself from 0.40.12 to 0.40.16. The runner
checks the version at the start of each seed and stopped before making
a call. It left an empty trace file for seed 7101, which was removed. No
confirmatory prompt had been sent.

The confirmatory run uses Ollama 0.40.16 with the same model digest and
settings. The two development seeds were rerun on 0.40.16
(`development-0.40.16/`). All 186 prompts were identical to the 0.40.12
run and all 186 responses were identical, so the interface observations
above stand. Mean request times were 8.0 s, 2.3 s, and 3.5 s.

The runner still checks the version at each seed. If the runtime changes
again during the run, the run stops, the completed seeds are kept, and
the change is recorded in a further amendment before continuing. All
arms of a seed always share one runtime. Results are not expected to
reproduce E002 outputs byte for byte, and no analysis depends on that.

## Replay

```sh
python3 -m unittest discover -s experiments/E015-confirmatory
root=experiments/E015-confirmatory/results/qwen3-8b
python3 -m src.confirmatory "$root" --audit | cmp - "$root/aggregate.json"
```

A live run uses `python3 -m src.confirmatory OUTPUT --ollama-port 11434`.

## Cost

2,790 local calls. The development seeds took 306 s each, so the run
is expected to take about 2.6 hours on the Apple M1 Pro. No paid compute.
