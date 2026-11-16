"""Run, replay and report E016: the E015 policies with Gemma 4 E4B as the acquisition model."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

from src.admission_audit import decode_answers, read_calls, require
from src.benchmark import FAMILIES, RARE
from src.confirmatory import (DEV_SEEDS, MEMORIES, SEEDS, UPDATING, all_cases, conformance,
                              contrast, replay_seed, study, trajectory)
from src.diverse_paths import DETOUR
from src.pilot import counts, oracle_answer
from src.planning import is_correct
from src.representation import GemmaBackend, verify_gemma_files

MODE = {"single_solve": True, "labels": False, "single_entry": True}
RUNTIME = "LM Studio"
CALLS = 3 * 4 * 3 + 5 * 9


def run_seed(seed, pools, port, directory, model_dir):
    verify_gemma_files(model_dir)
    directory.mkdir(parents=True)
    with (directory / "calls.jsonl").open("w") as trace:
        backend = GemmaBackend(port, trace)
        summary = trajectory(seed, pools, lambda phase, arm, round_, cases, memory:
                             backend.call(phase, arm, round_, cases, memory, sampling_seed=seed),
                             **MODE)
    summary.update(backend=GemmaBackend.model, digest=None, runtime_version=backend.version)
    (directory / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    raw = directory / "calls.jsonl"
    (directory / "calls.jsonl.gz").write_bytes(gzip.compress(raw.read_bytes(), mtime=0))
    raw.unlink()


def interface(root, seeds):
    """Interface counts only: formats, returned IDs, tokens, seconds. No memory comparison."""
    pools = study()
    usage, returned = Counter(), Counter()
    for seed in seeds:
        summary, seed_usage = replay_seed(root / str(seed), seed, pools[seed], **MODE)
        usage.update(seed_usage)
        for marks in summary["readout"].values():
            returned.update(requested=len(marks),
                            answered=sum(mark["answered"] for mark in marks.values()))
    return {"seeds": list(seeds),
            "usage": {key: (round(value, 1) if key.endswith("seconds") else int(value))
                      for key, value in sorted(usage.items())},
            "readout_answers": dict(returned)}


def report(root, seeds=SEEDS):
    pools = study()
    usage, fifo, answered = Counter(), Counter(), Counter()
    score = {name: {family: [] for family in FAMILIES} for name in MEMORIES}
    present = {name: [] for name in MEMORIES}
    stages = {arm: {field: Counter() for field in ("attempted", "admitted", "evicted")}
              for arm in UPDATING}
    supplements = {arm: Counter() for arm in UPDATING}
    coverage = {group: Counter() for group in ("present", "absent")}
    path_split = {group: Counter() for group in ("path_in_memory", "path_not_in_memory",
                                                 "no_key_detour_example")}
    declared = Counter()
    strict = {name: [] for name in MEMORIES}
    per_seed = {}
    for seed in seeds:
        cases = all_cases(pools[seed])
        initial, _, _, holdout = pools[seed]
        by_id = {case.id: case for case in cases}
        summary, seed_usage = replay_seed(root / str(seed), seed, pools[seed], **MODE)
        require((summary["backend"], summary["runtime_version"])
                == (GemmaBackend.model, RUNTIME), "Unexpected inference provenance")
        require(seed_usage["calls"] == CALLS, f"Unexpected call count in seed {seed}")
        usage.update(seed_usage)
        fifo.update(conformance(summary, cases))
        for row in read_calls(root / str(seed)):
            answers, _ = decode_answers(row["response"])
            asked = json.loads(row["prompt"])["tasks"][0]["id"]
            stage = "acquisition" if row["phase"] == "solve" else "readout"
            declared.update({f"{stage}_answers": 1,
                             f"{stage}_returned_requested_id": asked in answers,
                             f"{stage}_{by_id[asked].family}_tasks": 1,
                             f"{stage}_{by_id[asked].family}_declared_unreachable":
                                 {"unreachable": True} in answers.values()})
        contents = {"empty": [], "frozen": list(initial)}
        for arm in UPDATING:
            record = summary["arms"][arm]
            for row in record["rounds"]:
                supplements[arm][row["supplement"]["family"]] += 1
                for field in stages[arm]:
                    stages[arm][field].update(row[field])
            contents[arm] = [by_id[item] for item in record["final_memory"]]
        per_seed[str(seed)] = {}
        for name in MEMORIES:
            marks = summary["readout"][name]
            correct = Counter(case.family for case in holdout if marks[case.id]["correct"])
            answered.update(answered=sum(mark["answered"] for mark in marks.values()),
                            requested=len(marks))
            held = counts(contents[name])
            strict[name].append(sum(marks[case.id]["correct"] and marks[case.id]["answered"]
                                    for case in holdout if case.family == DETOUR))
            for family in FAMILIES:
                score[name][family].append(correct[family])
            present[name].append(int(held[DETOUR] > 0))
            coverage["present" if held[DETOUR] else "absent"].update(
                memories=1, correct=correct[DETOUR], total=3)
            paths = [oracle_answer(case) for case in contents[name] if case.family == DETOUR]
            for case in holdout:
                if case.family != DETOUR:
                    continue
                group = ("no_key_detour_example" if not paths else
                         "path_in_memory" if any(is_correct(case.task, p) for p in paths)
                         else "path_not_in_memory")
                path_split[group].update(correct=marks[case.id]["correct"], total=1)
            per_seed[str(seed)][name] = {"correct": {f: correct[f] for f in FAMILIES},
                                         "retained": held}

    def paired(first, second, families):
        return [sum(score[first][f][i] - score[second][f][i] for f in families)
                for i in range(len(seeds))]

    tidy = lambda counter: {key: int(value) for key, value in counter.items()}
    return {
        "seeds": list(seeds),
        "calls": usage["calls"],
        "format_failures": usage["format_failures"],
        "answers_returned": tidy(answered),
        "usage": {key: (round(value, 1) if key.endswith("seconds") else int(value))
                  for key, value in sorted(usage.items())},
        "scores": {name: {family: {"correct": sum(values), "total": 3 * len(seeds)}
                          for family, values in families.items()}
                   for name, families in score.items()},
        "seeds_retaining_a_key_detour_example": {n: sum(v) for n, v in present.items()},
        "supplement_families": {arm: tidy(c) for arm, c in supplements.items()},
        "stage_totals": {arm: {field: tidy(c) for field, c in fields.items()}
                         for arm, fields in stages.items()},
        "primary_frozen_minus_mixture_key_detour":
            contrast(paired("frozen", "random_model", (DETOUR,)), 3),
        "secondary_adaptive_minus_balanced_rare":
            contrast(paired("targeted_model", "rare_only_model", RARE), 6),
        "descriptive": {
            "frozen_minus_empty_key_detour": contrast(paired("frozen", "empty", (DETOUR,)), 3),
            "balanced_minus_mixture_key_detour":
                contrast(paired("rare_only_model", "random_model", (DETOUR,)), 3),
            "adaptive_minus_mixture_key_detour":
                contrast(paired("targeted_model", "random_model", (DETOUR,)), 3),
        },
        "primary_under_strict_id_rule": contrast(
            [a - b for a, b in zip(strict["frozen"], strict["random_model"])], 3),
        "key_detour_correct_under_strict_id_rule": {n: sum(v) for n, v in strict.items()},
        "responses": tidy(declared),
        "retained_coverage_split_key_detour": {g: tidy(c) for g, c in coverage.items()},
        "key_detour_by_path_availability": {g: tidy(c) for g, c in path_split.items()},
        "fifo_conformance": {"trajectories": 3 * len(seeds), **tidy(fifo)},
        "per_seed": per_seed,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--lmstudio-port", type=int, default=1234)
    parser.add_argument("--gemma-model-dir", type=Path)
    parser.add_argument("--development", action="store_true")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--interface", action="store_true")
    args = parser.parse_args()
    seeds = DEV_SEEDS if args.development else SEEDS
    if args.interface:
        print(json.dumps(interface(args.output, seeds), indent=2))
        return
    if args.audit:
        print(json.dumps(report(args.output, seeds), indent=2))
        return
    require(args.gemma_model_dir is not None, "--gemma-model-dir is required for a live run")
    pools = study()
    for seed in seeds:
        directory = args.output / str(seed)
        if (directory / "summary.json").exists():
            continue
        if directory.exists():
            index = 1
            while (args.output / f"{seed}.partial-{index}").exists():
                index += 1
            directory.rename(args.output / f"{seed}.partial-{index}")
        run_seed(seed, pools[seed], args.lmstudio_port, directory, args.gemma_model_dir)
        print(f"Seed {seed} complete", flush=True)


if __name__ == "__main__":
    main()
