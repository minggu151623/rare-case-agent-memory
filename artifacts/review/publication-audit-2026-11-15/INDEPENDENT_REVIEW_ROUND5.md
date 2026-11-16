# Fifth-round re-review of the second-model fixes

Produced on 2026-11-16 by the same AI reviewer agent as
[round four](INDEPENDENT_REVIEW_ROUND4.md), read-only, on commit
`98c6d07`. The report is reproduced verbatim below. After it, the two
disclosures the reviewer suggested as non-blocking were added: the
repeatability observation (manuscript and `analysis.md`) and a clause
that the 81-call rerun was committed with its result. This is an AI
review, not human peer review.

---

**Verdict: READY — no required fixes.** All three required fixes from the last round are resolved. Every replay passes, and the strict-rule rerun of seed 7125 is exactly what the manuscript says it is. One new observation, that Gemma did not always give the same answer to the same prompt, is not disclosed. It does not touch any reported contrast, so I list it as non-blocking.

The tree is clean. f725427 changed the text, checks and analysis and added the rerun, and 98c6d07 re-exported the archive. Nothing under `src/` or `results/gemma-e4b/` changed since 87937d4, so the locked E016 analysis is still the one that was archived.

## 1. Status of earlier items (current line numbers in paper/main.tex)

**Required fixes**

| Fix | Status | Where |
|---|---|---|
| R1. Scoring-rule statements | Resolved | Lines 798–811, 917–919 |
| R2. Stale trace pin | Resolved | Lines 1001–1005 |
| R3. Stale "Gemma experiment" sentence | Resolved | Lines 961–964 |

- **R1.** "Only for the empty memory" is now "mainly for the empty memory" (line 798). The text now states:
  - the two frozen-memory ungated answers the rule rescued;
  - 1,077 of 1,080 solve calls returned the requested ID;
  - the rule admitted b000 in round one of seed 7125, once in each of the three updating arms;
  - the readout-only rescoring kept trajectories acquired under the locked rule;
  - seed 7125 was rerun under the strict rule.

  The Limitations clause now adds "admitted one example in one seed". analysis.md and `check_manuscript.py` were corrected to match, with three new assertions.
- **R2.** E001–E015 are pinned to 7df0cbdbc499 and E016 to 9c26ca535178, and the later strict-rule rerun is mentioned. The statement counts are now 76/50/27, which matches the scripts.
- **R3.** The sentence now names "The Gemma readout experiments E006 and E010".

**Earlier non-blocking items**

| Item | Status | Where |
|---|---|---|
| "Acquisition experiments used Qwen3 8B" | Resolved | Line 393 |
| "Null results on one model" | Resolved | Line 874 |
| Wording that read the nulls as equivalence | Resolved | Lines 888–889 |
| Abstract path split not marked as Qwen3-only | Resolved | Line 36 |
| Appendix omitted the four bodies read and the development-seed report run | Resolved | Lines 1257–1260 |
| No runtime or quantization details for E016 in the main text | Resolved | Lines 507–508 |
| No wall-clock timestamps in the traces | Not resolved | Inherent to the archive |
| Unreachable floor, two small models, one domain | Not resolved | Inherent; disclosed |

Line 393 now names E001 through E015. That range loosely includes the Gemma readout studies E006 and E010, but the sentence is not misleading.

## 2. Strict-rule material

**Replay.** `python3 -m experiments.E016-second-model.strict_rule | cmp - strict_rule.json` is identical.

**Independent check of `sensitivity-strict-rule/7125`.** I rescored all 45 readout calls with my own verifier and compared them with the stored summary.
- The trace has 81 calls. Provenance is `rare-case-gemma-e4b` on LM Studio.
- No lone-answer rescue was applied:
  - The three round-1 b000 solve responses are again keyed `"id"`. Each arm admitted only `['b001']` in round 1.
  - Seven empty-memory readout responses keyed `"id"` were all scored incorrect. Every readout mark agrees with strict scoring.
- The new scores match the manuscript:
  - key detours: frozen 3, mixture 1, balanced 2, adaptive 2, empty 0;
  - primary difference +2;
  - secondary difference 0.
