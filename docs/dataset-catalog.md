# External Data-Center Dataset Catalog

This catalog helps researchers find data-center datasets and judge whether a record can support a cooling-model task. It contains source metadata only. It does not host, mirror, transform, or redistribute third-party records, and it does not assert that a downloadable record is licensed for reuse.

The machine-readable source is [data/dataset_catalog.csv](../data/dataset_catalog.csv). Run `python scripts/check_dataset_catalog.py` after changing it.

## Scope and intended use

The catalog includes three distinct kinds of records:

| Record type | What it contains | Appropriate use | It does not establish |
| --- | --- | --- | --- |
| Measured operational telemetry | Signals collected during operation of an HPC, cloud, or cooling system | Telemetry analysis, control-oriented modeling, and data-contract audits | A calibrated rack model unless the heat path, topology, and sensor control volumes are known |
| Experiment and simulation case | A stated experimental configuration together with numerical inputs or outputs | Airflow/thermal CFD comparison within the stated configuration | General validity outside the documented geometry and operating conditions |
| Measured workload trace | Job or server utilization data without thermal signals | Constructing realistic heat-load schedules after a stated power model | Thermal or cooling-model validation |

The catalog deliberately excludes model repositories and tools that have no independent data package. Those belong in the main [software catalog](../README.md), not here.

## Metadata definitions

| Field | Meaning |
| --- | --- |
| `system_scale` | Physical extent represented by the record, from component/node to room or facility. |
| `cooling_architecture` | Cooling path explicitly reported by the original source. `not_reported` is intentional; it is not an inferred configuration. |
| `spatial_linkage` | Whether a signal can be tied to a component, node, rack, room, or loop. A node identifier alone is not a rack-to-loop mapping. |
| `primary_modalities` | Major measured or supplied variables, not a complete data dictionary. |
| `thermal_benchmark_role` | The narrow task the record could support. `workload_context_only` explicitly excludes thermal validation. |
| `benchmark_readiness` | A screening-level conclusion based only on the reviewed source record. It is not a claim of independent validation. |
| `rights_status` | License or rights statement located during catalog review. If a license was not identified, verify it with the source owner before reusing, redistributing, or publishing derivatives. |

## Curated records

