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
