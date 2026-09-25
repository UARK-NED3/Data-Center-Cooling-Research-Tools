# External-model adapters

An adapter must consume the canonical case inputs without silently changing
units, fluid properties, time basis, or heat-split definitions. Each adapter
run must record its external repository URL, immutable commit SHA or release,
runtime version, command, input hash, output schema, and unresolved mismatch.

Adapters may not vendor third-party source code, model binaries, licensed data,
or confidential facility records into this repository.

## Run-record contract

Start an adapter record from `run_record.template.json`. Validate it before
committing with:

```powershell
python -c "from benchmarks.ocp_tcs_rack_v0_1.adapters.validate_run_record import validate_run_record; validate_run_record('benchmarks/ocp_tcs_rack_v0_1/adapters/run_record.template.json')"
```

A `planned` record is not evidence of execution. A `completed` record requires
an immutable external-model revision and SHA-256 hashes for the canonical input
and produced output. `run_record.schema.json` is the machine-readable contract.

## MATLAB environment preflight

After installing the documented R2025b environment, start MATLAB and run:

```matlab
cd("<path-to-this-repository>/benchmarks/ocp_tcs_rack_v0_1/adapters")
report = matlab_preflight
```

The function writes `matlab_preflight_report.json` and checks MATLAB R2025b,
Simulink, Simscape, Simscape Electrical, Simscape Fluids, and Stateflow. It
does not clone, open, modify, or simulate the MathWorks project. Keep that
report local until a source revision, case-input mapping, and redistribution
status have been recorded.

## Candidate models

- **CompOpt**: a local rack-environment smoke run was completed at commit
  `4d9bfdc10d9c4bc42f99339a1913de3f64abe1ed`. Formal reuse remains pending
  maintainer confirmation because the repository packaging metadata says MIT
  but no standalone license file was present in the screened revision.
- **ORNL datacenterCoolingModel**: target only after the required Dymola,
  AutoCSM, TRANSFORM, and Modelica Buildings environment is available.
- **MathWorks Data-Center-Simscape**: target only after the documented R2025b
  baseline and required Simscape products are available. A newer release may
  be tested separately but is not the baseline until compatibility is recorded.
