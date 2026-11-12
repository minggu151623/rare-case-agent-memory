# E000 · Result

- Run date: 2026-11-12
- Protocol: `e31c23dd56be0e40163d399387f29c018b0e5f67`
- Implementation: `c967404cebd1e62adf55cb022df5b9dbfc5cdb56`
- Runtime: Python 3.14.5, standard library, CPU

Command:

```sh
python3 -m unittest discover -s experiments/E000-oracle-smoke -v
```

All nine test methods passed. The known key detour needed four moves and
revisited a node after acquiring the key. The scorer accepted the optimal
path and true unreachable answer and rejected the four planned invalid
answer cases. Zero API calls.

The fixtures check basic scorer behavior. They provide no evidence about
memory coverage or the effectiveness of supplementation.
