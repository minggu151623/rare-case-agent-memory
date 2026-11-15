"""Post-review sensitivity readings for E015: power, bootstrap stream, and where path gains sit."""
from collections import Counter
import json
from pathlib import Path
from random import Random

from src.confirmatory import MEMORIES, SEEDS, UPDATING, all_cases, exact_sign_flip, study
from src.diverse_paths import DETOUR
from src.pilot import oracle_answer
from src.planning import is_correct

ROOT = Path("experiments/E015-confirmatory/results/qwen3-8b")
RESULT = json.loads((ROOT / "aggregate.json").read_text())


def power(gap, base=51 / 90, seeds=30, runs=4000):
    """Share of simulated studies meeting the locked criterion, with independent binomial answers."""
    rng = Random(715300 + round(1000 * gap))
    draw = lambda p: sum(rng.random() < p for _ in range(3))
    hits = 0
    for _ in range(runs):
        differences = [draw(base + gap) - draw(base) for _ in range(seeds)]
        hits += sum(differences) > 0 and exact_sign_flip(differences) <= 0.05
    return round(hits / runs, 3)


def correlated_power(gap, share=0.544, base=51 / 90, seeds=30, runs=4000):
    """Power when the frozen answer copies the mixture answer on a share of queries.

    With share 0.544 the paired difference has a standard deviation of about 0.82
    answers at zero gap, the observed value. The remaining queries are answered
    independently at a rate that gives the stated mean gap, capped at one.
    """
    rng = Random(715400 + round(1000 * gap))
    other = min(1.0, base + gap / (1 - share))
    hits, spread = 0, []
    for _ in range(runs):
        differences = []
        for _ in range(seeds):
            total = 0
            for _ in range(3):
                mixture = rng.random() < base
                frozen = mixture if rng.random() < share else rng.random() < other
                total += frozen - mixture
            differences.append(total)
        mean = sum(differences) / seeds
        spread.append((sum((d - mean) ** 2 for d in differences) / (seeds - 1)) ** 0.5)
        hits += sum(differences) > 0 and exact_sign_flip(differences) <= 0.05
    return {"power": round(hits / runs, 3), "mean_sd_of_differences": round(sum(spread) / runs, 2),
            "achieved_gap_points": round(100 * (1 - share) * (other - base), 1)}


def interval(differences, denominator, stream):
    rng = Random(stream)
    count = len(differences)
    means = sorted(sum(rng.choices(differences, k=count)) / count for _ in range(10000))
    return [round(100 * means[249] / denominator, 2), round(100 * means[9749] / denominator, 2)]


def path_gains():
    pools = study()
    seeds, routes = Counter(), Counter()
    for seed in SEEDS:
        by_id = {case.id: case for case in all_cases(pools[seed])}
        initial, _, _, holdout = pools[seed]
        summary = json.loads((ROOT / str(seed) / "summary.json").read_text())
        contents = {"frozen": list(initial)}
        for arm in UPDATING:
            contents[arm] = [by_id[item] for item in summary["arms"][arm]["final_memory"]]
        for name in MEMORIES[1:]:
            paths = [oracle_answer(c) for c in contents[name] if c.family == DETOUR]
            for case in holdout:
                if case.family != DETOUR or not any(is_correct(case.task, p) for p in paths):
                    continue
                after = summary["readout"][name][case.id]["correct"]
                before = summary["readout"]["empty"][case.id]["correct"]
                if after and not before:
                    seeds[str(seed)] += 1
                    routes["".join(oracle_answer(case)["path"])] += 1
    return {"gained_answers": sum(seeds.values()), "seeds_with_a_gain": len(seeds),
            "largest_seed_share": max(seeds.values()), "routes_with_a_gain": len(routes),
            "by_seed": dict(sorted(seeds.items())), "by_route": dict(sorted(routes.items()))}


def main():
    labels = RESULT["secondary_label_interaction_adaptive_minus_balanced"]["per_seed"]
    primary = RESULT["primary_frozen_minus_mixture_key_detour"]["per_seed"]
    print(json.dumps({
        "power_of_locked_criterion_by_true_gap": {
            f"{round(100 * gap)}_points": power(gap) for gap in (0.10, 0.15, 0.20, 0.25, 0.30)},
        "false_positive_rate_at_zero_gap": power(0.0),
        "power_with_within_query_correlation": {
            f"{round(100 * gap)}_points": correlated_power(gap) for gap in (0.0, 0.10, 0.15, 0.20)},
        "bootstrap_interval_by_stream": {
            "primary": {str(s): interval(primary, 3, s) for s in (715200, 1, 2, 3)},
            "label_interaction": {str(s): interval(labels, 6, s) for s in (715200, 1, 2, 3)}},
        "path_matched_gains": path_gains(),
    }, indent=1))


if __name__ == "__main__":
    main()
