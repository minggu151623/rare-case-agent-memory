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
