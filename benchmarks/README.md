# Benchmarks

This directory contains NED3-authored benchmark definitions, reference
calculations, provenance records, and model-adapter contracts. Third-party
model source code, model binaries, licensed data, and confidential facility
records are intentionally not included.

## Maturity labels

- **Synthetic verification case**: checks units, interfaces, conservation, and
  reproducible execution. It is not calibrated or experimentally validated.
- **Validated benchmark**: includes an authorized independent measurement or
  other traceable validation record, uncertainty information, and documented
  applicability limits.

The initial case is [OCP TCS Rack v0.1](ocp_tcs_rack_v0_1/README.md).

## Evidence gate

[Evidence-gated benchmark contracts v0.1](evidence_gate_v0_1/README.md)
provide a metadata-first admission check before a model is numerically scored.
They distinguish a valid verification calculation, a conditional diagnostic,
and a blocked comparison whose control volume, topology, input provenance, or
measurement-aligned execution is incomplete.
