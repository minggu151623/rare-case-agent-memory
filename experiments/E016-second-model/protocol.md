# E016 · Second acquisition model

Locked on 2026-11-16, before any Gemma call on the 30 seeds. It repeats
the policy comparison of [E015](../E015-confirmatory/protocol.md) with a
second model that builds and reads its own memory.

## Why

Every acquisition result so far comes from Qwen3 8B. Three review rounds
named the single model as the main limit on significance. Qwen3 never
declared a task unreachable in E015, so one rare family sat at a
response floor. A second model tests whether the E015 conclusions
depend on that model.

## Questions

- **Primary (Q1, retention).** As in E015: is held-out key-detour
  accuracy lower after reference-mixture updates than with the frozen
  initial memory?
- **Secondary (Q2, adaptation).** Does adaptive allocation exceed
  balanced rare-only allocation in rare accuracy?

E016 is a replication on a second model. It has no label sub-study.

## Tasks

The 30 seeds 7101–7130 and the task pools of E015, unchanged
(`src.confirmatory.study`). No Gemma call was ever made on these graphs.
Using the same pools pairs the two models on identical tasks. The two
development seeds 7001 and 7002 test the interface only.

## Model

Gemma 4 E4B, the MLX 4-bit snapshot of E006 and E010
(`deadbydawn101/gemma-4-E4B-mlx-4bit`), with the four file hashes pinned
in `src.representation.GEMMA_HASHES` verified at the start of every
seed. LM Studio 0.4.25+1, model loaded as `rare-case-gemma-e4b` with a
4096-token context. Temperature zero, 384 output tokens, the E002 system
instruction, and the E006 response grammar that requires the outer
`answers` object.

## Differences from E015

1. **One task per solve call.** In E006 Gemma returned only the first of
   nine answers in every batched call. Each round therefore solves its
   three candidates in three calls that share the round's memory.
   Admission, order, capacity, and FIFO eviction are unchanged. A test
   shows that with complete answers the two call patterns admit the
   same examples.
2. **No label sub-study.** 81 calls per seed, 2,430 in total: 36 solve
   calls and 45 readout calls.
3. **Single-entry scoring.** See the next section.

Arms, plans, arm order, readout order, memories, and the holdout are
those of E015.

## Development seeds and the scoring rule

Seeds 7001 and 7002 were run once before locking. We looked at the
interface: all 162 calls returned valid outer JSON and stopped normally,
the longest response had 43 output tokens, the largest prompt plus
response had 1,096 tokens, and mean request times were 3.1 s per solve
call and 2.2 s per readout call. All 72 solve calls returned the
requested ID.

Twelve of the 90 readout calls did not. All twelve are empty-memory
calls, and each returned one answer under the literal key `"id"`, the
placeholder of the instruction's example format. To find this we read
the keys of those twelve responses and four of their bodies. We did not
score any answer or compare memories.

Under E015's rule these answers would score zero for a formatting
reason that only the empty memory can trigger. E016 therefore fixes this
rule before the confirmatory run:

> A call asks for one task. If the response holds exactly one answer and
> its key is not the requested ID, that answer is scored as the answer to
> the requested task. A response with no answer or several answers under
> other keys scores zero.

The rule applies to solve and readout calls. The number of calls that
returned the requested ID is reported separately, and the primary
contrast is also reported under the strict E015 rule as a sensitivity
analysis. The first development run is kept as
`development-strict-scoring/`. The seeds were rerun with the final code
into `development/`.

The rerun returned the same 162 responses as the first run. To check
that the report code executes, we ran it on the development seeds and
printed only its response counts and conformance block. This showed that
Gemma declared none of the 47 unreachable development tasks
unreachable, so the unreachable family may sit at a floor for this
model as well. We did not print scores or contrasts for these seeds.

No prompt, schema, generator, or other scoring change followed.

## Analysis

Unit: seed. Contrasts, intervals, and the exact sign-flip calculation
are those of E015 (`src.confirmatory.contrast`).

**Primary.** `D = frozen − reference mixture`, correct key-detour
answers out of three. The retention reading is confirmed for this model
if the mean is positive and the exact two-sided sign-flip value is at
most 0.05. Otherwise it is not confirmed for this model.

**Secondary.** Adaptive minus balanced rare-only, correct rare answers
out of six. One secondary contrast, tested at 0.05.

**Descriptive.** Family scores for the five memories; frozen minus
empty, balanced minus mixture, and adaptive minus mixture on key
detours; the retained-coverage split; key-detour accuracy by path
availability; seeds retaining a key-detour example; attempts,
admissions, and evictions by family; supplement families; unreachable
declarations; answers returned under the requested ID; a side-by-side
table with E015. No pooled test across the two models is planned.

**Conformance.** Every update trajectory is checked against the Lean
FIFO characterization.

**Reading the result.** Agreement with E015 on Q1 and Q2 would show that
its null results are not specific to Qwen3. A confirmed Q1 here would
show that they are. Either outcome is reported. One model pair does not
establish generality.

## Rules

- All 30 seeds are run. No interim analysis, no early stop, no added
  seeds. `--audit` is not run on the 30 seeds before the last completes.
- A transport failure reruns the whole seed. The partial directory is
  kept as `<seed>.partial-N`. Content errors are never retried.
- Every score is recomputed from stored prompts and responses.
- If LM Studio or the snapshot changes during the run, the run stops and
  the change is recorded in an amendment before continuing.
- Deviations and unexpected observations go in `analysis.md`.

## Replay

```sh
python3 -m unittest discover -s experiments/E016-second-model
root=experiments/E016-second-model/results/gemma-e4b
python3 -m src.second_model "$root" --audit | cmp - "$root/aggregate.json"
```

A live run needs the snapshot loaded in LM Studio as
`rare-case-gemma-e4b` and uses
`python3 -m src.second_model OUTPUT --gemma-model-dir MODEL_DIR`.

## Cost

2,430 local calls, about 209 s per seed on the development seeds, so
about 1.7 hours on the Apple M1 Pro. No paid compute.
