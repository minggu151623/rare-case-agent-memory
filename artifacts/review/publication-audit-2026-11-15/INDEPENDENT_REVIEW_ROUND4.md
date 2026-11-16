# Fourth-round independent review: the second-model experiment

Produced on 2026-11-16 by a new AI reviewer agent, on a different model
from the reviewer of rounds one to three, with no access to the revision
session's context, working read-only on commit `87937d4`. The report is
reproduced verbatim below. The responses are in
[REVIEW_VI.md](REVIEW_VI.md). This is an AI review, not human peer review.

---

## Summary of the change under review

E016 runs the E015 policy comparison again with Gemma 4 E4B as the acquisition model. It uses the same 30 seeds and task pools, one task per solve call, no label sub-study, and a single-entry scoring rule. The headline is that the retention reading is not confirmed. Frozen minus mixture is −8.9 points (bootstrap −21.1 to +3.3, exact sign-flip 0.240). Adaptive minus balanced is not established (+1.7 points, p = 0.375). The numbers are correct, and in the main text they are reported with appropriate restraint. However, I found one factual misstatement about the scoring rule that the authors' own checks do not catch. There are also two passages that are now stale.

## 1. Protocol discipline

- The commit order is correct. The protocol, runner (`src/second_model.py`), tests, the `src/confirmatory.py` changes (`only_entry`, `single_solve`, `labels`, `single_entry`) and both development directories were committed at 0a2f99a (08:49). The 30-seed results came at 9c26ca5 (10:00) and the text at 87937d4 (10:02).
- No file under `src/` changed after 0a2f99a. The analysis code is therefore exactly what was locked.
- The 71 minutes between the two commits barely covers the 1.15 h of request time. The traces carry no wall-clock timestamps, so git commit times are the only evidence for the order. This is not a third-party guarantee.
- The rule was chosen after reading the response keys of the two interface seeds and four response bodies. This is disclosed in protocol.md and in the Appendix (lines 1240–1245). The Appendix leaves out two facts:
  - four bodies were read;
  - the report code was run on the development seeds, which revealed the unreachable floor.
- Bias assessment: the rule cannot affect the primary contrast through readout scoring, because neither the frozen nor the mixture readout had a key-detour answer rescued. It raises the empty-memory score, from 4/90 to 48/90 on key detours, so it works against any frozen-over-empty benefit. That is a conservative direction.
- **The rule also acted on acquisition, which the paper does not say.** In seed 7125, round 1, all three updating arms got a solve response keyed `"id"` for ungated task b000. The rule scored it, and b000 was admitted (`admitted_ids: ['b000','b001']` in all three arms). It also rescued two frozen-memory ungated readout answers (7101/h05, 7130/h06).
- So the "strict rule" sensitivity only rescores readout on trajectories that were acquired under the lenient rule. A genuine strict-rule run of seed 7125 would have different memories. Seed 7125 is the seed with the single +2 primary difference.
- This cannot overturn a result with p = 0.24. But lines 796–801 state as fact that "The scoring rule matters only for the empty memory" and that the contrasts are "identical under both rules", and that statement is false. analysis.md line 48 has the same gap, and `check_manuscript.py` only compares the readout-rescored per-seed vector.

## 2. Reruns

All seven commands passed. Details are in the verification list.

## 3. Independent recomputation

I wrote my own path verifier (BFS on location and key, with the optimality check), my own family classifier and my own single-entry rule. I ran them on the raw `calls.jsonl.gz` traces, plus a separate sign-flip enumeration and bootstrap.

- **Every value matched the archive.** That covers family scores, retained counts, the primary and secondary contrasts (means, sign counts and exact p), the descriptive contrasts, the coverage and path splits, the same-query control, the strict-rule empty-memory score, the response-key counts and the unreachable declarations. All are itemized in the verification list.
- My bootstrap uses a different random stream. It reproduced the archived intervals to within one grid step: balanced minus mixture gave −17.8 against the archived −16.7, and everything else was identical.
- The Qwen3 column of Table `tab:second-model` matches the E015 aggregate.

## 4. Manuscript reading

**Accurate and well hedged:**
- The abstract (lines 33–35, 38–41).
- The contribution bullet (97–99).
- The design paragraph (492–507).
- The subsection at lines 760–803, which explicitly says the opposite-signed estimate is not an effect ("Neither is established").
- The Limitations sentence "Two models do not establish generality" (907–909).
- The Conclusion (968–969).
- The trajectory total: 42 + 90 + 90 = 222.
- The statement counts 76/50/24, which match the three scripts.

