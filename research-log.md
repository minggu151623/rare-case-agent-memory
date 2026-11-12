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

## 2026-11-12 · E001b local feasibility

Locked the follow-up protocol and constrained proposal outputs to the current
menu. All six model proposals contained three distinct allowed IDs. The
unreachable family disappeared from all three memories through solve failure
and FIFO eviction, even while aggregate rare-family counts rose. Final
rare-holdout accuracy tied across arms. The main study remains a draft.

## 2026-11-12 · E002 locked and started

E002 crosses random versus targeted task selection with model versus exact
supplement answers. It uses six fresh paired seeds, disjoint graph splits,
opaque task IDs, and frozen- and empty-memory controls. The locked protocol
precedes implementation and inference. The offline fixture reproduced
byte-for-byte. The manuscript introduction and methods were drafted using
Orchestra Research's ml-paper-writing skill and compiled with a verified
bibliography.

## 2026-11-12 · E002 completed

Archived and replayed 84 responses from the six locked seeds. Recorded
both primary contrasts, controls, and family-level results. Integrated
them into the preprint draft. The main follow-up is to test sensitivity
to fixed node labels and graph templates on fresh graphs.

## 2026-11-12 · E003 and manuscript completed

Ran and replayed all 36 transfer calls. Renaming vertices removed the
targeted key-detour advantage. The same advantage was absent on fresh
motifs. These results bound the E002 performance claim. The author
will handle Zenodo publication.

## 2026-11-12 · Extended study

The author requested a stronger manuscript with self-critique.
E004 separated demonstration and query labels and added a shared
derangement. E005 checked the exact FIFO reference model on 3,150
cases. E007 audited 216 scored records and found no literal path
reuse among lost key-detour answers. E008 tests relabeling throughout
acquisition. E006 is a pre-specified Phi evaluation of the frozen
Qwen memories. The author's Zenodo submission remains separate.
