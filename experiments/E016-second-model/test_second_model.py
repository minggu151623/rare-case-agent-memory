import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.admission_audit import read_calls
from src.confirmatory import DEV_SEEDS, ROUNDS, UPDATING, all_cases, conformance, replay_seed, \
    study, trajectory
from src.pilot import Backend
from src.second_model import CALLS, MODE

POOLS = study()


def fixture_run(seed, directory):
    directory.mkdir(parents=True)
    with (directory / "calls.jsonl").open("w") as trace:
        backend = Backend(None, trace)
        summary = trajectory(seed, POOLS[seed], lambda phase, arm, round_, cases, memory:
                             backend.call(phase, arm, round_, cases, memory, sampling_seed=seed),
                             **MODE)
    summary.update(backend="fixture", digest=None, runtime_version="fixture")
    (directory / "summary.json").write_text(json.dumps(summary))
    raw = directory / "calls.jsonl"
    (directory / "calls.jsonl.gz").write_bytes(gzip.compress(raw.read_bytes(), mtime=0))
    raw.unlink()


class SecondModelTest(unittest.TestCase):
    def test_every_call_holds_one_task_and_the_run_replays(self):
        seed = DEV_SEEDS[0]
        with TemporaryDirectory() as folder:
            directory = Path(folder) / str(seed)
            fixture_run(seed, directory)
            rows = read_calls(directory)
            self.assertEqual(len(rows), CALLS)
            self.assertEqual(CALLS, 3 * ROUNDS * 3 + 5 * 9)
            self.assertEqual({len(json.loads(row["prompt"])["tasks"]) for row in rows}, {1})
            self.assertFalse([row for row in rows if row["arm"].startswith("label/")])
            self.assertEqual(sum(row["phase"] == "solve" for row in rows), 3 * ROUNDS * 3)
            summary, usage = replay_seed(directory, seed, POOLS[seed], **MODE)
            self.assertEqual(usage["calls"], CALLS)
            self.assertEqual(conformance(summary, all_cases(POOLS[seed]))["checks"], 9)
            tampered = json.loads((directory / "summary.json").read_text())
            tampered["readout"]["frozen"]["h00"]["correct"] = False
            (directory / "summary.json").write_text(json.dumps(tampered))
            with self.assertRaises(ValueError):
                replay_seed(directory, seed, POOLS[seed], **MODE)

    def test_single_solve_admits_the_same_examples_as_one_batched_call(self):
        seed = DEV_SEEDS[1]
        from src.pilot import oracle_answer
        ask = lambda phase, arm, round_, cases, memory: {c.id: oracle_answer(c) for c in cases}
        batched = trajectory(seed, POOLS[seed], ask, labels=False)
        single = trajectory(seed, POOLS[seed], ask, **MODE)
        for arm in UPDATING:
            self.assertEqual(batched["arms"][arm], single["arms"][arm])
        self.assertEqual(batched["readout"], single["readout"])


class SingleEntryTest(unittest.TestCase):
    def test_a_lone_answer_under_another_key_is_scored_and_counted_as_unreturned(self):
        seed = DEV_SEEDS[0]
        from src.pilot import oracle_answer
        ask = lambda phase, arm, round_, cases, memory: {"id": oracle_answer(cases[0])}
        summary = trajectory(seed, POOLS[seed], ask, **MODE)
        marks = [mark for memory in summary["readout"].values() for mark in memory.values()]
        self.assertTrue(all(mark["correct"] and not mark["answered"] for mark in marks))
        strict = trajectory(seed, POOLS[seed], ask, single_solve=True, labels=False)
        self.assertFalse(any(mark["correct"] for memory in strict["readout"].values()
                             for mark in memory.values()))
        two = lambda phase, arm, round_, cases, memory: {"x": 1, "y": 2}
        self.assertFalse(any(mark["correct"] for memory in
                             trajectory(seed, POOLS[seed], two, **MODE)["readout"].values()
                             for mark in memory.values()))


if __name__ == "__main__":
    unittest.main()
