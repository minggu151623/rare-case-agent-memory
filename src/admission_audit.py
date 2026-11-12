"""Reconstruct E002 summaries from logged responses and verify split isolation."""

import argparse
import gzip
import json
from pathlib import Path
from random import Random

from src.admission import ARMS, RARE, ROUNDS, SEEDS, study_pools
from src.benchmark import FAMILIES, REFERENCE_WEIGHTS
from src.pilot import CAPACITY, DIGEST, MODEL, counts, oracle_answer
from src.planning import is_correct


def require(condition, description):
    if not condition:
        raise ValueError(description)


def read_calls(directory):
    compressed = directory / "calls.jsonl.gz"
    if compressed.is_file():
        return [json.loads(line) for line in gzip.decompress(compressed.read_bytes()).splitlines()]
    return [json.loads(line) for line in (directory / "calls.jsonl").read_text().splitlines()]


def decode_answers(raw):
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}, False
    if isinstance(value, dict) and isinstance(value.get("answers"), dict):
        return value["answers"], True
    return {}, False


def audit_seed(directory, seed, pools, *, arms=ARMS, include_controls=True):
    summary = json.loads((directory / "summary.json").read_text())
    initial, backgrounds, supplements, holdout = pools
    rows = read_calls(directory)
    rng = Random(seed + 100_000)
    random_families = rng.choices(FAMILIES, weights=REFERENCE_WEIGHTS, k=ROUNDS)
    tie_order = rng.sample(RARE, len(RARE))
    order = [arm for arm in rng.sample(ARMS, len(ARMS)) if arm in arms]
    require(summary["seed"] == seed, f"Wrong seed label in {directory}")
    require(summary["initial_memory"] == counts(initial), "Wrong initial family counts")
    expected_calls = len(arms) * (ROUNDS + 1) + 2 * include_controls
    require(len(rows) == summary["calls"] == expected_calls, "Unexpected call count")
    if summary["backend"] == MODEL:
        require(summary["digest"] == DIGEST, "Unexpected model snapshot")
        for row in rows:
            require(row["output_tokens"] <= 384, "Generation cap exceeded")
            require(row["prompt_tokens"] + row["output_tokens"] <= 4096, "Context cap exceeded")
    require(summary["format_failures"] == sum(not row["valid_format"] for row in rows),
            "Unexpected format-failure count")

    call_iter = iter(rows)

    def replay(phase, arm, round_, cases, memory):
        row = next(call_iter)
        require((row["phase"], row["arm"], row["round"]) == (phase, arm, round_),
                "Call out of order")
        prompt = json.loads(row["prompt"])
        expected_tasks = json.loads(json.dumps([case.prompt_record() for case in cases]))
        expected_memory = json.loads(json.dumps(
            [{**case.prompt_record(), "solution": answer} for case, answer in memory]
        ))
        require(prompt["tasks"] == expected_tasks, "Task pool mismatch")
        require(prompt["memory"] == expected_memory, "Memory or evaluation leakage")
        answers, valid = decode_answers(row["response"])
        require(valid == row["valid_format"], "Outer JSON status mismatch")
        return answers

    def score(cases, answers):
        return counts(case for case in cases if is_correct(case.task, answers.get(case.id)))

    initial_memory = [(case, oracle_answer(case)) for case in initial]
    controls = (("empty", []), ("frozen", initial_memory)) if include_controls else ()
    for arm, memory in controls:
        actual = {"correct": score(holdout, replay("evaluation", arm, 0, holdout, memory)),
                  "total": counts(holdout)}
        require(summary["controls"][arm] == actual, f"{arm} score mismatch")

    for allocation, source in order:
        arm = f"{allocation}_{source}"
        memory = initial_memory.copy()
        for index, record in enumerate(summary["arms"][arm]["rounds"]):
            require(record["round"] == index + 1, "Round mismatch")
            before = counts(case for case, _ in memory)
            family = (min(tie_order, key=before.__getitem__) if allocation == "targeted"
                      else random_families[index])
            supplement = next(case for case in supplements[index] if case.family == family)
            cases = [*backgrounds[index], supplement]
            answers = replay("solve", arm, index + 1, cases, memory)
            require(record["attempted"] == counts(cases), "Attempt count mismatch")
            require(record["model_passes"] == score(cases, answers), "Model-pass count mismatch")
            passed = is_correct(supplement.task, answers.get(supplement.id))
            if source == "oracle":
                answers[supplement.id] = oracle_answer(supplement)
            admitted = [(case, answers[case.id]) for case in cases
                        if is_correct(case.task, answers.get(case.id))]
            require(record["supplement"] == {
                "id": supplement.id,
                "family": family,
                "model_pass": passed,
                "admitted": any(case == supplement for case, _ in admitted),
            }, "Supplement mismatch")
            require(record["admitted"] == counts(case for case, _ in admitted),
                    "Admission count mismatch")
            combined = memory + admitted
            require(record["evicted"] == counts(case for case, _ in combined[:-CAPACITY]),
                    "Eviction count mismatch")
            memory = combined[-CAPACITY:]
            require(record["retained"] == counts(case for case, _ in memory),
                    "Retention count mismatch")
        final = {"correct": score(holdout, replay("evaluation", arm, ROUNDS, holdout, memory)),
                 "total": counts(holdout)}
        require(summary["arms"][arm]["final"] == final, f"{arm} final score mismatch")
    require(next(call_iter, None) is None, "Unused calls")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    pools = study_pools()
    for seed in SEEDS:
        audit_seed(args.output / str(seed), seed, pools[seed])
    print(f"Replayed all {14 * len(SEEDS)} calls across {len(SEEDS)} seeds")
