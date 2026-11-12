# E007 · Error audit on equivalent relabelings

Exploratory analysis following E003. It uses the original E002 and
independently relabeled E003 evaluation logs for the two policy arms
also used in E004, across the same six seeds. Count mutually exclusive
first-error categories per family: malformed or missing answer,
false unreachable claim, wrong endpoint, nonexistent edge, locked edge
before acquiring the key, and a valid but suboptimal path. Count
correct answers separately. Check that the classification agrees with
the exact verifier on every item.

Among renamed failures for which the same arm and graph had a correct
original path, separately count exact literal repetitions of that
original path. Report both the number of failures with a correct
original path and the number with exact literal reuse. This measure
tracks token-string persistence. It cannot identify the internal
mechanism that generated the path. The analysis was proposed after
seeing E003 scores, so treat it as exploratory.
