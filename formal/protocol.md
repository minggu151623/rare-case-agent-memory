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

The positive-capacity i.i.d. reference model is the scope of this
formalization. A history-dependent analysis would require additional
assumptions about future admissions and a separate validation.
