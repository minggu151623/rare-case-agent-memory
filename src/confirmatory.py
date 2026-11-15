"""Run, replay and report the E015 confirmatory experiment."""
import argparse
from collections import Counter
import gzip
from itertools import permutations, product
import json
from pathlib import Path
from random import Random

from src.admission import study_pools
from src.admission_audit import decode_answers, read_calls, require
from src.benchmark import (Case, FAMILIES, RARE, REFERENCE_WEIGHTS, generate, make_pools,
                           structural_key)
from src.diverse_paths import DETOUR, FIXED_PATHS, batches, detour
from src.matched_labels import maps_for_seed
from src.pilot import Backend, CAPACITY, DIGEST, MODEL, counts, oracle_answer
from src.planning import is_correct
from src.representation import rename_memory
from src.transfer import flatten, inputs, rename_with_labels

DEV_SEEDS = (7001, 7002)
SEEDS = tuple(range(7101, 7131))
ROUNDS = 4
RUNTIME = "0.40.16"
UPDATING = ("random_model", "rare_only_model", "targeted_model")
MEMORIES = ("empty", "frozen", *UPDATING)
CONDITIONS = ("shared", "mixed")
PAIRS = tuple(product("DEF", repeat=2))
UNREACHABLE = "unreachable"


def prior_keys():
    """Structural keys of every graph used in E001 through E013."""
    earlier = study_pools()
    cases = flatten(make_pools(4101, 2))
    cases += [case for pools in earlier.values() for case in flatten(pools)]
    cases += [case for _, _, fresh in inputs() for case in fresh]
    cases += [case for _, holdouts in batches(earlier) for case in holdouts["varied"]]
    return {structural_key(case.task) for case in cases}


def holdout_pairs(seeds, salt):
    """One return route and two through routes per seed, balanced over blocks of three."""
    rng = Random(salt)
    schedule = {}
    for offset in range(0, len(seeds), 3):
        returns = rng.sample([(x, x) for x in "DEF"], 3)
        through = rng.sample(list(permutations("DEF", 2)), 6)
        for index, seed in enumerate(seeds[offset:offset + 3]):
            pairs = [returns[index], *through[2 * index:2 * index + 2]]
            rng.shuffle(pairs)
            schedule[seed] = pairs
    return schedule


def study():
    """Task pools for the development and confirmatory seeds, deduplicated globally."""
    seen = prior_keys()
    pools = {}
    for seeds, salt in ((DEV_SEEDS, 714000), (SEEDS, 715000)):
        schedule = holdout_pairs(seeds, salt)
        for seed in seeds:
            rng = Random(seed)

            def task_for(family, pair):
                if family == DETOUR:
                    return detour(*(pair or rng.choice(PAIRS)), rng, seen)
                for _ in range(20000):
                    task = generate(family, rng)
                    key = structural_key(task)
                    if key not in seen:
                        seen.add(key)
                        return task
                raise RuntimeError(f"Exhausted unique {family} tasks for {seed}")

            def pool(prefix, families, pairs=()):
                routes = iter(pairs)
                tasks = [(family, task_for(family, next(routes, None) if family == DETOUR
                                           else None)) for family in families]
                rng.shuffle(tasks)
                return [Case(f"{prefix}{index:02d}", family, task)
                        for index, (family, task) in enumerate(tasks)]

            initial = pool("i", (FAMILIES[0],) * 4 + RARE)
            backgrounds = [pool(f"b{r}", rng.choices(FAMILIES, weights=REFERENCE_WEIGHTS, k=2))
                           for r in range(ROUNDS)]
            supplements = [pool(f"s{r}", FAMILIES) for r in range(ROUNDS)]
            holdout = pool("h", (FAMILIES[0],) * 3 + (DETOUR,) * 3 + (UNREACHABLE,) * 3,
                           schedule[seed])
            pools[seed] = initial, backgrounds, supplements, holdout
    return pools


def all_cases(pools):
    initial, backgrounds, supplements, holdout = pools
    return initial + holdout + [case for pool in backgrounds + supplements for case in pool]


