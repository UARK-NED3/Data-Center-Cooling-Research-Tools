# Validation Debt Report

Generated on 2026-08-11 from `README.md` metadata.

This report tracks unresolved validation debt by age and execution readiness. It does not prove that a tool has been reproduced; it identifies where the catalog has carried the same open caveat long enough to need closure evidence or a demotion decision.

## Debt Summary

| Metric | Count |
| --- | ---: |
| Queued resources | 49 |
| Not-run queued resources | 25 |
| Ready execution or inspection items | 29 |
| Blocked items | 6 |
| Manual evidence-review items | 14 |
| Source-inspected queued resources | 19 |
| Source-inspected resources still requiring execution | 10 |
| Stale queued resources (7+ days) | 45 |
| Stale ready items (7+ days) | 25 |
| Stale high-priority items (7+ days) | 20 |
| Queued resources without URLs | 0 |

## Age Buckets

| Review age | Count |
| --- | ---: |
| 0-2 days | 4 |
| 14+ days | 45 |

## Oldest Ready Items

| Priority | Resource | Track | Readiness | Reviewed | Age (days) | Closure evidence required |
| --- | --- | --- | --- | --- | ---: | --- |
| medium | [cldunlap73/BubbleID](https://github.com/cldunlap73/BubbleID) | paper artifact matching | ready: local code smoke test | 2026-06-22 | 50 | Paper-to-code/data mapping, minimal reproduction command, and mismatch notes. |
| medium | [UARK-NED3/AELab](https://github.com/UARK-NED3/AELab) | local code smoke test | ready: local code smoke test | 2026-06-22 | 50 | Smoke-test command, environment, observed output, and unresolved errors. |
| medium | [UARK-NED3/BubbleID-Flow](https://github.com/UARK-NED3/BubbleID-Flow) | local code smoke test | ready: local code smoke test | 2026-06-22 | 50 | Smoke-test command, environment, observed output, and unresolved errors. |
| medium | [UARK-NED3/FlowLab](https://github.com/UARK-NED3/FlowLab) | notebook/data review | ready: notebook review or execution | 2026-06-22 | 50 | Notebook/data provenance check, assumptions, units, and reproducible output note. |
| medium | [DOE/LBNL data center Modelica toolkit](https://sites.psu.edu/sbslab/publications/tools/end-to-end-modeling-and-optimization-package-for-data-center-cooling/) | local code smoke test | ready: local code smoke test | 2026-06-22 | 50 | Smoke-test command, environment, observed output, and unresolved errors. |
| medium | [EnergyPlus](https://energyplus.net/) | notebook/data review | ready: local code smoke test | 2026-06-22 | 50 | Notebook/data provenance check, assumptions, units, and reproducible output note. |
| medium | [lbl-srg/modelica-buildings](https://github.com/lbl-srg/modelica-buildings) | local code smoke test | ready: local code smoke test | 2026-06-22 | 50 | Smoke-test command, environment, observed output, and unresolved errors. |
| medium | [nuoaleon/Data-center-PUE-prediction-tool](https://github.com/nuoaleon/Data-center-PUE-prediction-tool) | notebook/data review | ready: notebook review or execution | 2026-06-22 | 50 | Notebook/data provenance check, assumptions, units, and reproducible output note. |
| medium | [HewlettPackard/c2g-bench](https://github.com/HewlettPackard/c2g-bench) | benchmark smoke test | ready: notebook review or execution | 2026-06-24 | 48 | Command, version/config, seed if used, output metrics, and failure notes. |
| medium | [HewlettPackard/compopt](https://github.com/HewlettPackard/compopt) | benchmark smoke test | ready: test-suite or example smoke test | 2026-06-24 | 48 | Command, version/config, seed if used, output metrics, and failure notes. |
| medium | [kardashev-lab/datacenter-cooling-sim](https://github.com/kardashev-lab/datacenter-cooling-sim) | local code smoke test | ready: container or service smoke test | 2026-06-25 | 47 | Smoke-test command, environment, observed output, and unresolved errors. |
| medium | [Visum-ai/aif-ops](https://github.com/Visum-ai/aif-ops) | semantic validation | ready: semantic validation command | 2026-06-25 | 47 | Validation command, shapes or instance graph, pass/fail result, and constraints checked. |
| medium | [JuwanHa/-BETlab-Data-Center-Modeling](https://github.com/JuwanHa/-BETlab-Data-Center-Modeling) | paper artifact matching | ready: local code smoke test | 2026-06-25 | 47 | Paper-to-code/data mapping, minimal reproduction command, and mismatch notes. |
| high | [rishithayanidhi/Data_Center_Cooling_Optimization_Environment](https://github.com/rishithayanidhi/Data_Center_Cooling_Optimization_Environment) | local code smoke test | ready: local code smoke test | 2026-06-27 | 45 | Smoke-test command, environment, observed output, and unresolved errors. |
| medium | [nehemiyawicks/densewatch](https://github.com/nehemiyawicks/densewatch) | local code smoke test | ready: container or service smoke test | 2026-06-28 | 44 | Smoke-test command, environment, observed output, and unresolved errors. |

## Current Blockers

| Resource | Track | Readiness | Reviewed | Age (days) | Blocking condition |
| --- | --- | --- | --- | ---: | --- |
| [LianLiTech/Data-Center-Liquid-Cooling-System](https://github.com/LianLiTech/Data-Center-Liquid-Cooling-System) | vendor evidence follow-up | blocked: needs datasheet or test method | 2026-06-22 | 50 | Datasheet, test method, independent report, or explicit vendor-only caveat. |
| [LianLiTech/In-Rack-Coolant-Distribution-Unit](https://github.com/LianLiTech/In-Rack-Coolant-Distribution-Unit) | vendor evidence follow-up | blocked: needs datasheet or test method | 2026-06-22 | 50 | Datasheet, test method, independent report, or explicit vendor-only caveat. |
| [NVIDIA DSX Platform](https://docs.nvidia.com/dsx) | vendor evidence follow-up | blocked: needs datasheet or test method | 2026-06-23 | 49 | Datasheet, test method, independent report, or explicit vendor-only caveat. |
| [iaziz6/Digital-Twin-for-Data-Center-Cooling](https://github.com/iaziz6/Digital-Twin-for-Data-Center-Cooling) | documented example/manual check | blocked: no runnable artifact found | 2026-06-27 | 45 | Dated missing-entry or no-runnable-artifact evidence plus demotion, reclassification, or retained-blocked decision. |
| [xiaodongwang991481/energy_saving](https://github.com/xiaodongwang991481/energy_saving) | documented example/manual check | blocked: no runnable artifact found | 2026-06-27 | 45 | Dated missing-entry or no-runnable-artifact evidence plus demotion, reclassification, or retained-blocked decision. |
| [NSTuttle/EfficiencyCalculatorWeb](https://github.com/NSTuttle/EfficiencyCalculatorWeb) | educational/prototype scope check | blocked: no runnable artifact found | 2026-07-05 | 37 | Dated missing-entry or no-runnable-artifact evidence plus demotion, reclassification, or retained-blocked decision. |

## Closure Rule For Recurring Reviews

Before promoting another batch of candidates, close at least one stale ready item (7+ days) with observed evidence, or record why execution is blocked and demote/reclassify the entry if the artifact cannot support its catalog role.
