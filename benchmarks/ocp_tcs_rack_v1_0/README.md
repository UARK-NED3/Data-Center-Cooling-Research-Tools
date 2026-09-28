# Synthetic Rack Model-Comparison Suite v1.0

This NED3-authored suite defines a common technology cooling system (TCS)
control volume from the rack-manifold supply to rack-manifold return. It is a
synthetic, derived reference for software verification and controlled
model-structure comparison. It is not an OCP-certified test, vendor rack
specification, calibration record, or experimental validation dataset.

## Model levels

- **M1, quasi-steady rack balance.** The reference maps declared IT heat,
  liquid-capture fraction, coolant flow, and constant specific heat to return
  temperature. It has no thermal storage.
- **M2, two-node reduced-order model.** An effective hardware/cold-plate node
  and a mixed coolant-return node exchange heat through a declared effective
  conductance. The capacitances and conductance are illustrative synthetic
  values, not fitted physical properties.
- **M3, component-network adapter.** The planned Simscape Fluids adapter will
  accept this suite's inputs and return canonical results. It is intentionally
  not counted as a completed model run until the one-rack model, solver
  settings, and output mapping are committed with an executed run record.

The Python and MATLAB implementations of M1 are an independent
cross-language verification check. They are not independent model forms.

## Governing equations

The quasi-steady reference uses

\[
Q_{\ell}=f_{\ell}Q_{IT},\qquad
T_r=T_s+\frac{Q_{\ell}}{\dot m c_p}.
\]

M2 uses

\[
C_h\frac{dT_h}{dt}=Q_{\ell}-UA(T_h-T_r),
\]

\[
C_f\frac{dT_r}{dt}=UA(T_h-T_r)-\dot m c_p(T_r-T_s).
\]

The model excludes branch-level hydraulic maldistribution, component-specific
cold-plate correlations, pump power, CDU performance, facility heat
rejection, air-side recirculation, and hardware-calibrated parameters.

## Run

```powershell
python -m benchmarks.ocp_tcs_rack_v1_0.generate_artifacts
python -m unittest tests.test_v1_synthetic_suite -v
```

The generated results are public synthetic derivatives. They record source
hashes, declared model identities, and conservation residuals. No third-party
dataset is read by this suite.

## Claim boundary

Agreement with M1 verifies a declared heat balance. Agreement or disagreement
between M1 and M2 under the synthetic scenarios reveals the consequence of the
declared model structures. Neither result establishes prediction accuracy for a
physical rack. A future M3 result or field-data score requires a separate run
record and evidence-gate decision.
