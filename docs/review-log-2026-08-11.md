# Sustainability Catalog Update: 2026-08-11

## Scope

Added a dedicated sustainability topic to the public research-tools catalog and refreshed the GitHub discovery corpus. This pass is source inspection and catalog curation, not independent reproduction of third-party tools or measured facility-impact validation.

## Sources Screened

| Resource | Directly checked evidence | Catalog decision |
| --- | --- | --- |
| [UARK-NED3/OpenDC-LCA](https://github.com/UARK-NED3/OpenDC-LCA) | Public GitHub metadata and README: active MIT-licensed repository; cooling-system life-cycle screening for greenhouse gas, primary energy, and blue water; documentation explicitly limits claims to screening when decision-grade foreground/background data and uncertainty are absent. | Included as an LCA screening tool with an explicit screening boundary. |
| [Data-Center Exposure Atlas](https://hanhuark.github.io/Data-Center-Water-Research/atlas/) | Live public page returned HTTP 200 and identifies itself as an interactive U.S. water-data validation-priority layer; it explicitly labels stress classes as modeled screening estimates rather than measured impacts. | Included as an interactive water-exposure screening resource. |
| [LukeJYK/IPDPS26_WaterSplit](https://github.com/LukeJYK/IPDPS26_WaterSplit) | Public GitHub metadata and README: active MIT-licensed paper artifact with hybrid wet/dry cooling model, PUE/on-site WUE estimates, cooling-allocation optimization, and workload scheduling. | Included as a source-inspected paper artifact; execution, input/assumption review, and result matching remain open. |
| [HewlettPackard/sustain-cluster](https://github.com/HewlettPackard/sustain-cluster) | Public GitHub metadata and README: active MIT-licensed multi-data-center scheduling benchmark with weather, price, carbon, AI-trace, and documented data-center/HVAC proxy inputs. | Included as a source-inspected benchmark; data-license, thermal/HVAC-assumption, and smallest-run checks remain open. |
| [cloud-carbon-footprint/cloud-carbon-footprint](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint) | Public GitHub metadata and README: active Apache-2.0 tool with methodology and CI metadata for public-cloud energy/carbon estimation. | Included as adjacent workload-boundary carbon accounting, explicitly not as a cooling, water, or LCA solver. |
| [ExaDigiT/RAPS](https://github.com/ExaDigiT/RAPS) | Official ExaDigiT and ORNL software records describe an ORNL-led liquid-cooled-supercomputer digital-twin framework with a Python resource allocator/power simulator, Modelica thermo-fluid cooling model, and visualization module. The public RAPS mirror documents Python 3.9+ setup, synthetic-workload and telemetry-replay paths, CDU-level FMU interaction, and plotting; GitHub metadata reports no asserted SPDX license. | Included in the AI/control/digital-twins section as public research software. Local run, FMU/model dependency review, telemetry-access review, and reuse-term confirmation remain open. |

## Discovery Refresh

The public GitHub Search API refresh completed on 2026-08-11 after adding these repeatable streams to `scripts/discover_github_repos.py`:

- `data center sustainability`
- `data center water cooling`
- `data center life cycle assessment`

The resulting candidate report contains 78 unique repositories. It is a discovery aid, not an automatic citation or promotion list; source inspection and claim-boundary review remain required before adding later candidates to the main catalog.

## Verification

| Check | Result |
| --- | --- |
| Runtime prerequisite check | Passed: Python, Python launcher, Git, `latexmk`, and `pdflatex` were available in the active shell. |
| Discovery refresh | Passed: `py -3.12 scripts/discover_github_repos.py --per-page 15` wrote the CSV and Markdown candidate reports. |
| Catalog build | Passed: `py -3.12 scripts/build_catalog_assets.py --generated-on 2026-08-11` parsed 81 resources across 8 sections. |
| Catalog quality gate | Passed: `py -3.12 scripts/check_catalog_quality.py --generated-on 2026-08-11` reported 0 failures and 0 warnings. |

## Remaining Limits

- The five additions are source-inspected catalog entries. No third-party benchmark, scheduler, accounting tool, or OpenDC-LCA workflow was locally executed in this pass.
- The Atlas is a modeled screening layer; it is not a measured site-level water-impact inventory.
- The discovery report surfaces candidates only. It does not establish physical-model validity, licensing compatibility beyond the directly inspected entries, or operational effectiveness.
