# Research log

## 2026-11-12 · Bootstrap

- The project owner agreed to study rare-case coverage in iterative LLM agent
  memory and compare targeted and random supplementation at matched budgets.
- We chose a finite planning domain and a CPU-based oracle. We reformulated
  correctness as separate questions about proposals, successful solutions,
  retained examples, and performance on unseen instances.
- The autoresearch workflow separates the protocol, implementation and results.
  Repository state provides a handoff for subsequent sessions.

## 2026-11-12 · E000 completed

The protocol was committed before implementation and execution. All nine
local oracle checks passed. The live pilot design remains a draft.

## 2026-11-12 · E001a local feasibility

Locked the protocol before implementation. The offline fixture reproduced
byte-for-byte and the Qwen3 pilot ran all 19 calls locally. Model-selected
slots were all invalid because the model picked IDs from example memory.
The observation motivates a menu-constrained proposal interface for E001b.
