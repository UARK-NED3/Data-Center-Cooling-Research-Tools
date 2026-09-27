# M100 RDHx liquid-circuit analysis plan

## Current status

The benchmark repository contains only the documented metric map. The M100
Parquet archive is not yet present in the local research-data directory, so no
M100 result, model fit, or validation statistic has been produced.

The intended M100 lane is a **dynamic RDHx liquid-circuit comparison**, not a
cold-plate or rack-branch benchmark. Its evidence scope complements the
Frontier facility-secondary-loop and NREL hybrid-cooling records.

## Questions and testable hypotheses

1. Can a model reproduce the observed coupled temperature and flow response of
   the RDHx circuit across changing HPC workloads?
   - Inputs: synchronized node or job power, supply temperature, and controller
     commands.
   - Outputs: return temperature, temperature rise, active flow, sensor flows,
     pump PID output, and valve positions.
   - Decision measures: held-out MAE, bias, peak error, and lag for each output.

2. Does the circuit show load-dependent control action that a steady-state
   energy balance would miss?
   - Prediction: for similar IT power, changes in supply temperature, pump
     command, or valve position shift the flow and temperature-rise trajectory.
   - Evidence: matched operating windows, lag estimates, and a dynamic-model
     comparison against a quasi-steady baseline.

3. Can three independent implementations agree on the same measurable circuit
   behavior?
   - Candidate implementations: a transparent first-principles dynamic model,
     a Simscape Fluids implementation, and a facility-system implementation
     such as an EnergyPlus adapter at a coarser compatible time base.
   - Agreement is assessed against measurements and against one another. A
     model is not credited merely because it conserves heat algebraically.

## Intake and quality-control gates

1. Record the downloaded archive version, checksum, file list, coverage,
   timezone, and exact metric names before extracting signals.
2. Decode documented integer scales. For example, `Temp_mandata`,
   `Temp_ritorno`, and `Delta_temp` use a factor of 10; two flow sensors use a
   factor of 50; active flow uses a factor of 10; valve positions use a factor
   of 100.
3. Audit duplicate timestamps, gaps, missing values, implausible signs, and
   nonphysical values before filtering. Preserve exclusions in a quality flag
   table rather than deleting rows silently.
4. Verify that the reported `Delta_temp` agrees with decoded return-minus-supply
   temperature within the documented resolution. Compare the two flow-sensor
   readings with active flow only after their control-volume definitions are
   established.
5. Align power/workload signals and PLC signals on a documented time base.
   Use contiguous holdout periods, rather than random individual rows, to avoid
   temporal leakage.

## Figures to generate after intake passes

| Figure | Data and reduction | Scientific purpose |
| --- | --- | --- |
| Signal integrity | Decoded supply, return, and reported delta-T. Flow sensors and active flow. Gaps and quality flags. | Establish which signals can be compared and whether their reported scales and time bases are coherent. |
| Event trace | A pre-registered 24-hour or step-load interval with IT power, supply/return temperature, flow, pump output, and valve positions. | Show coupled thermal and control dynamics, including delay and saturation. |
| Operating surface | Binned return temperature or delta-T versus IT power and active flow, stratified by supply-temperature band. | Separate load, flow, and inlet-temperature effects without collapsing unlike operating conditions. |
| Lag and frequency response | Cross-correlation and identified step-response metrics for workload-to-temperature and command-to-flow paths. | Quantify dynamics that a static heat-balance calculation cannot reproduce. |
| Model validation | Held-out measured versus predicted flow, return temperature, and delta-T, with bias and residual time traces. | Compare model accuracy and failure modes. |
| Cross-implementation comparison | Common input trace, initial condition, time base, and output definitions for the three models. | Distinguish numerical/implementation disagreement from error against measurements. |
| Guardrailed counterfactual | Only after validation. Small supply-temperature or flow-control perturbations screened against observed temperature limits. | Evaluate control tradeoffs without claiming deployable savings. |

## Required result records

Every model run should declare the raw-data version, metric scaling, selected
time window, synchronization rule, fluid-property assumption, initial state,
control configuration, numerical time step, output definitions, and exclusions.
The model must report its thermal residual and any pressure-drop or pump-power
assumptions. M100 does not provide a cold-plate branch pressure-drop
measurement, so that output remains unvalidated unless an additional dataset
is obtained.

## Stopping rules

- If the PLC and workload streams cannot be synchronized, limit the work to
  liquid-circuit quality assessment and do not claim coupled IT-to-cooling
  prediction.
- If flow and temperature signals fail the documented consistency checks, do
  not use them as validation targets until the schema or source contact resolves
  the discrepancy.
- If only a facility-scale flow and temperature response is available, retain
  the facility/RDHx label. Do not relabel the result as rack or cold-plate
  validation.
