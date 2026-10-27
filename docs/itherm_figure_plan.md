# ITherm Figure Architecture: Evidence-Gated Rack-Model Benchmark

This figure architecture is for the ITherm manuscript on an executable,
evidence-gated benchmark for liquid-cooled data-center rack models.  It is a
publication plan, not a claim that every planned capability has already been
executed. The public v1.1 results are synthetic and unvalidated. The M3
parallel-branch network is implemented in Python; a Simscape adapter remains
planned. M100, Summit, and Kuzay are reviewed only at the level supported by
their published metadata and the locally held records; no protected raw data
or derivatives are included in the repository.

## Narrative sequence

1. What physical rack-level prediction is being compared, and which signals sit
   on its boundary?
2. How does a catalog of tools become a comparison that is gated by evidence?
3. What inputs does the executable suite declare, and how do M1 and M2 respond?
4. Are the implementations numerically verified before they are interpreted?
5. What do M1, M2, and M3 predict at a common rack manifold?
6. Which declared parameters set the hidden hardware state, and which only set
   its response time?
7. Which public records document what a rack-model validation would need?
8. What does a real M100 PLC record support when the power-to-panel topology is
   not documented?

## Main figures and table (v0.5 manuscript)

Seven figures and one readiness table replace the ten figures of the v0.4
draft.  Two figures are double-column.

| ID | Question | Source | Evidence class and claim boundary |
| --- | --- | --- | --- |
| Fig. 1 | **Physical target.** What is inside the rack TCS boundary? | `docs/figures/itherm2027/fig_rack_tcs_schematic.tex` (TikZ). Supply and return manifolds, four synthetic branches, boundary signals ($T_s$, $\dot m$, $T_r$) versus branch states ($\dot m_i$, $T_{h,i}$), the 8 kW liquid and 2 kW residual-air paths, and the excluded CDU. | Conceptual drawing of the declared synthetic v1.1 case. Not a measured or commercial rack topology. |
| Fig. 2 | **Framework.** How does the evidence gate prevent an unsupported comparison? | `docs/figures/itherm2027/fig_evidence_gated_framework.tex` (TikZ). Tools hub, case contract, gate with an explicit *block* loop, adapters, M1/M2/M3 and a planned external solver, common metrics, claim tier set by gate status. | Framework design. M1--M3 implemented; external solver planned. |
| Fig. 3 | **Inputs and response.** What is applied to every model, and how do M1 and M2 respond? | `paper_figures.inputs_response_figure` from the v1.0 suite. | NED3-authored synthetic stimuli and model responses. |
| Fig. 4 | **Verification.** Does M2 converge to the exact solution at the expected order? | `paper_figures.convergence_figure`; closed-form reference `two_node_exact_state`. | Numerical verification only. |
| Fig. 5 | **Model structure.** Same bulk return, different hidden state. | `paper_figures.model_structure_figure` from the v1.1 scenario table (C1--C4). | Synthetic model-structure comparison; not hardware accuracy. |
| Fig. 6 | **Sensitivity.** Which parameter sets the equilibrium and which sets the response time? | `paper_figures.sensitivity_figure`; exact equilibrium and exact 98 % rise time. | Synthetic, one-at-a-time; not parameter identification. |
| Table IV | **Readiness.** Which published records document the rack TCS boundary? | Manuscript table (D/P/N with filled, half, and open symbols). | Metadata audit of cited sources; not a data-quality score. |
| Fig. 7 | **M100 conditional diagnostic.** | `benchmarks/m100_rdhx_v0_1/local_result_report.py`, written outside the repository. | Measured PLC records, derived screening quantities, unassigned power proxy. Local variants are labeled D0--D2 to keep them distinct from M1--M3. |

The v0.4 analytical M1 plot (temperature rise versus flow and an 8 kW / 2 kW
bar chart) is not carried forward: Eq. (2) states the $1/\dot m$ dependence and
Fig. 1 carries the heat split.

## Design rules

- Draw at printed size: 3.5 in single column, 7.16 in double column.  Include
  at `\columnwidth` or `\textwidth` with no further scaling.
- Arial (plots) or Helvetica (TikZ), 8 pt labels and 7 pt ticks;
  `publication_style.save_figure` refuses to write a figure with smaller text.
- No titles or footers inside figures; the caption states the evidence class.
- One color per entity across all figures (`publication_style.ENTITY_STYLE`):
  measured data black; supply blue; return vermillion; residual air gray;
  M1 sky blue circles; M2 orange squares; M3 green triangles; local M100
  variants D0--D2 reddish purple with distinct line styles.
- Categorical cases are plotted as markers, never joined by lines.
- Axis labels use *quantity, symbol (unit)* with SI exponent units.

## Promotion criteria

The implemented M3 result does not validate M3. A future Simscape
implementation can be added only after its input/output mapping, solver
settings, version, and run record are captured. A field-data comparison may
enter the main results only when the selected record documents the model
boundary, power-to-loop allocation, supply and return sensor positions, flow,
time alignment, coolant properties, uncertainty or quality flags, and rights
for the intended use.  Otherwise it remains a conditional diagnostic or a
data-readiness item.
