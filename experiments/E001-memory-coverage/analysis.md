# E001 feasibility results

## E001a · Unconstrained JSON proposal

Protocol commit `ea95b0f`, runner commit `ecffdc5`, Ollama 0.40.12 on
Apple M1 Pro. The fixture produced byte-identical outputs across two runs.
Three regression checks passed alongside the nine existing oracle checks.
An independent state-space relaxation agreed with the BFS oracle on all 36
graphs. Structural keys were unique across the four pools.

The live pilot completed 19 local calls, totaling 27,828 prompt and 1,096
output tokens in 126.3 seconds of request time. All calls returned JSON in
the expected outer shape. All six proposal calls selected IDs from example
memory, and zero of 14 model-selected slots contained a menu ID. The
predefined empty-slot policy was applied. Holdout IDs appear only in
evaluation tasks, never in memory or proposal/solve tasks.

| Arm | Initial rare examples | Final rare examples | Initial rare holdout | Final rare holdout |
| --- | ---: | ---: | ---: | ---: |
| Self-selected | 2/6 | 2/6 | 1/4 | 1/4 |
| Random | 2/6 | 1/6 | 1/4 | 0/4 |
| Targeted | 2/6 | 3/6 | 1/4 | 1/4 |

Both random supplements were correct ungated answers. Both targeted
supplements were key-detour tasks and one was solved correctly. Ungated
holdout accuracy was 2/2 throughout. The self-selected memory did not update,
so the intended selection comparison was unexercised. This run is a
diagnostic of the interface, with no inference about H1 or H2.

[Summary](results/e001a-qwen3-summary.json) ·
[Per-call trace](results/e001a-qwen3-calls.jsonl.gz)

## E001b · Constrained menu proposal

Protocol commit `3fa7d58`, runner commit `46bc8a9`. The follow-up completed
19 local calls, totaling 29,817 prompt and 1,156 output tokens in 127.9 seconds
of request time. All six proposals contained three distinct current menu
IDs, and all 14 consumed self-selected slots were valid. The change combined
an explicit allowed-ID prompt with a JSON schema enum.

| Arm | Final ungated memory | Final key-detour memory | Final unreachable memory | Final rare holdout |
| --- | ---: | ---: | ---: | ---: |
| Self-selected | 2/6 | 4/6 | 0/6 | 2/4 |
| Random | 3/6 | 3/6 | 0/6 | 2/4 |
| Targeted | 2/6 | 4/6 | 0/6 | 2/4 |

The initial memory included one example of each rare family. All three
arms ended with zero unreachable examples. Across arms and rounds, 3/3
ungated and 8/8 key-detour attempts passed verification, compared with
0/7 unreachable attempts. This counts attempts, including repeated tasks
across arms. Each arm's initial unreachable example was evicted by FIFO,
so that family disappeared even as the total number of rare examples
increased in every arm. On the fixed holdout, the initial scores were
2/2 ungated, 1/2 key detour, and 0/2 unreachable. Final scores were
2/2, 2/2, and 0/2 respectively in every arm. Targeted supplementation
gave no final accuracy gain over random on this run.

Replayed the saved responses through the scorer and confirmed stage counts,
FIFO transitions, held-out scores, and isolation of held-out tasks in both
pilots. E001b used the same graphs and holdout as E001a. This is one seed,
one model and two rounds. It tests choosing from balanced menus, and the
supplement arms had almost identical realized tokens (9,426/352 versus
9,424/352 prompt/output tokens). The ID numbering depends on pool order and
should be made opaque in new runs. The two solvable families have matched
graph size and optimal path length, while unreachable tasks have no such
match. H1 and H2 remain pending.

For the full study, retain family-level metrics and include frozen- and
empty-memory controls. Add a diagnostic arm that supplies an independently
verified answer for a supplemented task to test whether the solvability
bottleneck persists when the model need not solve the example to admit it.
That diagnostic changes the feedback signal and should be reported
separately from the matched supplementation comparison.

[Summary](results/e001b-qwen3-summary.json) ·
[Per-call trace](results/e001b-qwen3-calls.jsonl.gz)
