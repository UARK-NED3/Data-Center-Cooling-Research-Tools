# OCP TCS Rack v0.1

`ocp-tcs-rack-v0.1` is a NED3-authored, synthetic, steady-state verification
case for a liquid-cooled rack technology-cooling system (TCS). It uses an
OCP-aligned loop topology, but it is **not** an OCP-certified case, a vendor
rack specification, a calibrated cooling model, or an experimental validation
dataset.

## Purpose

The case provides a common, minimal contract for checking that an adapter
reports heat-path quantities and TCS inlet/outlet temperatures with consistent
units and sign conventions. Its analytical reference uses

\[
Q_{\rm liquid}=f_{\rm liquid}Q_{\rm IT},
\qquad
Q_{\rm air}=Q_{\rm IT}-Q_{\rm liquid},
\qquad
T_{\rm return}=T_{\rm supply}+\frac{Q_{\rm liquid}}{\dot m c_p}.
\]

The steady rack energy residual is

\[
R_{\rm rack}=Q_{\rm IT}-Q_{\rm liquid}-Q_{\rm air}.
\]

The required value is zero to floating-point tolerance because the v0.1
reference has no thermal storage term.

## Files

- `case.json`: canonical synthetic input values and explicit exclusions.
- `case.schema.json`: machine-readable input contract.
- `provenance.csv`: source, units, and evidence class for every core input.
- `analytical_reference.py`: dependency-free verification oracle.
- `generate_reference_results.py`: deterministic baseline and flow-sweep
  artifact generator.
- `results/`: generated synthetic results, source hashes, and an SVG figure.
- `adapters/run_record.schema.json`: external-run traceability contract.
- `adapters/matlab_preflight.m`: a local R2025b product check that does not
  open or run a third-party model.
- `adapters/matlab_steady_state_reference.m`: an independent MATLAB
  implementation of the declared steady energy balance.
- `adapters/`: external-model integration contracts. No external source code
  is vendored.

## Run

From the repository root:

```powershell
python -m benchmarks.ocp_tcs_rack_v0_1.analytical_reference
python -m benchmarks.ocp_tcs_rack_v0_1.generate_reference_results
python -m unittest discover -s tests -q
```

With MATLAB R2025b, evaluate the independent MATLAB implementation and compare
its output to the Python result:

```matlab
addpath("benchmarks/ocp_tcs_rack_v0_1/adapters")
matlab_steady_state_reference( ...
    "benchmarks/ocp_tcs_rack_v0_1/case.json", ...
    "local_matlab_result.json")
```

```powershell
python -m benchmarks.ocp_tcs_rack_v0_1.adapters.build_matlab_comparison `
  local_matlab_result.json `
  benchmarks/ocp_tcs_rack_v0_1/results/canonical_steady_state_result.json `
  local_matlab_comparison.json
```

## What v0.1 does not establish

It does not establish cold-plate temperatures, hydraulic pressure drops, CDU
performance, pump power, facility energy, water use, transient response, or
agreement with measured equipment. Those require authorized component curves
and an independent validation record before a later benchmark version can make
such claims.
