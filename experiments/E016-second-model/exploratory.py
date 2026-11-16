"""Readings of the E016 traces added after the locked aggregate was archived."""
from collections import Counter
import json
from pathlib import Path

from src.admission_audit import decode_answers, read_calls
from src.confirmatory import MEMORIES, SEEDS, UPDATING, all_cases, study
from src.diverse_paths import DETOUR
from src.pilot import oracle_answer
from src.planning import is_correct

ROOT = Path("experiments/E016-second-model/results/gemma-e4b")


def main():
    pools = study()
    declarations, keys = [], Counter()
    matched = {group: Counter() for group in ("path_in_memory", "path_not_in_memory")}
    for seed in SEEDS:
        by_id = {case.id: case for case in all_cases(pools[seed])}
        initial, _, _, holdout = pools[seed]
        summary = json.loads((ROOT / str(seed) / "summary.json").read_text())
        for row in read_calls(ROOT / str(seed)):
            answers, _ = decode_answers(row["response"])
            asked = json.loads(row["prompt"])["tasks"][0]["id"]
            memory = row["arm"].split("/")[1] if row["phase"] == "evaluation" else row["arm"]
            if asked not in answers:
                keys[(row["phase"], memory, ",".join(sorted(answers)))] += 1
            if {"unreachable": True} in answers.values():
                declarations.append({"seed": seed, "arm": row["arm"],
                                     "family": by_id[asked].family,
                                     "keys": sorted(answers), "response": row["response"]})
        contents = {"frozen": list(initial)}
        for arm in UPDATING:
            contents[arm] = [by_id[item] for item in summary["arms"][arm]["final_memory"]]
        for name in MEMORIES[1:]:
            paths = [oracle_answer(c) for c in contents[name] if c.family == DETOUR]
            for case in holdout:
                if case.family != DETOUR or not paths:
                    continue
                group = ("path_in_memory" if any(is_correct(case.task, p) for p in paths)
                         else "path_not_in_memory")
                before = summary["readout"]["empty"][case.id]["correct"]
                after = summary["readout"][name][case.id]["correct"]
                matched[group].update(answers=1, with_memory=after, empty_memory=before,
                                      gained=after and not before, lost=before and not after)
    print(json.dumps({
        "unreachable_declarations": declarations,
        "responses_without_the_requested_id": [
            {"phase": phase, "memory": memory, "keys": key, "calls": count}
            for (phase, memory, key), count in sorted(keys.items())],
        "path_split_against_empty_memory_on_same_queries": {
            group: {key: int(value) for key, value in cell.items()}
            for group, cell in matched.items()},
    }, indent=1))


if __name__ == "__main__":
    main()