def plan(seed):
    rng = Random(seed + 715100)
    return {
        "random_model": rng.choices(FAMILIES, weights=REFERENCE_WEIGHTS, k=ROUNDS),
        "rare_only_model": rng.sample(RARE * (ROUNDS // 2), ROUNDS),
        "tie_order": rng.sample(RARE, len(RARE)),
        "arm_order": rng.sample(UPDATING, len(UPDATING)),
        "readout_order": rng.sample(MEMORIES, len(MEMORIES)),
        "label_order": rng.sample(list(product(UPDATING, CONDITIONS, (0, 1))), 12),
    }


def rendered(case, memory, maps, condition, repetition):
    """Relabel one query and its memory. Mixed prompts alternate the two maps by position."""
    def labels_at(index):
        return maps[(repetition + (index % 2 if condition == "mixed" else 0)) % 2]

    position = {example.id: index for index, (example, _) in enumerate(memory)}
    examples = rename_memory(memory, lambda example: (
        rename_with_labels(example, labels_at(position[example.id])),
        labels_at(position[example.id]),
    ))
    return rename_with_labels(case, maps[repetition]), examples


def trajectory(seed, pools, ask):
    """All calls of one seed. `ask` is a live backend call or a replay of a stored call."""
    initial, backgrounds, supplements, holdout = pools
    schedule = plan(seed)
    start = [(case, oracle_answer(case)) for case in initial]
    memories = {"empty": [], "frozen": start}
    arms = {}
    for arm in schedule["arm_order"]:
        memory, records = list(start), []
        for index in range(ROUNDS):
            if arm == "targeted_model":
                held = counts(case for case, _ in memory)
                family = min(schedule["tie_order"], key=held.__getitem__)
            else:
                family = schedule[arm][index]
            supplement = next(case for case in supplements[index] if case.family == family)
            candidates = [*backgrounds[index], supplement]
            answers = ask("solve", arm, index + 1, candidates, memory)
            admitted = [(case, answers[case.id]) for case in candidates
                        if is_correct(case.task, answers.get(case.id))]
            combined = memory + admitted
            memory = combined[-CAPACITY:]
            records.append({
                "round": index + 1,
                "supplement": {"id": supplement.id, "family": family},
                "attempted": counts(candidates),
                "admitted": counts(case for case, _ in admitted),
                "admitted_ids": [case.id for case, _ in admitted],
                "evicted": counts(case for case, _ in combined[:-CAPACITY]),
                "retained": counts(case for case, _ in memory),
            })
        arms[arm] = {"rounds": records, "final_memory": [case.id for case, _ in memory]}
        memories[arm] = memory

    readout = {}
    for name in schedule["readout_order"]:
        readout[name] = {}
        for case in holdout:
            answers = ask("evaluation", f"readout/{name}/{case.id}", ROUNDS, [case],
                          memories[name])
            readout[name][case.id] = {"answered": case.id in answers,
                                      "correct": is_correct(case.task, answers.get(case.id))}

    maps = maps_for_seed(seed)
    label = {name: {condition: {"0": {}, "1": {}} for condition in CONDITIONS}
             for name in UPDATING}
    for name, condition, repetition in schedule["label_order"]:
        for case in holdout:
            if case.family != DETOUR:
                continue
            query, examples = rendered(case, memories[name], maps, condition, repetition)
            answers = ask("evaluation", f"label/{name}/{condition}/{repetition}/{case.id}",
                          ROUNDS, [query], examples)
            label[name][condition][str(repetition)][case.id] = is_correct(
                query.task, answers.get(case.id))
    return json.loads(json.dumps({
        "seed": seed, "initial_memory": counts(initial), "plan": schedule,
        "arms": arms, "readout": readout, "label": label,
    }))


def run_seed(seed, pools, port, directory):
    directory.mkdir(parents=True)
    with (directory / "calls.jsonl").open("w") as trace:
        backend = Backend(port, trace)
        if port is not None:
            require(backend.version == RUNTIME, "Wrong Ollama runtime")
        summary = trajectory(seed, pools, lambda phase, arm, round_, cases, memory:
                             backend.call(phase, arm, round_, cases, memory, sampling_seed=seed))
    summary.update(backend=MODEL if port is not None else "fixture",
                   digest=DIGEST if port is not None else None,
                   runtime_version=backend.version)
    (directory / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    raw = directory / "calls.jsonl"
    (directory / "calls.jsonl.gz").write_bytes(gzip.compress(raw.read_bytes(), mtime=0))
    raw.unlink()


def replay_seed(directory, seed, pools):
    """Recompute every prompt, admission and score from the stored responses."""
    rows = iter(read_calls(directory))
    usage = Counter()

    def ask(phase, arm, round_, cases, memory):
        row = next(rows)
        require((row["phase"], row["arm"], row["round"]) == (phase, arm, round_),
                f"Call out of order in seed {seed}: {row['arm']}")
        expected = {
            "memory": [{**case.prompt_record(), "solution": answer} for case, answer in memory],
            "tasks": [case.prompt_record() for case in cases],
        }
        require(json.loads(row["prompt"]) == json.loads(json.dumps(expected)),
                f"Prompt mismatch in seed {seed}: {arm}")
        if row["output_tokens"] is not None:
            require(row["output_tokens"] <= 384
                    and row["prompt_tokens"] + row["output_tokens"] <= 4096,
                    "Token cap exceeded")
        answers, valid = decode_answers(row["response"])
        require(valid == row["valid_format"], "Format mismatch")
        stage = "acquisition" if phase == "solve" else arm.split("/")[0]
        usage.update({"calls": 1, "format_failures": int(not valid),
                      f"{stage}_calls": 1,
                      f"{stage}_prompt_tokens": row["prompt_tokens"] or 0,
                      f"{stage}_output_tokens": row["output_tokens"] or 0,
                      f"{stage}_seconds": row.get("seconds", 0)})
        return answers

    replayed = trajectory(seed, pools, ask)
    require(next(rows, None) is None, f"Unused calls in seed {seed}")
    stored = json.loads((directory / "summary.json").read_text())
    require({key: stored.get(key) for key in replayed} == replayed,
            f"Summary mismatch in seed {seed}")
    return stored, usage


def exact_sign_flip(differences):
    """Exact two-sided sign-flip value for integer paired differences, by convolution."""
    observed = abs(sum(differences))
    sums = Counter({0: 1})
    for delta in differences:
        following = Counter()
        for total, ways in sums.items():
            following[total + delta] += ways
            following[total - delta] += ways
        sums = following
    extreme = sum(ways for total, ways in sums.items() if abs(total) >= observed)
    return extreme / 2 ** len(differences)


def contrast(differences, denominator):
    count = len(differences)
    mean = sum(differences) / count
    spread = (sum((d - mean) ** 2 for d in differences) / (count - 1)) ** 0.5
    rng = Random(715200)
    means = sorted(sum(rng.choices(differences, k=count)) / count for _ in range(10000))
    return {
        "per_seed": differences,
        "mean": round(mean, 4),
        "sd": round(spread, 4),
        "mean_percentage_points": round(100 * mean / denominator, 2),
        "bootstrap_95_percentage_points": [round(100 * means[249] / denominator, 2),
                                           round(100 * means[9749] / denominator, 2)],
        "positive_zero_negative": [sum(d > 0 for d in differences),
                                   sum(d == 0 for d in differences),
                                   sum(d < 0 for d in differences)],
        "exact_sign_flip_p_two_sided": exact_sign_flip(differences),
    }


def last_focal(labels):
    return max((index + 1 for index, focal in enumerate(labels) if focal), default=0)


def conformance(summary, cases):
    """Check the Lean FIFO characterization on the three update trajectories of a seed."""
    start = [case.id for case in cases if case.id.startswith("i")]
    start.sort()
    checks = Counter()
    for arm, record in summary["arms"].items():
        admitted = [item for row in record["rounds"] for item in row["admitted_ids"]]
        final = record["final_memory"]
        family = {case.id: case.family for case in cases}
        require(final == (start + admitted)[-CAPACITY:], f"Not a FIFO suffix: {arm}")
        for focal in FAMILIES:
            labels = [family[item] == focal for item in admitted]
            position = last_focal([family[item] == focal for item in start])
            predicted = position <= len(labels) and not any(labels[-CAPACITY:])
            observed = all(family[item] != focal for item in final)
            require(predicted == observed, f"FIFO law violated: {arm} {focal}")
            checks.update(checks=1)
            if focal in RARE:
                checks.update({"rare_losses": observed,
                               "rare_losses_without_admission": observed and not any(labels)})
    return checks


def report(root, seeds=SEEDS):
    pools = study()
    usage, fifo = Counter(), Counter()
    seeds_table = {}
    score = {name: {family: [] for family in FAMILIES} for name in MEMORIES}
    answered = Counter()
    present = {name: {family: [] for family in RARE} for name in MEMORIES}
    label = {name: {condition: [] for condition in CONDITIONS} for name in UPDATING}
    stages = {arm: {field: Counter() for field in ("attempted", "admitted", "evicted")}
              for arm in UPDATING}
    supplements = {arm: Counter() for arm in UPDATING}
    coverage = {family: {group: Counter() for group in ("present", "absent")} for family in RARE}
    path_split = {group: Counter() for group in ("path_in_memory", "path_not_in_memory",
                                                 "no_key_detour_example")}
    holdout_detours = []
    exposures = 0
    for seed in seeds:
        cases = all_cases(pools[seed])
        initial, _, _, holdout = pools[seed]
        by_id = {case.id: case for case in cases}
        summary, seed_usage = replay_seed(root / str(seed), seed, pools[seed])
        require((summary["backend"], summary["digest"], summary["runtime_version"])
                == (MODEL, DIGEST, RUNTIME), "Unexpected inference provenance")
        usage.update(seed_usage)
        fifo.update(conformance(summary, cases))
        holdout_detours += [case for case in holdout if case.family == DETOUR]
        contents = {"empty": [], "frozen": [(case, oracle_answer(case)) for case in initial]}
        for arm in UPDATING:
            record = summary["arms"][arm]
            for row in record["rounds"]:
                supplements[arm][row["supplement"]["family"]] += 1
                for field in stages[arm]:
                    stages[arm][field].update(row[field])
            contents[arm] = [(by_id[item], None) for item in record["final_memory"]]
        row_scores = {}
        for name in MEMORIES:
            marks = summary["readout"][name]
            correct = Counter(case.family for case in holdout if marks[case.id]["correct"])
            answered.update(answered=sum(mark["answered"] for mark in marks.values()),
                            requested=len(marks))
            held = counts(case for case, _ in contents[name])
            row_scores[name] = {family: correct[family] for family in FAMILIES}
            for family in FAMILIES:
                score[name][family].append(correct[family])
            for family in RARE:
                present[name][family].append(int(held[family] > 0))
                coverage[family]["present" if held[family] else "absent"].update(
                    memories=1, correct=correct[family], total=3,
                    perfect=correct[family] == 3, zero=correct[family] == 0)
            paths = [oracle_answer(case) for case, _ in contents[name] if case.family == DETOUR]
            for case in holdout:
                if case.family != DETOUR:
                    continue
                if not paths:
                    group = "no_key_detour_example"
                elif any(is_correct(case.task, path) for path in paths):
                    group = "path_in_memory"
                else:
                    group = "path_not_in_memory"
                path_split[group].update(correct=marks[case.id]["correct"], total=1)
        maps = maps_for_seed(seed)
        for name in UPDATING:
            memory = [(by_id[item], oracle_answer(by_id[item]))
                      for item in summary["arms"][name]["final_memory"]]
            shown = {condition: Counter() for condition in CONDITIONS}
            for condition, repetition in product(CONDITIONS, (0, 1)):
                for case in holdout:
                    if case.family != DETOUR:
                        continue
                    query, examples = rendered(case, memory, maps, condition, repetition)
                    shown[condition].update(
                        [(query.id, query.task), *((ex.id, ex.task) for ex, _ in examples)])
            require(shown["shared"] == shown["mixed"], f"Unmatched exposures: {seed} {name}")
            exposures += 1
            for condition in CONDITIONS:
                label[name][condition].append(sum(
                    correct for marks in summary["label"][name][condition].values()
                    for correct in marks.values()))
        seeds_table[str(seed)] = {
            "readout_correct": row_scores,
            "retained": {name: counts(case for case, _ in contents[name]) for name in MEMORIES},
            "label_key_detour_correct_out_of_six": {
                name: {condition: label[name][condition][-1] for condition in CONDITIONS}
                for name in UPDATING},
        }

    def paired(first, second, families):
        return [sum(score[first][f][i] - score[second][f][i] for f in families)
                for i in range(len(seeds))]

    def label_gap(first, second):
        return [(label[first]["shared"][i] - label[second]["shared"][i])
                - (label[first]["mixed"][i] - label[second]["mixed"][i])
                for i in range(len(seeds))]

    primary = contrast(paired("frozen", "random_model", (DETOUR,)), 3)
    adaptation = contrast(paired("targeted_model", "rare_only_model", RARE), 6)
    labels = contrast(label_gap("targeted_model", "rare_only_model"), 6)
    raw = sorted([("adaptation", adaptation), ("labels", labels)],
                 key=lambda item: item[1]["exact_sign_flip_p_two_sided"])
    smaller = min(1.0, 2 * raw[0][1]["exact_sign_flip_p_two_sided"])
    raw[0][1]["holm_adjusted_p"] = smaller
    raw[1][1]["holm_adjusted_p"] = max(smaller, raw[1][1]["exact_sign_flip_p_two_sided"])
    paths = Counter(tuple(path) for path in FIXED_PATHS for case in holdout_detours
                    if is_correct(case.task, {"path": path}))
    tidy = lambda counter: {key: int(value) for key, value in counter.items()}
    return {
        "seeds": list(seeds),
        "calls": usage["calls"],
        "format_failures": usage["format_failures"],
        "answers_returned": tidy(answered),
        "usage": {key: (round(value, 1) if key.endswith("seconds") else int(value))
                  for key, value in sorted(usage.items())},
        "holdout_constant_path": {"key_detour_queries": len(holdout_detours),
                                  "optimal_paths": len(paths),
                                  "best_fixed_path_correct": max(paths.values())},
        "scores": {name: {family: {"correct": sum(values), "total": 3 * len(seeds)}
                          for family, values in families.items()}
                   for name, families in score.items()},
        "seeds_retaining_an_example": {
            name: {family: sum(values) for family, values in families.items()}
            for name, families in present.items()},
        "supplement_families": {arm: tidy(c) for arm, c in supplements.items()},
        "stage_totals": {arm: {field: tidy(c) for field, c in fields.items()}
                         for arm, fields in stages.items()},
        "primary_frozen_minus_mixture_key_detour": primary,
        "secondary_adaptive_minus_balanced_rare": adaptation,
        "secondary_label_interaction_adaptive_minus_balanced": labels,
        "descriptive": {
            "balanced_minus_mixture_key_detour":
                contrast(paired("rare_only_model", "random_model", (DETOUR,)), 3),
            "adaptive_minus_mixture_key_detour":
                contrast(paired("targeted_model", "random_model", (DETOUR,)), 3),
            "frozen_minus_empty_key_detour": contrast(paired("frozen", "empty", (DETOUR,)), 3),
            "label_interaction_adaptive_minus_mixture":
                contrast(label_gap("targeted_model", "random_model"), 6),
            "shared_minus_mixed_key_detour": {
                name: contrast([s - m for s, m in zip(label[name]["shared"],
                                                      label[name]["mixed"])], 6)
                for name in UPDATING},
            "label_key_detour_correct": {
                name: {condition: {"correct": sum(values), "total": 6 * len(seeds)}
                       for condition, values in conditions.items()}
                for name, conditions in label.items()},
        },
        "retained_coverage_split": {family: {group: tidy(cell) for group, cell in groups.items()}
                                    for family, groups in coverage.items()},
        "key_detour_by_path_availability": {group: tidy(cell)
                                            for group, cell in path_split.items()},
        "fifo_conformance": {"trajectories": 3 * len(seeds), **tidy(fifo)},
        "matched_exposure_checks": exposures,
        "per_seed": seeds_table,
    }


def preflight():
    """CPU checks that must pass before any model call."""
    pools = study()
    earlier = prior_keys()
    keys = Counter()
    for seed, seed_pools in pools.items():
        for case in all_cases(seed_pools):
            keys[structural_key(case.task)] += 1
    require(max(keys.values()) == 1, "Duplicate graph within E015")
    require(not earlier.intersection(keys), "Graph reused from E001 through E013")
    holdout = [case for seed in SEEDS for case in pools[seed][-1] if case.family == DETOUR]
    acquisition = [case for seed in SEEDS for case in all_cases(pools[seed])
                   if case.family == DETOUR and not case.id.startswith("h")]

    def best(cases):
        tally = Counter(tuple(path) for path in FIXED_PATHS for case in cases
                        if is_correct(case.task, {"path": path}))
        return {"queries": len(cases), "optimal_paths": len(tally),
                "best_fixed_path_correct": max(tally.values())}

    require(best(holdout) == {"queries": 90, "optimal_paths": 9, "best_fixed_path_correct": 10},
            "Holdout routes are not balanced")
    return {"graphs": sum(keys.values()), "duplicates": 0, "reused_from_earlier": 0,
            "holdout_key_detours": best(holdout), "acquisition_key_detours": best(acquisition)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--ollama-port", type=int)
    parser.add_argument("--development", action="store_true", help="Use the two development seeds.")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    seeds = DEV_SEEDS if args.development else SEEDS
    if args.preflight:
        print(json.dumps(preflight(), indent=2))
        return
    if args.audit:
        print(json.dumps(report(args.output, seeds), indent=2))
        return
    preflight()
    pools = study()
    for seed in seeds:
        directory = args.output / str(seed)
        if directory.exists() and not (directory / "summary.json").exists():
            attempt = 1
            while (args.output / f"{seed}.partial-{attempt}").exists():
                attempt += 1
            directory.rename(args.output / f"{seed}.partial-{attempt}")
        if not directory.exists():
            run_seed(seed, pools[seed], args.ollama_port, directory)
        replay_seed(directory, seed, pools[seed])
        print(f"Seed {seed} complete", flush=True)


if __name__ == "__main__":
    main()
