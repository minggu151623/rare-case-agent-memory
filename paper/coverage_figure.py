"""Draw retained key-detour coverage against key-detour accuracy for E002/E012 and E015."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
E014 = json.loads((ROOT / "experiments/E014-publication-audit/results.json").read_text())
E015 = json.loads(
    (ROOT / "experiments/E015-confirmatory/results/qwen3-8b/aggregate.json").read_text())
MEMORIES = (("empty", "Empty"), ("frozen", "Frozen"), ("random_model", "Mixture"),
            ("rare_only_model", "Balanced"), ("targeted_model", "Adaptive"))
BLUE, ORANGE, INK, MUTED = "#0072B2", "#E69F00", "#222222", "#666666"


def exploratory():
    cells = E014["coverage_and_readout"]["original_batch"]["key_detour"]["by_memory"]
    rows = []
    for key, _ in MEMORIES:
        present = cells[key].get("present", {"units": 0, "correct": 0})
        absent = cells[key].get("absent", {"units": 0, "correct": 0})
        units = present["units"] + absent["units"]
        rows.append((100 * present["units"] / units,
                     100 * (present["correct"] + absent["correct"]) / (3 * units)))
    return rows


def confirmatory():
    seeds = len(E015["seeds"])
    return [(100 * E015["seeds_retaining_an_example"][key]["key_detour"] / seeds,
             100 * E015["scores"][key]["key_detour"]["correct"]
             / E015["scores"][key]["key_detour"]["total"]) for key, _ in MEMORIES]


def main():
    plt.rcParams.update({"font.family": "serif", "font.size": 8, "pdf.fonttype": 42})
    figure, axes = plt.subplots(1, 2, figsize=(6.4, 2.5), sharey=True)
    panels = (("Exploratory, 6 seeds, one answer path", exploratory()),
              ("Confirmatory, 30 seeds, nine answer paths", confirmatory()))
    width = 0.36
    for axis, (title, rows) in zip(axes, panels):
        for index, (kept, accuracy) in enumerate(rows):
            first = axis.bar(index - width / 2 - 0.01, kept, width, color=BLUE)
            second = axis.bar(index + width / 2 + 0.01, accuracy, width, color=ORANGE,
                              hatch="///", edgecolor="white", linewidth=0)
            for bar, value in ((first, kept), (second, accuracy)):
                axis.text(bar[0].get_x() + width / 2, value + 2, f"{value:.0f}",
                          ha="center", va="bottom", fontsize=6.5, color=INK)
        axis.set_title(title, fontsize=8, color=INK)
        axis.set_xticks(range(len(MEMORIES)), [label for _, label in MEMORIES])
        axis.set_ylim(0, 112)
        axis.set_yticks((0, 25, 50, 75, 100))
        axis.grid(axis="y", color="#dddddd", linewidth=0.5)
        axis.set_axisbelow(True)
        for side in ("top", "right", "left"):
            axis.spines[side].set_visible(False)
        axis.spines["bottom"].set_color(MUTED)
        axis.tick_params(length=0, colors=MUTED)
    axes[0].set_ylabel("Percent", color=MUTED)
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE),
               plt.Rectangle((0, 0), 1, 1, facecolor=ORANGE, hatch="///", edgecolor="white",
                             linewidth=0)]
    figure.legend(handles, ["Seeds whose memory retains a key-detour example",
                            "Held-out key-detour accuracy"],
                  loc="lower center", ncol=2, frameon=False, fontsize=7.5)
    figure.tight_layout(rect=(0, 0.09, 1, 1))
    figure.savefig(ROOT / "paper/coverage-accuracy.pdf", metadata={"CreationDate": None})


if __name__ == "__main__":
    main()
