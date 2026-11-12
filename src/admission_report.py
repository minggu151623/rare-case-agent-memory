"""Aggregate the complete locked E002 run by paired seed and task family."""

import argparse
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

from src.admission import ARMS, SEEDS
from src.benchmark import FAMILIES, RARE, REFERENCE_WEIGHTS


def mean(values):
    return sum(values) / len(values)


def accuracy(record, families):
    return mean([Fraction(record["correct"][family], record["total"][family])
                 for family in families])


def sign_flip_p(differences):
    observed = abs(sum(differences))
    patterns = list(product((-1, 1), repeat=len(differences)))
    extreme = sum(abs(sum(sign * delta for sign, delta in zip(signs, differences))) >= observed
                  for signs in patterns)
    return extreme / len(patterns)


def effect(differences):
    return {
        "per_seed": [float(delta) for delta in differences],
        "mean": float(mean(differences)),
        "exact_sign_flip_p_two_sided": sign_flip_p(differences),
    }


def arm_metrics(records):
    evaluations = [record["final"] for record in records]
    return {
        "final_correct": {family: sum(row["correct"][family] for row in evaluations)
                          for family in FAMILIES},
        "final_total": {family: sum(row["total"][family] for row in evaluations)
                        for family in FAMILIES},
        "weighted_accuracy": float(mean([
            sum(weight * accuracy(row, (family,))
                for family, weight in zip(FAMILIES, REFERENCE_WEIGHTS)) / sum(REFERENCE_WEIGHTS)
            for row in evaluations
        ])),
        "rare_macro_accuracy": float(mean([accuracy(row, RARE) for row in evaluations])),
    }


def report(root):
    summaries = [json.loads((root / str(seed) / "summary.json").read_text()) for seed in SEEDS]
    for seed, summary in zip(SEEDS, summaries):
        if summary["seed"] != seed or summary["calls"] != 14:
            raise ValueError(f"Incomplete or mislabeled seed {seed}")
    arms = {}
    for allocation, source in ARMS:
        arm = f"{allocation}_{source}"
        records = [summary["arms"][arm] for summary in summaries]
        rounds = [row for record in records for row in record["rounds"]]
        arms[arm] = arm_metrics(records) | {
            "final_memory_by_seed": [row["rounds"][-1]["retained"] for row in records],
            "stage_totals": {
                stage: {family: sum(row[stage][family] for row in rounds) for family in FAMILIES}
                for stage in ("attempted", "model_passes", "admitted", "evicted")
            },
        }

    def final_rare(row, arm):
        return accuracy(row["arms"][arm]["final"], RARE)

    primary_coverage = []
    primary_accuracy = []
    interaction_accuracy = []
    for row in summaries:
        memory = {arm: result["rounds"][-1]["retained"] for arm, result in row["arms"].items()}
        primary_coverage.append(
            memory["targeted_oracle"]["unreachable"] - memory["targeted_model"]["unreachable"]
        )
        model_delta = final_rare(row, "targeted_model") - final_rare(row, "random_model")
        oracle_delta = final_rare(row, "targeted_oracle") - final_rare(row, "random_oracle")
        primary_accuracy.append(model_delta)
        interaction_accuracy.append(oracle_delta - model_delta)
    return {
        "backend": summaries[0]["backend"],
        "seeds": SEEDS,
        "calls": sum(row["calls"] for row in summaries),
        "format_failures": sum(row["format_failures"] for row in summaries),
        "prompt_tokens": sum(row["prompt_tokens"] or 0 for row in summaries),
        "output_tokens": sum(row["output_tokens"] or 0 for row in summaries),
        "primary_unreachable_memory_targeted_oracle_minus_model": effect(primary_coverage),
        "primary_rare_accuracy_targeted_model_minus_random_model": effect(primary_accuracy),
        "secondary_rare_accuracy_allocation_answer_source_interaction": effect(interaction_accuracy),
        "arms": arms,
        "controls": {
            control: arm_metrics([{"final": row["controls"][control]} for row in summaries])
            for control in ("empty", "frozen")
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Root containing all six seed directories.")
    args = parser.parse_args()
    print(json.dumps(report(args.output), indent=2))
