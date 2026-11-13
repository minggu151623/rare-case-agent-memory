from collections import Counter
from dataclasses import replace
from importlib import import_module
import unittest

from src.admission import study_pools
from src.diverse_paths import DETOUR, batches, constant_coverage, route_schedule
from src.planning import is_correct, shortest_distance

reference_distance = import_module(
    "experiments.E011-manuscript-audit.check"
).reference_distance


class DiverseHoldoutTest(unittest.TestCase):
    def test_stable_labels_and_balanced_unique_optima(self):
        schedule = route_schedule()
        pair_counts = Counter(pair for pairs in schedule.values() for pair in pairs)
        self.assertEqual(len(pair_counts), 9)
        self.assertEqual(set(pair_counts.values()), {2})
        detours = {"original": [], "varied": []}

        for seed, holdouts in batches(study_pools()):
            pairs = iter(schedule[seed])
            self.assertEqual(sum(x == y for x, y in schedule[seed]), 1)
            for before, after in zip(holdouts["original"], holdouts["varied"], strict=True):
                self.assertEqual((before.id, before.family), (after.id, after.family))
                if before.family != DETOUR:
                    self.assertEqual(before, after)
                    continue
                x, y = next(pairs)
                task = after.task
                self.assertEqual((task.start, task.key_at, task.goal), ("A", "C", "B"))
                self.assertEqual(len(task.edges), 7)
                self.assertEqual(reference_distance(task), 4)
                self.assertEqual(shortest_distance(task), 4)
                self.assertIsNone(reference_distance(replace(task, key_at=None)))
                self.assertTrue(is_correct(task, {"path": ["A", x, "C", y, "B"]}))
                detours["original"].append(before)
                detours["varied"].append(after)
        self.assertEqual(constant_coverage(detours["original"]), {
            "total": 18, "optimal_paths": 1, "best_fixed_path_correct": 18,
        })
        self.assertEqual(constant_coverage(detours["varied"]), {
            "total": 18, "optimal_paths": 9, "best_fixed_path_correct": 2,
        })


if __name__ == "__main__":
    unittest.main()
