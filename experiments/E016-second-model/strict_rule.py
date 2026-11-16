"""Where the single-entry rule changed a score, and a strict-rule rerun of the one seed it touched.

Added after the fourth-round review. The rerun of seed 7125 made 81 new Gemma calls with
`single_entry` off, so its acquisition and readout both follow the strict E015 rule.
"""
from collections import Counter
import json
from pathlib import Path

from src.admission_audit import decode_answers, read_calls
from src.confirmatory import MEMORIES, SEEDS, all_cases, replay_seed, study
from src.diverse_paths import DETOUR
from src.planning import is_correct

HERE = Path("experiments/E016-second-model")
ROOT = HERE / "results/gemma-e4b"
STRICT = {"single_solve": True, "labels": False}


def main():
    pools = study()
    rescued, by_seed = [], Counter()
    for seed in SEEDS:
        by_id = {case.id: case for case in all_cases(pools[seed])}
        for row in read_calls(ROOT / str(seed)):
            answers, _ = decode_answers(row["response"])
            asked = json.loads(row["prompt"])["tasks"][0]["id"]
            if asked in answers or len(answers) != 1:
                continue
            answer = next(iter(answers.values()))
            if is_correct(by_id[asked].task, answer):
                memory = row["arm"].split("/")[1] if row["phase"] == "evaluation" else row["arm"]
                rescued.append({"seed": seed, "phase": row["phase"], "memory": memory,
                                "round": row["round"], "task": asked,
                                "family": by_id[asked].family})
                by_seed[(row["phase"], seed)] += 1
    seed = 7125
    locked = json.loads((ROOT / str(seed) / "summary.json").read_text())
    strict, usage = replay_seed(HERE / "sensitivity-strict-rule" / str(seed), seed, pools[seed],
                                **STRICT)
    holdout = pools[seed][-1]

    def score(summary, name, families):
        return sum(summary["readout"][name][case.id]["correct"] for case in holdout
                   if case.family in families)

    tally = Counter((row["phase"], row["memory"], row["family"]) for row in rescued)
    print(json.dumps({
        "correct_answers_scored_only_by_the_single_entry_rule": [
            {"phase": phase, "memory": memory, "family": family, "answers": count}
            for (phase, memory, family), count in sorted(tally.items())],
        "solve_rescues": [row for row in rescued if row["phase"] == "solve"],
        "seeds_with_a_solve_rescue": sorted({s for (phase, s) in by_seed if phase == "solve"}),
        "strict_rerun_of_seed_7125": {
            "calls": usage["calls"],
            "final_memory": {arm: {"locked": locked["arms"][arm]["final_memory"],
                                   "strict": strict["arms"][arm]["final_memory"]}
                             for arm in strict["arms"]},
            "key_detour_correct": {name: {"locked": score(locked, name, (DETOUR,)),
                                          "strict": score(strict, name, (DETOUR,))}
                                   for name in MEMORIES},
            "primary_difference": {
                "locked": score(locked, "frozen", (DETOUR,))
                - score(locked, "random_model", (DETOUR,)),
                "strict": score(strict, "frozen", (DETOUR,))
                - score(strict, "random_model", (DETOUR,))},
            "secondary_difference": {
                "locked": score(locked, "targeted_model", (DETOUR, "unreachable"))
                - score(locked, "rare_only_model", (DETOUR, "unreachable")),
                "strict": score(strict, "targeted_model", (DETOUR, "unreachable"))
                - score(strict, "rare_only_model", (DETOUR, "unreachable"))},
        },
    }, indent=1))


if __name__ == "__main__":
    main()
