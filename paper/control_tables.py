"""Render the matched-budget and diverse-path tables from audited aggregates."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E012 = ROOT / "experiments/E012-rare-only/results/qwen3-8b/aggregate.json"
E013 = ROOT / "experiments/E013-diverse-paths/results/qwen3-8b/aggregate.json"
ARMS = (
    ("random_model", "Reference-mixture random"),
    ("rare_only_model", "Balanced rare-only random"),
    ("targeted_model", "Adaptive"),
)


def count(score):
    return f"{score['correct']}/{score['total']}"


def render_totals(varied):
    print(r"""\begin{table}[H]
\centering
\caption{Fixed-label evaluation with frozen memories (E013). Each cell
pools 18 queries over six paired seeds. Only the key-detour queries change
between batches. The balanced and adaptive memories come from E012,
and the reference-mixture memories come from E002.}
\label{tab:diverse-paths}
\begin{tabular}{lrrrr}
\toprule
& \multicolumn{2}{c}{Key detour} & \multicolumn{2}{c}{Unreachable} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Policy & Original & Varied & Original & Varied \\
\midrule""")
    for arm, label in ARMS:
        scores = varied["scores"][arm]
        values = [count(scores[condition][family])
                  for family in ("key_detour", "unreachable")
                  for condition in ("original", "varied")]
        print(" & ".join([label, *values]) + r" \\")
    print(r"""\bottomrule
\end{tabular}
\end{table}""")


def render_seeds(rare, varied):
    print(r"""\begin{table}[H]
\centering
\caption{Paired control results. E012 cells are rare-query correct
counts out of six. E013 cells are adaptive-minus-comparator differences
in key-detour correct counts out of three, on the original and varied
batches in that order.}
\label{tab:controls-seeds}
\begin{tabular}{lrrrr}
\toprule
& \multicolumn{2}{c}{E012 rare score} & \multicolumn{2}{c}{E013 adaptive gap} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Seed & Balanced & Adaptive & vs.\ mixture & vs.\ balanced \\
\midrule""")
    for index, (seed, scores) in enumerate(rare["per_seed_correct"].items()):
        totals = [sum(scores[arm][family] for family in ("key_detour", "unreachable"))
                  for arm in ("rare_only_model", "targeted_model")]
        values = []
        for arm in ("random_model", "rare_only_model"):
            pair = varied["contrasts"][arm]["per_seed_original_varied_gaps_out_of_three"][index]
            values.append(", ".join(f"{gap:+d}" if gap else "0" for gap in pair))
        print(" & ".join([seed, *map(str, totals), *values]) + r" \\")
    print(r"""\bottomrule
\end{tabular}
\end{table}""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", action="store_true", help="Render the paired appendix table.")
    args = parser.parse_args()
    varied = json.loads(E013.read_text())
    if args.seeds:
        render_seeds(json.loads(E012.read_text()), varied)
    else:
        render_totals(varied)
