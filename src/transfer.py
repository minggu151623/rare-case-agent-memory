"""Run E003 on frozen final memories recovered from the audited E002 logs."""

import argparse
from dataclasses import replace
from itertools import permutations
import json
from pathlib import Path
from random import Random

from src.admission import SEEDS, study_pools
from src.admission_audit import read_calls
from src.benchmark import Case, FAMILIES, make_pools, structural_key
from src.pilot import Backend
from src.planning import Edge, Task, is_correct, shortest_distance

ARMS = ("random_model", "targeted_model", "targeted_oracle")
NODES = "ABCDEF"


def novel(family, rng):
    if family == "ungated":
        base = [Edge(a, b) for a, b in ("AC", "CD", "AF", "FD", "DE", "EB")]
        key = None
    elif family == "key_detour":
        base = [Edge(a, b, a == "E") for a, b in ("AD", "DC", "CE", "EB")]
        key = "C"
    elif family == "unreachable":
        base = [Edge(a, b, a == "D") for a, b in ("AD", "DE", "EC", "CB")]
        key = "C"
    else:
        raise ValueError(family)
    used = {(edge.source, edge.destination) for edge in base}
    extra = [Edge(a, b) for a, b in permutations(NODES, 2) if (a, b) not in used]
    for _ in range(1000):
        edges = base + rng.sample(extra, 7 - len(base))
        if {node for edge in edges for node in (edge.source, edge.destination)} != set(NODES):
            continue
        rng.shuffle(edges)
        task = Task("A", "B", tuple(edges), key)
        distance = shortest_distance(task)
        if family == "unreachable" and distance is None:
            return task
        if family == "ungated" and distance == 4:
            return task
        if family == "key_detour" and distance == 4:
            if shortest_distance(replace(task, key_at=None)) is None:
                return task
    raise RuntimeError(f"Could not generate {family}")


def rename(case, seed):
    labels = dict(zip(NODES, Random(f"{seed + 210000}:{case.id}").sample(list(NODES), len(NODES))))
    task = case.task
    renamed = Task(labels[task.start], labels[task.goal], tuple(
        Edge(labels[edge.source], labels[edge.destination], edge.requires_key)
        for edge in task.edges
    ), labels.get(task.key_at))
    return replace(case, task=renamed), labels


def flatten(pools):
    initial, first, second, holdout = pools
    return initial + holdout + [case for pool in first + second for case in pool]


def inputs():
    studies = study_pools()
    keys = {structural_key(case.task) for case in flatten(make_pools(4101, 2))}
    keys.update(structural_key(case.task) for pools in studies.values() for case in flatten(pools))
    for seed, pools in studies.items():
        rng = Random(seed + 310000)
        new = []
        for family in FAMILIES * 3:
            for _ in range(5000):
                task = novel(family, rng)
                signature = structural_key(task)
                if signature not in keys:
                    keys.add(signature)
                    new.append(Case("", family, task))
                    break
            else:
                raise RuntimeError(f"Could not find unique graph for {seed} {family}")
        rng.shuffle(new)
        new = [replace(case, id=f"n{index:02d}") for index, case in enumerate(new)]
        yield seed, pools, new


def prepare(seed, pools, fresh, rows):
    source_cases = {case.id: case for case in flatten(pools)}
    original = pools[-1]
    holdouts = {name: [rename(case, seed)[0] for case in cases]
                for name, cases in (("renamed", original), ("new_motif", fresh))}
    memories = {}
    original_scores = {}
    for row in rows:
        if row["phase"] != "evaluation" or row["round"] != 2 or row["arm"] not in ARMS:
            continue
        arm = row["arm"]
        if arm in memories:
            raise ValueError(f"Repeated evaluation: {seed} {arm}")
        prompt = json.loads(row["prompt"])
        if prompt["tasks"] != json.loads(json.dumps([case.prompt_record() for case in original])):
            raise ValueError(f"Wrong original holdout: {seed} {arm}")
        answers = parse_answers(row["response"])
        original_scores[arm] = [is_correct(case.task, answers.get(case.id)) for case in original]
        memory = []
        for record in prompt["memory"]:
            case = source_cases[record["id"]]
            answer = record["solution"]
            if not is_correct(case.task, answer):
                raise ValueError(f"Invalid original memory answer: {seed} {arm} {case.id}")
            renamed, labels = rename(case, seed)
            if "path" in answer:
                answer = {"path": [labels[node] for node in answer["path"]]}
            if not is_correct(renamed.task, answer):
                raise ValueError(f"Renamed answer mismatch: {seed} {arm} {case.id}")
            memory.append((renamed, answer))
        memories[arm] = memory
    if set(memories) != set(ARMS):
        raise ValueError(f"Missing E002 final evaluations for seed {seed}")
    return original, holdouts, memories, original_scores


def parse_answers(raw):
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if isinstance(value, dict) and isinstance(value.get("answers"), dict):
        return value["answers"]
    return {}


def score(cases, marks):
    return [{"id": case.id, "family": case.family, "correct": mark}
            for case, mark in zip(cases, marks, strict=True)]


def run(archive, output, port):
    output.mkdir(parents=True)
    with (output / "calls.jsonl").open("w") as trace:
        backend = Backend(port, trace)
        for seed, pools, fresh in inputs():
            rows = read_calls(archive / str(seed))
            original, holdouts, memories, original_scores = prepare(seed, pools, fresh, rows)
            records = {}
            for arm in ARMS:
                records[arm] = {"original": score(original, original_scores[arm])}
                for name, cases in holdouts.items():
                    answers = backend.call("evaluation", f"{seed}/{arm}/{name}", 2, cases,
                                           memories[arm], sampling_seed=seed)
                    records[arm][name] = score(
                        cases, [is_correct(case.task, answers.get(case.id)) for case in cases],
                    )
            (output / f"{seed}.json").write_text(json.dumps(records, indent=2) + "\n")
            print(f"Seed {seed} complete", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Archived E002 seed directories.")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ollama-port", type=int)
    args = parser.parse_args()
    run(args.archive, args.output, args.ollama_port)
