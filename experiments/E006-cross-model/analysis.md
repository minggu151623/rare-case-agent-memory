# E006 · Cross-model batch readout

The original Phi download failed before inference. The locked Gemma
amendment records the cached model hashes and the response schema
adjustment. The complete run used LM Studio 0.4.25+1, the pinned Gemma 4
E4B MLX 4-bit model, and the frozen Qwen memories. The interrupted
object-only diagnostic is archived separately and is excluded from
the reported batch outcomes.

All 60 calls completed. They consumed 121,455 prompt tokens and 1,707
output tokens in 269.7 seconds of request time. All outer answers
objects parsed, and no separate reasoning content was returned.
Each call included exactly the first query ID. Across the 540
requested answers, 60 IDs appeared and 480 were missing. Scoring
missing answers as incorrect reproduces the following counts.

| Condition | Random ungated | Targeted ungated | Random key detour | Targeted key detour |
| --- | ---: | ---: | ---: | ---: |
| Original | 3/18 | 3/18 | 0/18 | 0/18 |
| Memory only | 3/18 | 3/18 | 0/18 | 0/18 |
| Queries only | 0/18 | 1/18 | 0/18 | 0/18 |
| Independent both | 1/18 | 1/18 | 0/18 | 0/18 |
| Shared | 3/18 | 3/18 | 0/18 | 0/18 |

All unreachable scores were 0/18. Replay reconstructs every prompt
and item score. The all-zero key-detour cells cannot distinguish
invariance from a floor caused partly by missing answers. E010
measures single-query behavior separately. E006 varies model,
quantization, backend, and response grammar together and holds
memory acquisition fixed. It provides no replication of the Qwen
memory-policy advantage.

[Family and seed counts](results/aggregate.json) ·
[Answer completeness](results/completeness.json) · [Raw calls](results/gemma-e4b)
