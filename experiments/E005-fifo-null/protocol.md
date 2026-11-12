# E005 · Exact FIFO absence under independent attempts

This analytic reference model separates proposal frequency, verifier
admission and FIFO retention. It has stationary, independent attempts
and a full fixed-capacity initial memory. It is not a stochastic model
fitted to E002, where targeting and solving can depend on memory.

For one focal family, an attempt yields a focal admission with
probability u, another admission with probability v, or no admission
with probability 1-u-v. Let K be the capacity and r the position of the
last initial focal example counted from the oldest (r=0 if absent).
Given N=n admissions, their labels are independently focal with
q=u/(u+v) for u+v>0. The absence event requires n >= r and no focal
label among the last min(n,K) admissions. Therefore the finite-time
probability is the binomial average of that indicator times
(1-q)^min(n,K). When u+v=0 the initial memory is unchanged. The limit
for u+v>0 is (1-q)^K. Inverting the limit gives the proposal share
needed to attain a desired absence bound when both pass rates are
positive.

Verify the finite expression by exhaustive simulation of every
three-symbol outcome string, using exact rational weights. Use
capacities 1 through 4, every binary initial memory, T=0 through 6,
and all u,v >= 0 on the denominator-4 grid with u+v <= 1.
Record the number of exact comparisons. Retain the proof and separate
this reference calculation from empirical claims.
