# E012 · Matched rare-only supplementation

## Question

E002 compared adaptive targeting with a reference mixture that allocated only
3 of 12 supplements to rare families. Does adapting to the current memory
improve held-out rare accuracy when both policies spend every supplement on
rare tasks?

## Design

Reuse all six E002 pools and seeds (6201–6206). Rerun both model-answer arms
in the same local session using the E002 Qwen3 8B digest, Ollama 0.40.12,
prompt and decoding options. Each seed has two rounds, six FIFO slots, two
shared background candidates plus one rare supplement per round, and one
nine-query final evaluation per arm. Initial memory and all candidate pools
are identical across arms. Correctness gates all admissions. There are six
calls per seed and 36 total. No oracle supplies new answers.

Adaptive targeting uses E002's least-represented rule and its seed-specific
tie order. The nonadaptive control preassigns one key detour and one
unreachable supplement, in an independently randomized order per seed.
Draw the schedule with Random(seed + 612000) and shuffle arm order with
Random(seed + 612001). This matches the rare budget at each round and
tests adaptation against a balanced random order. Per-family proposal
counts can differ because adaptive allocation can repeat a family.

Use the unchanged E002 holdout and count missing or invalid answers as
incorrect. Score without retries for content errors. For a transport
failure, preserve the incomplete trace and retry the same entire seed in a
new directory. Keep run and report separate so the archived prompts and
responses can be replayed before interpretation.

## Analysis

Primary outcome is adaptive minus rare-only random final rare macro
accuracy. The two rare families have three queries each. Report the
numerators by family, seed-level paired gaps, mean and two-sided exact
sign-flip sensitivity under sign exchangeability. Report counts of
attempted, admitted and retained cases by family. A positive gap would
support adaptive allocation against this specific control. A small or
negative gap will be reported without an equivalence claim. Reused tasks
make E012 a controlled follow-up on E002 rather than an independent
benchmark replication. The archived E002 mixture arm is historical context.
