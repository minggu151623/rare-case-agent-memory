"""Assert the manuscript's E016 statements against the archived aggregate and traces."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = json.loads((HERE / "results/gemma-e4b/aggregate.json").read_text())
EXTRA = json.loads((HERE / "exploratory.json").read_text())
E015 = json.loads((HERE.parent / "E015-confirmatory/results/qwen3-8b/aggregate.json").read_text())
E014 = json.loads((HERE.parent / "E014-publication-audit/results.json").read_text())


def statements():
    checked = []

    def claim(name, actual, expected):
        agrees = (abs(actual - expected) < 0.05 if isinstance(expected, float)
                  else actual == expected)
        if not agrees:
            raise AssertionError(f"{name}: archive gives {actual}, manuscript states {expected}")
        checked.append(name)

    def numbers(cell):
        return (round(cell["mean_percentage_points"], 1),
                *[round(x, 1) for x in cell["bootstrap_95_percentage_points"]],
                round(cell["exact_sign_flip_p_two_sided"], 2))

    scores = {name: tuple(row[f]["correct"] for f in ("ungated", "key_detour", "unreachable"))
              for name, row in RESULT["scores"].items()}
    primary = RESULT["primary_frozen_minus_mixture_key_detour"]
    rare = RESULT["secondary_adaptive_minus_balanced_rare"]
    extra, stages, said = RESULT["descriptive"], RESULT["stage_totals"], RESULT["responses"]
    split, paths = RESULT["retained_coverage_split_key_detour"], RESULT["key_detour_by_path_availability"]
    fifo = RESULT["fifo_conformance"]
    same = EXTRA["path_split_against_empty_memory_on_same_queries"]["path_in_memory"]
    usage = RESULT["usage"]

    claim("seeds, calls, format failures",
          (len(RESULT["seeds"]), RESULT["calls"], RESULT["format_failures"]), (30, 2430, 0))
    claim("request hours", (usage["acquisition_seconds"] + usage["readout_seconds"]) / 3600, 1.2)
    claim("family scores", scores,
          {"empty": (86, 48, 0), "frozen": (87, 47, 0), "random_model": (87, 55, 0),
           "rare_only_model": (88, 49, 0), "targeted_model": (88, 52, 0)})
    claim("Qwen3 key-detour column",
          [E015["scores"][n]["key_detour"]["correct"] for n in scores], [53, 55, 51, 59, 56])
    claim("seeds retaining a key-detour example", RESULT["seeds_retaining_a_key_detour_example"],
          {"empty": 0, "frozen": 30, "random_model": 6, "rare_only_model": 29,
           "targeted_model": 21})
    claim("primary sign counts", primary["positive_zero_negative"], [5, 15, 10])
    claim("primary mean, interval, sign-flip", numbers(primary), (-8.9, -21.1, 3.3, 0.24))
    claim("primary criterion not met",
          primary["mean"] > 0 and primary["exact_sign_flip_p_two_sided"] <= 0.05, False)
    claim("primary identical under the strict rule",
          RESULT["primary_under_strict_id_rule"]["per_seed"] == primary["per_seed"], True)
    claim("frozen minus empty key-detour answers", scores["frozen"][1] - scores["empty"][1], -1)
    claim("secondary mean, interval, sign-flip", numbers(rare), (1.7, -0.6, 3.9, 0.38))
    claim("secondary in key-detour points, both models",
          (round(100 * (scores["targeted_model"][1] - scores["rare_only_model"][1]) / 90, 1),
           round(100 * (56 - 59) / 90, 1)), (3.3, -3.3))
    claim("unreachable attempts and admissions",
          (sum(s["attempted"]["unreachable"] for s in stages.values()),
           sum(s["admitted"]["unreachable"] for s in stages.values())), (210, 0))
    claim("adaptive supplements on unreachable tasks",
          (RESULT["supplement_families"]["targeted_model"]["unreachable"],
           sum(RESULT["supplement_families"]["targeted_model"].values())), (86, 120))
    claim("rare-enriched minus mixture",
          (numbers(extra["balanced_minus_mixture_key_detour"])[0],
           numbers(extra["adaptive_minus_mixture_key_detour"])[0]), (-6.7, -3.3))
    claim("coverage split",
          [(split[g]["correct"], split[g]["total"]) for g in ("present", "absent")],
          [(140, 258), (111, 192)])
    claim("path split and same-query control",
          (paths["path_in_memory"]["correct"], paths["path_in_memory"]["total"],
           same["empty_memory"], same["answers"]), (25, 36, 21, 36))
    claim("matched gain smaller than with Qwen3",
          same["with_memory"] - same["empty_memory"] < 29 - 20, True)
    claim("requested IDs returned in readout",
          (said["readout_returned_requested_id"], said["readout_answers"]), (1176, 1350))
    claim("empty-memory placeholder responses among those without the requested ID",
          (sum(r["calls"] for r in EXTRA["responses_without_the_requested_id"]
               if r["phase"] == "evaluation" and r["memory"] == "empty" and r["keys"] == "id"),
           said["readout_answers"] - said["readout_returned_requested_id"]), (169, 174))
    claim("empty memory under the strict rule",
          RESULT["key_detour_correct_under_strict_id_rule"]["empty"], 4)
    claim("unreachable tasks asked and declarations of an asked task",
          (said["acquisition_unreachable_tasks"] + said["readout_unreachable_tasks"],
           sum(d["keys"].count(d["arm"].split("/")[-1]) and
               json.loads(d["response"])["answers"].get(d["arm"].split("/")[-1])
               == {"unreachable": True} for d in EXTRA["unreachable_declarations"]),
           len(EXTRA["unreachable_declarations"])), (660, 0, 2))
    claim("FIFO conformance", (fifo["trajectories"], fifo["checks"]), (90, 270))
    claim("trajectories audited in total",
          fifo["trajectories"] + E015["fifo_conformance"]["trajectories"]
          + E014["fifo_conformance"]["trajectories"], 222)
    return checked


if __name__ == "__main__":
    print(json.dumps({"manuscript_statements_checked": statements()}, indent=2))
