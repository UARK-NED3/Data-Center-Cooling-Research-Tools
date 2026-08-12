# Validation Next Actions

Generated on 2026-08-11 from `README.md` metadata.

This report converts the validation queue into a finite daily closure batch. It favors stale `ready:` rows, high-priority caveats, and blockers that need demotion, reclassification, or retained-blocked evidence. It is a planning artifact, not reproduction evidence.

## Batch Summary

| Metric | Count |
| --- | ---: |
| Queued resources | 49 |
| Selected next-action resources | 8 |
| Selected ready items | 8 |
| Selected blocked items | 0 |
| Selected stale items (7+ days) | 8 |
| Selected high-priority items | 5 |

## Selected Validation Closure Batch

| Rank | Resource | Track | Readiness | Reviewed | Age (days) | Why this now | Probe template | Evidence packet |
| ---: | --- | --- | --- | --- | ---: | --- | --- | --- |
| 1 | [rishithayanidhi/Data_Center_Cooling_Optimization_Environment](https://github.com/rishithayanidhi/Data_Center_Cooling_Optimization_Environment) | local code smoke test | ready: local code smoke test | 2026-06-27 | 45 | stale queue item; ready for closure evidence; untouched not-run row; high-priority caveat | Install documented dependencies and run the smallest CLI, script, notebook, or import check that exercises the advertised workflow. | Smoke-test command, environment, observed output, and unresolved errors. |
| 2 | [c50346867/data-center-pue-optimizer](https://github.com/c50346867/data-center-pue-optimizer) | educational/prototype scope check | ready: test-suite or example smoke test | 2026-06-29 | 43 | stale queue item; ready for closure evidence; untouched not-run row; high-priority caveat | Inspect files or run the smallest demo to identify equations, inputs, assumptions, outputs, and validation gaps. | Small run or code inspection showing assumptions, limits, and teaching/prototype scope. |
| 3 | [Jalaljalili/Cooling-Dynamic-Model](https://github.com/Jalaljalili/Cooling-Dynamic-Model) | educational/prototype scope check | ready: local code smoke test | 2026-07-01 | 41 | stale queue item; ready for closure evidence; untouched not-run row; high-priority caveat | Inspect files or run the smallest demo to identify equations, inputs, assumptions, outputs, and validation gaps. | Small run or code inspection showing assumptions, limits, and teaching/prototype scope. |
| 4 | [Lucabr01/RL-and-Gradient-Free-Based-Datacenter-Cooling-Controller](https://github.com/Lucabr01/RL-and-Gradient-Free-Based-Datacenter-Cooling-Controller) | educational/prototype scope check | ready: local code smoke test | 2026-07-01 | 41 | stale queue item; ready for closure evidence; untouched not-run row; high-priority caveat | Inspect files or run the smallest demo to identify equations, inputs, assumptions, outputs, and validation gaps. | Small run or code inspection showing assumptions, limits, and teaching/prototype scope. |
| 5 | [4g/dcool](https://github.com/4g/dcool) | independent validation search | ready: notebook review or execution | 2026-07-01 | 41 | stale queue item; ready for closure evidence; untouched not-run row; high-priority caveat | Search papers, issues, releases, and third-party uses for independent validation; retain an unvalidated label if none is found. | Independent validation source or retained unvalidated label with dated search note. |
| 6 | [DOE/LBNL data center Modelica toolkit](https://sites.psu.edu/sbslab/publications/tools/end-to-end-modeling-and-optimization-package-for-data-center-cooling/) | local code smoke test | ready: local code smoke test | 2026-06-22 | 50 | stale queue item; ready for closure evidence; untouched not-run row | Install documented dependencies and run the smallest CLI, script, notebook, or import check that exercises the advertised workflow. | Smoke-test command, environment, observed output, and unresolved errors. |
| 7 | [lbl-srg/modelica-buildings](https://github.com/lbl-srg/modelica-buildings) | local code smoke test | ready: local code smoke test | 2026-06-22 | 50 | stale queue item; ready for closure evidence; untouched not-run row | Install documented dependencies and run the smallest CLI, script, notebook, or import check that exercises the advertised workflow. | Smoke-test command, environment, observed output, and unresolved errors. |
| 8 | [UARK-NED3/AELab](https://github.com/UARK-NED3/AELab) | local code smoke test | ready: local code smoke test | 2026-06-22 | 50 | stale queue item; ready for closure evidence; untouched not-run row | Install documented dependencies and run the smallest CLI, script, notebook, or import check that exercises the advertised workflow. | Smoke-test command, environment, observed output, and unresolved errors. |

## Selected Tracks

| Track | Count |
| --- | ---: |
| local code smoke test | 4 |
| educational/prototype scope check | 3 |
| independent validation search | 1 |

## Daily Closure Rule

Close at least one selected `ready:` row with command/output evidence, or convert one selected blocked row into a dated demotion, reclassification, non-applicability, or retained-blocked decision before adding new catalog candidates.
