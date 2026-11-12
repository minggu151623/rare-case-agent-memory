# E002 · Separating task selection from answer admission

Locked design for the six-seed mechanism study. E001b motivated this design.
E001 graphs and scores are pilot material and are excluded from E002.

## Question and predictions

Does selecting underrepresented task families improve coverage when the
agent must solve each selected task itself? Does providing a verified
answer for the external supplement change that result?

- Primary mechanism contrast: final number of unreachable examples in
  targeted+oracle minus targeted+model.
- Primary performance contrast: final rare-family macro accuracy in
  targeted+model minus random+model, at matched call and slot budgets.
- Secondary: final unreachable and key-detour accuracy, family-level
  coverage and stage counts, weighted accuracy (80/10/10), frozen- and
  empty-memory comparisons, and the targeting × answer-source interaction.
  Retention and held-out accuracy are separate outcomes.

Predict positive unreachable coverage for the primary mechanism contrast.
The performance contrast may be small if selection alone cannot overcome
admission failures. Report the signed differences even if negative.

## Population and assignment

Use the existing six-node, seven-edge directed graph generators. The
solvable families have shortest distance four. Unreachable tasks have a
route when locks are ignored. Use paired seeds 6201 through 6206. Generate
all pools in seed order and reject graph isomorphs across seeds, all pools,
and E001. Assign IDs only after shuffling each pool. The independent
holdout has three tasks per family. It is never used to generate, select,
solve, label or retain training examples. Each seed starts with the same
six verified examples across its four arms (four ungated, one key detour,
one unreachable), with a seed-shuffled FIFO order.

Two rounds, capacity six. Each round offers two background candidates
with families drawn independently from the 80/10/10 reference mixture.
Both graphs are shared across all arms in a seed and round. The third slot
is one supplement chosen from a shared independent pool with one instance
per family. Random draws its family from 80/10/10, shared between the two
random arms. Targeted chooses the least represented rare family in the
pre-round memory, with a tie order drawn once per seed. The task itself
then comes from the same supplement pool. The four arms are:

| Allocation | Supplement answer source |
| --- | --- |
| Random | Model |
| Targeted | Model |
| Random | Exact oracle |
| Targeted | Exact oracle |

In every arm, request model answers for all three candidates and log those
answers. For oracle arms, substitute the exact answer for the supplement
only before applying the common correctness and FIFO admission rules.
This matches calls, candidate count, token caps and admission rule while
changing access to a verified answer. Background examples always use
model answers. The adaptive targeting rule can choose different families
after earlier admissions differ, so the comparison estimates a policy
effect across two rounds. It is not an estimate with fixed supplement
identities.

Use the E001 pinned Qwen3 8B snapshot via loopback Ollama, temperature zero,
JSON mode, thinking disabled, context 4096, generation cap 384, one
fresh request per phase. A seed deterministically sets model sampling
and arm order. Collect an empty-memory and frozen-initial-memory
evaluation, then two solve calls and one final evaluation per arm, for
14 calls per seed and 84 total. Record token usage. Invalid or missing
answers score zero. A transport failure leaves partial logs, and that seed
may be restarted in a new directory. Never substitute a new seed after
seeing results.

## Analysis

Use the seed as the paired unit and report all six seed differences and
the mean. Report a two-sided exact paired sign-flip test of the mean
(64 sign patterns) as a sensitivity calculation under sign exchangeability.
Report raw numerators and denominators by family and across rounds. Treat
repeated tasks across arms as paired observations. Count attempts and
passes before and after oracle substitution. Keep the two primary
contrasts visible regardless of outcome and interpret this as a small
single-model mechanism study. E002 uses a fixed background task schedule,
so it does not directly test self-generated proposals or H1.
