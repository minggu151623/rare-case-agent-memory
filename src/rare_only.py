"""Run and replay the E012 matched rare-only comparison."""
import argparse
from itertools import product
import json
from pathlib import Path
from random import Random

from src.admission import assignment, run_seed, study_pools
from src.admission_audit import audit_seed, require
from src.benchmark import RARE
from src.pilot import DIGEST, MODEL

ARMS = (("targeted", "model"), ("rare_only", "model"))
RUNTIME = "0.40.12"


def plan_for(seed):
    _, tie_order, _ = assignment(seed, ARMS)
    families = Random(seed + 612000).sample(RARE, len(RARE))
    order = Random(seed + 612001).sample(ARMS, len(ARMS))
    return families, tie_order, order


def sensitivity(gaps):
    observed = abs(sum(gaps))
    extreme = sum(
        abs(sum(gap * sign for gap, sign in zip(gaps, signs, strict=True))) >= observed
        for signs in product((-1, 1), repeat=len(gaps))
    )
    return extreme / 2**len(gaps)


def replay_seed(output, seed, pools):
    directory = output / str(seed)
    audit_seed(directory, seed, pools, arms=ARMS, include_controls=False, plan=plan_for(seed))
    summary = json.loads((directory / "summary.json").read_text())
    require(
        (summary["backend"], summary["digest"], summary["runtime_version"])
        == (MODEL, DIGEST, RUNTIME), "Unexpected inference provenance",
    )
    return summary


def report(output):
    summaries = [replay_seed(output, seed, pools) for seed, pools in study_pools().items()]
    names = ["_".join(arm) for arm in ARMS]
    gaps = [
        sum(summary["arms"][names[0]]["final"]["correct"][family]
            - summary["arms"][names[1]]["final"]["correct"][family] for family in RARE)
        for summary in summaries
    ]
    return {
        "calls": sum(summary["calls"] for summary in summaries),
        "format_failures": sum(summary["format_failures"] for summary in summaries),
        "scores": {name: {
            family: {field: sum(s["arms"][name]["final"][field][family] for s in summaries)
                     for field in ("correct", "total")}
            for family in summaries[0]["arms"][name]["final"]["total"]
        } for name in names},
        "coverage": {name: {
            family: {
                "supplement_attempts": sum(
                    row["supplement"]["family"] == family
                    for s in summaries for row in s["arms"][name]["rounds"]
                ),
                "supplement_admissions": sum(
                    row["supplement"]["family"] == family and row["supplement"]["admitted"]
                    for s in summaries for row in s["arms"][name]["rounds"]
                ),
                "final_retained": sum(s["arms"][name]["rounds"][-1]["retained"][family]
                                      for s in summaries),
            } for family in RARE
        } for name in names},
        "per_seed_correct": {s["seed"]: {name: s["arms"][name]["final"]["correct"]
                                        for name in names} for s in summaries},
        "rare_gaps_out_of_six": gaps,
        "rare_mean_gap": sum(gaps) / (6 * len(gaps)),
        "sign_flip_p": sensitivity(gaps),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ollama-port", type=int)
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if args.audit:
        print(json.dumps(report(args.output), indent=2))
        return
    if args.ollama_port is None:
        parser.error("--ollama-port is required for inference")
    for seed, pools in study_pools().items():
        if (args.output / str(seed)).exists():
            replay_seed(args.output, seed, pools)
        else:
            run_seed(seed, pools, args.ollama_port, args.output / str(seed), arms=ARMS,
                     include_controls=False, plan=plan_for(seed))
            replay_seed(args.output, seed, pools)
        print(f"Seed {seed} complete", flush=True)


if __name__ == "__main__":
    main()
