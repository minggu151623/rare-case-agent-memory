"""Post hoc publication audit: E009 sensitivity, coverage versus readout, manuscript numbers."""
from collections import Counter
import json
from pathlib import Path

from src.admission import SEEDS, study_pools
from src.admission_audit import decode_answers, read_calls
from src.admission_report import report as admission_report, sign_flip_p
from src.benchmark import FAMILIES
from src.matched_labels import report as matched_report
from src.path_errors import classify
from src.pilot import CAPACITY
from src.rare_only import report as rare_report

ROOT = Path("experiments")
E002 = ROOT / "E002-admission/results/qwen3-8b"
E008 = ROOT / "E008-end-to-end/results/qwen3-8b"
E009 = ROOT / "E009-matched-labels/results/qwen3-8b"
E012 = ROOT / "E012-rare-only/results/qwen3-8b"
RARE = ("key_detour", "unreachable")
EMPTY = {"ungated": 0, "key_detour": 0, "unreachable": 0}


def load(path):
    return json.loads((ROOT / path).read_text())


def units():
    """One evaluated memory per seed: retained family counts and original-batch scores."""
    rows = []
    for seed in SEEDS:
        base = json.loads((E002 / str(seed) / "summary.json").read_text())
        rare = json.loads((E012 / str(seed) / "summary.json").read_text())
        adaptive, repeat = base["arms"]["targeted_model"], rare["arms"]["targeted_model"]
        if (adaptive["final"], adaptive["rounds"][-1]["retained"]) != (
                repeat["final"], repeat["rounds"][-1]["retained"]):
            raise ValueError(f"E012 adaptive arm differs from E002 in seed {seed}")
        memories = {arm: (record["rounds"][-1]["retained"], record["final"]["correct"])
                    for arm, record in base["arms"].items()}
        memories["rare_only_model"] = (
            rare["arms"]["rare_only_model"]["rounds"][-1]["retained"],
            rare["arms"]["rare_only_model"]["final"]["correct"],
        )
        memories["frozen"] = (base["initial_memory"], base["controls"]["frozen"]["correct"])
        memories["empty"] = (EMPTY, base["controls"]["empty"]["correct"])
        rows += [{"seed": seed, "memory": name, "retained": retained, "correct": correct}
                 for name, (retained, correct) in memories.items()]
    return rows


def split(rows, family, score=lambda row, family: row["correct"][family]):
    groups = {name: Counter() for name in ("present", "absent")}
    by_memory, by_seed = {}, {}
    for row in rows:
        name = "present" if row["retained"][family] else "absent"
        correct = score(row, family)
        empty = lambda: {"present": Counter(), "absent": Counter()}
        for cell in (groups[name], by_memory.setdefault(row["memory"], empty())[name],
                     by_seed.setdefault(str(row["seed"]), empty())[name]):
            cell.update(units=1, correct=correct, total=3,
                        perfect=correct == 3, zero=correct == 0)
    fields = ("units", "correct", "total", "perfect", "zero")
    tidy = lambda cell: {field: int(cell[field]) for field in fields}
    return {
        "pooled": {name: tidy(cell) for name, cell in groups.items()},
        "by_memory": {memory: {name: tidy(cell) for name, cell in cells.items() if cell["units"]}
                      for memory, cells in by_memory.items()},
        "by_seed": {seed: {name: tidy(cell) for name, cell in cells.items() if cell["units"]}
                    for seed, cells in by_seed.items()},
    }


def coverage():
    rows = units()
    varied = load("E013-diverse-paths/results/qwen3-8b/aggregate.json")["per_seed"]
    frozen_e013 = [row for row in rows
                   if row["memory"] in ("random_model", "targeted_model", "rare_only_model")]
    return {
        "units": len(rows),
        "units_with_correct_unreachable_answers": blanket_responses(rows),
        "original_batch": {family: split(rows, family) for family in RARE},
        "varied_batch_key_detour": split(
            frozen_e013, "key_detour",
            lambda row, family: varied[str(row["seed"])][row["memory"]]["varied"]["correct"][family],
        ),
        "unit_table": [
            {"seed": row["seed"], "memory": row["memory"],
             **{f"{family}_retained": row["retained"][family] for family in RARE},
             **{f"{family}_correct": row["correct"][family] for family in RARE}}
            for row in rows
        ],
    }


