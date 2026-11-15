from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.admission_report import sign_flip_p
from src.benchmark import FAMILIES, RARE, structural_key
from src.confirmatory import (CONDITIONS, DEV_SEEDS, MEMORIES, ROUNDS, SEEDS, UPDATING,
                              all_cases, conformance, exact_sign_flip, holdout_pairs, plan,
                              preflight, prior_keys, rendered, replay_seed, run_seed, study,
                              trajectory)
from src.diverse_paths import DETOUR, FIXED_PATHS
from src.matched_labels import maps_for_seed
from src.pilot import oracle_answer
from src.planning import is_correct, shortest_distance

POOLS = study()


def relaxed_distance(task):
    """Shortest distance by repeated relaxation over (node, has key) states."""
    nodes = {node for edge in task.edges for node in (edge.source, edge.destination)}
    distance = {(task.start, task.start == task.key_at): 0}
    for _ in range(2 * len(nodes)):
        for edge in task.edges:
            for has_key in (False, True):
                source = (edge.source, has_key)
                if source in distance and (has_key or not edge.requires_key):
                    target = (edge.destination, has_key or edge.destination == task.key_at)
                    distance[target] = min(distance.get(target, 99), distance[source] + 1)
    reached = [cost for (node, _), cost in distance.items() if node == task.goal]
    return min(reached, default=None)


def independent_score(task, answer):
    """Scorer written separately from src.planning.is_correct."""
    optimum = relaxed_distance(task)
    if answer == {"unreachable": True}:
        return optimum is None
    if not (isinstance(answer, dict) and list(answer) == ["path"]
            and isinstance(answer["path"], list) and answer["path"]):
        return False
    path = answer["path"]
    if not all(isinstance(node, str) for node in path):
        return False
    if path[0] != task.start or path[-1] != task.goal or len(path) - 1 != optimum:
        return False
    has_key = task.start == task.key_at
    for source, target in zip(path, path[1:]):
        usable = [edge for edge in task.edges
                  if (edge.source, edge.destination) == (source, target)
                  and (has_key or not edge.requires_key)]
        if not usable:
            return False
        has_key = has_key or target == task.key_at
    return True


class PoolTest(unittest.TestCase):
    def test_seeds_are_new_and_pools_have_the_locked_shape(self):
        self.assertEqual(len(SEEDS), 30)
        self.assertFalse(set(SEEDS + DEV_SEEDS).intersection({4101, *range(6201, 6207)}))
        self.assertFalse(set(SEEDS).intersection(DEV_SEEDS))
        for seed in SEEDS + DEV_SEEDS:
            initial, backgrounds, supplements, holdout = POOLS[seed]
            self.assertEqual(Counter(c.family for c in initial),
                             {"ungated": 4, "key_detour": 1, "unreachable": 1})
            self.assertEqual((len(backgrounds), len(supplements)), (ROUNDS, ROUNDS))
            for background, supplement in zip(backgrounds, supplements):
                self.assertEqual(len(background), 2)
                self.assertEqual(sorted(c.family for c in supplement), sorted(FAMILIES))
            self.assertEqual(Counter(c.family for c in holdout), dict.fromkeys(FAMILIES, 3))

    def test_every_graph_passes_an_independent_solver(self):
        checked = 0
        for pools in POOLS.values():
            for case in all_cases(pools):
                task = case.task
                self.assertEqual(relaxed_distance(task), shortest_distance(task))
                self.assertEqual(len(task.edges), 7)
                self.assertEqual((task.start, task.goal), ("A", "B"))
                if case.family == "unreachable":
                    self.assertIsNone(relaxed_distance(task))
                else:
                    self.assertEqual(relaxed_distance(task), 4)
                if case.family == DETOUR:
                    self.assertIsNone(relaxed_distance(replace(task, key_at=None)))
                    optimal = [p for p in FIXED_PATHS if independent_score(task, {"path": p})]
                    self.assertEqual(len(optimal), 1)
                    self.assertEqual(optimal[0][2], "C")
                self.assertTrue(independent_score(task, oracle_answer(case)))
                checked += 1
        self.assertEqual(checked, 32 * 35)

    def test_splits_are_isolated(self):
        keys = Counter(structural_key(case.task)
                       for pools in POOLS.values() for case in all_cases(pools))
        self.assertEqual(max(keys.values()), 1)
        self.assertFalse(prior_keys().intersection(keys))

    def test_holdout_routes_are_balanced(self):
        schedule = holdout_pairs(SEEDS, 715000)
        self.assertEqual(set(Counter(p for pairs in schedule.values() for p in pairs).values()),
                         {10})
        for seed in SEEDS:
            self.assertEqual(sum(x == y for x, y in schedule[seed]), 1)
            routes = sorted(tuple(oracle_answer(c)["path"]) for c in POOLS[seed][-1]
                            if c.family == DETOUR)
            self.assertEqual(routes, sorted(("A", x, "C", y, "B") for x, y in schedule[seed]))
        checks = preflight()
        self.assertEqual(checks["holdout_key_detours"],
                         {"queries": 90, "optimal_paths": 9, "best_fixed_path_correct": 10})
        self.assertEqual(checks["graphs"], 1120)


