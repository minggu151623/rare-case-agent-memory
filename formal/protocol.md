# Formal verification of the FIFO reference model

Formalize the FIFO proposition in Section 4 and E005. Represent entries
oldest first, using Booleans for membership of the focal family. A
rejection leaves the full buffer untouched. An admission drops its head
and appends the new entry. Check that loss without focal replenishment
occurs once the admission count reaches the last initial focal position.

Define the finite i.i.d. law by weighting the three possible outcomes
(rejection, other admission, focal admission) independently at each
attempt. Prove the printed binomial formula and the no-admission case
for all finite horizons, and prove the positive-admission limit.
Check the equivalence of the absence event used in the calculation
to the FIFO update semantics. Run Lean with warnings as errors and
inspect the axioms of the exported theorems. Retain E005's independent
rational-enumeration check.

## Amendment, 2026-11-15 · normalization and the proposal-share threshold

The publication review found two statements that Section 4 uses and the
first formalization left unchecked.

1. The product weighting is called a probability, yet no theorem states
   that it is normalized or that the absence value lies in the unit
   interval. Prove that the weighted sum of the constant observable 1
   equals 1 for every horizon, and that `iidAbsence` lies in `[0, 1]`
   when `u, v ≥ 0` and `u + v ≤ 1`.
2. The paragraph after the proposition converts a long-run absence
   target into a minimum admitted share and a minimum proposal share.
   Prove, for capacity `K ≥ 1`: (a) with `0 ≤ q, q⋆ ≤ 1`, the limit
   `(1 - q)^K` is at most `(1 - q⋆)^K` exactly when `q ≥ q⋆`; (b) with
   proposal share `p ∈ [0, 1]` and positive pass rates `α, β`, the
   admitted share `pα / (pα + (1 - p)β)` is at least `q⋆ ∈ [0, 1]`
   exactly when `p ≥ q⋆β / (α(1 - q⋆) + q⋆β)`; (c) the composition of the
   two, stated for the admission weights `u = pα`, `v = (1 - p)β`.
   State (a) with `δ = (1 - q⋆)^K` so that no real root is needed. The
   manuscript's `q⋆ = 1 - δ^{1/K}` is the unique such value in `[0, 1]`
   for `0 < δ < 1`.

Also print the axioms of `foldl_admit_absent_iff`, which the README
table lists and the first version checked only as a dependency. Build
with warnings as errors and require the same three axioms.

The positive-capacity i.i.d. reference model is the scope of this
formalization. A history-dependent analysis would require additional
assumptions about future admissions and a separate validation.
