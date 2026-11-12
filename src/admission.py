"""Run the locked E002 factorial mechanism study or its offline fixture."""

import argparse
from itertools import product
import json
from pathlib import Path
from random import Random

from src.benchmark import (
    Case, FAMILIES, RARE, REFERENCE_WEIGHTS, generate, make_pools, structural_key,
)
from src.pilot import Backend, CAPACITY, DIGEST, MODEL, counts, oracle_answer
from src.planning import is_correct

SEEDS = tuple(range(6201, 6207))
ROUNDS = 2
ARMS = tuple(product(("random", "targeted"), ("model", "oracle")))


class AdmissionBackend(Backend):
    def fixture_answer(self, case):
        if case.family == "unreachable":
            return {"path": [case.task.start, case.task.goal]}
        return oracle_answer(case)


def study_pools():
    initial, menus, supplements, holdout = make_pools(4101, ROUNDS)
    pilot_cases = initial + holdout + [case for pool in menus + supplements for case in pool]
    seen = {structural_key(case.task) for case in pilot_cases}
    pools = {}

    for seed in SEEDS:
        rng = Random(seed)

        def pool(prefix, families):
            tasks = []
            for family in families:
                for _ in range(5000):
                    task = generate(family, rng)
                    key = structural_key(task)
                    if key not in seen:
                        tasks.append((family, task))
                        seen.add(key)
                        break
                else:
                    raise RuntimeError(f"Exhausted unique tasks for {seed} {family}")
            rng.shuffle(tasks)
            return [
                Case(f"{prefix}{index:02d}", family, task)
                for index, (family, task) in enumerate(tasks)
            ]

        initial = pool("i", (FAMILIES[0],) * 4 + RARE)
        backgrounds = [
            pool(f"b{round_}", rng.choices(FAMILIES, weights=REFERENCE_WEIGHTS, k=2))
            for round_ in range(ROUNDS)
        ]
        supplements = [pool(f"s{round_}", FAMILIES) for round_ in range(ROUNDS)]
        holdout = pool("h", FAMILIES * 3)
        pools[seed] = initial, backgrounds, supplements, holdout
    return pools


def evaluation(backend, arm, round_, cases, memory, seed):
    answers = backend.call("evaluation", arm, round_, cases, memory, sampling_seed=seed)
    correct = [case for case in cases if is_correct(case.task, answers.get(case.id))]
    return {"correct": counts(correct), "total": counts(cases)}


def run_seed(seed, pools, port, output, *, arms=ARMS, include_controls=True):
    initial, backgrounds, supplements, holdout = pools
    initial_memory = [(case, oracle_answer(case)) for case in initial]
    output.mkdir(parents=True)
    rng = Random(seed + 100_000)
    random_families = rng.choices(FAMILIES, weights=REFERENCE_WEIGHTS, k=ROUNDS)
    tie_order = rng.sample(RARE, len(RARE))
    arm_order = [arm for arm in rng.sample(ARMS, len(ARMS)) if arm in arms]

    with (output / "calls.jsonl").open("w") as trace:
        backend = AdmissionBackend(port, trace)
        summary = {
            "seed": seed,
            "backend": MODEL if port is not None else "fixture",
            "digest": DIGEST if port is not None else None,
            "runtime_version": backend.version,
            "initial_memory": counts(initial),
            "controls": {
                "empty": evaluation(backend, "empty", 0, holdout, [], seed),
                "frozen": evaluation(backend, "frozen", 0, holdout, initial_memory, seed),
            } if include_controls else {},
            "arms": {},
        }
        for allocation, source in arm_order:
            arm = f"{allocation}_{source}"
            memory = initial_memory.copy()
            records = []
            for index in range(ROUNDS):
                if allocation == "targeted":
                    frequencies = counts(case for case, _ in memory)
                    family = min(tie_order, key=frequencies.__getitem__)
                else:
                    family = random_families[index]
                supplement = next(case for case in supplements[index] if case.family == family)
                candidates = [*backgrounds[index], supplement]
                answers = backend.call(
                    "solve", arm, index + 1, candidates, memory, sampling_seed=seed,
                )
                model_passes = [
                    case for case in candidates if is_correct(case.task, answers.get(case.id))
                ]
                if source == "oracle":
                    answers[supplement.id] = oracle_answer(supplement)
                admitted = [
                    (case, answers[case.id]) for case in candidates
                    if is_correct(case.task, answers.get(case.id))
                ]
                combined = memory + admitted
                memory = combined[-CAPACITY:]
                records.append({
                    "round": index + 1,
                    "attempted": counts(candidates),
                    "model_passes": counts(model_passes),
                    "admitted": counts(case for case, _ in admitted),
                    "evicted": counts(case for case, _ in combined[:-CAPACITY]),
                    "retained": counts(case for case, _ in memory),
                    "supplement": {
                        "id": supplement.id,
                        "family": family,
                        "model_pass": supplement in model_passes,
                        "admitted": any(case == supplement for case, _ in admitted),
                    },
                })
            summary["arms"][arm] = {
                "rounds": records,
                "final": evaluation(backend, arm, ROUNDS, holdout, memory, seed),
            }

    calls = [json.loads(line) for line in (output / "calls.jsonl").read_text().splitlines()]
    summary["calls"] = len(calls)
    summary["format_failures"] = sum(not row["valid_format"] for row in calls)
    for field in ("prompt_tokens", "output_tokens", "seconds"):
        summary[field] = sum(row.get(field) or 0 for row in calls) if port is not None else None
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ollama-port", type=int, help="Loopback Ollama port. Omit for fixture.")
    parser.add_argument("--output", type=Path, required=True, help="New output directory.")
    parser.add_argument("--seed", type=int, choices=SEEDS, help="Run just one locked seed.")
    args = parser.parse_args()
    pools = study_pools()
    args.output.mkdir(parents=True)
    for seed in (args.seed,) if args.seed is not None else SEEDS:
        run_seed(seed, pools[seed], args.ollama_port, args.output / str(seed))
        print(f"Seed {seed} complete", flush=True)


if __name__ == "__main__":
    main()
