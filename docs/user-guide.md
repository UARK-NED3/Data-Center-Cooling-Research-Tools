# User Guide

This repository is a starting map for data center cooling research tools. It is not a validation stamp. Use the notes and caveats to decide which resources are mature enough for engineering analysis, which are educational examples, and which are candidates for deeper review.

## Pick A Starting Point

| If you are trying to... | Start with | Then check |
| --- | --- | --- |
| Model annual facility energy, PUE, heat recovery, or climate sensitivity | Room, Building, And Campus Modeling | System Metrics, Standards, And Accounting |
| Study direct-to-chip or rack liquid cooling | Rack, CDU, And Liquid Loop Systems | Chip, Package, And Server Cooling |
| Build a cooling control or RL benchmark | AI, Control, Digital Twins, And Operations | Room, Building, And Campus Modeling |
| Connect cooling to water, carbon, or site-selection risk | System Metrics, Standards, And Accounting | Data center water and energy-water nexus resources outside this repository |
| Process boiling, bubble, droplet, IR, or acoustic-emission experiments | Fundamental Thermal-Fluid Mechanisms | Chip, Package, And Server Cooling |
| Prepare a literature review, proposal, or paper around data center cooling tools | Generated Catalog Snapshot | `paper/arxiv/main.tex` |

## How To Interpret Entries

| Label or caveat | What it means |
| --- | --- |
| Standard/guideline | Strong reference for definitions, requirements, environmental classes, or test framing. It may not provide runnable code. |
| Open-source environment or benchmark | Usually best for reproducible control, simulation, or ML experiments. Check assumptions, validation, and maintenance before citing results. |
| Educational | Useful for teaching or fast prototyping, but not enough evidence for design decisions without independent checks. |
| Vendor/product material | Useful for hardware landscape awareness. Treat performance claims cautiously unless datasheets, test data, or standards-based validation are available. |
| Candidate or low-confidence | Relevant enough to track, but not ready for the main catalog without a repository-level review. |
| Source missing | A named item has no confirmed canonical URL yet. Treat it as a maintenance task, not a usable evidence source. |

## Suggested Workflows

### Literature Review Or Proposal

1. Read [docs/trends.md](trends.md) for the current landscape summary.
2. Use [docs/generated/catalog_resources.csv](generated/catalog_resources.csv) to filter by section, status, scale, or workflow tag.
3. Check `validation_basis`, `run_status`, `artifact_status`, `reviewed_on`, `validation_signal`, and `review_priority` before relying on an entry as evidence.
4. Review [docs/generated/validation_execution_matrix.md](generated/validation_execution_matrix.md) when you need to know whether an entry is ready for a smoke test, blocked by missing source/evidence, or only suitable for manual review.
5. Review [docs/generated/validation_runbook.md](generated/validation_runbook.md) when you need to know the command, configuration, output, pass/fail, or blocking evidence required to close an item.
6. Review [docs/generated/validation_next_actions.md](generated/validation_next_actions.md) when you need a ranked closure batch instead of the full validation queue.
7. Review [docs/generated/validation_debt_report.md](generated/validation_debt_report.md) when you need to know which not-run entries have been stale long enough to require execution evidence or demotion.
8. Review [docs/generated/catalog_quality_report.md](generated/catalog_quality_report.md) for current label warnings.
9. Follow links only for entries whose evidence level matches your use case.
10. Record any new resources in [docs/candidate-repos.md](candidate-repos.md) before promoting them to the README.

### Tool Selection For A Study

1. Define the physical scale: chip, rack, CDU, room, building, campus, or operations.
2. Define the dominant output metric: junction temperature, pressure drop, pumping power, PUE, WUE, ERE, carbon, uptime, or cost.
3. Prefer tools with explicit inputs, outputs, assumptions, and validation data.
4. For CFD, Modelica, EnergyPlus, or RL studies, keep a small baseline case that can be reproduced before adding optimization or AI control.
5. Treat "not specified" validation or run metadata as a prompt to inspect the linked source, not as a defect by itself.

### Repository Maintenance

1. Run `powershell -ExecutionPolicy Bypass -File scripts/check_runtime_prereqs.ps1` to confirm Python and Git are usable.
2. Run `python scripts/discover_github_repos.py` to mine current GitHub search streams.
3. Open a repository review issue for promising new candidates.
4. Apply [docs/repo-review-workflow.md](repo-review-workflow.md).
5. Edit `README.md` only after deciding the entry belongs in the main catalog.
6. Run `python scripts/build_catalog_assets.py` to refresh the generated summary and figures.
7. Run `python scripts/check_catalog_quality.py` to refresh the quality report and catch label conflicts.
8. Use `docs/generated/validation_execution_matrix.md` to choose a runnable or blocked validation item for the next dated review log.
9. Use `docs/generated/validation_runbook.md` to define the minimum evidence packet before closing a queue item.
10. Use `docs/generated/validation_next_actions.md` to pick the next ranked closure target before adding new catalog candidates.
11. Use `docs/generated/validation_debt_report.md` to avoid carrying the same stale not-run item through multiple review cycles without a closure decision.

## Quality Bar

The catalog is most useful when it says what each resource can do and what it cannot prove. A good entry should identify the scale, workflow, inputs/outputs, and validation caveat in one sentence. Avoid broad claims such as "best cooling tool" or "AI optimized data center" unless the linked resource directly supports that claim.
