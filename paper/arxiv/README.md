# arXiv Manuscript Draft

This folder contains an arXiv-ready manuscript draft describing the repository as a living catalog of data center cooling research tools.

Files:

- `main.tex`: manuscript source.
- `references.bib`: bibliography for standards, tools, and repository artifacts.

Suggested build command:

```bash
latexmk -pdf main.tex
```

If `latexmk` is unavailable, use:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Before submission, update the draft author metadata if needed, check every cited tool link, and update the repository commit hash or release tag in the data availability statement.

Repository-side checks used by the daily review workflow:

```bash
powershell -ExecutionPolicy Bypass -File ../../scripts/check_runtime_prereqs.ps1
python ../../scripts/check_manuscript_citations.py
python ../../scripts/check_catalog_quality.py
```

The generated catalog package also includes `docs/generated/validation_runbook.md`, `docs/generated/validation_next_actions.md`, and `docs/generated/validation_debt_report.md`; update the manuscript counts after regenerating dated outputs. If Python or TeX is unavailable, record the exact blocked command in the dated review log and avoid changing generated counts as if the scripts ran.
