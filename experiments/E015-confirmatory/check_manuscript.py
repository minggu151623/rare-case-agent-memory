"""Assert the manuscript's E015 statements against the archived aggregate and traces."""
from collections import Counter
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = json.loads((HERE / "results/qwen3-8b/aggregate.json").read_text())
EXTRA = json.loads((HERE / "exploratory.json").read_text())
E014 = json.loads((HERE.parent / "E014-publication-audit/results.json").read_text())


def statements():
    checked = []

    def claim(name, actual, expected):
        agrees = (abs(actual - expected) < 0.05 if isinstance(expected, float)
                  else actual == expected)
        if not agrees:
            raise AssertionError(f"{name}: archive gives {actual}, manuscript states {expected}")
        checked.append(name)

    def numbers(cell, digits=1):
        return (round(cell["mean_percentage_points"], digits),
                *[round(x, digits) for x in cell["bootstrap_95_percentage_points"]],
                round(cell["exact_sign_flip_p_two_sided"], 2))

    scores = {name: tuple(row[f]["correct"] for f in ("ungated", "key_detour", "unreachable"))
              for name, row in RESULT["scores"].items()}
    kept = {name: row["key_detour"] for name, row in RESULT["seeds_retaining_an_example"].items()}
    primary = RESULT["primary_frozen_minus_mixture_key_detour"]
    rare = RESULT["secondary_adaptive_minus_balanced_rare"]
    labels = RESULT["secondary_label_interaction_adaptive_minus_balanced"]
    extra = RESULT["descriptive"]
    stages, families = RESULT["stage_totals"], RESULT["supplement_families"]
    split, paths = RESULT["retained_coverage_split"], RESULT["key_detour_by_path_availability"]
    fifo, said = RESULT["fifo_conformance"], EXTRA["unreachable_declarations"]

    claim("seeds, calls, format failures",
          (len(RESULT["seeds"]), RESULT["calls"], RESULT["format_failures"]), (30, 2790, 1))
    claim("readout answers returned", RESULT["answers_returned"],
          {"answered": 1350, "requested": 1350})
    claim("format failure is in the label sub-study at the output limit",
          [(f["arm"].split("/")[0], f["done_reason"]) for f in EXTRA["format_failures"]],
          [("label", "length")])
    claim("best fixed key-detour path", RESULT["holdout_constant_path"],
          {"key_detour_queries": 90, "optimal_paths": 9, "best_fixed_path_correct": 10})
    claim("family scores, empty", scores["empty"], (62, 53, 0))
    claim("family scores, frozen", scores["frozen"], (87, 55, 0))
    claim("family scores, mixture", scores["random_model"], (88, 51, 0))
    claim("family scores, balanced", scores["rare_only_model"], (88, 59, 0))
    claim("family scores, adaptive", scores["targeted_model"], (88, 56, 0))
    claim("unreachable readout total", sum(row[2] for row in scores.values()), 0)
    claim("seeds retaining a key-detour example", kept,
          {"empty": 0, "frozen": 30, "random_model": 6, "rare_only_model": 24,
           "targeted_model": 20})
    claim("frozen memories hold an unreachable example",
          RESULT["seeds_retaining_an_example"]["frozen"]["unreachable"], 30)
    claim("rare supplements",
          {arm: (c.get("key_detour", 0), c.get("unreachable", 0), sum(c.values()))
           for arm, c in families.items()},
          {"random_model": (13, 13, 120), "rare_only_model": (60, 60, 120),
           "targeted_model": (36, 84, 120)})
    claim("primary difference distribution", sorted(Counter(primary["per_seed"]).items()),
          [(-2, 1), (-1, 5), (0, 13), (1, 11)])
    claim("primary sign counts", primary["positive_zero_negative"], [11, 13, 6])
    claim("primary mean, interval, sign-flip", numbers(primary), (4.4, -5.6, 13.3, 0.51))
    claim("primary criterion not met",
          primary["mean"] > 0 and primary["exact_sign_flip_p_two_sided"] <= 0.05, False)
    claim("primary standardized effect", primary["mean"] / primary["sd"], 0.16)
    claim("adaptation mean, interval, sign-flip", numbers(rare), (-1.7, -5.0, 1.7, 0.51))
    claim("adaptation Holm value", round(rare["holm_adjusted_p"], 2), 0.51)
    claim("label interaction mean, interval, sign-flip", numbers(labels),
          (-5.0, -11.7, 1.1, 0.18))
    claim("label interaction Holm value", round(labels["holm_adjusted_p"], 2), 0.36)
    claim("unreachable attempts and admissions",
          (sum(s["attempted"]["unreachable"] for s in stages.values()),
           sum(s["admitted"]["unreachable"] for s in stages.values())), (208, 0))
    claim("key-detour admissions, adaptive and balanced",
          (stages["targeted_model"]["admitted"]["key_detour"],
           stages["rare_only_model"]["admitted"]["key_detour"]), (27, 45))
    claim("coverage split, key detour",
          [(split["key_detour"][g]["memories"], split["key_detour"][g]["correct"],
            split["key_detour"][g]["total"]) for g in ("present", "absent")],
          [(80, 145, 240), (70, 129, 210)])
    claim("coverage split percentages", (round(100 * split["key_detour"]["present"]["correct"] / 240, 1),
           round(100 * split["key_detour"]["absent"]["correct"] / 210, 1)), (60.4, 61.4))
    claim("path availability",
          [(paths[g]["correct"], paths[g]["total"])
           for g in ("path_in_memory", "path_not_in_memory", "no_key_detour_example")],
          [(29, 32), (116, 208), (129, 210)])
    claim("balanced minus mixture", numbers(extra["balanced_minus_mixture_key_detour"]),
          (8.9, 0.0, 17.8, 0.10))
    claim("adaptive minus mixture", numbers(extra["adaptive_minus_mixture_key_detour"]),
          (5.6, -1.1, 12.2, 0.23))
    claim("label interaction against mixture",
          numbers(extra["label_interaction_adaptive_minus_mixture"]), (-10.0, -17.8, -2.2, 0.03))
    claim("frozen minus empty key-detour answers", scores["frozen"][1] - scores["empty"][1], 2)
    claim("FIFO conformance", (fifo["trajectories"], fifo["checks"]), (90, 270))
    claim("rare losses and losses without admission",
          (fifo["rare_losses"], fifo["rare_losses_without_admission"]), (130, 121))
    claim("trajectories checked in total",
          fifo["trajectories"] + E014["fifo_conformance"]["trajectories"], 132)
    claim("unreachable declarations",
          (sum(v for stage in said.values() for k, v in stage.items()
               if k.endswith("declared_unreachable")),
           sum(v for stage in said.values() for k, v in stage.items()
               if k.endswith("_queries"))), (0, 3510))
    claim("mixture seeds that lost the key-detour example", 30 - kept["random_model"], 24)
    claim("E002 frozen minus mixture, original holdout", 16 - 7, 9)
    same = EXTRA["path_split_against_empty_memory_on_same_queries"]
    claim("path-matched queries against the empty memory",
          [same["path_in_memory"][k] for k in
           ("answers", "unique_queries", "with_memory", "empty_memory", "gained", "lost")],
          [32, 23, 29, 20, 11, 2])
    claim("other-path queries against the empty memory",
          (same["path_not_in_memory"]["empty_memory"], same["path_not_in_memory"]["answers"]),
          (117, 208))
    claim("primary standard deviation", primary["sd"], 0.82)
    claim("adaptation contrast in key-detour points",
          round(100 * (scores["targeted_model"][1] - scores["rare_only_model"][1]) / 90, 1), -3.3)
    claim("frozen minus empty interval",
          numbers(extra["frozen_minus_empty_key_detour"])[1:3], (-10.0, 14.4))
    claim("descriptive sign-flip values",
          str(extra).count("exact_sign_flip_p_two_sided"), 7)
    extra_checks = json.loads((HERE / "sensitivity.json").read_text())
    gains = extra_checks["path_matched_gains"]
    claim("path gains by seed and route",
          (gains["gained_answers"], gains["seeds_with_a_gain"], gains["routes_with_a_gain"]),
          (11, 9, 6))
    claim("simulated power at 25, 20 and 15 points",
          [round(100 * extra_checks["power_of_locked_criterion_by_true_gap"][f"{g}_points"])
           for g in (25, 20, 15)], [93, 74, 46])
    tied = extra_checks["power_with_within_query_correlation"]
    claim("correlated-answer power at 15 and 10 points, and its spread at zero gap",
          (round(100 * tied["15_points"]["power"]), round(100 * tied["10_points"]["power"]),
           tied["0_points"]["mean_sd_of_differences"]), (87, 44, 0.81))
    claim("independent-answer spread of the paired difference",
          (2 * 3 * (51 / 90) * (1 - 51 / 90)) ** 0.5, 1.2)
    claim("sizing effect in points at the observed spread",
          round(100 * 0.55 * primary["sd"] / 3), 15)
    claim("label-interaction lower bound across streams",
          sorted({v[0] for v in
                  extra_checks["bootstrap_interval_by_stream"]["label_interaction"].values()}),
          [-11.67, -11.11])
    usage = RESULT["usage"]
    claim("request hours",
          sum(usage[f"{stage}_seconds"] for stage in ("acquisition", "readout", "label")) / 3600,
          2.8)
    return checked


if __name__ == "__main__":
    print(json.dumps({"manuscript_statements_checked": statements()}, indent=2))
