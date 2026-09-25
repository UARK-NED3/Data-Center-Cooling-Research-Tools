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

## Local structural inspection

The passing R2025b preflight was followed by a read-only local structural
inspection of the published `DataCenterCooling.slx` model at the source
revision above. The generated inspection artifact remains local because it
contains an absolute checkout path. The inspection did not simulate or save
the external model.

- The model declares the `daessc` solver and a stop-time expression of
  `(env.nDays-1)*24*3600`; the source initialization file sets `env.nDays =
  8`, so the published workflow is configured for a seven-day horizon.
- The loaded model contained 777 blocks, including twelve repeated
  `Datacenter_i_j` server-unit blocks under a 3-by-4 data-center layout and a
  CDU pipe-layout subsystem.
- A representative `Datacenter_1_1` mask exposes component-level server
  nameplate inputs, utilization, and power-supply efficiency. Its published
  values include 3,326 CPUs per server unit, a 0.6 actual-to-nameplate ratio,
  and 0.85 power-supply efficiency. These are source-model configuration
  values, not a 10 kW rack calibration or a measured heat load.
- The inspected structure does not identify an explicit 30 degC TCS-supply
  boundary, a 0.5 kg/s rack-flow boundary, or an 80/20 liquid-versus-air heat
  split. Pipe `mdot_nominal` fields are component parameters and are not, by
  themselves, a canonical rack-flow mapping.

The source therefore supports a future, separately constructed one-rack
Simscape adapter, but the existing 3-by-4 example cannot be relabeled as the
v0.1 case by changing the aggregate 6 MW rating alone.

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

The local R2025b preflight now reports `ready: true` with all products listed
by the upstream project, including Stateflow. The remaining blocker is model
definition, not software installation: a one-rack derivative needs explicit
source/measurement mappings for IT heat, TCS supply temperature, rack flow,
fluid properties, and the residual-air heat path before it can produce a
canonical comparison.
