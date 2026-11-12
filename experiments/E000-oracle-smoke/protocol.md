# E000 · Planning oracle smoke check

Check breadth-first search over (location, has key) on directed graphs with
unit-cost edges. Entering the key node grants the key permanently. An edge can
require the key. The target is a goal node.

Before executing, define these expected checks:

1. A direct chain reaches its goal at distance 2.
2. A route requiring a key collected in a dead-end branch reaches its goal in
   4 steps and revisits a node. A node-only visited set would miss this route.
3. A locked edge with an inaccessible key makes the goal unreachable.
4. Starting on the goal has cost 0. Starting on the key unlocks a first step.
5. The scorer rejects a path using a locked edge, a feasible but suboptimal
   path, a false unreachable answer, and a response that combines both answer
   forms. It accepts the known optimal path and the true unreachable answer.

The check passes when every case matches its expected answer. This is an
engineering check of the oracle and scorer. H1 and H2 require live model runs.
