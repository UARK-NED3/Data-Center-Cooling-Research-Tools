# Evidence-gated benchmark contracts v0.1

This package decides whether a proposed cooling-model comparison is ready for
a numerical benchmark score. It evaluates metadata and declared evidence; it
does **not** calculate model accuracy or infer missing physical topology from
correlated signals.

## Why this exists

Data-center cooling models may predict a cold-plate temperature, rack return
temperature, PLC-panel signal, room sensor temperature, or facility heat
rejection. A comparison is scientifically meaningful only when the model and
measurement have the same quantity, unit, time basis, and control volume, and
when the relevant heat/cooling path and input provenance are documented.

The gate therefore returns one of three decisions:

| Decision | Meaning | Metric use |
| --- | --- | --- |
| `admit` | The stated metadata contract supports a score at its declared claim ceiling. | A benchmark score is permitted. This alone does not establish experimental validation. |
| `conditional` | The target matches, but a declared proxy or uncertainty limitation remains. | Diagnostic metrics may be reported with the limitation; do not present them as a validation score. |
| `block` | A required match, input-evidence item, topology link, or measurement-aligned run is missing. | Do not produce a benchmark score. Use the gap report to plan the minimum additional evidence. |

## Registered contracts

- `ocp_tcs_rack_v0_1.json` — NED3-authored synthetic rack case. It is
  admitted for cross-implementation verification, not hardware validation.
- `m100_rdhx_q101_stress_test.json` — local M100 PLC-circuit stress test.
  Facility-wide IPMI power is explicitly recorded as an unassigned proxy, so
  the contract is conditional and cannot validate a panel, RDHx, rack, or
  cold-plate model.
- `retrofit_openfoam_smoke_test.json` — derived OpenFOAM execution record for
  the public retrofit case. It is blocked because a short smoke run and
  assumed sensor-coordinate mapping are not a measurement-aligned CFD
  validation.

The contracts contain metadata only. They do not host M100, Summit, NREL, or
retrofit observations, or derived third-party result tables.

## Reproduce the metadata report

From the repository root:

```powershell
python -m benchmarks.evidence_gate_v0_1.generate_reports `
  --output-dir benchmarks/evidence_gate_v0_1/results
```

This writes a machine-readable JSON summary and a Markdown report. The checked
in [admissibility summary](results/admissibility_summary.md) is deterministic
for the bundled contracts.

## Contract fields

`case_contract.schema.json` provides a portable schema, while
`contracts.py` validates the supported fields without requiring the external
`jsonschema` package. Each contract declares:

- prediction and measurement quantity, unit, time basis, and control volume;
- model inputs and whether each is documented, a proxy, or unknown;
- named topology links and their documentation status;
- source/rights boundary and whether raw data enter the repository; and
- run and validation state.

The `build_run_record` function produces a canonical SHA-256-addressed record
of a model identity, input/output hashes, environment, evidence decision, and
rights boundary. It is designed for local results and does not grant permission
to release a source-data derivative.

## Extension rule

Add a new model or data case by adding a contract and tests. Do not change an
`unknown` or `assumed` topology link to `documented` unless a citable source or
authorized facility record establishes that link.
