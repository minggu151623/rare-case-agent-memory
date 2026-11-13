"""Run and replay the E013 diverse-path transfer experiment."""
import argparse
from collections import Counter
from dataclasses import replace
from itertools import permutations, product
import json
from pathlib import Path
from random import Random

from src.admission import ROUNDS, SEEDS, study_pools
from src.admission_audit import audit_seed, decode_answers, read_calls, require
from src.benchmark import Case, FAMILIES, make_pools, structural_key
from src.pilot import Backend, counts
from src.planning import Edge, Task, is_correct, shortest_distance
from src.rare_only import RUNTIME, replay_seed as replay_rare_seed, sensitivity
from src.representation import score_call
from src.transfer import flatten, inputs

NODES = "ABCDEF"
ARMS = ("random_model", "targeted_model", "rare_only_model")
CONDITIONS = ("original", "varied")
DETOUR = "key_detour"
FIXED_PATHS = [["A", *middle, "B"] for middle in product(NODES, repeat=3)]


def route_schedule():
    rng = Random(613000)
    schedule = {}
    for offset in (0, 3):
        returns = rng.sample([(x, x) for x in "DEF"], 3)
        through = rng.sample(list(permutations("DEF", 2)), 6)
        for index, seed in enumerate(SEEDS[offset:offset + 3]):
            pairs = [returns[index], *through[2 * index:2 * index + 2]]
            rng.shuffle(pairs)
            schedule[seed] = pairs
    return schedule


def detour(x, y, rng, seen):
    path = ["A", x, "C", y, "B"]
    base = [Edge(a, b, i == 3) for i, (a, b) in enumerate(zip(path, path[1:]))]
    occupied = {(edge.source, edge.destination) for edge in base}
    extras = [Edge(a, b) for a, b in permutations(NODES, 2) if (a, b) not in occupied]
    for _ in range(5000):
        edges = base + rng.sample(extras, 3)
        if {node for edge in edges for node in (edge.source, edge.destination)} != set(NODES):
            continue
        rng.shuffle(edges)
        task = Task("A", "B", tuple(edges), "C")
        if shortest_distance(task) != 4 or shortest_distance(replace(task, key_at=None)) is not None:
            continue
        optimal = [p for p in FIXED_PATHS if is_correct(task, {"path": p})]
        if optimal != [path]:
            continue
        key = structural_key(task)
        if key not in seen:
            seen.add(key)
            return task
    raise RuntimeError(f"Could not generate a unique detour for {x}, {y}")


def batches(study):
    seen = {structural_key(case.task) for case in flatten(make_pools(4101, ROUNDS))}
    for pools in study.values():
        seen.update(structural_key(case.task) for case in flatten(pools))
    for _, _, cases in inputs():
        seen.update(structural_key(case.task) for case in cases)
    for seed, pairs in route_schedule().items():
        original = study[seed][-1]
        rng = Random(seed + 613100)
        varied_tasks = iter(detour(x, y, rng, seen) for x, y in pairs)
        varied = [Case(case.id, case.family, next(varied_tasks))
                  if case.family == DETOUR else case for case in original]
        require(next(varied_tasks, None) is None, "Unused detours")
        yield seed, {"original": original, "varied": varied}


def frozen_memory(directory, cases, arm):
    rows = [row for row in read_calls(directory) if
            (row["phase"], row["round"], row["arm"]) == ("evaluation", ROUNDS, arm)]
    require(len(rows) == 1, f"Expected one frozen memory for {arm} in {directory}")
    records = json.loads(rows[0]["prompt"])["memory"]
    return [(cases[row["id"]], row["solution"]) for row in records]


def prepared(mixture, rare):
    study = study_pools()
    for seed, holdouts in batches(study):
        pools = study[seed]
        audit_seed(mixture / str(seed), seed, pools)
        replay_rare_seed(rare, seed, pools)
        cases = {case.id: case for case in flatten(pools)}
        memories = {
            arm: frozen_memory((mixture if arm == "random_model" else rare) / str(seed),
                               cases, arm)
            for arm in ARMS
        }
        order = list(product(ARMS, CONDITIONS))
        Random(seed + 613200).shuffle(order)
        yield seed, holdouts, memories, order


