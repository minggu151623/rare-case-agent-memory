# E008 · Relabeling during acquisition

All 36 local calls completed, with 51,988 prompt tokens and 3,088
output tokens in 307.7 seconds of request time. All calls returned
valid outer JSON. Replay verified every prompt, admission, eviction,
and held-out score. Structural keys, IDs, and families match the
original E002 pools for all 150 graphs.

| Condition | Policy | Ungated | Key detour | Unreachable |
| --- | --- | ---: | ---: | ---: |
| E002 fixed original labels | Random | 18/18 | 7/18 | 3/18 |
| E002 fixed original labels | Targeted | 18/18 | 18/18 | 0/18 |
| E004 rename frozen memory and queries | Random | 9/18 | 2/18 | 0/18 |
| E004 rename frozen memory and queries | Targeted | 11/18 | 1/18 | 0/18 |
| E008 rename throughout acquisition and evaluation | Random | 8/18 | 3/18 | 0/18 |
| E008 rename throughout acquisition and evaluation | Targeted | 8/18 | 2/18 | 0/18 |

In E008, targeted attempted 12 key-detour tasks and admitted two.
Random attempted three and admitted one. In the original E002
targeted arm nine of ten key-detour attempts were admitted. The
differences reflect the joint acquisition and evaluation change,
including the changes in adaptive allocation and memory composition.
Targeted key-detour results stayed near the floor after using
renamed inputs throughout, so an evaluation-only distribution
change cannot by itself account for the disappearance of the
original advantage in this setup.

[Aggregated results and paired counts](results/aggregate.json) ·
[Raw responses](results/qwen3-8b)
