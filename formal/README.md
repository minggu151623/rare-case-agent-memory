# FIFO coverage in Lean 4

Formalization of the full positive-capacity FIFO reference model in
[Section 4](../paper/main.tex) and [E005](../experiments/E005-fifo-null/analysis.md).

The pinned Lean and Mathlib versions are 4.26.0. With
[Elan installed](https://lean-lang.org/install/manual/), run from this
directory:

```sh
lake exe cache get \
  Mathlib.Algebra.BigOperators.Pi \
  Mathlib.Algebra.Module.Pi \
  Mathlib.Algebra.Module.Submodule.LinearMap \
  Mathlib.Analysis.SpecificLimits.Normed \
  Mathlib.Data.Nat.Choose.Bounds Mathlib.Data.Nat.Choose.Sum \
  Mathlib.Tactic.FieldSimp Mathlib.Tactic.Linarith Mathlib.Tactic.Ring
lake build
lake env lean -DwarningAsError=true FifoCoverage.lean
```

The last command prints the axioms of the sixteen exported statements. The
checked theorems use only `propext`, `Classical.choice`, and `Quot.sound`.
No file contains `sorry`. The
[Python check](../experiments/E005-fifo-null/verify.py) independently compares
the finite formula with rational enumeration on 3,150 configurations.

| Statement | Meaning |
| --- | --- |
| `no_replenishment` | With no new focal example, the focal family is absent once the number of admissions reaches its last initial position. |
| `foldl_admit_absent_iff` | Absence requires that neither the surviving initial suffix nor the surviving admission suffix contains the focal label. |
| `paper_weights` | The normalized parameters reproduce the direct i.i.d. outcome weights from E005. |
| `iid_finite` | Exact finite-horizon formula, written as a sum over 0 through T with terms below the last initial position set to zero. |
| `iid_absent_before_last` | When T is below the last initial focal position, the absence probability is zero. |
| `iid_no_admission_of_rate_zero` | At zero admission rate the initial focal-absence indicator is unchanged. |
| `iid_limit` | At positive admission rate the long-run absence probability converges to the nonfocal share raised to the capacity. |
| `iid_absence_add_presence` | The product weighting is normalized: the absence and presence weights sum to one at every horizon. |
| `iidAbsence_nonneg`, `iidAbsence_le_one` | With `u, v ≥ 0` and `u + v ≤ 1` the absence value lies in the unit interval. |
| `absence_limit_le_iff` | For capacity `K ≥ 1` and shares in `[0, 1]`, the limit `(1 - q)^K` is at most `(1 - q⋆)^K` exactly when `q ≥ q⋆`. |
| `admitted_share_ge_iff` | With proposal share `p ∈ [0, 1]` and positive pass rates, the admitted share `pα / (pα + (1 - p)β)` is at least `q⋆` exactly when `p ≥ q⋆β / (α(1 - q⋆) + q⋆β)`. |
| `long_run_absence_le_iff` | The two previous statements composed: Section 4's proposal-share threshold for a long-run absence target. |
| `example_equal_rates`, `example_unequal_rates` | The two worked examples in Section 4: `0.9^6 = 0.531441`, admitted share `1/37`, and `0.84 < (36/37)^6 < 0.85`. |

The initial list is full and ordered oldest first. The probability model
uses a finite product weighting of the three possible outcomes per
attempt, with focal admission, other admission, and rejection weights
`u`, `v`, and `1-u-v`. The probabilistic interpretation assumes
`u,v ≥ 0` and `u+v ≤ 1`. The theorem concerns this reference model.
Empirical scores continue to use the archived model outputs and Python
scorer.

The threshold statements use `δ = (1 - q⋆)^K`, so no real root appears.
For `0 < δ < 1` the manuscript's `q⋆ = 1 - δ^{1/K}` is the unique value
in `[0, 1]` with that property.

## What the proofs do and do not cover

The proofs cover the FIFO update on lists, the i.i.d. reference law, its
normalization, its limit, and the threshold algebra. They do not cover
the Python generator, verifier, or scorer, any model output, or any
empirical score in the manuscript. The adaptive experiments do not
follow the i.i.d. law. [E014](../experiments/E014-publication-audit/analysis.md)
checks the list-level lemma `foldl_admit_absent_iff` against all 42
archived update trajectories and finds no mismatch in 126
family-trajectory checks. That replay ties the experiment code to the
formal update rule on those runs only.

The list-level lemma `absent_after_flush` also applies to histories
from adaptive policies. Once at least K admissions have occurred, the
last K admissions determine coverage. A policy-level guarantee that
every such window contains the focal family is a separate assumption.