def blanket_responses(rows):
    """Key-detour answer classes in units that answered an unreachable query correctly."""
    pools = study_pools()
    found = []
    for row in rows:
        if not row["correct"]["unreachable"]:
            continue
        holdout = pools[row["seed"]][-1]
        call = next(call for call in read_calls(E002 / str(row["seed"]))
                    if (call["phase"], call["arm"]) == ("evaluation", row["memory"]))
        answers, _ = decode_answers(call["response"])
        classes = Counter(classify(case.task, answers.get(case.id))
                          for case in holdout if case.family == "key_detour")
        found.append({"seed": row["seed"], "memory": row["memory"],
                      "unreachable_correct": row["correct"]["unreachable"],
                      "key_detour_answer_classes": dict(classes)})
    return found


def last_focal(labels):
    """Mirror of the Lean definition: one-based index of the last focal entry, else zero."""
    return max((index + 1 for index, focal in enumerate(labels) if focal), default=0)


def conformance():
    """Check the Lean FIFO characterization on every archived update trajectory."""
    pools = study_pools()
    sources = (("E002", E002, ("random_model", "random_oracle", "targeted_model",
                               "targeted_oracle")),
               ("E012", E012, ("rare_only_model",)),
               ("E008", E008, ("random_model", "targeted_model")))
    checks = 0
    table = {}
    for study, root, arms in sources:
        for seed in SEEDS:
            initial, backgrounds, supplements, _ = pools[seed]
            family = {case.id: case.family
                      for pool in (initial, *backgrounds, *supplements) for case in pool}
            calls = read_calls(root / str(seed))
            for arm in arms:
                snapshots = [[entry["id"] for entry in json.loads(call["prompt"])["memory"]]
                             for call in calls if call["arm"] == arm]
                start, middle, final = snapshots
                if len(start) != CAPACITY or start != [case.id for case in initial]:
                    raise ValueError(f"Unexpected initial memory: {study} {seed} {arm}")
                admitted = ([item for item in middle if item not in start]
                            + [item for item in final if item not in middle])
                if final != (start + admitted)[-CAPACITY:]:
                    raise AssertionError(f"Not a FIFO suffix: {study} {seed} {arm}")
                for focal in FAMILIES:
                    labels = [family[item] == focal for item in admitted]
                    position = last_focal([family[item] == focal for item in start])
                    predicted = (position <= len(labels)
                                 and not any(labels[max(0, len(labels) - CAPACITY):]))
                    observed = all(family[item] != focal for item in final)
                    if predicted != observed:
                        raise AssertionError(f"FIFO law violated: {study} {seed} {arm} {focal}")
                    checks += 1
                    cell = table.setdefault(study, {}).setdefault(arm, {}).setdefault(
                        focal, Counter())
                    cell.update(trajectories=1, absent_at_end=observed,
                                absent_without_focal_admission=observed and not any(labels))
    fields = ("trajectories", "absent_at_end", "absent_without_focal_admission")
    return {
        "trajectories": checks // len(FAMILIES),
        "family_trajectory_checks": checks,
        "mismatches": 0,
        "by_study_arm_family": {
            study: {arm: {focal: {field: int(cell[field]) for field in fields}
                          for focal, cell in families.items()}
                    for arm, families in arms.items()}
            for study, arms in table.items()
        },
    }


