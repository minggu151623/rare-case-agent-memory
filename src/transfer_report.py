"""Audit E003 traces and calculate paired and family-level transfer scores."""

import argparse
from collections import Counter
import json
from pathlib import Path

from src.admission_audit import read_calls
from src.benchmark import FAMILIES
from src.planning import is_correct
from src.transfer import ARMS, inputs, parse_answers, prepare, score

CONDITIONS = ("original", "renamed", "new_motif")


def summarize(archive, run):
    rows = read_calls(run)
    indexed = {row["arm"]: row for row in rows}
    if len(indexed) != len(rows) or len(rows) != 36:
        raise ValueError("Expected 36 uniquely keyed E003 calls")
    results = {arm: {condition: {family: Counter() for family in FAMILIES}
                     for condition in CONDITIONS} for arm in ARMS}
    paired_key_detour = {}
    paired_items = {}
    for seed, pools, fresh in inputs():
        original, holdouts, memories, original_scores = prepare(
            seed, pools, fresh, read_calls(archive / str(seed)),
        )
        recorded = json.loads((run / f"{seed}.json").read_text())
        paired_key_detour[str(seed)] = {}
        for arm in ARMS:
            records = {"original": score(original, original_scores[arm])}
            for condition, cases in holdouts.items():
                row = indexed.pop(f"{seed}/{arm}/{condition}")
                if (row["phase"], row["round"]) != ("evaluation", 2):
                    raise ValueError("Unexpected call phase")
                if row["output_tokens"] is not None and (
                    row["output_tokens"] > 384 or row["prompt_tokens"] + row["output_tokens"] > 4096
                ):
                    raise ValueError("Generation or context cap exceeded")
                prompt = json.loads(row["prompt"])
                expected = {
                    "tasks": [case.prompt_record() for case in cases],
                    "memory": [{**case.prompt_record(), "solution": answer}
                               for case, answer in memories[arm]],
                }
                if prompt != json.loads(json.dumps(expected)):
                    raise ValueError(f"Prompt mismatch: {seed} {arm} {condition}")
                answers = parse_answers(row["response"])
                records[condition] = score(
                    cases, [is_correct(case.task, answers.get(case.id)) for case in cases],
                )
            if records != recorded[arm]:
                raise ValueError(f"Scoring mismatch: {seed} {arm}")
            before = {item["id"]: item for item in records["original"]}
            for item in records["renamed"]:
                original_item = before[item["id"]]
                status = ("retained" if item["correct"] else "lost") if original_item["correct"] else (
                    "gained" if item["correct"] else "both_wrong"
                )
                paired_items.setdefault(arm, {}).setdefault(item["family"], Counter())[status] += 1
            paired_key_detour[str(seed)][arm] = {}
            for condition, tasks in records.items():
                for item in tasks:
                    group = results[arm][condition][item["family"]]
                    group["total"] += 1
                    group["correct"] += int(item["correct"])
                paired_key_detour[str(seed)][arm][condition] = sum(
                    item["correct"] for item in tasks if item["family"] == "key_detour"
                )
    if indexed:
        raise ValueError("Unexpected extra trace rows")
    return {
        "calls": len(rows),
        "format_failures": sum(not row["valid_format"] for row in rows),
        "prompt_tokens": sum(row["prompt_tokens"] or 0 for row in rows),
        "output_tokens": sum(row["output_tokens"] or 0 for row in rows),
        "request_seconds": round(sum(row.get("seconds", 0) for row in rows), 3),
        "scores": results,
        "key_detour_correct_per_seed": paired_key_detour,
        "original_to_renamed_item_transitions": paired_items,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.archive, args.run), indent=2))
