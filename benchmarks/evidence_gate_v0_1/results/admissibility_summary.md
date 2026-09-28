# Evidence-gated benchmark admissibility summary

This generated report evaluates metadata contracts only. It contains no third-party observations, derived third-party results, or model-accuracy claims.

| Case | Decision | Benchmark score | Claim ceiling | Reasons |
| --- | --- | --- | --- | --- |
| m100_rdhx_q101_stress_test | conditional | not permitted | demonstration | unassigned_input_proxy, measurement_uncertainty_unknown |
| ocp_tcs_rack_v0_1 | admit | permitted | verification | none |
| retrofit_openfoam_smoke_test | block | not permitted | demonstration | undocumented_topology, incomplete_run, measurement_uncertainty_unknown |

## Minimum actions for blocked or conditional cases

### m100_rdhx_q101_stress_test
- `document_proxy_to_target_heat_or_load_mapping`
- `document_measurement_calibration_and_uncertainty`

### ocp_tcs_rack_v0_1
- No additional evidence action is registered for the stated verification scope.

### retrofit_openfoam_smoke_test
- `document_published_sensor_coordinate_to_cfd_sampling_location_mapping`
- `complete_measurement_aligned_model_run`
- `document_measurement_calibration_and_uncertainty`
