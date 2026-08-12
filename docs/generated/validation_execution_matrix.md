# Validation Execution Matrix

Generated on 2026-08-11 from `README.md` metadata.

This matrix splits the validation queue into executable tracks. It is a planning artifact, not evidence that any queued resource has been reproduced.

## Execution Summary

| Metric | Count |
| --- | ---: |
| Queued resources | 49 |
| Ready execution or inspection items | 29 |
| Blocked items | 6 |
| Manual evidence-review items | 14 |
| Source-inspected queued resources | 19 |
| Source-inspected resources still requiring execution | 10 |

## By Validation Track

| Track | Count |
| --- | ---: |
| benchmark smoke test | 5 |
| paper artifact matching | 5 |
| semantic validation | 1 |
| hardware-in-loop/manual check | 2 |
| local code smoke test | 11 |
| notebook/data review | 3 |
| educational/prototype scope check | 12 |
| vendor evidence follow-up | 3 |
| independent validation search | 1 |
| documented example/manual check | 6 |

## By Execution Readiness

| Readiness | Count |
| --- | ---: |
| ready: local code smoke test | 10 |
| manual: source-inspected, local execution optional | 7 |
| manual: evidence review | 5 |
| ready: notebook review or execution | 4 |
| ready: source-inspected smoke test still required | 4 |
| blocked: needs datasheet or test method | 3 |
| blocked: no runnable artifact found | 3 |
| ready: artifact reproduction still required | 3 |
| ready: benchmark execution still required | 3 |
| manual: source-inspected hardware validation not run | 2 |
| ready: container or service smoke test | 2 |
| ready: test-suite or example smoke test | 2 |
| ready: semantic validation command | 1 |

## Queue Execution Plan

