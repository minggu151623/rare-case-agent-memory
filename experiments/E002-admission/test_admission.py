import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.admission import SEEDS, run_seed, study_pools
from src.benchmark import make_pools, structural_key


def flatten(pools):
    initial, first, second, holdout = pools
    return initial + holdout + [case for pool in first + second for case in pool]


class AdmissionStudyTest(unittest.TestCase):
    def test_all_splits_are_structurally_disjoint(self):
        graphs = flatten(make_pools(4101, 2))
        for pools in study_pools().values():
            graphs.extend(flatten(pools))
        keys = [structural_key(case.task) for case in graphs]
        self.assertEqual(len(keys), 186)
        self.assertEqual(len(set(keys)), len(keys))

    def test_oracle_injection_uses_same_slots_and_excludes_holdout(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "fixture"
            run_seed(SEEDS[0], study_pools()[SEEDS[0]], None, output)
            summary = json.loads((output / "summary.json").read_text())
            trace = [json.loads(line) for line in
                     (output / "calls.jsonl").read_text().splitlines()]

        self.assertEqual(summary["calls"], 14)
        self.assertEqual(summary["format_failures"], 0)
        for call in trace:
            prompt = json.loads(call["prompt"])
            self.assertFalse(any(item["id"].startswith("h") for item in prompt["memory"]))
            self.assertTrue(all(item["id"].startswith("h") == (call["phase"] == "evaluation")
                                for item in prompt["tasks"]))
            if call["phase"] == "solve":
                self.assertEqual(len(prompt["tasks"]), 3)
        for arm, arm_result in summary["arms"].items():
            for round_ in arm_result["rounds"]:
                self.assertEqual(sum(round_["retained"].values()), 6)
                self.assertEqual(sum(round_["attempted"].values()), 3)
                supplement = round_["supplement"]
                if supplement["family"] == "unreachable":
                    self.assertFalse(supplement["model_pass"])
                    self.assertEqual(supplement["admitted"], arm.endswith("_oracle"))
        self.assertEqual(
            [row["supplement"]["id"] for row in summary["arms"]["random_model"]["rounds"]],
            [row["supplement"]["id"] for row in summary["arms"]["random_oracle"]["rounds"]],
        )