| Dataset | Category and physical scope | Main variables and time base | Potential benchmark role | Access and rights status |
| --- | --- | --- | --- | --- |
| [M100 ExaData operational telemetry](https://zenodo.org/records/7588815) | Measured operational telemetry; Marconi100 compute nodes and facility. Liquid-cooling infrastructure and air conditioning are reported. | Node load, temperature, frequency, power, fan, and GPU metrics; also facility cooling, workload, alert, and weather metrics. The companion index spans March 2020 to September 2022. | Facility/loop behavior candidate only after sensor definitions, control volumes, uncertainty, and rack-to-panel/loop mappings are audited. It is not a direct rack-validation record as catalogued. | Downloadable Zenodo records with a [companion repository](https://gitlab.com/ecs-lab/exadata). No explicit license was identified in the reviewed record. |
| [M100 time-aggregated anomaly dataset](https://zenodo.org/records/7541722) | Derived operational telemetry; node and selected system metrics from M100. | Time-aggregated features intended for anomaly analysis across March 2020 to September 2022. | Node-telemetry modeling candidate. Parent metric definitions and spatial mappings remain prerequisites for any physical comparison. | Downloadable Zenodo record indexed by the [ExaData repository](https://gitlab.com/ecs-lab/exadata). No explicit license was identified in the reviewed record. |
| [HazardNet Marconi-A2 telemetry](https://zenodo.org/records/10050368) | Measured operational telemetry; 3,312 compute nodes at a Tier-0 system. | Inlet air temperature, outlet air temperature, and power from 14 January through 31 December 2019. | Node-level thermal-hazard or telemetry-modeling candidate. The reviewed record does not establish sensor locations or topology needed for a physics rack model. | Downloadable Zenodo record with [code](https://github.com/MSKazemi/HazardNet). No explicit license was identified in the reviewed record. |
| [OLCF Summit power and thermal measurements](https://doi.ccs.ornl.gov/dataset/086578e9-8a9f-56b1-a657-0ed8b7393deb) | Measured operational telemetry; CPU/GPU components and nodes in a system reported to use direct liquid cooling and rear-door heat exchangers. | Per-component power and temperature in 10-second and 1-minute aggregates from selected 2020-2022 months. | Node-telemetry modeling candidate. Rack/loop validation still needs topology and coolant-boundary metadata. | Official record with [companion code](https://github.com/at-aaims/summit_power_and_thermal_data). The companion repository states CC BY 4.0; follow the source terms and citation requirements. |
| [NREL ESIF HPC cooling-system measurements](https://github.com/M-D-Murphy/Data-Centre-Waste-Heat) | Measured operational telemetry; air-side and liquid-side facility cooling systems. | Supply temperature, return temperature, and cooling power at one-minute resolution for 12 months. | Facility or loop behavior candidate. Flow, control-volume definitions, and uncertainty information are still required before an energy-balance validation claim. | Public repository linking to NREL background material. No license was identified in the reviewed repository. |
| [Retrofitted air-cooled data-center experiment and OpenFOAM case](https://zenodo.org/records/6793217) | Experiment and simulation case; four racks and an in-row cooling unit. | Exhaust temperatures, flow rate, layout, and OpenFOAM cases for previous/retrofitted 2 kW cases; additional fictitious 15.5 kW cases. The reported temperature sampling frequency is 0.1 Hz. | Airflow/thermal CFD validation candidate within its published geometry and conditions. | Zenodo record and [Data in Brief article](https://doi.org/10.1016/j.dib.2022.108587). Confirm the source-record license before reuse or redistribution. |
| [University of Melbourne cloud PM logs](https://zenodo.org/records/10069402) | Measured operational telemetry; physical machines in a research cloud. | CPU, memory, network, power, CPU temperature, fan speed, and selected inlet-temperature signals. About 9 months and 5 months for the two sets, at 10-minute resolution. | Server load-to-power/temperature modeling candidate. It is not a rack or facility cooling validation case. | Downloadable Zenodo record with a [UCC 2023 paper](http://hpc.ec.tuwien.ac.at/files/UCC_23_data_center_analysis.pdf). No explicit license was identified in the reviewed record. |
| [Google clusterdata 2019](https://github.com/google/cluster-data/blob/master/ClusterData2019.md) | Measured workload trace; eight Borg cells, without thermal measurements. | Resource requests and usage, 5-minute CPU-usage histograms, alloc sets, and job-parent relationships. | Workload context only: may supply a demand schedule to a separately specified heat-generation model. It cannot validate a thermal or cooling model. | Google documentation states CC BY 4.0; access is via BigQuery and the source documentation. |
| [Alibaba GPU cluster trace v2026](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-gpu-v2026) | Measured operational workload trace; GPU servers with anonymized topology, without cooling telemetry. | Six months of hourly workload requests, GPU/CPU utilization, server inventory, anonymized topology, and selected network data. | Workload context only. The released topology does not supply cooling-system physics or validation measurements. | Download details and terms are in the source repository. A license was not identified during this catalog review. |

## Use and citation boundary

Download and cite a dataset from its original record. Before analysis or publication, inspect the source license, access terms, version, documentation, and any site-identification restrictions. Before redistributing raw data, processed data, figures based on nonpublic records, or trained models, obtain a dataset-specific rights determination.

For a cooling-model benchmark, the minimum addition beyond the dataset itself is a benchmark contract: declared geometry/topology; heat inputs and heat-path definitions; fluid properties and boundary conditions; variable units; time base and synchronization; sensor locations/control volumes; uncertainty or quality flags; and a split/evaluation plan. A large telemetry volume does not replace these items.

## Maintenance

Catalog rows are reviewed source descriptions, not endorsements. Add a record only after checking its original access page and companion documentation. Preserve `not_reported` and `license_not_identified` when that is the evidence state. Do not infer a cooling architecture, spatial mapping, calibration, or reuse right from a dataset title, repository location, or a public download button.
