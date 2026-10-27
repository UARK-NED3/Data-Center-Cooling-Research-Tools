# Synthetic Multi-Branch Liquid-Rack Suite v1.1

This NED3-authored benchmark extends the v1.0 rack-manifold control volume
with four synthetic parallel liquid branches.  It is designed for controlled
model-structure comparison and code verification.  It is not a vendor-rack
specification, OCP-certified test, fitted component model, or empirical
validation dataset.

## Model levels

- **M1:** whole-rack quasi-steady energy balance from the v1.0 suite.
- **M2:** mixed two-node effective hardware/coolant model from the v1.0 suite.
- **M3:** parallel-branch thermal-hydraulic network implemented in this folder.

For M3, every branch obeys the synthetic hydraulic closure

\[
\Delta p_i = K_i\dot m_i^2, \qquad \sum_i \dot m_i = \dot m_{rack},
\]

and a branch liquid balance

\[
T_{r,i}=T_s+\frac{Q_{\ell,i}}{\dot m_i c_p}.
\]

The effective branch hardware state is defined by

\[
T_{h,i}=T_{r,i}+\frac{Q_{\ell,i}}{UA_i}.
\]

The pressure-drop and pump-power outputs depend on declared synthetic
resistances, density, and pump efficiency.  They do not represent a measured
pump curve or cold-plate correlation.

## Mechanism-focused scenarios

`suite.json` declares four deterministic cases, each with its full branch
table, so that an external implementation can reproduce them without reading
this repository's Python:

1. **C1 balanced reference:** M3 must reduce to the whole-rack energy balance.
2. **C2 nominal nonuniform:** declared branch heat loads, resistances, and UA vary.
3. **C3 hydraulic imbalance:** branch B4 resistance is increased fourfold at equal heat load.
4. **C4 coupled load-hydraulic stress:** branch B1 carries 55 % of the heat with a tripled resistance.

M1 uses the heat-weighted aggregate capture fraction.  M2 is evaluated at its
closed-form constant-input equilibrium with summed branch UA and
capacitances; a 1,800 s forward-Euler run is kept as a settling cross-check.
The intended comparison is whether identical bulk heat and flow conditions can
hide different branch-flow and effective-hardware-temperature predictions.
The results do not identify a best model for physical equipment.

## Run

```powershell
python -m benchmarks.ocp_tcs_rack_v1_1.generate_artifacts
python -m benchmarks.ocp_tcs_rack_v1_1.paper_figures
python -m pytest tests/test_v1_1_multibranch_suite.py tests/test_itherm_paper_figures.py
```

`paper_figures.py` writes the ITherm publication figures to `results/itherm/`
at printed IEEE size, each with the CSV of plotted values, plus
`itherm_figure_metrics.json` with every scalar quoted in the manuscript
(observed convergence order, normalized residual, rise times).  The checked-in
CSV, SVG, PDF, and JSON files are public synthetic derivatives; PNG previews
are ignored.

## Claim boundary

M1/M2/M3 agreement in mixed return temperature verifies compatibility with the
declared control volume.  M3 differences in effective branch temperature,
flow distribution, pressure drop, or pump power are model-structure findings.
They become hardware-accuracy claims only after a separately evidence-gated,
measurement-aligned validation case supplies the required topology, boundary,
sensor, uncertainty, and rights information.
