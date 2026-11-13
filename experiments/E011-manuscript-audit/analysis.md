# E011 · Manuscript evidence audit

Post hoc checks on archived outputs and deterministic graphs. No new
model inference. Run from the repository root with
python3 -m experiments.E011-manuscript-audit.check.

- Independent state-space relaxation agrees with the production BFS on
  204 E002 and fresh E003 graphs.
- The generator-aware constant path A-D-C-D-B scores 18/18 on original
  key detours and 0/18 on fresh key-required E003 graphs, both before
  relabeling. This is a shortcut audit, with knowledge of the family and
  generator. It does not measure classification or model mechanism.
- Qwen's archived batch results on the exact six E010 queries show
  targeted-minus-random gaps of +3/6, 0/6, +3/6. Gemma's single-query
  results give +3/6, -1/6, +2/6. Only a qualitative comparison is justified.
- E002 targeted/model allocated 12/12 supplements to rare families
  versus 3/12 for random/model. A rare-only random baseline is missing.
- E009 reproduces a 19.4-point difference in policy gaps. Leave-one-seed-out
  means span 3.3 to 36.7 points. The prompt manipulation also changes
  consistency among memory items and among queries, and call order
  was fixed. It cannot isolate alignment between the two lists.
- All archived aggregate reports E002–E004 and E006–E010 reproduced.
  The E005 enumeration and 14 existing unit tests passed.

## Editorial judgment

The evidence supports a narrow empirical case about representation-dependent
policy comparisons. Prior work documents graph-encoding and few-shot
sensitivity and compares memory with ground-truth executions. The useful
increment is testing a memory-policy gap with graph-level renderings
matched across prompt conditions, alongside a trace of family admission
and eviction. E005 is a reference calculation under i.i.d. assumptions.
A general claim of improved planning, adaptive selection, or cross-model
replication needs new evidence. The main missing comparisons are varied
optimal paths under stable labels and a nonadaptive rare-only sampler.