class DesignTest(unittest.TestCase):
    def test_plans_match_the_rare_budget_and_shuffle_blocks(self):
        for seed in SEEDS:
            schedule = plan(seed)
            self.assertEqual(Counter(schedule["rare_only_model"]),
                             {"key_detour": ROUNDS // 2, "unreachable": ROUNDS // 2})
            self.assertEqual(sorted(schedule["arm_order"]), sorted(UPDATING))
            self.assertEqual(sorted(schedule["readout_order"]), sorted(MEMORIES))
            self.assertEqual(len(set(schedule["label_order"])), 12)

    def test_label_conditions_show_the_same_rendered_graphs(self):
        for seed in SEEDS:
            initial, _, _, holdout = POOLS[seed]
            memory = [(case, oracle_answer(case)) for case in initial]
            maps = maps_for_seed(seed)
            self.assertTrue(all(maps[0][n] != n and maps[1][n] != n and maps[0][n] != maps[1][n]
                                for n in "ABCDEF"))
            shown = {condition: Counter() for condition in CONDITIONS}
            for condition in CONDITIONS:
                for repetition in (0, 1):
                    for case in holdout:
                        query, examples = rendered(case, memory, maps, condition, repetition)
                        shown[condition].update([(query.id, query.task)])
                        shown[condition].update((ex.id, ex.task) for ex, _ in examples)
                        if condition == "shared":
                            used = {tuple(sorted(maps[repetition].items()))}
                            self.assertEqual(query.task.start, maps[repetition]["A"])
                            self.assertEqual({ex.task.start for ex, _ in examples},
                                             {maps[repetition]["A"]})
                        else:
                            self.assertEqual({ex.task.start for ex, _ in examples},
                                             {maps[0]["A"], maps[1]["A"]})
            self.assertEqual(shown["shared"], shown["mixed"])
            self.assertEqual(set(shown["shared"].values()), {1, 9})

    def test_exact_sign_flip_matches_enumeration(self):
        for differences in ([3, 6, -4, 2, -1, 1], [0, 0, 0, 0, 0, 2], [1, 1, 1, 0, 1, 0],
                            [3, 0, 0, 3, 3, 0, -1, 2], [0] * 5):
            self.assertEqual(exact_sign_flip(differences), sign_flip_p(differences))


class ReplayTest(unittest.TestCase):
    def test_fixture_run_replays_and_conforms_to_fifo(self):
        seed = DEV_SEEDS[0]
        with TemporaryDirectory() as folder:
            directory = Path(folder) / str(seed)
            run_seed(seed, POOLS[seed], None, directory)
            summary, usage = replay_seed(directory, seed, POOLS[seed])
            self.assertEqual(usage["calls"], 3 * ROUNDS + 5 * 9 + 3 * 2 * 2 * 3)
            self.assertEqual(usage["format_failures"], 0)
            checks = conformance(summary, all_cases(POOLS[seed]))
            self.assertEqual(checks["checks"], 9)
            for name in MEMORIES:
                self.assertTrue(all(mark["correct"] for mark in summary["readout"][name].values()))
            tampered = json.loads((directory / "summary.json").read_text())
            tampered["readout"]["frozen"]["h00"]["correct"] = False
            (directory / "summary.json").write_text(json.dumps(tampered))
            with self.assertRaises(ValueError):
                replay_seed(directory, seed, POOLS[seed])

    def test_failed_unreachable_answers_are_never_admitted(self):
        seed = DEV_SEEDS[1]

        def ask(phase, arm, round_, cases, memory):
            return {case.id: ({"path": ["A", "B"]} if case.family == "unreachable"
                              else oracle_answer(case)) for case in cases}

        summary = trajectory(seed, POOLS[seed], ask)
        for arm in UPDATING:
            self.assertEqual(sum(row["admitted"]["unreachable"]
                                 for row in summary["arms"][arm]["rounds"]), 0)
        self.assertEqual(conformance(summary, all_cases(POOLS[seed]))["checks"], 9)
        family = {case.id: case.family for case in POOLS[seed][-1]}
        for name in MEMORIES:
            wrong = [item for item, mark in summary["readout"][name].items() if not mark["correct"]]
            self.assertEqual({family[item] for item in wrong}, {"unreachable"})
        self.assertEqual({r for r in RARE}, {"key_detour", "unreachable"})


if __name__ == "__main__":
    unittest.main()
