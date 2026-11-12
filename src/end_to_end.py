"""Run or replay the E008 fully renamed memory trajectories."""

import argparse
import json
from pathlib import Path

from src.admission import ARMS, run_seed, study_pools
from src.admission_audit import audit_seed
from src.benchmark import FAMILIES
from src.transfer import rename

MODEL_ARMS = tuple(arm for arm in ARMS if arm[1] == "model")


def renamed_study():
    for seed, (initial, backgrounds, supplements, holdout) in study_pools().items():
        def transform(pool):
            return [rename(case, seed)[0] for case in pool]
        yield seed, (
            transform(initial), [transform(pool) for pool in backgrounds],
            [transform(pool) for pool in supplements], transform(holdout),
        )


def summarize(root):
    per_seed = {}
    for seed, pools in renamed_study():
        directory = root / str(seed)
        audit_seed(directory, seed, pools, arms=MODEL_ARMS, include_controls=False)
        per_seed[str(seed)] = json.loads((directory / "summary.json").read_text())
    totals = {}
    for allocation, source in MODEL_ARMS:
        arm = f"{allocation}_{source}"
        values = [row["arms"][arm] for row in per_seed.values()]
        totals[arm] = {
            "final_correct": {family: sum(value["final"]["correct"][family] for value in values)
                              for family in FAMILIES},
            "final_total": {family: sum(value["final"]["total"][family] for value in values)
                            for family in FAMILIES},
            "final_memory_by_seed": [value["rounds"][-1]["retained"] for value in values],
            "stage_totals": {
                stage: {family: sum(round_[stage][family] for value in values
                                    for round_ in value["rounds"]) for family in FAMILIES}
                for stage in ("attempted", "model_passes", "admitted", "evicted")
            },
        }
    return {
        "calls": sum(row["calls"] for row in per_seed.values()),
        "format_failures": sum(row["format_failures"] for row in per_seed.values()),
        "prompt_tokens": sum(row["prompt_tokens"] or 0 for row in per_seed.values()),
        "output_tokens": sum(row["output_tokens"] or 0 for row in per_seed.values()),
        "request_seconds": round(sum(row["seconds"] or 0 for row in per_seed.values()), 3),
        "arms": totals,
        "per_seed_correct": {seed: {arm: value["final"]["correct"]
                                   for arm, value in row["arms"].items()}
                             for seed, row in per_seed.items()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ollama-port", type=int)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if args.audit:
        print(json.dumps(summarize(args.output), indent=2))
    else:
        args.output.mkdir(parents=True)
        for seed, pools in renamed_study():
            run_seed(seed, pools, args.ollama_port, args.output / str(seed),
                     arms=MODEL_ARMS, include_controls=False)
            print(f"Seed {seed} complete", flush=True)
