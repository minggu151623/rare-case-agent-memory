"""Run or audit E009's shared and mixed conditions with matched marginals."""

import argparse
from collections import Counter
import json
from pathlib import Path
from random import Random

from src.admission import study_pools
from src.admission_audit import read_calls
from src.benchmark import FAMILIES
from src.pilot import Backend
from src.representation import ARMS, NODES, prompts, rename_memory, score_call
from src.transfer import rename_with_labels

CONDITIONS = ("shared", "mixed")


def maps_for_seed(seed):
    rng = Random(seed + 510000)
    choices = []
    while len(choices) < 2:
        values = rng.sample(list(NODES), len(NODES))
        if any(old == new for old, new in zip(NODES, values)):
            continue
        if choices and any(choices[0][old] == new for old, new in zip(NODES, values)):
            continue
        choices.append(dict(zip(NODES, values)))
    return choices


def transform(cases, memory, mappings, repetition, condition):
    offsets = (0,) if condition == "shared" else (0, 1)
    query_maps = [mappings[(repetition + offsets[i % len(offsets)]) % 2]
                  for i in range(len(cases))]
    memory_maps = {case.id: mappings[(repetition + offsets[i % len(offsets)]) % 2]
                   for i, (case, _) in enumerate(memory)}

    def transform_example(case):
        labels = memory_maps[case.id]
        return rename_with_labels(case, labels), labels

    return (
        [rename_with_labels(case, labels) for case, labels in zip(cases, query_maps, strict=True)],
        rename_memory(memory, transform_example),
    )


def keyed_prompts(source):
    for seed, pools in study_pools().items():
        originals = prompts(seed, pools, read_calls(source / str(seed)))
        mappings = maps_for_seed(seed)
        for arm in ARMS:
            cases, memory = originals[arm]["original"]
            for condition in CONDITIONS:
                for repetition in range(2):
                    yield seed, arm, condition, repetition, transform(
                        cases, memory, mappings, repetition, condition,
                    )


def run(source, output, port):
    output.mkdir(parents=True)
    with (output / "calls.jsonl").open("w") as trace:
        backend = Backend(port, trace)
        for seed, arm, condition, repetition, (cases, memory) in keyed_prompts(source):
            backend.call(
                "evaluation", f"{seed}/{arm}/{condition}/{repetition}",
                2, cases, memory, sampling_seed=seed,
            )
            if arm == ARMS[-1] and condition == CONDITIONS[-1] and repetition == 1:
                print(f"Seed {seed} complete", flush=True)


def report(source, run_root):
    raw = read_calls(run_root)
    calls = {row["arm"]: row for row in raw}
    if len(calls) != len(raw) or len(calls) != 48:
        raise ValueError("Expected 48 unique E009 calls")
    scores = {}
    exposures = {}
    for seed, arm, condition, repetition, (cases, memory) in keyed_prompts(source):
        key = f"{seed}/{arm}/{condition}/{repetition}"
        row = calls.pop(key)
        if (row["phase"], row["round"]) != ("evaluation", 2):
            raise ValueError(f"Wrong phase for {key}")
        per_seed = scores.setdefault(str(seed), {}).setdefault(arm, {})
        per_condition = per_seed.setdefault(condition, {family: Counter() for family in FAMILIES})
        per_exposure = exposures.setdefault((seed, arm), {}).setdefault(condition, Counter())
        for case in cases + [case for case, _ in memory]:
            per_exposure[(case.id, case.task)] += 1
        for item in score_call(row, cases, memory):
            family = per_condition[item["family"]]
            family["total"] += 1
            family["correct"] += int(item["correct"])
    if calls or any(x["shared"] != x["mixed"] for x in exposures.values()):
        raise ValueError("Unmatched calls or marginal graph exposures")
    contrasts = []
    for row in scores.values():
        def key_correct(arm, condition):
            return row[arm][condition]["key_detour"]["correct"]

        random = key_correct("random_model", "shared") - key_correct("random_model", "mixed")
        targeted = key_correct("targeted_model", "shared") - key_correct("targeted_model", "mixed")
        contrasts.append({"random": random, "targeted": targeted, "gap": targeted - random})
    totals = {
        arm: {condition: {family: {
            field: sum(row[arm][condition][family][field] for row in scores.values())
            for field in ("correct", "total")
        } for family in FAMILIES} for condition in CONDITIONS} for arm in ARMS
    }
    return {
        "calls": len(raw),
        "format_failures": sum(not row["valid_format"] for row in raw),
        "prompt_tokens": sum(row["prompt_tokens"] or 0 for row in raw),
        "output_tokens": sum(row["output_tokens"] or 0 for row in raw),
        "request_seconds": round(sum(row.get("seconds", 0) for row in raw), 3),
        "scores": totals,
        "per_seed_correct": scores,
        "key_detour_gap_difference_by_seed": [row["gap"] / 6 for row in contrasts],
        "key_detour_gap_difference": sum(row["gap"] for row in contrasts) / 36,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ollama-port", type=int)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if args.audit:
        print(json.dumps(report(args.source, args.output), indent=2))
    else:
        run(args.source, args.output, args.ollama_port)