def manuscript(e009, cover, fifo):
    """Assert the manuscript's numeric statements against archives and replays."""
    checked = []

    def claim(name, actual, expected):
        if isinstance(expected, float):
            agrees = abs(actual - expected) < 0.05
        else:
            agrees = actual == expected
        if not agrees:
            raise AssertionError(f"{name}: archive gives {actual}, manuscript states {expected}")
        checked.append(name)

    def counts(scores, family="key_detour"):
        return scores[family]["correct"]

    e002 = admission_report(E002)
    arms = e002["arms"]
    claim("E002 calls", e002["calls"], 84)
    primary = e002["primary_unreachable_memory_targeted_oracle_minus_model"]
    claim("E002 unreachable-memory differences", primary["per_seed"], [1, 1, 1, 0, 1, 0])
    claim("E002 unreachable-memory mean", primary["mean"], 0.67)
    claim("E002 unreachable-memory sign-flip", primary["exact_sign_flip_p_two_sided"], 0.125)
    rare = e002["primary_rare_accuracy_targeted_model_minus_random_model"]
    claim("E002 rare macro differences", [round(6 * x) for x in rare["per_seed"]],
          [3, 0, 0, 0, 3, 2])
    claim("E002 rare macro mean (points)", 100 * rare["mean"], 22.2)
    claim("E002 rare macro sign-flip", rare["exact_sign_flip_p_two_sided"], 0.25)
    table = {"random_model": (18, 7, 3, 27.8), "targeted_model": (18, 18, 0, 50.0),
             "random_oracle": (18, 8, 0, 22.2), "targeted_oracle": (17, 17, 0, 47.2)}
    for arm, (ungated, detour, unreachable, macro) in table.items():
        correct = arms[arm]["final_correct"]
        claim(f"E002 {arm} family scores",
              (correct["ungated"], correct["key_detour"], correct["unreachable"]),
              (ungated, detour, unreachable))
        claim(f"E002 {arm} rare macro", 100 * arms[arm]["rare_macro_accuracy"], macro)
    stages = {arm: arms[arm]["stage_totals"] for arm in arms}
    claim("E002 unreachable attempts",
          [stages[arm]["attempted"]["unreachable"] for arm in
           ("random_model", "random_oracle", "targeted_model", "targeted_oracle")], [3, 3, 5, 6])
    claim("E002 unreachable model passes",
          sum(stages[arm]["model_passes"]["unreachable"] for arm in arms), 0)
    claim("E002 unreachable admissions",
          [stages[arm]["admitted"]["unreachable"] for arm in
           ("random_model", "random_oracle", "targeted_model", "targeted_oracle")], [0, 1, 0, 4])
    claim("E002 mean final unreachable examples",
          [round(sum(m["unreachable"] for m in arms[arm]["final_memory_by_seed"]) / 6, 2)
           for arm in ("random_model", "random_oracle", "targeted_model", "targeted_oracle")],
          [0.17, 0.33, 0.17, 0.83])
    claim("E002 targeted key-detour attempts and admissions",
          (stages["targeted_model"]["attempted"]["key_detour"],
           stages["targeted_model"]["admitted"]["key_detour"]), (10, 9))
    controls = {name: Counter() for name in ("empty", "frozen")}
    for seed in SEEDS:
        summary = json.loads((E002 / str(seed) / "summary.json").read_text())
        for name in controls:
            controls[name].update(summary["controls"][name]["correct"])
    claim("E002 empty memory scores",
          (controls["empty"]["ungated"], controls["empty"]["key_detour"],
           controls["empty"]["unreachable"]), (15, 7, 0))
    claim("E002 frozen memory scores",
          (controls["frozen"]["ungated"], controls["frozen"]["key_detour"],
           controls["frozen"]["unreachable"]), (18, 16, 0))

    e011 = load("E011-manuscript-audit/results.json")
    supplements = e011["e002_supplement_family_counts"]
    claim("E002 mixture supplement families", supplements["random_model"],
          {"ungated": 9, "key_detour": 2, "unreachable": 1})
    claim("E002 adaptive supplement families", supplements["targeted_model"],
          {"key_detour": 9, "unreachable": 3})
    fixed = e011["generator_aware_fixed_path"]
    claim("E011 fixed path", (fixed["original"]["correct"], fixed["new_motif"]["correct"]), (18, 0))
    subset = e011["qwen_batched_e010_subset_correct_out_of_six"]
    claim("E011 Qwen subset gaps",
          [subset["targeted_model"][c] - subset["random_model"][c]
           for c in ("original", "independent_both", "shared_map")], [3, 0, 3])

    e003 = load("E003-transfer/results/aggregate.json")["scores"]
    for arm, expected in {"random_model": (7, 2, 10), "targeted_model": (18, 1, 9),
                          "targeted_oracle": (17, 0, 9)}.items():
        claim(f"E003 {arm} key detours",
              tuple(counts(e003[arm][c]) for c in ("original", "renamed", "new_motif")), expected)
        claim(f"E003 {arm} unreachable after transfer",
              [counts(e003[arm][c], "unreachable") for c in ("renamed", "new_motif")], [0, 0])

    e004 = load("E004-representation/results/aggregate.json")
    order = ("original", "memory_only", "query_only", "independent_both", "shared_map")
    claim("E004 random key detours",
          [counts(e004["scores"]["random_model"][c]) for c in order], [7, 3, 1, 2, 2])
    claim("E004 targeted key detours",
          [counts(e004["scores"]["targeted_model"][c]) for c in order], [18, 3, 2, 1, 12])
    for arm, expected in {"targeted_model": (-44.4, -50.0, 77.8),
                          "random_model": (-8.3, -19.4, 27.8)}.items():
        effects = e004["key_detour_factorial_effects"][arm]
        for name, value in zip(("memory_main", "query_main", "interaction"), expected):
            claim(f"E004 {arm} {name}", 100 * effects[name]["mean"], value)

    e007 = load("E007-error-audit/results/aggregate.json")
    lost = e007["first_error_counts"]["targeted_model"]["renamed"]["key_detour"]
    claim("E007 targeted first errors",
          (lost["locked_before_key"], lost["nonexistent_edge"], lost["wrong_endpoint"]), (8, 7, 2))
    reuse = e007["literal_path_reuse"]
    claim("E007 losses after a correct original",
          (reuse["targeted_model"]["key_detour"]["failures_after_correct_original_path"],
           reuse["random_model"]["key_detour"]["failures_after_correct_original_path"]), (17, 6))

    e008 = load("E008-end-to-end/results/aggregate.json")["arms"]
    claim("E008 scores", [(e008[arm]["final_correct"]["ungated"],
                           e008[arm]["final_correct"]["key_detour"],
                           e008[arm]["final_correct"]["unreachable"])
                          for arm in ("random_model", "targeted_model")], [(8, 3, 0), (8, 2, 0)])
    claim("E008 targeted key-detour attempts and admissions",
          (e008["targeted_model"]["stage_totals"]["attempted"]["key_detour"],
           e008["targeted_model"]["stage_totals"]["admitted"]["key_detour"]), (12, 2))

    scores = e009["scores"]
    claim("E009 key detours",
          [counts(scores[arm][c]) for c in ("shared", "mixed")
           for arm in ("targeted_model", "random_model")], [20, 10, 10, 7])
    differences = [round(6 * x) for x in e009["key_detour_gap_difference_by_seed"]]
    claim("E009 seed differences", differences, [3, 6, -4, 2, -1, 1])
    claim("E009 mean difference (points)", 100 * e009["key_detour_gap_difference"], 19.4)
    leave_one_out = [100 * (sum(differences) - d) / 30 for d in differences]
    claim("E009 leave-one-seed-out minimum", min(leave_one_out), 3.3)
    claim("E009 leave-one-seed-out maximum", max(leave_one_out), 36.7)
    claim("E009 post hoc sign-flip", sign_flip_p(differences), 0.5)

    complete = load("E006-cross-model/results/completeness.json")
    claim("E006 completeness",
          (complete["calls"], complete["returned_case_ids"], complete["expected_case_ids"]),
          (60, 60, 540))
    e010 = load("E010-single-query/results/aggregate.json")["scores"]
    claim("E010 Gemma correct counts",
          [e010[arm][c]["correct"] for arm in ("random_model", "targeted_model")
           for c in ("original", "independent_both", "shared_map")], [1, 1, 1, 4, 0, 3])

    e012 = rare_report(E012)
    claim("E012 scores", [(e012["scores"][arm]["ungated"]["correct"],
                           e012["scores"][arm]["key_detour"]["correct"],
                           e012["scores"][arm]["unreachable"]["correct"])
                          for arm in ("targeted_model", "rare_only_model")],
          [(18, 18, 0), (18, 16, 0)])
    claim("E012 rare gaps", e012["rare_gaps_out_of_six"], [0, 0, 0, 0, 0, 2])
    claim("E012 rare macro gap (points)", 100 * e012["rare_mean_gap"], 5.6)
    claim("E012 sign-flip", e012["sign_flip_p"], 1.0)
    detours = {arm: e012["coverage"][arm]["key_detour"] for arm in e012["coverage"]}
    claim("E012 key-detour supplements",
          [(detours[arm]["supplement_attempts"], detours[arm]["supplement_admissions"])
           for arm in ("targeted_model", "rare_only_model")], [(9, 8), (6, 6)])
    claim("E012 unreachable supplement admissions",
          [e012["coverage"][arm]["unreachable"]["supplement_admissions"]
           for arm in ("targeted_model", "rare_only_model")], [0, 0])

    e013 = load("E013-diverse-paths/results/qwen3-8b/aggregate.json")
    paths = e013["constant_path_coverage"]
    claim("E013 fixed-path coverage",
          (paths["original"]["best_fixed_path_correct"], paths["varied"]["best_fixed_path_correct"],
           paths["varied"]["optimal_paths"]), (18, 2, 9))
    claim("E013 key detours",
          [(counts(e013["scores"][arm]["original"]), counts(e013["scores"][arm]["varied"]))
           for arm in ("targeted_model", "random_model", "rare_only_model")],
          [(18, 7), (7, 3), (16, 5)])
    mixture = e013["scores"]["random_model"]
    claim("E013 mixture unchanged queries",
          [(mixture[c]["ungated"]["correct"], mixture[c]["unreachable"]["correct"])
           for c in ("original", "varied")], [(18, 3), (17, 1)])
    contrast = e013["contrasts"]["random_model"]
    claim("E013 gap change (points)", 100 * contrast["varied_minus_original"], -38.9)
    claim("E013 gap change sign-flip", contrast["sign_flip_p"], 0.125)

    detour, unreachable = (cover["original_batch"][f]["pooled"] for f in RARE)
    claim("E014 key-detour readout by retained coverage",
          [(detour[g]["correct"], detour[g]["total"]) for g in ("present", "absent")],
          [(80, 87), (9, 39)])
    claim("E014 unreachable readout by retained coverage",
          [(unreachable[g]["correct"], unreachable[g]["total"]) for g in ("present", "absent")],
          [(3, 51), (0, 75)])
    varied = cover["varied_batch_key_detour"]["pooled"]
    claim("E014 varied-batch key-detour readout by retained coverage",
          [(varied[g]["correct"], varied[g]["total"]) for g in ("present", "absent")],
          [(15, 42), (0, 12)])
    seeds = cover["original_batch"]["key_detour"]["by_seed"].values()
    claim("E014 seeds with higher key-detour accuracy when the example is retained",
          sum(s["present"]["correct"] * s["absent"]["total"]
              > s["absent"]["correct"] * s["present"]["total"] for s in seeds), 5)
    detour_units = cover["original_batch"]["key_detour"]["pooled"]
    claim("E014 key-detour units with a perfect or zero score",
          (detour_units["present"]["perfect"], detour_units["present"]["units"],
           detour_units["absent"]["zero"], detour_units["absent"]["units"]), (25, 29, 8, 13))
    mixture = cover["original_batch"]["key_detour"]["by_memory"]["random_model"]
    claim("E014 mixture arm by retained key-detour example",
          [(mixture[g]["units"], mixture[g]["correct"], mixture[g]["total"])
           for g in ("present", "absent")], [(2, 6, 6), (4, 1, 12)])
    blanket = cover["units_with_correct_unreachable_answers"]
    claim("E014 units with a correct unreachable answer",
          [(unit["seed"], unit["memory"], unit["key_detour_answer_classes"])
           for unit in blanket], [(6204, "random_model", {"false_unreachable": 3})])
    losses = [cell for arms in fifo["by_study_arm_family"].values()
              for families in arms.values() for cell in families.values()]
    claim("E014 FIFO conformance",
          (fifo["trajectories"], fifo["family_trajectory_checks"], fifo["mismatches"]),
          (42, 126, 0))
    claim("E014 family losses and losses without replenishment",
          (sum(cell["absent_at_end"] for cell in losses),
           sum(cell["absent_without_focal_admission"] for cell in losses)), (32, 32))
    return checked


def audit():
    e009 = matched_report(E002, E009)
    differences = [round(6 * x) for x in e009["key_detour_gap_difference_by_seed"]]
    cover, fifo = coverage(), conformance()
    return {
        "e009_post_hoc_sensitivity": {
            "seed_differences_out_of_six": differences,
            "mean_percentage_points": round(100 * sum(differences) / 36, 3),
            "sign_assignments": 2 ** len(differences),
            "exact_sign_flip_p_two_sided": sign_flip_p(differences),
        },
        "coverage_and_readout": cover,
        "fifo_conformance": fifo,
        "manuscript_statements_checked": manuscript(e009, cover, fifo),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
