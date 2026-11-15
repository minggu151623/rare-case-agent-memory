# Second-round independent review

Produced on 2026-11-16 by the same AI reviewer agent as
[INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md), read-only, on commit
`3ffb8c2`. The reviewer's findings are reproduced below in its own
words, condensed only by removing the per-line status tables, which are
summarized in [REVIEW_VI.md](REVIEW_VI.md). This is an AI review, not
human peer review.

---

**Verdict: ready after two listed fixes.** All four round-one must-fix items are addressed, three fully and one partly. The revision introduces one new problem: the power statement in Limitations rests on an assumption the data contradict.

## Check scripts

All three reproduce their archives byte for byte: `check_manuscript` (47 statements), `E014-publication-audit.check` (76 statements), and `sensitivity`.

## Status of round-one must-fix items

1. Soften the "reusable answer" claims: **partly resolved.** Fixed in the Discussion heading, "working hypothesis", "suggest one reason", "similar", the abstract, and the conclusion. Not fixed: the contribution bullet still says "A stored example helped mainly when its own answer path solved the query", causal and unhedged. In the conclusion, "only" is stronger than the data.
2. "eight" descriptive values: **resolved.**
3. FIFO conformance framed as a finding: **resolved.**
4. Unreachable floor and Q2: **resolved.**

Optional items: matched-query control, primary standard deviation, the two uses of "42", the results figure, related work, Table 2 placement and the Q3 bootstrap bound are resolved. The frozen-minus-empty null is stated in the Discussion but not in the abstract. The abstract grew to 287 words. Both naming schemes remain. The title's "LLM Agents" remains for a single stateless-prompt model.

## New material

- **Same-query control: correct.** 29/32 with memory against 20/32 for the empty memory, 11 gained and 2 lost, 23 distinct queries, 117/208 for the other-path group; nine seeds and six routes.
- **Q2 restatement: correct.** (56 − 59)/90 = −3.3 points.
- **Figure 1: correct.** All twenty bar values were recomputed and match. The caption should give the denominators (18 answers per bar on the left, 90 on the right).
- **Appendix move: nothing lost.** Every removed sentence is an intended edit or present in Appendix B; all twelve `\input` files are still included; no undefined references. Three small defects: the E008 summary does not say which policy scored 3/18 and which 2/18; the fresh-motif result (9/18 and 10/18) is missing from the summary; "The measured gap therefore depends on how labels correspond" is stronger than six reused seeds allow.
- **Related work: modest and accurate, as far as I could check** without network access. All five are cited as arXiv preprints although each has a published venue. The Min et al. finding is closer to a contrast with the path split than a "related observation".
- **Power simulation: assumption named, but not stated fairly.** Independence implies a paired-difference standard deviation of about 1.2 answers; the observed value is 0.82, because both arms answer the same queries. With within-query correlation that reproduces the observed spread, power is roughly 35%, 68%, 91% and 99% at 10, 15, 20 and 25 points. The printed figures therefore understate power, and they sit awkwardly with the sizing statement (0.55 times 0.82 answers is 15 points). The error is in the conservative direction for a null result, but the text should say so.
- **Bootstrap streams: correct.**

## Scores

| Dimension | Round one | Round two |
|---|---|---|
| Quality | 3/4 | 3/4 |
| Clarity | 2/4 | 3/4 |
| Significance | 2/4 | 2/4 |
| Originality | 2/4 | 2/4 |
| **Overall (NeurIPS 1-6, main track)** | 3 | **3, borderline reject** |

Clarity improved through the figure, the appendix move and consistent hedging. The overall score is unchanged because scope is unchanged: one 8B model, a toy domain, confirmed nulls, and a positive account that remains descriptive.

## Zenodo verdict: ready after listed fixes

**Fixes required (both are one-sentence edits):**

1. Replace "A stored example helped mainly when its own answer path solved the query" in the contribution bullet with a descriptive form.
2. In the Limitations, add that the independent-answer assumption gives a larger paired-difference spread (about 1.2 answers) than observed (0.82), so the printed power values are conservative, and reconcile this with the sizing statement.

**Recommended, not blocking:** "therefore depends" to "is consistent with"; name the arms in the E008 summary; add the fresh-motif scores to the summary; drop "only" in the conclusion; add "post hoc" to the conclusion; mention that later commits add derived analyses; state the frozen-minus-empty null in the abstract and bring the abstract under 250 words; give n per bar in the Figure 1 caption; cite the published versions of the five new references; reconsider "Agents" in the title.
