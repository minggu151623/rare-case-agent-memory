# E001b · Menu-constrained proposal feasibility

Follow up on E001a's invalid proposal IDs. Keep the model, seed, graph pools,
holdout, arms, capacities, budgets, and scoring fixed. Change the proposal
interface to explicitly distinguish solved examples from new candidates.
Use an Ollama JSON schema with exactly three array entries from the menu
ID enum. The application still rejects repeated IDs and never retries an
invalid selection. Keep solve and evaluation prompts unchanged.

The prespecified feasibility check passes if all six proposal calls supply
three distinct menu IDs. Record raw and consumed slots, solve/admission
counts, and both holdout denominators. All accuracy contrasts are
exploratory. This is a rerun on the same seed and holdout as E001a, with the
prompt and output schema changed together. The hypotheses remain pending.
