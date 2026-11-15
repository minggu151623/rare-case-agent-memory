"""Render the summary and coverage tables from the E013 aggregate and the E014 audit."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E013 = ROOT / "experiments/E013-diverse-paths/results/qwen3-8b/aggregate.json"
E014 = ROOT / "experiments/E014-publication-audit/results.json"
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", action="store_true")
    args = parser.parse_args()
    audit = json.loads(E014.read_text())
    if args.coverage:
        render_coverage(audit)
    else:
        render_summary(json.loads(E013.read_text()), audit)
