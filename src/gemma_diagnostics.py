"""Check answer completeness for E006 and replay the E010 diagnostic."""

import argparse
import json
from pathlib import Path

from src.admission import study_pools
from src.admission_audit import read_calls
from src.representation import ARMS, prompts, score_call
from src.transfer import parse_answers

SINGLE_CELLS = ("original", "independent_both", "shared_map")


def batch_completeness(root):
    calls = read_calls(root)
    if len(calls) != 60:
        raise ValueError("Expected 60 batch calls")
    by_position = [0] * 9
    returned = []
    for row in calls:
        tasks = json.loads(row["prompt"])["tasks"]
        if len(tasks) != 9:
            raise ValueError("Expected nine cases in each batch")
        answers = parse_answers(row["response"])
        present = [case["id"] in answers for case in tasks]
        returned.append(sum(present))
        by_position = [count + int(flag) for count, flag in zip(by_position, present, strict=True)]
    return {
        "calls": len(calls), "expected_case_ids": len(calls) * 9,
        "returned_case_ids": sum(returned), "complete_calls": returned.count(9),
        "returned_by_position": by_position,
        "returned_per_call": returned,
    }


def audit_single(source, root):
    raw = read_calls(root)
    calls = {row["arm"]: row for row in raw}
    if len(calls) != len(raw) or len(calls) != 36:
        raise ValueError("Expected 36 single-query calls")
    per_seed = {}
    totals = {arm: {cell: {"correct": 0, "answered": 0, "total": 0}
                    for cell in SINGLE_CELLS} for arm in ARMS}
    for seed, pools in study_pools().items():
        by_arm = prompts(seed, pools, read_calls(source / str(seed)))
        stored = json.loads((root / f"{seed}.json").read_text())
        per_seed[str(seed)] = {}
        for arm in ARMS:
            per_seed[str(seed)][arm] = {}
            for cell in SINGLE_CELLS:
                cases, memory = by_arm[arm][cell]
                case = next(case for case in cases if case.family == "key_detour")
                row = calls.pop(f"{seed}/{arm}/{cell}")
                if (row["phase"], row["round"]) != ("evaluation", 2):
                    raise ValueError("Unexpected call phase")
                scored = score_call(row, [case], memory)
                if scored != stored[arm][cell]:
                    raise ValueError(f"Score mismatch: {seed} {arm} {cell}")
                result = {
                    "id": case.id, "correct": scored[0]["correct"],
                    "answered": case.id in parse_answers(row["response"]),
                }
                per_seed[str(seed)][arm][cell] = result
                totals[arm][cell]["correct"] += int(result["correct"])
                totals[arm][cell]["answered"] += int(result["answered"])
                totals[arm][cell]["total"] += 1
    if calls:
        raise ValueError("Unused responses")
    return {
        "calls": len(raw), "format_failures": sum(not row["valid_format"] for row in raw),
        "reasoning_present_calls": sum(bool(row.get("reasoning_present")) for row in raw),
        "scores": totals, "per_seed": per_seed,
        "request_seconds": round(sum(row.get("seconds", 0) for row in raw), 3),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--source", type=Path, help="E002 archive for E010. Omit for E006 completeness.")
    args = parser.parse_args()
    result = audit_single(args.source, args.root) if args.source else batch_completeness(args.root)
    print(json.dumps(result, indent=2))
