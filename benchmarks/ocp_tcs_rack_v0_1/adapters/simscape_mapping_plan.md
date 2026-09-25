# MathWorks Data-Center-Simscape mapping plan

## Evidence status

This is an adapter-planning record, not a completed simulation, calibrated
comparison, or validation result. The external source was inspected at commit
`6bafcf54315b59ffe41f30f5da276db48a0e4965`:

- Source: <https://github.com/simscape/Data-Center-Simscape>
- License declared by the source: BSD-3-Clause.
- Documented project entry point: `DataCenterDesignSimscape.prj`.
- Inspected liquid-cooling workflow:
  `Workflow/HVAC/DatacenterLiquidCooling.m`.

The workflow creates a thermal 12-rack, 6 MW data-center model and attaches a
CDU pipe layout. It is useful as an external-model execution target, but it is
not the v0.1 rack case and must not be presented as one.

## Canonical-case mapping status

| v0.1 quantity | Unit | Candidate external quantity | Status | Reason |
| --- | --- | --- | --- | --- |
| `rack.it_heat_w = 10000` | W | `RatingDatacenter` plus server nameplate and utilization inputs | Unresolved | The published workflow uses a 6 MW aggregate design rating. A 10 kW realized heat load needs an explicit one-rack configuration and a verified measurement point. |
| `rack.liquid_capture_fraction = 0.8` | 1 | No identified published signal | Unmapped | The external workflow describes liquid cooling at each rack but does not expose the 80/20 liquid-versus-air heat split required by v0.1. |
| `tcs.supply_temperature_c = 30` | degC | No identified published parameter | Unresolved | The liquid-loop supply state must be traced to an external block parameter or measured signal before comparison. |
| `tcs.mass_flow_kg_s = 0.5` | kg/s | No identified published parameter or output | Unresolved | Flow must be read from or set at an identified liquid-domain measurement or boundary block. |
| `fluid.specific_heat_j_kg_k = 4180` | J/(kg K) | Simscape fluid-property definition | Unresolved | The external model's fluid and property state must be recorded rather than assumed equivalent. |
| TCS return temperature | degC | `simRes.temperature_degC.serverCoolantOutlet` | Candidate output | The utility reports a server-coolant outlet temperature; signal location and physical equivalence to the v0.1 TCS return remain to be verified. |
| cooling auxiliary power | kW | `simRes.avgAuxLosses_kW.*` | Candidate supplemental output | This lies outside the v0.1 conservation oracle and cannot be used for a v0.1 agreement metric. |

## Staged use

1. **Upstream smoke run:** run the untouched 12-rack, 6 MW workflow after a
   passing environment preflight. Record the exact command, source revision,
   runtime, and output hash. This establishes only local reproducibility of
   the upstream example.
2. **Adapter design review:** identify the source blocks and measurements needed
   for one rack, 10 kW IT heat, 30 degC supply, and 0.5 kg/s TCS flow. Preserve
   an external copy of the source; do not modify or vendor the upstream project.
3. **Canonical comparison:** implement a separate adapter configuration only
   after every table row above has an explicit source/measurement mapping. The
   0.8 liquid-capture fraction needs a modeled or measured residual-air path;
   otherwise it remains out of scope rather than silently set to 1.0.

## Current blocker

The local R2025b preflight found all required products except Stateflow. Do not
run the project until the preflight reports `ready: true`, because the upstream
project lists Stateflow among its required products.
