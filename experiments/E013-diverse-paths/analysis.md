# E013 · Diverse-path results under fixed labels

All 36 Qwen3 calls passed replay. The 18 original-batch prompts and
responses match their source archives byte for byte. No outer JSON
format failures occurred. An independent state-space solver verified
that all 18 replacement graphs require the key and have distance four.
Exhaustive enumeration over four-move paths found nine distinct unique
optima, each solving two queries. The best constant path scores 2/18
on the replacement batch and 18/18 on the original detours.

| Frozen memory | Key detour, original | Key detour, varied | Unreachable, original | Unreachable, varied | Ungated, original | Ungated, varied |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Reference-mixture random | 7/18 | 3/18 | 3/18 | 1/18 | 18/18 | 17/18 |
| Balanced rare-only random | 16/18 | 5/18 | 0/18 | 0/18 | 18/18 | 18/18 |
| Adaptive | 18/18 | 7/18 | 0/18 | 0/18 | 18/18 | 18/18 |

The targeted-minus-mixture gap for key detours shrinks from 11/18 to
4/18 (+61.1 to +22.2 percentage points). The varied-minus-original change
is -38.9 points. Its seed-level changes in correct counts out of three
are [-1, -1, 0, -2, -3, 0] (two-sided sign-flip sensitivity p=0.125).
The adaptive and balanced policies each lose 11 correct detours.
Their gap is +2/18 under both batches, entirely from seed 6206.
All six seed-level changes in that policy gap are zero.

The original advantage over mixture narrows but stays positive on the
varied batch. Adaptive and balanced rare-only memories both transfer
poorly in absolute accuracy. The small adaptive advantage over the
matched comparator is unchanged and concentrated in one seed. This
tests readout from frozen memories. The changed detours differ in
topology and the mix of return and through routes. Small changes in
the mixture arm on unchanged query families also show that replacing
queries can affect other answers in a batch. The experiment does not
identify the model's solution strategy or establish equivalence.
