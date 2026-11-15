# Independent review: "Auditing Rare-Case Coverage in LLM Agents with Iterative Example Memory"

Produced on 2026-11-16 by a separate AI reviewer agent with no access to
the revision session's context, working read-only, following the pinned
ml-paper-writing skill's `reviewer-guidelines.md` and `checklists.md`.
The text below is the reviewer's report, verbatim. Line numbers refer to
`paper/main.tex` at commit `c8c98ba`. The responses are in
[REVIEW_VI.md](REVIEW_VI.md). This is an AI review, not human peer review.

---

Scope: `paper/main.tex` and its `\input` files, read against the three review instruments. Read-only; no model or network calls. The offline replay, the manuscript check script and the Lean build were run, and nothing in the repository was modified.

## Summary

The paper audits a six-slot FIFO memory of verified graph-planning examples used by Qwen3 8B. An exploratory six-seed study found that adaptive allocation toward rare task families beat reference-mixture sampling 18/18 to 7/18 on key-detour queries. Frozen, empty and budget-matched controls, plus a fixed-path diagnostic, suggested the gap came from retaining one reusable example. A confirmatory experiment (E015: 30 fresh seeds, protocol committed first) did not confirm that reading: frozen 55/90 against mixture 51/90, sign-flip p = 0.51. Neither secondary contrast was established. A Lean 4 development proves the FIFO reference model.

The claimed contribution is a negative, methodological one: a memory-policy gap can vanish under matched controls, and coverage is not readout.

## Strengths

1. **Honest negative result.** The authors test and fail to confirm their own post hoc reading, and say so in the abstract, introduction, discussion and conclusion.
2. **Protocol discipline is verifiable.** The lock commit `7cb1188` (19:28) and the amendment `5dd2363` (19:39) both precede the results commit `6ae076f` (22:32). Between lock and results, `src/confirmatory.py` changed by one line (`RUNTIME` 0.40.12 to 0.40.16) and `protocol.md` only gained the 20-line amendment.
3. **Reproducibility is high.** `python3 -m src.confirmatory … --audit | cmp` reproduces `aggregate.json` byte for byte from stored traces. `check_manuscript.py` passes with 38 statements; the E014 archive lists 76.
4. **Lean claims are scoped correctly.** The manuscript says the proofs do not cover the generator, verifier, scorer or model output (ll. 291-292, 940-941).
5. **Useful controls.** The constant-answer baseline, frozen and empty memories and the rare-budget match are cheap and worth adopting.

## Weaknesses

1. **The confirmatory test ran where the retained item had no measurable value.** Frozen beat empty by only 2/90 (interval −10.0 to +14.4), so "retention does not matter" cannot be separated from "the example was never useful here".
   - Why it matters: E015 changed the generator, the round count and the readout format together (acknowledged at ll. 882-884). The E002 gap may equally be a batched-prompt or six-seed artifact.
   - Suggestion: state in the abstract that the frozen-minus-empty gap was itself null. Rerun the original generator with one-query readout on fresh seeds.

2. **The "reusable answer" account is stated more firmly than the protocol allows.** It rests on a split the protocol lists as descriptive (29/32, observational).
   - Where: the Discussion heading "The original gap was retention of a reusable answer" (l. 822), "Accuracy followed coverage only where a stored answer could be reused" (l. 955), "show why adaptation had no room to help" (l. 782), "accuracy was the same" (l. 855), and "helped" in the abstract (l. 38).
   - Extra evidence I computed from the traces: the 32 answers cover only 23 unique queries. The empty memory answers 20/32 of those same queries, so the matched gain is 9/32 (11 gained, 2 lost), not the 35 points implied by 29/32 against 116/208. For the "other path" group the matched comparison is 116/208 against 117/208.
   - Suggestion: report this matched comparison, soften the heading and l. 955, and call the account a hypothesis.

