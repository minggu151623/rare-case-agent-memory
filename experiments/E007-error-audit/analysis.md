# E007 · Error audit

The scorer classified the first failure for each original and renamed
answer and agreed with the exact verifier on all 216 scored records.
The targeted/model condition lost 17 previously correct key-detour
answers after renaming. The first detected failure was an early
locked traversal in eight, a nonexistent edge in seven, and the
wrong endpoint in two. The random/model condition lost six previously
correct key-detour answers and gained one.

None of the 17 lost targeted key-detour answers exactly repeated the
path returned on the original graph. There was also no exact literal
reuse among the six corresponding random/model losses. This argues
against the narrow explanation that the failed answers simply copied
the complete original path string. It leaves open other forms of
representation sensitivity, including partial label associations and
differences in how the model interprets the lock constraint. These
are post hoc diagnostics using E002 and E003 responses.

[Audited counts](results/aggregate.json)
