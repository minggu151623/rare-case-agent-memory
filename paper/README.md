# Manuscript and reproducibility

The manuscript source is [main.tex](main.tex). The bibliography was fetched
from the primary records listed in [reference-sources.md](reference-sources.md).
The data, code, and protocols are included in the accompanying archive.

## Build the PDF

From this directory, use a standard LaTeX distribution with BibTeX.

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Verify the results

From the archive root, run the checks with Python 3.10 or later. These
commands use only the standard library and replay archived model answers.

```sh
python3 -m unittest discover -s experiments/E000-oracle-smoke
python3 -m unittest discover -s experiments/E001-memory-coverage
python3 -m unittest discover -s experiments/E002-admission
python3 -m src.admission_audit experiments/E002-admission/results/qwen3-8b
python3 -m src.admission_report experiments/E002-admission/results/qwen3-8b
python3 -m src.transfer_report experiments/E002-admission/results/qwen3-8b experiments/E003-transfer/results/qwen3-8b
```

The live run commands in the root README require the pinned Qwen3 8B model
and local Ollama. For exact reconstruction of the published counts, use
the archived responses. Hardware and inference implementation can affect
regenerated model responses.

For the extended experiments, replay the following from the archive root.
Each JSON command reproduces the corresponding file in the experiment's
results directory.

```sh
a=experiments/E002-admission/results/qwen3-8b
b=experiments/E003-transfer/results/qwen3-8b
python3 -m src.representation_report "$a" "$b" experiments/E004-representation/results/qwen3-8b
python3 experiments/E005-fifo-null/verify.py
python3 -m src.representation_report "$a" "$b" experiments/E006-cross-model/results/gemma-e4b --cross-model
python3 -m src.gemma_diagnostics experiments/E006-cross-model/results/gemma-e4b
python3 -m src.path_errors "$a" "$b"
python3 -m src.end_to_end experiments/E008-end-to-end/results/qwen3-8b --audit
python3 -m src.matched_labels "$a" experiments/E009-matched-labels/results/qwen3-8b --audit
python3 -m src.gemma_diagnostics experiments/E010-single-query/results/gemma-e4b --source "$a"
```

E006's batch completeness command reproduces
`completeness.json`. The other JSON commands reproduce
`aggregate.json`. The FIFO command prints the count of exact checks.

The November 13 manuscript audit reproduces its evidence with
~~~
python3 -m experiments.E011-manuscript-audit.check
~~~
Compare with experiments/E011-manuscript-audit/results.json.

## Replay the matched-budget and diverse-path controls

From the archive root, run:

```sh
e002=experiments/E002-admission/results/qwen3-8b
e012=experiments/E012-rare-only/results/qwen3-8b
e013=experiments/E013-diverse-paths/results/qwen3-8b
python3 -m unittest discover -s experiments/E013-diverse-paths
python3 -m src.rare_only "$e012" --audit | cmp - "$e012/aggregate.json"
python3 -m src.diverse_paths "$e002" "$e012" "$e013" --audit | cmp - "$e013/aggregate.json"
```

For a live run, use separate output directories and replace `--audit`
with `--ollama-port 11434` after starting Ollama 0.40.12 with the
pinned Qwen3 8B snapshot. E013 takes the completed E012 run as input.
The study protocols record the seeds, schedule, and failure handling.
Completed seed directories can be reused after audit. To retry a partial
seed, preserve its directory outside the run root before invoking the same
command again.

Regenerate the two new manuscript tables with:

```sh
python3 paper/control_tables.py > paper/diverse-paths-table.tex
python3 paper/control_tables.py --seeds > paper/control-seeds.tex
```

## Check the FIFO proof in Lean

See [the Lean artifact](../formal/README.md) for the pinned toolchain,
theorem names, and commands for kernel checking. The Python E005
enumeration above provides an independent check of the finite formula.
