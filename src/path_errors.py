"""Classify errors and literal path reuse on equivalent E002/E003 graphs."""

import argparse
from collections import Counter
import json
from pathlib import Path

from src.admission import study_pools
from src.admission_audit import read_calls
from src.planning import is_correct, shortest_distance
from src.representation import ARMS, prompts
from src.transfer import parse_answers


def classify(task, answer):
    if not isinstance(answer, dict):
        return "malformed_or_missing"
    if answer == {"unreachable": True} and answer["unreachable"] is True:
        return "correct" if shortest_distance(task) is None else "false_unreachable"
    path = answer.get("path")
    if set(answer) != {"path"} or not isinstance(path, list) or not path:
        return "malformed_or_missing"
    if not all(isinstance(node, str) for node in path):
        return "malformed_or_missing"
    if path[0] != task.start or path[-1] != task.goal:
        return "wrong_endpoint"
    has_key = task.start == task.key_at
    for source, target in zip(path, path[1:]):
        edges = [edge for edge in task.edges if (edge.source, edge.destination) == (source, target)]
        if not edges:
            return "nonexistent_edge"
        if not has_key and all(edge.requires_key for edge in edges):
            return "locked_before_key"
        has_key = has_key or target == task.key_at
    return "correct" if len(path) - 1 == shortest_distance(task) else "suboptimal"


def audit(source, transfer):
    renamed_rows = {row["arm"]: row for row in read_calls(transfer)}
    counts = {}
    repeats = {}
    for seed, pools in study_pools().items():
        source_rows = read_calls(source / str(seed))
        original_rows = {row["arm"]: row for row in source_rows
                         if (row["phase"], row["round"]) == ("evaluation", 2)}
        arms = prompts(seed, pools, source_rows)
        for arm in ARMS:
            cases = arms[arm]["original"][0]
            renamed_cases = arms[arm]["independent_both"][0]
            original = parse_answers(original_rows[arm]["response"])
            renamed = parse_answers(renamed_rows[f"{seed}/{arm}/renamed"]["response"])
            for case, mapped in zip(cases, renamed_cases, strict=True):
                before = original.get(case.id)
                after = renamed.get(case.id)
                for condition, item, answer in (("original", case, before),
                                                ("renamed", mapped, after)):
                    category = classify(item.task, answer)
                    if (category == "correct") != is_correct(item.task, answer):
                        raise ValueError(f"Classifier disagrees with scorer: {seed} {arm} {item.id}")
                    groups = counts.setdefault(arm, {}).setdefault(condition, {})
                    groups.setdefault(item.family, Counter())[category] += 1
                if isinstance(before, dict) and "path" in before and is_correct(case.task, before):
                    if not is_correct(mapped.task, after):
                        tally = repeats.setdefault(arm, {}).setdefault(case.family, Counter())
                        tally["failures_after_correct_original_path"] += 1
                        if isinstance(after, dict) and after.get("path") == before["path"]:
                            tally["literal_reuses"] += 1
    return {"first_error_counts": counts, "literal_path_reuse": repeats}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("transfer", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.source, args.transfer), indent=2))
