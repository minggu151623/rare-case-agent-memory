"""Replay the E004 or E006 factorial cells and report paired contrasts."""

import argparse
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path

from src.admission import study_pools
from src.admission_audit import read_calls
from src.benchmark import FAMILIES
from src.representation import ARMS, CELLS, FRESH, prompts, read_seed, score_call


def effects(counts):
    original, memory, query, both = (
        Fraction(counts[cell], 3) for cell in CELLS[:4]
    )
    return {
        "memory_main": (memory - original + both - query) / 2,
        "query_main": (query - original + both - memory) / 2,
        "interaction": both - memory - query + original,
        "shared_minus_original": Fraction(counts["shared_map"], 3) - original,
    }


def report(source, e003, run, cross_model):
    calls = read_calls(run)
    rows = {row["arm"]: row for row in calls}
    expected_calls = 60 if cross_model else 36
    if len(rows) != len(calls) or len(rows) != expected_calls:
        raise ValueError(f"Expected {expected_calls} unique calls")
    e003_rows = {row["arm"]: row for row in read_calls(e003)} if not cross_model else {}
    seeds = {}
    totals = {
        arm: {cell: {family: Counter() for family in FAMILIES} for cell in CELLS}
        for arm in ARMS
    }
    for seed, pools in study_pools().items():
        original_rows = read_seed(source, seed)
        original = {row["arm"]: row for row in original_rows
                    if (row["phase"], row["round"]) == ("evaluation", 2)}
        cases_by_arm = prompts(seed, pools, original_rows)
        actual = json.loads((run / f"{seed}.json").read_text())
        seeds[str(seed)] = {}
        for arm in ARMS:
            seeds[str(seed)][arm] = {}
            for cell in CELLS:
                if not cross_model and cell == "original":
                    row = original[arm]
                elif not cross_model and cell == "independent_both":
                    row = e003_rows[f"{seed}/{arm}/renamed"]
                else:
                    row = rows.pop(f"{seed}/{arm}/{cell}")
                if (row["phase"], row["round"]) != ("evaluation", 2):
                    raise ValueError(f"Wrong phase for {seed}/{arm}/{cell}")
                items = score_call(row, *cases_by_arm[arm][cell])
                if (cross_model or cell in FRESH) and items != actual[arm][cell]:
                    raise ValueError(f"Score mismatch for {seed}/{arm}/{cell}")
                counts = Counter()
                for item in items:
                    family = item["family"]
                    totals[arm][cell][family]["total"] += 1
                    totals[arm][cell][family]["correct"] += int(item["correct"])
                    counts[family] += int(item["correct"])
                seeds[str(seed)][arm][cell] = dict(counts)
    if rows:
        raise ValueError("Unused calls")
    arm_effects = {}
    for arm in ARMS:
        per_seed = [effects({cell: row[arm][cell]["key_detour"] for cell in CELLS})
                    for row in seeds.values()]
        arm_effects[arm] = {}
        for key in per_seed[0]:
            values = [row[key] for row in per_seed]
            arm_effects[arm][key] = {
                "mean": float(sum(values) / len(values)),
                "per_seed": [float(value) for value in values],
            }
    gaps = {cell: totals["targeted_model"][cell]["key_detour"]["correct"]
                  - totals["random_model"][cell]["key_detour"]["correct"] for cell in CELLS}
    return {
        "calls": len(calls),
        "format_failures": sum(not row["valid_format"] for row in calls),
        "reasoning_present_calls": sum(bool(row.get("reasoning_present")) for row in calls),
        "prompt_tokens": sum(row["prompt_tokens"] or 0 for row in calls),
        "output_tokens": sum(row["output_tokens"] or 0 for row in calls),
        "request_seconds": round(sum(row.get("seconds", 0) for row in calls), 3),
        "scores": totals,
        "key_detour_targeted_minus_random_correct_count": gaps,
        "key_detour_factorial_effects": arm_effects,
        "per_seed_correct": seeds,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("e003", type=Path)
    parser.add_argument("run", type=Path)
    parser.add_argument("--cross-model", action="store_true")
    args = parser.parse_args()
    print(json.dumps(report(args.source, args.e003, args.run, args.cross_model), indent=2))
