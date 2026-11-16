# Third-round (final) independent review

Produced on 2026-11-16 by the same AI reviewer agent as rounds
[one](INDEPENDENT_REVIEW.md) and [two](INDEPENDENT_REVIEW_ROUND2.md),
read-only, on commit `b42ede3`. The report is reproduced verbatim below.
After it, one sentence of the Limitations was reworded exactly as the
reviewer's caveat in section 2 suggests ("at zero gap", and a note that
the values depend on the form of the correlation). This is an AI review,
not human peer review.

---

Scope: `paper/main.tex` at HEAD `b42ede3`, compared with `3ffb8c2`. Read-only; no model or network calls; the working tree is unchanged. Line numbers refer to the current file.

**Verdict: READY — no required fixes.**

## Check scripts

All three reproduce their archives byte for byte:

- `sensitivity` against `sensitivity.json`: match.
- `check_manuscript` against `manuscript-statements.json`: match, 50 statements (l. 914 says 50).
- `E014-publication-audit.check` against `results.json`: match, 76 statements.

There are no undefined references, and all 20 bibliography entries are cited.

## 1. Status of round-two items

### Required fixes

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Causal "helped" in the contribution bullet | Resolved | ll. 94-95 now read "Descriptively, accuracy was higher when a stored example's own answer path solved the query." |
| 2 | Power statement resting on independence | Resolved | ll. 834-845 state that independence implies a spread near 1.2 answers against the observed 0.82, call the first values conservative, add a correlated simulation, and reconcile it with the 0.55 sizing statement. One caveat is in section 2. |

### Recommended items

| Item | Status | Evidence |
|---|---|---|
| "therefore depends" softened | Resolved | ll. 635-637: "consistent with". |
| Name the arms | Resolved | l. 628: "the random and targeted policies". |
| Fresh-motif scores in the summary | Resolved | ll. 634-635: 9/18 and 10/18, matching the appendix. |
| Drop "only" in the conclusion | Resolved | ll. 892-893. |
| "post hoc" in the conclusion | Resolved | l. 885. |
| Later commits add derived analyses | Resolved | ll. 910-911. |
| Frozen-minus-empty null in the abstract; abstract under 250 words | Resolved | The abstract now says the frozen memory was "only two answers ahead of the empty memory (53/90)". It is 249 words. |
| n per bar in the Figure 1 caption | Resolved | ll. 127-128. |
| Published versions of the new references | Resolved for four of five | Voyager stays an arXiv record; the reason is documented in `reference-sources.md`. |
| "Agents" in the title | Not resolved | l. 8. Non-blocking. |

## 2. Correlated-answer power simulation

**The model is stated fairly.** `correlated_power` makes the frozen answer copy the mixture answer on 54.4% of queries and answers the rest independently at a raised rate. ll. 839-841 describe this in plain words.

**The printed numbers are correct:**

- Independent spread: √(6 · 0.567 · 0.433) = 1.21 answers, printed as "near 1.2".
- Zero-gap spread of the correlated model: 0.81, against the observed 0.82.
- Power: 87.2% at 15 points and 43.9% at 10 points.
- Sizing: 0.55 × 0.819 / 3 = 15.0 points.
- False-positive rate at zero gap: 1.5%.

**One caveat, not blocking.** The 87% figure depends on the chosen form of correlation.

- In this model the whole gap falls on the non-copied queries, whose success rate rises to about 0.90. The spread of the difference therefore shrinks to 0.73 at a 15-point gap. "Reproduces the observed spread" (l. 841) holds at zero gap only.
- I ran a different model calibrated to the same zero-gap spread, in which both arms share a latent draw on 54.4% of queries. It gives 67% at 15 points and 34% at 10 points, with a spread of 0.90.
- A fair summary is "roughly 70 to 90% at 15 points, depending on the correlation structure". The manuscript's figure is at the top of that range.

I do not require a change because the model is named explicitly, the independent figure (46%) is printed beside it, and the overall statement remains "power is limited for small gaps". No conclusion depends on the 87%. Adding "at zero gap" after "observed spread", and noting that the figure depends on the form of correlation, would be more exact.

