# ITherm 2027 schematics

TikZ sources for the two schematics in the evidence-gated benchmark manuscript.
Both are drawn at IEEE print width (3.5 in and 7.16 in) with 7 pt and 8 pt
Helvetica labels, so they should be included at `\columnwidth` or
`\textwidth` without further scaling.

| File | Figure | Content |
| --- | --- | --- |
| `fig_rack_tcs_schematic.tex` | Fig. 1 | Rack TCS control volume for the synthetic v1.1 suite: manifolds, four branches, boundary signals versus M3 branch states, liquid and residual-air heat paths, excluded CDU. |
| `fig_evidence_gated_framework.tex` | Fig. 2 | Tools hub, case contract, evidence gate with the block loop, adapters, M1--M3, common metrics, and the claim tier set by gate status. |

Build each with `pdflatex <file>.tex`; the PDFs are committed alongside the
sources.  The heat values in Fig. 1 are the declared synthetic baseline in
`benchmarks/ocp_tcs_rack_v1_1/suite.json`, not measurements.