3. **FIFO conformance is presented as an empirical finding.** "Memory coverage followed a machine-checked FIFO model" is listed as half of the main result (ll. 20-21, 954-955).
   - Why it matters: the memory is implemented as FIFO, so agreement in 132 trajectories is an implementation check. It is not evidence about the model.
   - Suggestion: move it to reproducibility. Say "132 audited trajectories", since E001 and the E012 adaptive rerun are not in the 42.

4. **The unreachable family and Q2 are at a structural floor.** The model never emitted an unreachable declaration (0 of 3,510).
   - Why it matters: "No memory helped on unreachable tasks (0/450)" measures a response the model does not produce. Q2's "rare accuracy" is key-detour accuracy with the denominator doubled, so −1.7 points is −3.3 key-detour points. The floor is disclosed only at l. 807.
   - Suggestion: say so where Q2 is reported and in the abstract.

5. **Significance and presentation are limited.** One 8B model, six-node graphs, a single stateless prompt ("agents" in the title is generous), and 15 references.
   - Why it matters: the narrative is carried by eleven internal experiment IDs and two naming schemes (ll. 322-325). There is no results figure, and the abstract is about 265 words of numbers.
   - Suggestion: move E003 to E010 to an appendix, use one name per policy, and add one figure showing retained coverage against accuracy for E002 and E015.

## Questions

1. What does the original generator give on fresh seeds with one-query readout? This would separate a seed artifact from a batching effect and from path reuse.
2. On the 23 path-matched queries, are the gains concentrated in a few seeds or routes?
3. The protocol records that the label interaction was demoted from primary to secondary on lock day. Was that decision made with any knowledge of the development-seed scores?
4. What power does the sign-flip test have on three-point outcomes with 13 of 30 ties? The "0.55" figure appears to be a t-test approximation.

## Minor issues (`paper/main.tex`)

- **l. 816:** "one of eight uncorrected descriptive values". `aggregate.json` under `descriptive` contains seven sign-flip values (balanced minus mixture, adaptive minus mixture, frozen minus empty, three shared-minus-mixed, one interaction). `analysis.md` also says eight. Not covered by the check script.
- **ll. 297 and 591:** "42" denotes two different sets (conformance trajectories from E002, E012 and E008; evaluated memories from E002, E012, frozen and empty). Disambiguate.
- **ll. 763-772:** the protocol requires the standard deviation of the primary differences (0.819; standardized effect 0.16). It appears only in `analysis.md`.
- **ll. 68-80:** the introduction interleaves six-seed and 30-seed results. Table 2 sits in the introduction but is first discussed at l. 758.
- **ll. 85-86:** "mostly retained coverage on the original holdout" reads as a finding in the contribution bullet. Add "post hoc".
- **l. 856:** "A coverage count therefore bounds what a memory can contribute" is not shown by the data.
- **l. 780:** the Q3 lower bound (−11.7) sits on a discreteness boundary. A different resampling stream gives −11.1. Note the Monte Carlo sensitivity.
- **ll. 972-973:** "evidence fixed at commit 7df0cbd", but `check_manuscript.py` and `manuscript-statements.json` changed afterwards. No data changed. Cite the release commit.
- **ll. 349, 352, 552, 706, 913, 933:** stray mid-line sentence joins left over from editing.

## Verification list

Twenty-four claims were recomputed from the per-seed data or archives. All match except the item at l. 816 above.