| Track | Readiness | Resource | Reviewed | Age (days) | Closure evidence required |
| --- | --- | --- | --- | ---: | --- |
| independent validation search | ready: notebook review or execution | [4g/dcool](https://github.com/4g/dcool) | 2026-07-01 | 41 | Independent validation source or retained unvalidated label with dated search note. |
| educational/prototype scope check | manual: source-inspected, local execution optional | [enrique-martinez-martel/collagen](https://github.com/enrique-martinez-martel/collagen) | 2026-07-04 | 38 | Source-inspection evidence recorded; local run remains optional for deeper reproducibility. |
| educational/prototype scope check | ready: local code smoke test | [Jalaljalili/Cooling-Dynamic-Model](https://github.com/Jalaljalili/Cooling-Dynamic-Model) | 2026-07-01 | 41 | Small run or code inspection showing assumptions, limits, and teaching/prototype scope. |
| educational/prototype scope check | ready: local code smoke test | [Lucabr01/RL-and-Gradient-Free-Based-Datacenter-Cooling-Controller](https://github.com/Lucabr01/RL-and-Gradient-Free-Based-Datacenter-Cooling-Controller) | 2026-07-01 | 41 | Small run or code inspection showing assumptions, limits, and teaching/prototype scope. |
| educational/prototype scope check | manual: source-inspected, local execution optional | [vk22006/predictive-cooling-optimizer-for-data-centers](https://github.com/vk22006/predictive-cooling-optimizer-for-data-centers) | 2026-07-02 | 40 | Source-inspection evidence recorded; local run remains optional for deeper reproducibility. |
| educational/prototype scope check | manual: source-inspected, local execution optional | [xenabmirza/magnetocaloric-thin-film-cooling](https://github.com/xenabmirza/magnetocaloric-thin-film-cooling) | 2026-07-04 | 38 | Source-inspection evidence recorded; local run remains optional for deeper reproducibility. |
| educational/prototype scope check | manual: source-inspected, local execution optional | [samrudition/dynamic-cooling-loop](https://github.com/samrudition/dynamic-cooling-loop) | 2026-07-04 | 38 | Source-inspection evidence recorded; local run remains optional for deeper reproducibility. |
| educational/prototype scope check | manual: source-inspected, local execution optional | [femmetronics/Data-Center-Cooling-System](https://github.com/femmetronics/Data-Center-Cooling-System) | 2026-07-03 | 39 | Source-inspection evidence recorded; local run remains optional for deeper reproducibility. |
| educational/prototype scope check | manual: source-inspected, local execution optional | [ME421-Capstone-Project/chiller-model](https://github.com/ME421-Capstone-Project/chiller-model) | 2026-07-03 | 39 | Source-inspection evidence recorded; local run remains optional for deeper reproducibility. |
| educational/prototype scope check | blocked: no runnable artifact found | [NSTuttle/EfficiencyCalculatorWeb](https://github.com/NSTuttle/EfficiencyCalculatorWeb) | 2026-07-05 | 37 | Dated missing-entry or no-runnable-artifact evidence plus demotion, reclassification, or retained-blocked decision. |
| educational/prototype scope check | ready: test-suite or example smoke test | [c50346867/data-center-pue-optimizer](https://github.com/c50346867/data-center-pue-optimizer) | 2026-06-29 | 43 | Small run or code inspection showing assumptions, limits, and teaching/prototype scope. |
| educational/prototype scope check | manual: source-inspected, local execution optional | [D1D104/fuzzy-miso-datacenter-cooling](https://github.com/D1D104/fuzzy-miso-datacenter-cooling) | 2026-07-03 | 39 | Source-inspection evidence recorded; local run remains optional for deeper reproducibility. |
| hardware-in-loop/manual check | manual: source-inspected hardware validation not run | [eeyx1/cooling-fan-predictive-maintenance-digital-twin](https://github.com/eeyx1/cooling-fan-predictive-maintenance-digital-twin) | 2026-07-02 | 40 | Source inspection plus hardware bill of materials; bench test, compile/upload result, sensor calibration, relay safety, or field trial still needed. |
| hardware-in-loop/manual check | manual: source-inspected hardware validation not run | [SohelHossain1218/Smart-IoT-Data-Center-Cooling-Environment-Monitor](https://github.com/SohelHossain1218/Smart-IoT-Data-Center-Cooling-Environment-Monitor) | 2026-07-03 | 39 | Source inspection plus hardware bill of materials; bench test, compile/upload result, sensor calibration, relay safety, or field trial still needed. |
| vendor evidence follow-up | blocked: needs datasheet or test method | [NVIDIA DSX Platform](https://docs.nvidia.com/dsx) | 2026-06-23 | 49 | Datasheet, test method, independent report, or explicit vendor-only caveat. |
| vendor evidence follow-up | blocked: needs datasheet or test method | [LianLiTech/Data-Center-Liquid-Cooling-System](https://github.com/LianLiTech/Data-Center-Liquid-Cooling-System) | 2026-06-22 | 50 | Datasheet, test method, independent report, or explicit vendor-only caveat. |
| vendor evidence follow-up | blocked: needs datasheet or test method | [LianLiTech/In-Rack-Coolant-Distribution-Unit](https://github.com/LianLiTech/In-Rack-Coolant-Distribution-Unit) | 2026-06-22 | 50 | Datasheet, test method, independent report, or explicit vendor-only caveat. |
| documented example/manual check | blocked: no runnable artifact found | [iaziz6/Digital-Twin-for-Data-Center-Cooling](https://github.com/iaziz6/Digital-Twin-for-Data-Center-Cooling) | 2026-06-27 | 45 | Dated missing-entry or no-runnable-artifact evidence plus demotion, reclassification, or retained-blocked decision. |
| local code smoke test | ready: local code smoke test | [rishithayanidhi/Data_Center_Cooling_Optimization_Environment](https://github.com/rishithayanidhi/Data_Center_Cooling_Optimization_Environment) | 2026-06-27 | 45 | Smoke-test command, environment, observed output, and unresolved errors. |
| documented example/manual check | blocked: no runnable artifact found | [xiaodongwang991481/energy_saving](https://github.com/xiaodongwang991481/energy_saving) | 2026-06-27 | 45 | Dated missing-entry or no-runnable-artifact evidence plus demotion, reclassification, or retained-blocked decision. |
| documented example/manual check | manual: evidence review | [Data Center Due Diligence Orchestrator](https://mcpmarket.com/tools/skills/data-center-due-diligence-orchestrator) | 2026-06-22 | 50 | Documented example result or reason execution remains unavailable. |
| benchmark smoke test | ready: notebook review or execution | [HewlettPackard/c2g-bench](https://github.com/HewlettPackard/c2g-bench) | 2026-06-24 | 48 | Command, version/config, seed if used, output metrics, and failure notes. |
| benchmark smoke test | ready: test-suite or example smoke test | [HewlettPackard/compopt](https://github.com/HewlettPackard/compopt) | 2026-06-24 | 48 | Command, version/config, seed if used, output metrics, and failure notes. |
| notebook/data review | ready: notebook review or execution | [UARK-NED3/FlowLab](https://github.com/UARK-NED3/FlowLab) | 2026-06-22 | 50 | Notebook/data provenance check, assumptions, units, and reproducible output note. |
| local code smoke test | ready: local code smoke test | [DOE/LBNL data center Modelica toolkit](https://sites.psu.edu/sbslab/publications/tools/end-to-end-modeling-and-optimization-package-for-data-center-cooling/) | 2026-06-22 | 50 | Smoke-test command, environment, observed output, and unresolved errors. |
| notebook/data review | ready: local code smoke test | [EnergyPlus](https://energyplus.net/) | 2026-06-22 | 50 | Notebook/data provenance check, assumptions, units, and reproducible output note. |
| local code smoke test | ready: local code smoke test | [lbl-srg/modelica-buildings](https://github.com/lbl-srg/modelica-buildings) | 2026-06-22 | 50 | Smoke-test command, environment, observed output, and unresolved errors. |
| notebook/data review | ready: notebook review or execution | [nuoaleon/Data-center-PUE-prediction-tool](https://github.com/nuoaleon/Data-center-PUE-prediction-tool) | 2026-06-22 | 50 | Notebook/data provenance check, assumptions, units, and reproducible output note. |
| documented example/manual check | manual: evidence review | [HyperYJ/ai-liquid-council](https://github.com/HyperYJ/ai-liquid-council) | 2026-06-22 | 50 | Documented example result or reason execution remains unavailable. |
| local code smoke test | ready: source-inspected smoke test still required | [Cloud Carbon Footprint](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint) | 2026-08-11 | 0 | Smoke-test command, environment, observed output, and unresolved errors. |
| local code smoke test | ready: source-inspected smoke test still required | [UARK-NED3/OpenDC-LCA](https://github.com/UARK-NED3/OpenDC-LCA) | 2026-08-11 | 0 | Smoke-test command, environment, observed output, and unresolved errors. |
| local code smoke test | ready: container or service smoke test | [kardashev-lab/datacenter-cooling-sim](https://github.com/kardashev-lab/datacenter-cooling-sim) | 2026-06-25 | 47 | Smoke-test command, environment, observed output, and unresolved errors. |
| local code smoke test | ready: container or service smoke test | [nehemiyawicks/densewatch](https://github.com/nehemiyawicks/densewatch) | 2026-06-28 | 44 | Smoke-test command, environment, observed output, and unresolved errors. |
| local code smoke test | ready: source-inspected smoke test still required | [UARK-NED3/CFDTwin](https://github.com/UARK-NED3/CFDTwin) | 2026-07-05 | 37 | Smoke-test command, environment, observed output, and unresolved errors. |
| semantic validation | ready: semantic validation command | [Visum-ai/aif-ops](https://github.com/Visum-ai/aif-ops) | 2026-06-25 | 47 | Validation command, shapes or instance graph, pass/fail result, and constraints checked. |
| local code smoke test | ready: local code smoke test | [UARK-NED3/AELab](https://github.com/UARK-NED3/AELab) | 2026-06-22 | 50 | Smoke-test command, environment, observed output, and unresolved errors. |
| local code smoke test | ready: local code smoke test | [UARK-NED3/BubbleID-Flow](https://github.com/UARK-NED3/BubbleID-Flow) | 2026-06-22 | 50 | Smoke-test command, environment, observed output, and unresolved errors. |
| local code smoke test | ready: source-inspected smoke test still required | [dell/IRC-Reference-Tools](https://github.com/dell/IRC-Reference-Tools) | 2026-07-05 | 37 | Smoke-test command, environment, observed output, and unresolved errors. |
| documented example/manual check | manual: evidence review | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | 2026-06-22 | 50 | Documented example result or reason execution remains unavailable. |
| documented example/manual check | manual: evidence review | [Mechanical Engineering Research Skill](https://github.com/hanhuark/mechanical-engineering-research-skill) | 2026-06-22 | 50 | Documented example result or reason execution remains unavailable. |
| benchmark smoke test | ready: benchmark execution still required | [HewlettPackard/dc-rl](https://github.com/HewlettPackard/dc-rl) | 2026-07-04 | 38 | Command, version/config, seed if used, output metrics, and failure notes. |
| benchmark smoke test | ready: benchmark execution still required | [HewlettPackard/sustain-lc](https://github.com/HewlettPackard/sustain-lc) | 2026-07-04 | 38 | Command, version/config, seed if used, output metrics, and failure notes. |
| benchmark smoke test | ready: benchmark execution still required | [HewlettPackard/sustain-cluster](https://github.com/HewlettPackard/sustain-cluster) | 2026-08-11 | 0 | Command, version/config, seed if used, output metrics, and failure notes. |
| paper artifact matching | ready: artifact reproduction still required | [imamdoula004/AI-Hybrid-EMPC-DataCenter-Cooling](https://github.com/imamdoula004/AI-Hybrid-EMPC-DataCenter-Cooling) | 2026-07-05 | 37 | Paper-to-code/data mapping, minimal reproduction command, and mismatch notes. |
| paper artifact matching | ready: local code smoke test | [cldunlap73/BubbleID](https://github.com/cldunlap73/BubbleID) | 2026-06-22 | 50 | Paper-to-code/data mapping, minimal reproduction command, and mismatch notes. |
| paper artifact matching | ready: local code smoke test | [JuwanHa/-BETlab-Data-Center-Modeling](https://github.com/JuwanHa/-BETlab-Data-Center-Modeling) | 2026-06-25 | 47 | Paper-to-code/data mapping, minimal reproduction command, and mismatch notes. |
| paper artifact matching | ready: artifact reproduction still required | [LukeJYK/IPDPS26_WaterSplit](https://github.com/LukeJYK/IPDPS26_WaterSplit) | 2026-08-11 | 0 | Paper-to-code/data mapping, minimal reproduction command, and mismatch notes. |
| educational/prototype scope check | manual: evidence review | [Sensibo Automation](https://mcpmarket.com/tools/skills/sensibo-automation) | 2026-06-22 | 50 | Small run or code inspection showing assumptions, limits, and teaching/prototype scope. |
| paper artifact matching | ready: artifact reproduction still required | [wfzheng/AlphaDataCenterCooling](https://github.com/wfzheng/AlphaDataCenterCooling) | 2026-07-05 | 37 | Paper-to-code/data mapping, minimal reproduction command, and mismatch notes. |

## How To Use This Matrix

1. Start with `ready:` items when the goal is to reduce not-run validation debt.
2. Use `blocked:` items for source-identification, datasheet, or artifact-availability work.
3. Record the exact command, input data, output metric, or reason execution remains unavailable in the next dated review log.
