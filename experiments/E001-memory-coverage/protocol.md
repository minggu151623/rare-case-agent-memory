# E001 · Coverage across example-memory updates

Status: Draft. Freeze the model snapshot, run count, seeds, task generator,
budgets, prompts and analysis plan in a protocol commit before collecting
live model results.

## Task and interventions

Use directed graphs with a start, goal, and optional key required by some
edges. The model returns a shortest valid path or an unreachable answer.
An exact solver verifies solutions. Track structural families such as
ungated, key detour, and unreachable. Define rarity by a low reference
frequency before seeing outcomes. Match solvable families on path length
and graph size where possible. Analyze unreachable tasks separately from
length-matched comparisons.

Start paired runs with the same examples and model configuration. At each
round, use a common proposal and solve schedule. The verified memory from
that round feeds the next round.

- Self-generated: allocate all slots to the model's proposals.
- Random supplementation: reserve a fixed number of proposal slots for
  independently generated tasks sampled from the reference mixture.
- Targeted supplementation: reserve the same number for independently
  generated tasks in families underrepresented in the current memory.
  Use the same generator and label schema as random supplementation.

Keep the candidate and solution call limits, memory limit, admission rule,
and token caps fixed across arms. Record realized tokens, accepted-example
counts and compute cost. For the two supplementation arms, match the number
of external proposals. Acceptance yield is an outcome. Use deterministic
family tie-breaking and a fixed memory eviction rule.

## Measures and interpretation

- H1: compare the rare-family share of retained examples in the initial
  and final memory of the self-generated arm. Log valid proposal counts,
  solve and verification rates, admission and eviction counts per family
  and round. Retain stage denominators and invalid output counts.
- H2: compare final rare-family macro accuracy for targeted versus random
  supplementation on a fixed, sealed holdout. Pair by run seed and report
  uncertainty across runs and per-family results. Also report performance
  under the reference mixture and by round. A decline in memory coverage
  and a decline in held-out accuracy are distinct outcomes.
- Generate the holdout independently. Disjoint seeds alone can produce
  equivalent graphs, so check structural overlap across splits. Evaluation
  prompts receive the current memory, and evaluation outputs stay outside
  all proposal, admission and intervention decisions.

Use the CPU-only check to validate mechanics before calling a model. The
experiment concerns agent behavior with fixed weights and iterative example
memory. Training-based model collapse is a separate empirical question.