| # | Claim | Result |
|---|---|---|
| 1 | Scores: empty 62/53/0, frozen 87/55/0, mixture 88/51/0, balanced 88/59/0, adaptive 88/56/0 | match |
| 2 | Key-detour example retained in 0/30/6/24/20 seeds | match |
| 3 | Primary mean +4.44 points; distribution +1×11, 0×13, −1×5, −2×1 | match |
| 4 | Primary exact sign-flip 0.5069 | match |
| 5 | Primary bootstrap −5.56 to +13.33 | match |
| 6 | Q2 −1.67 points, interval −5.0 to +1.67, p 0.508, Holm 0.508 | match |
| 7 | Q3 −5.0 points, p 0.180, Holm 0.360 | match (interval lower bound: see l. 780 note) |
| 8 | Balanced minus mixture +8.89 (0.0 to 17.78), p 0.096 | match |
| 9 | Adaptive minus mixture +5.56 (−1.11 to 12.22), p 0.227 | match |
| 10 | Label interaction, adaptive minus mixture −10.0 (−17.8 to −2.2), p 0.031 | match |
| 11 | Coverage split 145/240 (60.4%) and 129/210 (61.4%) | match |
| 12 | Path split 29/32, 116/208, 129/210 | match (recomputed from traces) |
| 13 | Unreachable 0/450; 0 of 208 attempts admitted | match |
| 14 | Supplements 84/36 adaptive, 60/60 balanced, mixture 26/120 | match |
| 15 | Key-detour admissions 27 and 45 | match |
| 16 | 2,790 calls, 1,350 answers, one format failure (label sub-study, output limit), 2.84 h | match |
| 17 | 0 unreachable declarations in 3,510 answers (1,080 + 1,350 + 1,080) | match |
| 18 | E015 conformance: 90 trajectories, 270 checks, 130 losses, 121 without admission | match |
| 19 | E014: 42 trajectories, 126 checks, 0 mismatches, 32 rare losses all without admission | match |
| 20 | 132 = 42 + 90 | match |
| 21 | E014 split 80/87 (25 at 3/3), 9/39 (8 at 0/3); unreachable 3/51 and 0/75 | match |
| 22 | E002/E012 key detour: empty 7, frozen 16, mixture 7, balanced 16, adaptive 18 of 18; mixture lost the example in 4 of 6 seeds | match |
| 23 | E013 varied 3/5/7 of 18; best fixed path 18/18 and 2/18; gap change −38.9 points, p 0.125; balanced gap from one seed | match |
| 24 | E009 differences (3, 6, −4, 2, −1, 1), 19.4 points, p 0.50 | match |

**Protocol conformance.** The primary contrast, decision rule, Holm adjustment over two secondaries and the descriptive list all match `protocol.md`. The runtime amendment, development seeds, format failure and the post-lock unreachable count are disclosed. There is no undisclosed deviation. The over-confident passages are those in Weakness 2. The commit timestamps are self-attested, which the manuscript acknowledges (l. 979).

**Lean.** `lake build` succeeded (1,708 jobs) in `/tmp/rare-case-lean/formal`, whose sources are byte-identical to `formal/`. There is no `sorry`, `admit`, custom `axiom` or `native_decide`. Sixteen statements are exported: 13 depend on `propext`, `Classical.choice` and `Quot.sound`, and the three list-level ones on `propext` and `Quot.sound` only. The paragraph at ll. 269-289 matches the theorem statements, and its hypotheses are equal to or stronger than Lean's. Two caveats: the "probability" is a finite product weighting, which l. 277 says, and "keeps the newest K entries" (`foldl_admit_eq_retain`) is proved but is not among the sixteen printed. The manuscript does not claim the proofs validate empirical results.

## Scores

| Dimension | Score |
|---|---|
| Quality | 3/4 |
| Clarity | 2/4 |
| Significance | 2/4 |
| Originality | 2/4 |
| **Overall (NeurIPS 1-6, main track)** | **3, borderline reject** |

The work is careful and honest, but the confirmed findings are nulls on one small model and a toy domain, and the positive account is descriptive.

## Zenodo preprint verdict: yes, after listed fixes

**Must fix**

1. Soften l. 822 (heading), l. 955, l. 782 and l. 855 to match the descriptive status; "helped" in the abstract likewise.
2. Correct or justify "eight" at l. 816 (the archive has seven).
3. Reframe FIFO conformance as an implementation check, not a "main result" (ll. 20-21, 954-955), and say "audited" rather than "all archived".
4. State at Q2 and in the abstract that the unreachable family is at a response floor.

**Optional**

- Add the matched-query control for the path split (20/32 with the empty memory on the same queries).
- Report the primary standard deviation.
- Disambiguate the two uses of "42".
- Add one results figure.
- Trim the abstract and the E-number narrative.
- Cite the release commit.
- Broaden the related work.