def constant_coverage(cases):
    coverage = Counter(tuple(path) for path in FIXED_PATHS for case in cases
                       if is_correct(case.task, {"path": path}))
    return {"total": len(cases), "optimal_paths": len(coverage),
            "best_fixed_path_correct": max(coverage.values())}


def replay_seed(directory, seed, holdouts, memories, order):
    require((directory / "runtime.txt").read_text().strip() == RUNTIME, "Wrong Ollama runtime")
    rows = read_calls(directory)
    require(len(rows) == len(order), f"Wrong call count for {seed}")
    scores = {arm: {} for arm in ARMS}
    for row, (arm, condition) in zip(rows, order, strict=True):
        require((row["phase"], row["round"], row["arm"])
                == ("evaluation", ROUNDS, f"{arm}/{condition}"), "Wrong E013 call order")
        require(row["output_tokens"] <= 384 and row["prompt_tokens"] + row["output_tokens"] <= 4096,
                "Token cap exceeded")
        require(decode_answers(row["response"])[1] == row["valid_format"], "Format mismatch")
        cases = holdouts[condition]
        marks = score_call(row, cases, memories[arm])
        correct_ids = {mark["id"] for mark in marks if mark["correct"]}
        scores[arm][condition] = {"correct": counts(case for case in cases if case.id in correct_ids),
                                  "total": counts(cases)}
    return scores, sum(not row["valid_format"] for row in rows)


def report(mixture, rare, output):
    per_seed = {}
    detours = {condition: [] for condition in CONDITIONS}
    failures = 0
    for seed, holdouts, memories, order in prepared(mixture, rare):
        per_seed[seed], bad = replay_seed(output / str(seed), seed, holdouts, memories, order)
        failures += bad
        for condition, cases in holdouts.items():
            detours[condition].extend(case for case in cases if case.family == DETOUR)
    scores = {arm: {condition: {
        family: {field: sum(s[arm][condition][field][family] for s in per_seed.values())
                 for field in ("correct", "total")} for family in FAMILIES
    } for condition in CONDITIONS} for arm in ARMS}
    contrasts = {}
    for comparator in ("random_model", "rare_only_model"):
        by_seed = [
            [s["targeted_model"][condition]["correct"][DETOUR]
             - s[comparator][condition]["correct"][DETOUR] for condition in CONDITIONS]
            for s in per_seed.values()
        ]
        changes = [varied - original for original, varied in by_seed]
        contrasts[comparator] = {
            "per_seed_original_varied_gaps_out_of_three": by_seed,
            "original_gap": sum(g[0] for g in by_seed) / 18,
            "varied_gap": sum(g[1] for g in by_seed) / 18,
            "varied_minus_original": sum(changes) / 18,
            "sign_flip_p": sensitivity(changes),
        }
    return {"calls": len(per_seed) * len(ARMS) * len(CONDITIONS),
            "format_failures": failures,
            "constant_path_coverage": {k: constant_coverage(v) for k, v in detours.items()},
            "scores": scores, "contrasts": contrasts, "per_seed": per_seed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mixture", type=Path)
    parser.add_argument("rare", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ollama-port", type=int)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if args.audit:
        print(json.dumps(report(args.mixture, args.rare, args.output), indent=2))
        return
    if args.ollama_port is None:
        parser.error("--ollama-port is required for inference")
    for seed, holdouts, memories, order in prepared(args.mixture, args.rare):
        directory = args.output / str(seed)
        if not directory.exists():
            directory.mkdir(parents=True)
            with (directory / "calls.jsonl").open("w") as trace:
                backend = Backend(args.ollama_port, trace)
                require(backend.version == RUNTIME, "Wrong Ollama runtime")
                (directory / "runtime.txt").write_text(backend.version + "\n")
                for arm, condition in order:
                    backend.call("evaluation", f"{arm}/{condition}", ROUNDS, holdouts[condition],
                                 memories[arm], sampling_seed=seed)
        replay_seed(directory, seed, holdouts, memories, order)
        print(f"Seed {seed} complete", flush=True)


if __name__ == "__main__":
    main()
