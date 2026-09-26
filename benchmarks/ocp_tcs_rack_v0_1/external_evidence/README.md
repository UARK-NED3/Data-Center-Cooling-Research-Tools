# External evidence intake

This directory provides small, reproducible adapters and source records for
third-party evidence used to assess the OCP-aligned rack benchmark.  It does
not redistribute third-party raw data, publisher PDFs, figures, or model code.

## Evidence classes

- `third_party_measured_time_series`: original measurements made available by
  another organization.
- `reported_table`: quantities transcribed from a paper table.
- `reported_relation`: an equation printed in a paper, sampled by this project.
- `digitized_figure`: points reconstructed from a plotted image.  These require
  an explicit calibration record and must not replace original measurements.

## NREL liquid-loop summary

The NREL ESIF HPC archive contains twelve monthly CSV files with a one-minute
nominal cadence.  Its duplicate temperature headers are mapped by the
documented position: columns 5--7 are liquid cooling power, supply temperature,
and return temperature.  The adapter deliberately retains the total source-row
count and separately flags rows with nonpositive reported liquid heat before
forming positive-heat aggregate statistics.

```powershell
python -m benchmarks.ocp_tcs_rack_v0_1.external_evidence.nrel_liquid_summary `
  --input-dir "C:\path\to\Data-Centre-Waste-Heat" `
  --output "C:\path\to\nrel_liquid_loop_summary.json"
```

`inferred_capacity_rate_kw_per_k = Q_dot / (T_return - T_supply)` is only a
derived screening quantity.  It is equivalent to mass-flow rate times specific
heat capacity only if the reported heat-flow and temperatures share a liquid
control volume.  The archive does not provide branch flow, pressure, rack
topology, or cold-plate thermal-resistance measurements.

## Paper-derived values

`stahlhut_2025_table_b1.csv` contains three values reported in Table B1 of the
open-access Stahlhut et al. paper.  The values remain labelled as reported table
data.  `stahlhut_2025_figure10_relation.csv` is sampled from the equation
printed inside Figure 10, not reconstructed from its plotted markers; this
avoids unnecessary digitization error.

Use digitized figures only when an equation or numerical table is unavailable.
For each new digitization, record the source PDF, page, figure, axis limits,
calibration coordinates, extraction date, and an uncertainty or verification
check.  Keep restricted PDFs and their rendered pages outside this repository.

## M100 liquid-circuit intake

The ExaData documentation identifies a Schneider PLC stream for the Marconi100
RDHx liquid-cooling circuit. It reports two flow sensors, active flow, supply
and return temperatures, delta-T, pump control output, and valve positions at a
20 s sampling period. The exact metric names and documented integer scalings
are captured in `m100_schneider_liquid_circuit_metrics.csv`.

This makes M100 a promising *dynamic liquid-loop and controller* comparison
case after download. It does not turn M100 into a cold-plate branch benchmark:
the documented signals are at the RDHx circuit scale and do not establish
individual cold-plate pressure losses, branch split, or chip temperature.

## Reuse boundary

The source registry is an intake record, not a redistribution license.  A
source with unknown or unassessed terms may be inspected locally but must not be
bundled into a public release.  Follow the data license and attribution of the
source record before using its code or data beyond local analysis.
