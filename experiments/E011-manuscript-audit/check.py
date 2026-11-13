"""Audit generator shortcuts and model readouts from the archived evidence."""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
from statistics import mean

from src.admission_audit import read_calls
from src.matched_labels import report as matched_report
from src.planning import is_correct, shortest_distance
from src.representation import ARMS, prompts, score_call
from src.transfer import flatten, inputs

E002 = Path("experiments/E002-admission/results/qwen3-8b")
E003 = Path("experiments/E003-transfer/results/qwen3-8b")
E004 = Path("experiments/E004-representation/results/qwen3-8b")
E009 = Path("experiments/E009-matched-labels/results/qwen3-8b")


def indexed(directory):
    return {row["arm"]: row for row in read_calls(directory)}


def reference_distance(task):
    # Repeated relaxation over explicit states, independent of the production BFS.
    vertices = {node for edge in task.edges for node in (edge.source, edge.destination)}
    distance = {(task.start, task.start == task.key_at): 0}
    for _ in range(2 * len(vertices) - 1):
        previous = distance.copy()
        for edge in task.edges:
            for has_key in (False, True):
                state = (edge.source, has_key)
                if state in previous and (has_key or not edge.requires_key):
                    target = (edge.destination, has_key or edge.destination == task.key_at)
                    candidate = previous[state] + 1
                    distance[target] = min(distance.get(target, candidate), candidate)
    return min((cost for (node, _), cost in distance.items() if node == task.goal), default=None)


def audit():
    renamed, shared = indexed(E003), indexed(E004)
    fixed = {"path": list("ADCDB")}
    template = {kind: Counter(correct=0, total=0) for kind in ("original", "new_motif")}
    subset = {arm: Counter(original=0, independent_both=0, shared_map=0) for arm in ARMS}
    supplements = {arm: Counter() for arm in ARMS}
    checked = 0
    for seed, pools, new in inputs():
        for case in flatten(pools) + new:
            if reference_distance(case.task) != shortest_distance(case.task):
                raise ValueError(f"Oracle mismatch: {seed}/{case.id}")
            checked += 1
        for kind, cases in (("original", pools[-1]), ("new_motif", new)):
            for case in cases:
                if case.family == "key_detour":
                    template[kind]["total"] += 1
                    template[kind]["correct"] += is_correct(case.task, fixed)
        rows = read_calls(E002 / str(seed))
        original = {row["arm"]: row for row in rows
                    if (row["phase"], row["round"]) == ("evaluation", 2)}
        by_arm = prompts(seed, pools, rows)
        recorded = json.loads((E002 / str(seed) / "summary.json").read_text())
        for arm in ARMS:
            supplements[arm].update(
                row["supplement"]["family"] for row in recorded["arms"][arm]["rounds"]
            )
            for condition, row in (
                ("original", original[arm]),
                ("independent_both", renamed[f"{seed}/{arm}/renamed"]),
                ("shared_map", shared[f"{seed}/{arm}/shared_map"]),
            ):
                scored = score_call(row, *by_arm[arm][condition])
                subset[arm][condition] += next(
                    item["correct"] for item in scored if item["family"] == "key_detour"
                )
    matches = matched_report(E002, E009)
    effects = [Fraction(value).limit_denominator(6)
               for value in matches["key_detour_gap_difference_by_seed"]]
    return {
        "independent_shortest_distance_checks": checked,
        "generator_aware_fixed_path": template,
        "qwen_batched_e010_subset_correct_out_of_six": subset,
        "e002_supplement_family_counts": supplements,
        "e009_gap_difference_percentage_points": float(100 * mean(effects)),
        "e009_leave_one_seed_out_percentage_points": [
            float(100 * mean(effects[:i] + effects[i+1:])) for i in range(len(effects))
        ],
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
