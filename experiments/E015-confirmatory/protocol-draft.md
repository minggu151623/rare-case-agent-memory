# E015 · Confirmatory experiment (design draft)

**Status: draft. Not locked, not implemented, not run. No result
exists.** This file records a proposed design and the decisions the
author still has to make. Lock it as `protocol.md` in its own commit
before any model call, as [AGENTS.md](../../AGENTS.md) requires.

## Why

The released manuscript is an exploratory audit on six reused seeds.
Three results rest on post hoc or underpowered evidence:

1. Updating at the reference mixture evicts the rare example and lowers
   key-detour accuracy to the empty-memory level (E002, E014 Part B).
2. Adaptive allocation beats a balanced rare-only budget by two answers
   from one seed (E012, E013).
3. Shared labels widen the policy gap by 19.4 points, sign-flip 0.50
   (E009).

No experiment combined a matched rare budget, held-out and acquisition
tasks without a constant answer path, and matched renderings.

## Questions, in proposed order of priority

- **Q1 (proposed primary). Retention.** On fresh seeds, with varied
  optimal paths in acquisition and evaluation, is held-out key-detour
  accuracy lower after reference-mixture updates than with the frozen
  initial memory?
- **Q2. Adaptation.** Does adaptive allocation exceed balanced
  rare-only allocation in rare macro accuracy?
- **Q3. Labels.** Is the adaptive-minus-balanced gap larger under
  shared than under mixed label assignments at matched renderings?

Q1 is proposed as primary because it is the manuscript's main reading
and showed the largest and most consistent seed-level differences. The
handoff proposed Q3 as primary. **Author decision 1: choose one
primary.** The other two become secondary with a stated multiplicity
rule (Holm over the two secondaries is the default proposal).

## Design to be completed

- **Seeds and graphs.** New seeds disjoint from 4101 and 6201–6206.
  Structural deduplication against every graph in E001–E013. Key-detour
  tasks drawn from the nine backbones `A→X→C→Y→B` of E013 in initial
  memory, backgrounds, supplements, and holdout. Before any model call,
  compute the best constant path on every pool and require at most 2/18
  per 18 queries, as in E013.
- **Arms.** Empty, frozen, reference-mixture, balanced rare-only,
  adaptive. Same initial memory, background tasks, supplement pools,
  capacity six, and FIFO rule across updating arms. Model answers only.
- **Rounds.** Four update rounds instead of two, so that eviction of
  the initial rare examples is not decided by the shuffled initial
  order alone. **Author decision 2: two rounds (comparable to E002) or
  four.**
- **Readout.** One query per call for the primary analysis, which
  removes batch completeness and query-to-query effects. Nine held-out
  queries per seed, three per family.
- **Label sub-study for Q3.** For the balanced and adaptive memories
  only, the six rare queries under shared and mixed assignments, two
  repetitions, with the E009 construction adapted to single queries:
  each query and each memory graph is rendered under both maps the same
  number of times in both conditions. A code check must confirm the
  matched marginal exposures before inference.
- **Model.** Qwen3 8B at the pinned digest in Ollama 0.40.12, as in
  E002. A second acquisition model is desirable. Gemma 4 E4B in LM
  Studio is cached locally. **Author decision 3: one model or two.**
- **Failure handling.** Missing or invalid answers score zero. A
  transport failure reruns the whole seed in a new directory and keeps
  the partial trace. No prompt changes after the first primary call.
  Schema and completeness are checked on separate development seeds
  that never enter the analysis.

## Sample size (rough, to be redone before locking)

From the archived seed-level differences in correct key-detour answers
out of three:

| Contrast | Differences | Mean | SD |
| --- | --- | ---: | ---: |
| Frozen minus mixture, original holdout | 3, 0, 0, 3, 3, 0 | 1.50 | 1.64 |
| Adaptive minus mixture, varied holdout | 2, −1, 0, 1, 0, 2 | 0.67 | 1.21 |
| Adaptive minus balanced, either holdout | 0, 0, 0, 0, 0, 2 | 0.33 | 0.82 |

These come from six reused seeds and a generator with a shortcut, so
they are weak planning inputs. A standardized effect near 0.55, as in
the second row, needs about 28 pairs for 80% power in a two-sided
paired test at 0.05. The proposal is **30 seeds**, fixed in advance,
with no interim look. Q2 at the observed 0.4 standardized effect would
need about 50 pairs, so 30 seeds can bound it and is unlikely to
confirm it. State that in the locked protocol.

## Cost estimate (one model, 30 seeds, four rounds)

| Stage | Calls per seed | Calls |
| --- | ---: | ---: |
| Acquisition, 3 arms × 4 rounds | 12 | 360 |
| Primary readout, 5 memories × 9 single queries | 45 | 1,350 |
| Label sub-study, 2 memories × 6 queries × 2 conditions × 2 repetitions | 48 | 1,440 |
| Total | 105 | 3,150 |

Archived timing: nine-query Qwen calls took 13–17 s on the M1 Pro, and
single-query Gemma calls about 3 s. At 4–8 s per single-query Qwen call
the run needs roughly 4–7 hours of local inference and no paid compute.
Measure the real rate on development seeds first. A second model
doubles the total.

## Analysis to lock

- Unit: seed. Paired differences, their mean, and the exact two-sided
  sign-flip value, named here as the confirmatory test for the primary
  contrast. With 30 seeds the sign-flip distribution is evaluated
  exactly or with a fixed-seed Monte Carlo of stated size.
- Report the retained-coverage split of E014 Part B as a pre-specified
  secondary description, and the FIFO conformance replay for every
  trajectory.
- Report token counts and wall time per arm.
- Offline replay of every score from stored prompts and responses, and
  an independent shortest-distance check of every generated graph,
  before the analysis is read.
- A null or reversed result is reported as such and the manuscript's
  claims are narrowed accordingly.

## Not in scope

Quota or protected-slot eviction policies, history-dependent theory,
and free-form task proposals. Each needs its own question.
