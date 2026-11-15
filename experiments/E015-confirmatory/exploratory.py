"""Exploratory readings of the E015 traces, written after the locked analysis was archived."""
from collections import Counter
import json
from pathlib import Path

from src.admission_audit import decode_answers, read_calls
from src.confirmatory import MEMORIES, SEEDS, UPDATING, all_cases, study
from src.diverse_paths import DETOUR
from src.path_errors import classify
from src.pilot import oracle_answer
from src.planning import is_correct

ROOT = Path("experiments/E015-confirmatory/results/qwen3-8b")


def main():
    pools = study()
    failures = []
    declared = {stage: Counter() for stage in ("acquisition", "readout", "label")}
    errors = Counter()
    by_memory = {name: {group: Counter() for group in ("path_in_memory", "path_not_in_memory",
                                                       "no_key_detour_example")}
                 for name in MEMORIES}
    mixture = {group: Counter() for group in ("kept", "lost")}
    matched = {group: Counter() for group in ("path_in_memory", "path_not_in_memory")}
    for seed in SEEDS:
        by_id = {case.id: case for case in all_cases(pools[seed])}
        initial, _, _, holdout = pools[seed]
        summary = json.loads((ROOT / str(seed) / "summary.json").read_text())
        for index, row in enumerate(read_calls(ROOT / str(seed))):
            answers, valid = decode_answers(row["response"])
            stage = "acquisition" if row["phase"] == "solve" else row["arm"].split("/")[0]
            if not valid:
                failures.append({"seed": seed, "call": index, "phase": row["phase"],
                                 "arm": row["arm"], "round": row["round"],
                                 "done_reason": row["done_reason"],
                                 "output_tokens": row["output_tokens"]})
            asked = [task["id"] for task in json.loads(row["prompt"])["tasks"]]
            for item in asked:
                family = by_id[item].family
                answer = answers.get(item)
                declared[stage].update({f"{family}_queries": 1,
                                        f"{family}_declared_unreachable":
                                            answer == {"unreachable": True}})
                if stage == "readout" and family == "unreachable":
                    errors[classify(by_id[item].task, answer)] += 1
        contents = {"empty": [], "frozen": list(initial)}
        for arm in UPDATING:
            contents[arm] = [by_id[item] for item in summary["arms"][arm]["final_memory"]]
        for name in MEMORIES:
            paths = [oracle_answer(case) for case in contents[name] if case.family == DETOUR]
            marks = summary["readout"][name]
            for case in holdout:
                if case.family != DETOUR:
                    continue
                group = ("no_key_detour_example" if not paths else
                         "path_in_memory" if any(is_correct(case.task, p) for p in paths)
                         else "path_not_in_memory")
                by_memory[name][group].update(correct=marks[case.id]["correct"], total=1)
                if group in matched:
                    before = summary["readout"]["empty"][case.id]["correct"]
                    after = marks[case.id]["correct"]
                    matched[group].update(answers=1, with_memory=after, empty_memory=before,
                                          gained=after and not before,
                                          lost=before and not after)
                    matched[group][f"query/{seed}/{case.id}"] = 1
                if name == "random_model":
                    mixture["kept" if paths else "lost"].update(
                        correct=marks[case.id]["correct"], total=1)
    tidy = lambda counter: {key: int(value) for key, value in sorted(counter.items())}
    print(json.dumps({
        "format_failures": failures,
        "unreachable_declarations": {stage: tidy(c) for stage, c in declared.items()},
        "first_error_on_unreachable_readout_queries": tidy(errors),
        "key_detour_by_path_availability_and_memory": {
            name: {group: tidy(cell) for group, cell in groups.items() if cell["total"]}
            for name, groups in by_memory.items()},
        "mixture_arm_key_detour_by_retention": {g: tidy(c) for g, c in mixture.items()},
        "path_split_against_empty_memory_on_same_queries": {
            group: {**{key: int(value) for key, value in cell.items()
                       if not key.startswith("query/")},
                    "unique_queries": sum(key.startswith("query/") for key in cell)}
            for group, cell in matched.items()},
    }, indent=1))


if __name__ == "__main__":
    main()
