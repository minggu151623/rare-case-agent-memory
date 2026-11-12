# Related work

- Shumailov et al. (2024), [AI models collapse when trained on recursively
  generated data](https://doi.org/10.1038/s41586-024-07566-y). Motivates measuring
  loss of low-frequency modes across rounds of feedback.
- Feng et al. (2025), [Beyond Model Collapse](https://arxiv.org/abs/2406.07515).
  Studies how verification can improve recursively generated training data.
  Our proposed verifier checks planning correctness, and the experiment measures
  the coverage of correct examples separately.
- [Propose, Solve, Verify](https://arxiv.org/abs/2512.18160). Uses formal
  verification in self-play and studies proposal diversity and difficulty.
  Compare its proposal and retention ablations to our stage-specific audit and
  budget-matched supplementation before making a novelty claim.
- [When Sample Selection Bias Precipitates Model Collapse](https://arxiv.org/abs/2606.13732).
  Analyzes selection against biased reference distributions. Compare this
  mechanism to changes in proposal frequency, solve rate and memory admission
  in the planning pilot.
- [METR Anthropic R&D assessment](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/).
  Motivates studying AI-assisted improvement loops. It studies organization-level
  R&D acceleration, which differs from the intervention studied here.

This is a targeted positioning scan. The novelty of the proposed contribution
remains to be assessed against the closest experimental protocols.

## Agent memory studies to compare against E001

- Xiong et al. (2025), [How Memory Management Impacts LLM
  Agents](https://arxiv.org/abs/2505.16067). Tests selective addition and deletion
  under memory constraints and distribution shift. Its evidence on experience
  following makes it a close comparison. Inspect whether its experimental
  contrasts can distinguish task availability, choice, solve success, and
  eviction, which the E001 log measures separately.
- Wang et al. (2026), [EvoMemBench](https://arxiv.org/abs/2605.18421). Compares
  evolving agent-memory systems across knowledge and execution tasks.
  Motivates a frozen-memory control for E001 and reporting whether the
  held-out tasks actually depend on examples for successful transfer.
- Wang, Panaganti, and Zhou (2026), [More Memory, Worse
  Agents](https://arxiv.org/abs/2610.27406). Studies the effect of persisting
  derived rules versus observed trajectories. E001 stores verified task-answer
  records and asks how their family coverage changes under repeated updates.
