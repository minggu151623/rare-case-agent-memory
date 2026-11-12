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
