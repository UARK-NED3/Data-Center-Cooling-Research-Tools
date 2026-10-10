# M100 provenance, reuse, and publication record

## Source record used by this benchmark

The initial local intake targets **M100 Dataset 12: 22-09**:

- DOI: [10.5281/zenodo.7590583](https://doi.org/10.5281/zenodo.7590583)
- Record: [Zenodo 7590583](https://zenodo.org/records/7590583)
- Publication date shown by the record: 2023-01-31
- License shown by the record: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- License and record metadata checked: 2026-10-10

The associated dataset paper is A. Borghesi *et al.*, “M100 ExaData: A data
collection campaign on the CINECA's Marconi100 Tier-0 supercomputer,”
*Scientific Data*, 2023, doi: [10.1038/s41597-023-02174-3](https://doi.org/10.1038/s41597-023-02174-3).

## Repository scope

This repository does not host, mirror, or redistribute raw M100 files,
extracted Parquet partitions, synchronized signal tables, or processed source
records. Users obtain the source archive independently from Zenodo and run the
local intake into a caller-selected directory outside the Git checkout.

The repository may publish original code, provenance manifests, aggregate
figures, summary statistics, and model-comparison results derived from the
source record when they i) cite the M100 paper and exact Zenodo record, ii)
follow the record-specific license and attribution requirements, and iii) do
not imply that the source observations are rehosted here.

## Interpretation restriction

Reuse rights do not establish physical validation. The published M100 metadata
currently do not document a power-to-panel mapping, panel-to-rack topology,
sensor locations, coolant specification, or measurement uncertainty record at
the level needed to validate a rack, rear-door heat-exchanger, or cold-plate
model. M100 results in this benchmark remain PLC-circuit diagnostics unless
those missing metadata are provided and audited.
