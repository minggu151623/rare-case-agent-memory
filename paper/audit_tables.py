"""Render the summary, coverage and confirmatory tables from the archived aggregates."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E013 = ROOT / "experiments/E013-diverse-paths/results/qwen3-8b/aggregate.json"
E014 = ROOT / "experiments/E014-publication-audit/results.json"
E015 = ROOT / "experiments/E015-confirmatory/results/qwen3-8b/aggregate.json"
E016 = ROOT / "experiments/E016-second-model/results/gemma-e4b/aggregate.json"
MEMORIES = (
    ("empty", "Empty", "--"),
    ("frozen", "Frozen initial memory", "--"),
    ("random_model", "Reference-mixture updates", "3/12"),
    ("rare_only_model", "Balanced rare-only updates", "12/12"),
    ("targeted_model", "Adaptive updates", "12/12"),
)


def render_summary(varied, audit):
    cells = audit["coverage_and_readout"]["original_batch"]["key_detour"]["by_memory"]
    print(r"""\begin{table}[t]
\centering
\caption{Held-out key-detour accuracy by evaluated memory, pooled over six
paired seeds with three queries each. Rare supplements counts the
supplement slots spent on the two rare families. Retained counts the seeds
whose evaluated memory still holds a key-detour example. The varied-path
holdout was evaluated for the three updated memories only. The last row
scores the single best fixed answer path with no model.}
\label{tab:summary}
\begin{tabular}{lrrrr}
\toprule
Evaluated memory & Rare supplements & Retained & Original & Varied paths \\
\midrule""")
    for key, label, budget in MEMORIES:
        groups = cells[key]
        present = groups.get("present", {"units": 0, "correct": 0})
        absent = groups.get("absent", {"units": 0, "correct": 0})
        units = present["units"] + absent["units"]
        correct = present["correct"] + absent["correct"]
        scores = varied["scores"].get(key)
        after = (f"{scores['varied']['key_detour']['correct']}/"
                 f"{scores['varied']['key_detour']['total']}") if scores else "--"
        print(f"{label} & {budget} & {present['units']}/{units} & {correct}/{3 * units} & {after} \\\\")
    paths = varied["constant_path_coverage"]
    print(r"\addlinespace")
    print("Best fixed path, no model & -- & -- & "
          f"{paths['original']['best_fixed_path_correct']}/{paths['original']['total']} & "
          f"{paths['varied']['best_fixed_path_correct']}/{paths['varied']['total']} \\\\")
    print(r"""\bottomrule
\end{tabular}
\end{table}""")


def render_coverage(audit):
    batch = audit["coverage_and_readout"]["original_batch"]
    print(r"""\begin{table}[H]
\centering
\caption{Post hoc split of the 42 evaluated memories (seven per seed) by
whether the memory still holds an example of the queried family. Scores
are on the original holdout, three queries per family and memory.}
\label{tab:coverage-readout}
\begin{tabular}{llrrrr}
\toprule
Family & Example retained & Memories & Correct & At 3/3 & At 0/3 \\
\midrule""")
    for family, label in (("key_detour", "Key detour"), ("unreachable", "Unreachable")):
        for group, name in (("present", "Yes"), ("absent", "No")):
            cell = batch[family]["pooled"][group]
            print(f"{label} & {name} & {cell['units']} & {cell['correct']}/{cell['total']} & "
                  f"{cell['perfect']} & {cell['zero']} \\\\")
    print(r"""\bottomrule
\end{tabular}
\end{table}""")


def render_confirmatory(result):
    seeds = len(result["seeds"])
    print(r"""\begin{table}[t]
\centering
\caption{Confirmatory experiment E015: 30 fresh seeds, four update
rounds, key-detour routes diversified in every pool, one held-out query
per call. Rare supplements counts supplement slots spent on the two rare
families. Retained counts the seeds whose evaluated memory still holds a
key-detour example. Scores are correct answers out of 90 per family. The
best fixed key-detour path solves 10 of 90 queries.}
\label{tab:confirmatory}
\setlength{\tabcolsep}{4.5pt}
\begin{tabular}{lrrrrr}
\toprule
Evaluated memory & Rare supplements & Retained & Ungated & Key detour & Unreachable \\
\midrule""")
    for key, label, _ in MEMORIES:
        families = result["supplement_families"].get(key)
        budget = (f"{families['key_detour'] + families['unreachable']}/{sum(families.values())}"
                  if families else "--")
        kept = result["seeds_retaining_an_example"][key]["key_detour"]
        row = result["scores"][key]
        cells = " & ".join(str(row[family]["correct"])
                           for family in ("ungated", "key_detour", "unreachable"))
        print(f"{label} & {budget} & {kept}/{seeds} & {cells} \\\\")
    print(r"""\bottomrule
\end{tabular}
\end{table}""")


def render_second_model(first, second):
    seeds = len(second["seeds"])
    print(r"""\begin{table}[t]
\centering
\caption{Second acquisition model, E016: Gemma 4 E4B on the 30 seeds
and task pools of E015, one task per call. Retained counts the seeds
whose evaluated memory still holds a key-detour example. Scores are
correct answers out of 90 per family. The last column repeats the
key-detour score of Qwen3 8B from Table~\ref{tab:confirmatory} on the
same queries.}
\label{tab:second-model}
\setlength{\tabcolsep}{4.5pt}
\begin{tabular}{lrrrrr}
\toprule
 & \multicolumn{4}{c}{Gemma 4 E4B} & Qwen3 8B \\
\cmidrule(lr){2-5}\cmidrule(lr){6-6}
Evaluated memory & Retained & Ungated & Key detour & Unreachable & Key detour \\
\midrule""")
    for key, label, _ in MEMORIES:
        kept = second["seeds_retaining_a_key_detour_example"][key]
        row = second["scores"][key]
        cells = " & ".join(str(row[family]["correct"])
                           for family in ("ungated", "key_detour", "unreachable"))
        print(f"{label} & {kept}/{seeds} & {cells} & "
              f"{first['scores'][key]['key_detour']['correct']} \\\\")
    print(r"""\bottomrule
\end{tabular}
\end{table}""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", action="store_true")
    parser.add_argument("--confirmatory", action="store_true")
    parser.add_argument("--second-model", action="store_true")
    args = parser.parse_args()
    audit = json.loads(E014.read_text())
    if args.second_model:
        render_second_model(json.loads(E015.read_text()), json.loads(E016.read_text()))
    elif args.confirmatory:
        render_confirmatory(json.loads(E015.read_text()))
    elif args.coverage:
        render_coverage(audit)
    else:
        render_summary(json.loads(E013.read_text()), audit)
