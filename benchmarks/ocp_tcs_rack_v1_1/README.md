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

`generate_artifacts.py` evaluates four deterministic cases:

1. **Balanced reference:** M3 must reduce to the whole-rack energy balance.
2. **Nominal nonuniform:** declared branch heat loads and resistances vary.
3. **Hydraulic imbalance:** one branch has increased resistance at equal heat load.
4. **Coupled load-hydraulic stress:** high branch heat load coincides with increased resistance.

The intended comparison is whether identical bulk heat and flow conditions can
hide different branch-flow and effective-hardware-temperature predictions.
The results do not identify a best model for physical equipment.

## Run

```powershell
python -m benchmarks.ocp_tcs_rack_v1_1.generate_artifacts
python -m unittest tests.test_v1_1_multibranch_suite -v
```

The checked-in CSV, SVG, and JSON files under `results/` are public synthetic
derivatives.  The PNG is a local preview and is intentionally ignored.

## Claim boundary

M1/M2/M3 agreement in mixed return temperature verifies compatibility with the
declared control volume.  M3 differences in effective branch temperature,
flow distribution, pressure drop, or pump power are model-structure findings.
They become hardware-accuracy claims only after a separately evidence-gated,
measurement-aligned validation case supplies the required topology, boundary,
sensor, uncertainty, and rights information.
