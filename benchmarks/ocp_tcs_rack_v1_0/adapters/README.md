# External model adapters

An adapter converts a benchmark case into a model-specific input set and
returns canonical result variables without silently changing the system
boundary. An external model is not considered benchmarked merely because it
opens or simulates. A completed adapter must provide an executed run record,
model revision, solver settings, input mapping, output mapping, and declared
unsupported quantities.

`simscape_adapter_contract.json` is a planning contract for a one-rack
Simscape Fluids implementation. The record deliberately states `planned`; it
must not be used as evidence of an executed M3 result.
