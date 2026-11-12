# E010 · Gemma single-query diagnostic

This follow-up was motivated by the early E006 observation that Gemma
often returns only one of the nine requested answers despite valid
outer JSON. Complete and retain E006 as specified. E010 changes
the number of questions per call to check whether the missing-answer
pattern masks any usable key-detour performance.

Use all six E002 seeds, both archived model-answer memories, and the
same Gemma snapshot and LM Studio settings as E006. For each seed,
choose the first key-detour case in the original holdout order.
Use the same case ID in all cells, preserving the original prompts
apart from the query list length. Compare original, independently
relabeled memory and query, and shared derangement. These choices
were specified before any E010 response. This gives 36 calls. Score
each answer exactly. Report six cases per policy and label condition
and report separately whether the expected case ID appeared at all.
This is a selected single-query diagnostic on existing graphs. It
cannot substitute for the multi-query cross-model comparison or
estimate acquisition by Gemma.