## 3. Abstract and bibliography

**Abstract (ll. 15-41): every number matches the archives.**

| Claim | Result |
|---|---|
| 18/18 against 7/18 | match |
| Frozen 16/18, empty 7/18, balanced 16/18 | match |
| One fixed path solves all 18 | match |
| Key-detour example kept in 6 of 30 seeds | match |
| 55/90 against 51/90 | match |
| +4.4 points, interval −5.6 to +13.3, p = 0.51 | match |
| Empty memory 53/90 | match |
| 29/32 against 20/32 on the same queries | match |
| 0/450 unreachable | match |
| 132 audited trajectories | match |

The framing is appropriately hedged. The path split is labelled descriptive, the retention reading is labelled post hoc, and FIFO conformance is described as the implemented update agreeing with the model.

**Bibliography.** The four upgraded entries are internally consistent with `reference-sources.md`: same DOIs, venues and years.

| Key | Venue | DOI |
|---|---|---|
| expel | AAAI 38(17), pp. 19632-19642, 2024 | 10.1609/aaai.v38i17.29936 |
| reflexion | NeurIPS 36, pp. 8634-8652, 2023 | 10.52202/075280-0377 |
| goodexamples | DeeLIO 2022, pp. 100-114 | 10.18653/v1/2022.deelio-1.10 |
| roledemonstrations | EMNLP 2022, pp. 11048-11064 | 10.18653/v1/2022.emnlp-main.759 |

The author lists are unchanged from the arXiv records, and the venues and years agree with what I know of these papers. I could not re-fetch the DOIs or page ranges without network access, so those rest on the authors' recorded Crossref lookups.

The sentence at ll. 188-190 now says the path split "points the other way" from Min et al. That is a fair and modest characterization.

## 4. Whole-manuscript scan

I found no remaining overclaim, inconsistency or numeric error that I would require fixed.

- **Hedging is consistent** across the abstract, the contributions (ll. 86-95), the results (ll. 707-721), the discussion (ll. 739-761), the limitations and the conclusion (ll. 882-896).
- **Protocol status is accurate** throughout: one primary contrast, two Holm-adjusted secondaries, the rest descriptive. Post-lock additions are identified as such (ll. 724-726 and Appendix C).
- **Lean claims** are unchanged from round one, when I rebuilt the proofs. They remain correctly scoped (ll. 327-341 and the last lines of Limitations).

## 5. Final scores

| Dimension | Score |
|---|---|
| Quality | 3/4 |
| Clarity | 3/4 |
| Significance | 2/4 |
| Originality | 2/4 |
| **Overall (NeurIPS 1-6, main track)** | **3, borderline reject** |

The venue score is unchanged and reflects scope, not errors. As a preprint the manuscript is accurate, reproducible and honestly framed.

## Final Zenodo verdict

**READY — no required fixes**

## Remaining non-blocking weaknesses

1. **Model-dependent power figure.** The 87% at 15 points is at the upper end of a plausible 67 to 87% range, and "reproduces the observed spread" holds at zero gap only (ll. 839-842).
2. **Uninformative confirmatory regime.** The frozen memory was barely better than the empty one, and three design factors changed together. The original generator was not rerun on fresh seeds, so a six-seed or batched-prompt artifact is not excluded. This is acknowledged at ll. 798-806.
3. **Narrow scope.** One 8B model, six-node synthetic graphs, a six-slot memory and stateless prompts. "LLM Agents" in the title overstates the setting.
4. **Thin positive account.** The path-reuse hypothesis rests on 32 observational answers covering 23 queries.
5. **Floor effect.** The unreachable family contributes no information beyond the floor.
6. **Presentation.** Two naming schemes for the same policies remain (ll. 363-366). Internal experiment IDs carry much of the narrative, and Figure 1 has no uncertainty marks.
7. **Self-attested timing.** The protocol timing rests on commit timestamps, not third-party registration, which the manuscript states. Voyager is cited as an arXiv record.