**Problems:**
- Lines 796–801 and 905–907: see section 1.
- Lines 988–990 say the traces and aggregates "are fixed at commit 7df0cbdbc499" and that later commits only "add analyses derived from the same traces". 7df0cbd is from 2026-11-15, before E016. The E016 traces were added later, at 9c26ca5. The pin is stale.
- Lines 949–951: "The Gemma experiment … Its single-query evidence measures only readout from Qwen-generated memories on a fixed subset." This was written for E006/E010. It now contradicts E016, where Gemma builds its own memory.
- Line 393 ("The acquisition … experiments used Qwen3 8B") and line 864 ("null results on one model") have become loose but are recoverable from context.
- Lines 876–878 ("which is what one would expect if the policies do not differ") come close to reading two non-significant opposite signs as support for no effect.
- The abstract's path-split figures (lines 36–38) are Qwen3-only, but the sentence does not say so.

## 5. Scores

| Criterion | Score |
|---|---|
| Quality | 3/4 |
| Clarity | 3/4 |
| Significance | 2/4 |
| Originality | 2/4 |
| Overall (NeurIPS main track) | 3, borderline reject: careful, honest, replayable, but a synthetic domain, two small models and null results |

**Zenodo preprint verdict: READY AFTER FIXES**

**Required fixes (paper/main.tex):**
1. **Lines 796–801, and the matching clause at 905–907.** Replace "The scoring rule matters only for the empty memory" and "identical under both rules" with an accurate statement. It should say:
   - the rule also scored 3 of 1,080 solve responses, all in seed 7125 round 1 (ungated b000, admitted in all three updating arms);
   - it scored 2 frozen-memory ungated readout answers;
   - the strict-rule primary is a readout-only rescoring of trajectories acquired under the locked rule.

   Also report 1,077/1,080 solve calls returning the requested ID, as protocol.md line 82 requires. analysis.md line 48 and `check_manuscript.py` should be aligned with this.
2. **Lines 988–990.** Update the trace pin to a commit that includes the E016 traces (9c26ca5 or later), or state that the E016 traces were added after 7df0cbd.
3. **Lines 949–951.** Change "The Gemma experiment" to "The Gemma readout experiments E006 and E010" so that it does not contradict E016.

**Non-blocking weaknesses:**
- Lines 393 and 864 are worded as if only one acquisition model was used.
- Lines 876–878 lean toward reading the nulls as equivalence.
- Abstract lines 36–38 do not say the path split is Qwen3-only.
- Appendix 1242–1244 leaves out the four bodies read and the development-seed report run.
- The main text gives no runtime or quantization details for E016.
- The traces have no wall-clock timestamps.
- Both models sit at a floor on unreachable tasks, which makes the secondary contrast a key-detour contrast that is unfavourable to the adaptive rule by construction.
- Two small models and one domain.

## Verification list

- HEAD = 87937d4; working tree clean; no `.partial-N` directories.
- `unittest discover -s experiments/E016-second-model`: 3 tests OK.
- E016 `--audit` | cmp aggregate.json: identical.
- E016 check_manuscript | cmp: identical (24 statements).
- E016 exploratory | cmp: identical.
- E015 `--audit` | cmp: identical.
- E015 check_manuscript | cmp: identical (50 statements).
- E014 check | cmp: identical (76 statements).
- Recomputed independently and matching:
  - Family scores (empty / frozen / mixture / balanced / adaptive), ungated: 86/87/87/88/88; key detour: 48/47/55/49/52; unreachable: all 0.
  - Seeds retaining a key-detour example: 0/30/6/29/21.
  - Primary: mean −0.2667 (−8.89 pp), signs 5/15/10, p = 0.23980712890625, interval −21.11 to +3.33.
  - Secondary: +1.67 pp, signs 4/25/1, p = 0.375, interval −0.56 to +3.89.
  - Frozen minus empty: −1.11 pp, p = 1.0.
  - Balanced minus mixture: −6.67 pp, p = 0.313.
  - Adaptive minus mixture: −3.33 pp, p = 0.613.
  - Coverage split: 140/258 (86 memories) against 111/192 (64 memories).
  - Path split: 25/36, 115/222, 111/192.
  - Same-query control: empty memory 21/36 (7 gained, 3 lost) and 118/222 (31 gained, 34 lost).
  - Strict-rule key-detour scores: 4/47/55/49/52.
  - Readout calls returning the requested ID: 1,176/1,350; the other 174 are 169 empty-memory `"id"`, 2 frozen `"id"`, and 3 frozen keyed i03/i06/i08.
  - Solve calls returning the requested ID: 1,077/1,080.
  - Zero asked tasks declared unreachable.
  - Unreachable attempts 210 with 0 admitted; adaptive spent 86 of 120 supplements on unreachable tasks.
  - Request time 4,152 s (1.15 h).
  - Qwen3 column 53/55/51/59/56.
- **Undisclosed finding:** the single-entry rule caused the admission of b000 in seed 7125 round 1 in all three updating arms. It also rescued frozen-memory ungated answers 7101/h05 and 7130/h06.
