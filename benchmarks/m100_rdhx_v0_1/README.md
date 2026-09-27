# M100 RDHx liquid-circuit benchmark, version 0.1

This benchmark is a reproducible intake and model-comparison contract for the
liquid cooling circuit monitored at the Marconi100 HPC facility. It is not a
direct-to-chip, cold-plate, or individual-rack benchmark. The public package
contains code, schemas, a synthetic test fixture, and documentation. It does
not distribute M100 observations or M100-derived result tables because the
source record's redistribution terms must be confirmed before publication.

## Engineering question

Can models predict the measured supply-to-return thermal and control response
of an RDHx liquid circuit under time-varying operation, using identical input
signals, output definitions, and contiguous time holdouts? The first output
targets are active flow, return temperature, and direct temperature rise. The
benchmark does not define an individual rack's fluid branch, pressure drop,
cold-plate temperature, or panel-to-rack topology.

## Data and signal scope

The initial intake targets M100 Dataset 12, September 2022, from the Marconi100
monitoring-data record. The Schneider PLC stream is sampled every 20 s per HMI
panel. The documented signals and integer scaling are recorded in
[`data_manifest.csv`](data_manifest.csv). The two panel identifiers, `Q101` and
`Q102`, are retained in every join. Do not join raw PLC signals on timestamp
alone.

For each synchronized timestamp and panel, the local analysis calculates

\[
\Delta T = T_{return} - T_{supply}, \qquad
\dot Q_{screen} = \rho\,c_p\,(\dot V/3600)\,\Delta T.
\]

`Q_screen` is a derived screening quantity at the PLC flow-and-temperature
control volume. The current code uses `rho = 997 kg m-3` and `cp = 4182 J kg-1
K-1` as explicit water-property assumptions. It is not an independent measured
heat rate, and Q101 plus Q102 must not be added until their physical topology
is documented.

## Evidence classes

| Item | Evidence class | Use | Restriction |
| --- | --- | --- | --- |
| PLC temperature, flow, control signals | Measured, source-reported | Model inputs and outputs | Panel-to-rack mapping is not documented here. |
| Temperature rise and screening heat rate | Derived | Signal audit and model diagnostic | Not independent validation data. |
| IT node power | Measured, source-reported | Candidate workload descriptor | Cannot be assigned to either PLC panel without topology evidence. |
| Analytical OCP case | Simulated reference | Software and dimensional-consistency check | Not calibrated against M100. |

## Local execution

The source archive must be downloaded separately. Keep it outside the Git
checkout. A user with access can extract only the required Parquet partitions
and run the analysis with a local output directory:

```powershell
python -m benchmarks.m100_rdhx_v0_1.local_intake `
  --source-root D:\path\to\selected_m100_partitions `
  --output-dir D:\path\to\private_outputs `
  --period 22-09 `
  --plot-start 2022-09-01T00:00:00Z `
  --plot-end 2022-09-02T00:00:00Z
```

The command records partition checksums, the date window, signal names,
property assumptions, and output locations in a local provenance file.
Install its local dependencies with
`python -m pip install -r requirements-m100-local.txt` from the repository
root. The command is intentionally not part of the default test suite because
it needs a separately obtained M100 source partition.

Before a public model-comparison claim, complete these gates:

1. Verify archive checksum and source permission for published derivatives.
2. Document whether Q101 and Q102 are redundant or independent loops and map
   each model control volume to the recorded sensors.
3. Use chronological holdouts. Never split adjacent 20-s records randomly.
4. Report prediction error against measured targets and independently report
   thermal residuals and uncertainty assumptions.

## Sources

- Marconi100 monitoring dataset, [Scientific Data article](https://doi.org/10.1038/s41597-023-02060-5).
- Dataset 12, [Zenodo record 7590583](https://zenodo.org/records/7590583).
- M100 source-layout and metric documentation in the [ExaData repository](https://github.com/necst/exadata).
