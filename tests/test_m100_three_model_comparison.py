"""Specification tests for distinct RDHx temperature-response model classes."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from benchmarks.m100_rdhx_v0_1.model_comparison import (
    fit_m0_load_fraction,
    predict_m0_quasisteady,
    simulate_m1_lumped,
    simulate_m2_two_state,
    split_contiguous_time_series,
)
from benchmarks.m100_rdhx_v0_1.local_three_model_benchmark import (
    build_panel_comparison_frame,
    calculate_error_metrics,
    run_three_model_comparison,
)


class ThreeModelComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.supply_c = np.full(500, 18.0)
        self.mass_flow_kg_s = np.full(500, 2.0)
        self.load_kw = np.full(500, 20.0)
        self.cp_j_kgk = 4000.0
        self.dt_s = 10.0

    def test_m0_matches_the_declared_steady_energy_balance(self):
        prediction = predict_m0_quasisteady(
            self.supply_c,
            self.mass_flow_kg_s,
            self.load_kw,
            load_to_circuit_fraction=1.0,
            cp_j_kgk=self.cp_j_kgk,
        )

        self.assertTrue(np.allclose(prediction, 20.5))

    def test_m0_fit_respects_a_declared_physical_fraction_bound(self):
        observed_return_c = np.full(10, 21.0)
        fraction = fit_m0_load_fraction(
            self.supply_c[:10],
            self.mass_flow_kg_s[:10],
            self.load_kw[:10],
            observed_return_c,
            cp_j_kgk=self.cp_j_kgk,
        )

        self.assertEqual(fraction, 1.0)

    def test_split_keeps_later_samples_out_of_parameter_selection(self):
        train, validation, test = split_contiguous_time_series(10, train_fraction=0.6, validation_fraction=0.2)

        self.assertEqual(train.tolist(), [0, 1, 2, 3, 4, 5])
        self.assertEqual(validation.tolist(), [6, 7])
        self.assertEqual(test.tolist(), [8, 9])

    def test_panel_frame_uses_only_complete_power_bins_and_one_panel(self):
        plc = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2022-09-01T00:00:00Z", "2022-09-01T00:00:20Z", "2022-09-01T00:00:00Z"], utc=True
                ),
                "panel": ["Q101", "Q101", "Q102"],
                "supply_temperature_c": [18.0, 18.0, 19.0],
                "return_temperature_c": [20.0, 20.0, 21.0],
                "mass_flow_kg_s": [2.0, 2.0, 2.0],
            }
        )
        power = pd.DataFrame(
            {
                "time_bin": pd.to_datetime(["2022-09-01T00:00:00Z", "2022-09-01T00:05:00Z"], utc=True),
                "mean_observed_cluster_power_kw": [20.0, 20.0],
                "mean_observed_node_count": [980.0, 900.0],
                "timestamp_count": [15, 15],
            }
        )

        result = build_panel_comparison_frame(plc, power, panel="Q101", minimum_node_count=961.0)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.loc[0, "panel"], "Q101")
        self.assertAlmostEqual(result.loc[0, "return_temperature_c"], 20.0)

    def test_error_metrics_reports_signed_and_unsigned_temperature_error(self):
        metrics = calculate_error_metrics(np.array([20.0, 22.0]), np.array([21.0, 20.0]))

        self.assertEqual(metrics["sample_count"], 2)
        self.assertAlmostEqual(metrics["mae_c"], 1.5)
        self.assertAlmostEqual(metrics["bias_c"], 0.5)

    def test_comparison_records_when_dynamic_parameters_hit_search_bounds(self):
        time = pd.date_range("2022-09-01", periods=10, freq="5min", tz="UTC")
        frame = pd.DataFrame(
            {
                "time_bin": time,
                "panel": "Q101",
                "supply_temperature_c": 18.0,
                "return_temperature_c": np.linspace(19.0, 20.0, 10),
                "mass_flow_kg_s": 2.0,
                "mean_observed_cluster_power_kw": 20.0,
            }
        )

        _, summary = run_three_model_comparison(frame)

        self.assertIn("parameter_at_candidate_bound", summary["m1"])
        self.assertIn("parameter_at_candidate_bound", summary["m2"])

    def test_m1_relaxes_to_the_same_steady_solution_without_storage_error(self):
        prediction = simulate_m1_lumped(
            self.supply_c,
            self.mass_flow_kg_s,
            self.load_kw,
            initial_return_temperature_c=18.0,
            load_to_circuit_fraction=1.0,
            thermal_capacitance_j_k=8.0e5,
            time_step_s=self.dt_s,
            cp_j_kgk=self.cp_j_kgk,
        )

        self.assertAlmostEqual(prediction[-1], 20.5, places=5)

    def test_m2_relaxes_to_the_same_steady_solution_with_finite_heat_exchange(self):
        prediction = simulate_m2_two_state(
            self.supply_c,
            self.mass_flow_kg_s,
            self.load_kw,
            initial_return_temperature_c=18.0,
            initial_load_temperature_c=18.0,
            load_to_circuit_fraction=1.0,
            load_thermal_capacitance_j_k=8.0e5,
            fluid_thermal_capacitance_j_k=8.0e5,
            heat_exchange_conductance_w_k=2.0e4,
            time_step_s=self.dt_s,
            cp_j_kgk=self.cp_j_kgk,
        )

        self.assertAlmostEqual(prediction[-1], 20.5, places=5)


if __name__ == "__main__":
    unittest.main()
