# GitHub Repository Review Log: 2026-06-20

This review pass refreshed the catalog against current GitHub search results and official data-center cooling resources. The focus was on tools that make the repository more useful for liquid-cooling, control, digital-twin, metric, and standards-aware research.

## Sources Checked

| Source | Use |
| --- | --- |
| [GitHub search: data center cooling](https://github.com/search?q=data%20center%20cooling&type=repositories) | Current cooling-specific repository discovery. |
| [GitHub search: datacenter cooling](https://github.com/search?q=datacenter%20cooling&type=repositories) | Variant spelling and newly updated candidates. |
| [GitHub search: data center liquid cooling](https://github.com/search?q=data%20center%20liquid%20cooling&type=repositories) | Liquid-cooling and CDU candidate discovery. |
| [GitHub topic: data-center](https://github.com/topics/data-center?o=desc&s=updated) | Broad adjacent stream for telemetry, control, and infrastructure. |
| [ASHRAE Data Center Resources](https://www.ashrae.org/technical-resources/bookstore/datacom-series) | Standards and thermal-guideline source hub. |
| [Open Compute Project Cooling Environments](https://www.opencompute.org/community/cooling-environments) | Open liquid-cooling ecosystem and specification tracking. |
| [The Green Grid WUE white paper](https://www.thegreengrid.org/system/files/store/WUE_v1.pdf) | Water accounting source. |
| [The Green Grid Water Usage Impact announcement](https://www.itic.org/news-events/news-releases/the-green-grid-releases-new-tool-to-help-data-centers-advance-water-efficiency) | 2025 water-impact metric update. |

## Promoted Or Added To README

| Resource | Decision | Rationale |
| --- | --- | --- |
| [HewlettPackard/sustain-lc](https://github.com/HewlettPackard/sustain-lc) | Include with validation caveat | Relevant liquid-cooling benchmark/control environment combining Modelica/FMUs, Gymnasium, rule-based/RL control, and LLM-agent experiments. Good fit for the AI/control and liquid-cooling trend, but model validation should be checked before using results as evidence. |
| [HewlettPackard/compopt](https://github.com/HewlettPackard/compopt) | Candidate include | Newly surfaced AI data center simulation benchmark spanning chip-to-CDU thermal models, workload scheduling, and energy/water/cost objectives. Include as a candidate because the repository is young and needs detailed model review. |
| [HewlettPackard/c2g-bench](https://github.com/HewlettPackard/c2g-bench) | Candidate include | Grid-interactive benchmark that treats liquid-cooling thermal inertia, battery storage, and schedulable compute as controllable resources. Useful for emerging grid-services research, pending deeper validation. |
| [dell/IRC-Reference-Tools](https://github.com/dell/IRC-Reference-Tools) | Include as reference tools | Practical reference implementation for in-rack coolant controller monitoring, leak events, valves, and automated shutdown actions. Useful for reliability/serviceability workflows rather than heat-transfer prediction. |
| [lbl-srg/modelica-buildings](https://github.com/lbl-srg/modelica-buildings) | Include | Mature Modelica Buildings library with data-center modeling lineage and active development, including liquid-cooling/cold-plate issue tracking. Useful for dynamic system modeling. |
| [DOE/LBNL data center Modelica toolkit](https://sites.psu.edu/sbslab/publications/tools/end-to-end-modeling-and-optimization-package-for-data-center-cooling/) | Include | Documents data-center cooling system and component models released through the Modelica Buildings library. |
| [Open Compute Project Cooling Environments](https://www.opencompute.org/community/cooling-environments) | Include | OCP community source for cooling-environment and liquid-cooling ecosystem material. |
| [OCP Single-Phase Direct-to-Chip Cold Plate Base Specification](https://www.opencompute.org/wiki/Cooling_Environments/Cold_Plate) | Include as emerging specification | Relevant vendor-neutral specification effort for D2C cold plates; useful to track, but not a validation dataset. |
| [OCP OAI System Liquid Cooling Guidelines](https://www.opencompute.org/documents/oai-system-liquid-cooling-guidelines-in-ocp-template-mar-3-2023-update-pdf) | Include | Guidance for design, validation, implementation, and risks in high-power OAI/OAM liquid cooling. |
| [ASHRAE Data Center Resources](https://www.ashrae.org/technical-resources/bookstore/datacom-series) | Include | Current official data-center guidance hub, including Standard 90.4, TC 9.9 resources, and liquid-cooling references. |
| [The Green Grid PUE white paper](https://datacenters.lbl.gov/sites/default/files/WP49-PUE%20A%20Comprehensive%20Examination%20of%20the%20Metric_v6.pdf) | Include | Important for avoiding PUE boundary misuse and contextualizing facility efficiency. |
| [The Green Grid WUE white paper](https://www.thegreengrid.org/system/files/store/WUE_v1.pdf) | Include | Baseline water-use metric source for data center cooling and sustainability accounting. |
| [The Green Grid Water Usage Impact metric](https://www.itic.org/news-events/news-releases/the-green-grid-releases-new-tool-to-help-data-centers-advance-water-efficiency) | Include as emerging metric | Newly announced 2025 metric linking water consumption and water stress; useful for tracking water-impact trends beyond WUE. |

## Kept In Candidate Queue

| Repository | Decision | Rationale |
| --- | --- | --- |
| [nehemiyawicks/densewatch](https://github.com/nehemiyawicks/densewatch) | Candidate | Metadata suggests rack power, GPU jobs, and liquid-cooling/CDU thermal correlation. Needs README/code review before inclusion. |
| [michaillogothetis/datacenter-cooling-cfd](https://github.com/michaillogothetis/datacenter-cooling-cfd) | Candidate | CFD-oriented data-center cooling optimization project. Needs validation, assumptions, and reproducibility review. |
| [samrudition/dynamic-cooling-loop](https://github.com/samrudition/dynamic-cooling-loop) | Candidate | MATLAB/Simulink transient active liquid-cooling loop model for data centers and other applications. Needs scope, equations, and validation review. |
| [cap-dcwiz/hybrid-cooling-early-warning](https://github.com/cap-dcwiz/hybrid-cooling-early-warning) | Candidate | Hybrid air/liquid early-warning demo. Needs confirmation of model depth and data sources. |
| [Pepperingomtang/Datacenter-D2C-FreeCooling-Korea](https://github.com/Pepperingomtang/Datacenter-D2C-FreeCooling-Korea) | Candidate | Climate/site-suitability notebook for D2C free cooling in Korea. Potentially useful for site/climate screening after language and method review. |
| [weiweisthl-maker/pue-solver](https://github.com/weiweisthl-maker/pue-solver) | Candidate | PUE solver surfaced in June 2026 search. Needs boundary-condition and calculation-method review. |
| [c50346867/data-center-pue-optimizer](https://github.com/c50346867/data-center-pue-optimizer) | Candidate | AI-powered PUE optimization claim. Needs code, assumptions, and validation review before promotion. |

## Exclusion Notes

Several recently updated repositories were generic infrastructure, marketing, dashboards without cooling assumptions, or very thin README-only projects. They were not promoted because the current catalog should stay cooling-centered and evidence-aware.

## Maintenance Changes

- Added `scripts/discover_github_repos.py` for repeatable GitHub candidate mining.
- Added `scripts/build_catalog_assets.py` for generated CSV summaries and SVG figures.
- Added weekly GitHub Actions discovery workflow.
- Added [user-guide.md](user-guide.md), [refresh-playbook.md](refresh-playbook.md), [trends.md](trends.md), and an arXiv manuscript draft under `paper/arxiv/`.

## Daily Review-Revision Cycle: 2026-06-20

This section records the independent reviewer comments, author/maintainer response, and verification results for the 2026-06-20 automation run. There was no previous automation memory for this recurring task, so no Day-2 recurrence comparison was applicable on this run.

### Independent Reviewer Comments

| ID | Severity | Comment |
| --- | --- | --- |
| R1 | Major | The generated evidence taxonomy had a correctness defect: notes saying a resource was "not a validated" solver or design tool could still be inferred as `validated model` because the parser matched the word `validated` without checking negation. This undermined the evidence map and could mislead readers. |
| R2 | Major | The arXiv manuscript described the catalog workflow but did not expose the generated data model, current coverage counts, or the quality-control role of generated artifacts. That weakened the claimed reproducibility contribution. |
| R3 | Major | Specification and standards resources need cleaner separation from validated engineering models. OCP cold-plate and liquid-cooling pages are important landscape sources, but they should not be presented as validation datasets. |
| R4 | Moderate | The manuscript was missing a recent direct-to-chip liquid-cooling design signal from 2026 arXiv literature. The paper should use it as landscape context without over-promoting it as a reusable tool. |
| R5 | Moderate | The local GitHub discovery script could not be re-run in the restricted automation environment because outbound sockets were blocked. The existing discovery report remains useful, but this run could not claim a fresh local GitHub API refresh. |
| R6 | Moderate | Verification depended on manual inspection of citations. A lightweight citation-key check would make future arXiv manuscript updates safer even when LaTeX is unavailable. |

### Author/Maintainer Revisions

| Reviewer item | Revision made on 2026-06-20 |
| --- | --- |
| R1, R3 | Updated `scripts/build_catalog_assets.py` so specifications are classified as standards/guidelines, vendor-neutral text does not trigger vendor/material status, candidate phrases are preserved, and negated validation statements block `validated model` labels. |
| R1, R3 | Regenerated `docs/generated/catalog_summary.md`, `docs/generated/catalog_resources.csv`, and all `docs/assets/catalog_*.svg` figures. The corrected summary now reports 68 resources, 8 candidate or low-confidence entries, 4 standards/guidelines, and 10 educational/prototype entries. |
| R2 | Revised `paper/arxiv/main.tex` with a new generated data model and quality-control subsection plus a table describing `section`, `resource_type`, `status`, `evidence_level`, and `workflow_tags`. |
| R4 | Added a 2026 direct-to-chip liquid-cooling arXiv citation to `paper/arxiv/references.bib` and discussed it in the manuscript as a landscape signal, not as a cataloged reusable tool. |
| R6 | Added `scripts/check_manuscript_citations.py` to verify that every `\cite{...}` key in the arXiv manuscript has a matching BibTeX entry. |
| R1 | Added a README caution that generated labels are curation aids, not validation stamps. |

### Verification Results

| Check | Result on 2026-06-20 |
| --- | --- |
| Catalog regeneration | Passed. `python scripts/build_catalog_assets.py` parsed 68 resources and rewrote generated CSV/Markdown/SVG artifacts. |
| Evidence-class spot check | Passed. OCP cold-plate specification is now `standard/guideline`; 2listic/datacenter-planner is no longer labeled as a validated model; CompOpt and C2G-Bench are treated as candidates. |
| Citation consistency | Passed. `python scripts/check_manuscript_citations.py` found 20 cited keys and 20 BibTeX entries with no missing entries. |
| Python syntax check | Passed. `python -m py_compile scripts\build_catalog_assets.py scripts\check_manuscript_citations.py scripts\discover_github_repos.py` completed without errors. |
| Local GitHub discovery refresh | Blocked by environment. `python scripts/discover_github_repos.py` failed with Windows socket permission error `WinError 10013`; no discovery files were intentionally rewritten from that failed run. |
| LaTeX/PDF build | Blocked by environment. Neither `latexmk` nor `pdflatex` was available in this workspace. The manuscript source and BibTeX citation keys were checked instead. |

### Remaining Open Issues

| Issue | Why it remains |
| --- | --- |
| Independent execution of linked tools | The catalog remains a curated map, not a validation study. Future work should pick high-impact benchmark/control/liquid-loop tools for runnable checks. |
| Fresh GitHub API discovery from this local run | Requires network/socket permissions or execution in GitHub Actions. Future automation should compare against the weekly issue/artifact when available. |
| Formal evidence grading | Current labels are pragmatic curation labels. A future update could add explicit fields for validation basis, model equations, data availability, and run status. |
| PDF build verification | Requires a local TeX distribution or CI job that compiles `paper/arxiv/main.tex`. |
