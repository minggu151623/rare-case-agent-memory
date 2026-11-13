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

E008 completed and replayed all 36 calls. Independent labels
throughout acquisition did not restore the E002 advantage. The
manuscript now includes the setup and the negative result.

E009 completed the matched-exposure control. The Phi download
failed for lack of disk space. We removed only its incomplete
download files and switched to the cached Gemma model under a
recorded protocol amendment. E006 completed 60 calls with severe
answer omissions. E010 completed 36 single-query calls with
complete answers and directional, subset-specific agreement.

## 2026-11-13 · Manuscript audit and controlled follow-up

E011 replayed the reported scores and found an original-holdout shortcut.
The author requested two follow-up controls before preparing the next
preprint draft. E012 reruns adaptive selection against a balanced
nonadaptive rare-only schedule on the E002 pools. E013 keeps the original
label convention and tests transfer with nine equally frequent optimal
paths. Both protocols were committed before their model runs. The
replacement graphs passed independent state-space distance checks.

E012 and E013 completed 36 calls each on Qwen3 8B with Ollama 0.40.12
on an Apple M1 Pro. The archived traces replayed without format
failures. The adaptive E012 responses and original-batch E013
responses matched their source archives byte for byte. E012's
matched-budget gain came from one seed. E013 narrowed the adaptive
gap against the reference mixture and left its two-answer gap against
the balanced rare-only control unchanged. The manuscript now reports
these bounds and includes the paired contrasts.
