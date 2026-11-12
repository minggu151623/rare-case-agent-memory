import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.benchmark import FAMILIES, make_pools, structural_key
from src.pilot import CAPACITY, ROUNDS, SEED, run
from src.planning import Edge, Task, shortest_distance


class PilotTest(unittest.TestCase):
    def test_pool_structures_are_disjoint_and_match_difficulty(self):
        initial, menus, supplements, holdout = make_pools(SEED, ROUNDS)
        cases = initial + [case for pool in menus + supplements for case in pool] + holdout
        self.assertEqual(len(cases), 36)
        self.assertEqual(len({structural_key(case.task) for case in cases}), 36)
        for case in cases:
            with self.subTest(case=case.id):
                expected = None if case.family == "unreachable" else 4
                self.assertEqual(shortest_distance(case.task), expected)
                self.assertEqual(len(case.task.edges), 7)

    def test_canonical_key_ignores_node_names_and_edge_order(self):
        task = Task("A", "B", (Edge("A", "C"), Edge("C", "B", True)), "C")
        renamed = Task("X", "Y", (Edge("Z", "Y", True), Edge("X", "Z")), "Z")
        self.assertEqual(structural_key(task), structural_key(renamed))

    def test_fixture_accounting_and_holdout_isolation(self):
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "fixture"
            run(None, output)
            summary = json.loads((output / "summary.json").read_text())
            calls = [json.loads(line) for line in (output / "calls.jsonl").read_text().splitlines()]
        self.assertEqual(summary["calls"], 19)
        self.assertEqual(summary["format_failures"], 0)
        for records in summary["arms"].values():
            for record in records:
                self.assertEqual(sum(record["retained"].values()), CAPACITY)
                self.assertEqual(sum(record["attempted"].values()), 3)
                self.assertEqual(record["attempted"], record["verified_and_admitted"])
                self.assertEqual(record["evaluation"]["correct"], dict.fromkeys(FAMILIES, 2))
        for call in calls:
            prompt = json.loads(call["prompt"])
            self.assertFalse(any(case["id"].startswith("h") for case in prompt["memory"]))
            self.assertTrue(all(
                case["id"].startswith("h") == (call["phase"] == "evaluation")
                for case in prompt["tasks"]
            ))
