# External-model adapters

An adapter must consume the canonical case inputs without silently changing
units, fluid properties, time basis, or heat-split definitions. Each adapter
run must record its external repository URL, immutable commit SHA or release,
runtime version, command, input hash, output schema, and unresolved mismatch.

Adapters may not vendor third-party source code, model binaries, licensed data,
or confidential facility records into this repository.

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
