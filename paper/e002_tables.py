"""Render manuscript tables from the audited E002 aggregate JSON."""

import argparse
import json
from pathlib import Path
from statistics import mean

FAMILIES = ("ungated", "key_detour", "unreachable")
LABELS = {
    "random_model": "Random / model",
    "targeted_model": "Targeted / model",
    "random_oracle": "Random / oracle",
    "targeted_oracle": "Targeted / oracle",
    "empty": "Empty memory",
    "frozen": "Frozen memory",
}


def row(*values):
    return " & ".join(map(str, values)) + r" \\"


def accuracy_rows(report):
    for arm, label in LABELS.items():
        record = (report["arms"] | report["controls"])[arm]
        scores = [f'{record["final_correct"][family]}/{record["final_total"][family]}'
                  for family in FAMILIES]
        yield row(label, *scores, f'{record["rare_macro_accuracy"]:.1%}'.replace("%", r"\%"))


def memory_rows(report):
    for arm, record in report["arms"].items():
        stages = record["stage_totals"]
        attempts = stages["attempted"]["unreachable"]
        passes = stages["model_passes"]["unreachable"]
        admitted = stages["admitted"]["unreachable"]
        final_count = mean(seed["unreachable"] for seed in record["final_memory_by_seed"])
        yield row(LABELS[arm], attempts, passes, admitted, f"{final_count:.2f}")


def render(report):
    return "\n".join([
        r"\begin{table}[tbp]",
        r"\centering",
        r"\caption{Held-out exact accuracy by task family across six paired seeds.}",
        r"\label{tab:e002-accuracy}",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        row("Condition", "Ungated", "Key detour", "Unreachable", "Rare macro"),
        r"\midrule",
        *accuracy_rows(report),
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
        "",
        r"\begin{table}[tbp]",
        r"\centering",
        r"\caption{Unreachable-task attempts and admissions in E002. Final memory is the mean number of unreachable examples per seed.}",
        r"\label{tab:e002-coverage}",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        row("Condition", "Attempts", "Model passes", "Admissions", "Final memory"),
        r"\midrule",
        *memory_rows(report),
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
        "",
    ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    print(render(json.loads(args.report.read_text())), end="")