- The rule-only rescues in the locked run match the text: 44 key-detour and 7 ungated answers for the empty memory, 2 ungated answers for the frozen memory, and 3 solve answers, all b000 in seed 7125 round 1.
- The balanced arm's final memory changed under the strict rule (b001 instead of s101). Its key-detour score did not.

**Undisclosed finding: one repeated prompt gave a different answer.** 57 of the rerun's prompts are byte-identical to prompts in the locked trace. One of them got a different response. Under the strict rule the balanced arm's final memory is identical to the locked adaptive arm's memory, so both runs asked h00 with the same memory, but:

| Run | Response to h00 |
|---|---|
| Locked run | `A,C,E,D,B` |
| Strict rerun | `A,C,E,B` |

h00 is ungated, so this does not affect any contrast. But it shows that Gemma's temperature-zero answers in LM Studio are not exactly repeatable. The rerun therefore mixes the rule change with run-to-run variation. Neither the manuscript nor analysis.md says so, and the protocol's development note says that a repeat run returned identical responses.

**Restraint.** The rerun is presented as a post hoc step prompted by a reviewer (lines 807–811, 1262–1263), on one seed. The conclusion "both contrasts are the same under either rule" is sound: seed 7125 is the only seed where the rule changed an admission. In every other seed the strict-rule trajectory follows from the stored responses. This is appropriately restrained. One gap: line 1010 still says "For every experiment that called a model, the protocol was committed before the results". The 81-call rerun had no prior protocol commit. It is disclosed as post hoc and is a sensitivity run rather than an experiment, so I treat this as non-blocking.

## 3. Reruns

All requested commands passed. Results are in the verification list.

## 4. Whole-manuscript scan

- Abstract, Introduction, design paragraph, the Results subsection at lines 762–814, Discussion, Limitations, Conclusion and Appendix are mutually consistent.
- The counts hold everywhere: 222 trajectories (42 + 90 + 90), 2,430 calls, 1.2 h, 270 queries, 660 unreachable tasks.
- No passage still implies a single acquisition model.
- No opposite-signed or non-significant estimate is read as an effect or as equivalence.
- I found nothing else I would require fixed before a Zenodo preprint.

## 5. Scores

| Criterion | Score |
|---|---|
| Quality | 3/4 |
| Clarity | 3/4 |
| Significance | 2/4 |
| Originality | 2/4 |
| Overall (NeurIPS main track) | 3, borderline reject: rigorous, transparent and replayable, but a synthetic domain, two small models and mostly null results |

**Zenodo preprint verdict: READY — no required fixes**

**Non-blocking weaknesses:**
- Gemma's temperature-zero answers in LM Studio are not exactly repeatable (1 of 57 repeated prompts in the rerun), and this is not disclosed. It should be noted in analysis.md and briefly near line 811.
- Line 1010's "for every experiment that called a model" sentence does not mention that the post hoc 81-call rerun was committed together with its results.
- Line 393's "E001 through E015" loosely includes the Gemma readout studies E006 and E010.
- The traces have no wall-clock timestamps, so git commit times are the only evidence for the protocol-before-results order. The E016 protocol and results commits are only 71 minutes apart.
- Both models fail every unreachable task. The secondary contrast is therefore effectively a key-detour contrast, and the adaptive rule is tested in a case that is unfavourable to it by construction.
- Two small models and one synthetic domain. The null results bound effects only within wide intervals: the primary intervals are about ±12 to 13 points with Qwen3 and run from −21 to +3 points with Gemma.

## Verification list (HEAD 98c6d07)

- strict_rule replay | cmp strict_rule.json: identical.
- E016 check_manuscript | cmp: identical, 27 statements.
- E016 `--audit` | cmp aggregate.json: identical.
- E015 check_manuscript | cmp: identical.
- E014 check | cmp: identical.
- E016 unit tests: OK.
- Strict rerun, checked independently: 81 calls; no rescue in acquisition or readout; round-1 admissions `['b001']` in all three arms; key detours 0/3/1/2/2; primary +2; secondary 0; 1 of 57 shared prompts gave a different response (ungated h00).
- Locked run, matching the manuscript: 1,077/1,080 solve calls returned the requested ID; 2 frozen-memory ungated answers rescued; one ungated example (b000) admitted in seed 7125 round 1 in all three arms.
