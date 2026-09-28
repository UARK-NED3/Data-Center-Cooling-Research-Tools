"""Tests for the v1.0 synthetic rack-model comparison suite."""

import unittest
from pathlib import Path
import tempfile

from benchmarks.ocp_tcs_rack_v1_0.model_suite import (
    DEFAULT_SUITE_PATH,
    evaluate_quasi_steady_case,
    simulate_two_node_case,
)
from benchmarks.ocp_tcs_rack_v1_0.generate_artifacts import generate_artifacts


class SyntheticSuiteTests(unittest.TestCase):
    def test_quasi_steady_reference_closes_the_declared_heat_balance(self):
        result = evaluate_quasi_steady_case(
            it_heat_w=10_000.0,
            liquid_capture_fraction=0.8,
            supply_temperature_c=30.0,
            mass_flow_kg_s=0.5,
            specific_heat_j_kg_k=4_180.0,
        )

        self.assertAlmostEqual(result["return_temperature_c"], 33.8277511962)
        self.assertAlmostEqual(result["energy_residual_w"], 0.0)

    def test_two_node_model_reaches_the_quasi_steady_limit_for_constant_input(self):
        result = simulate_two_node_case(
            supply_temperature_c=30.0,
            mass_flow_kg_s=0.5,
            specific_heat_j_kg_k=4_180.0,
            liquid_heat_w=8_000.0,
            heat_capacity_hardware_j_k=2.0e5,
            heat_capacity_coolant_j_k=2.0e4,
            ua_w_k=4_000.0,
            duration_s=3_600.0,
            time_step_s=1.0,
        )

        self.assertAlmostEqual(result[-1]["return_temperature_c"], 33.8277511962, places=3)
        self.assertLess(max(abs(row["energy_residual_w"]) for row in result), 1.0e-8)

    def test_suite_is_declared_as_synthetic_and_not_validated(self):
        self.assertTrue(DEFAULT_SUITE_PATH.is_file())
        contents = DEFAULT_SUITE_PATH.read_text(encoding="utf-8")
        self.assertIn('"evidence_class": "synthetic_derived"', contents)
        self.assertIn('"validation_state": "not_validated"', contents)

    def test_generator_writes_traceable_time_series_and_figure(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifacts = generate_artifacts(Path(temporary_directory))
            summary = artifacts["summary_json"].read_text(encoding="utf-8")
            figure = artifacts["transient_svg"].read_text(encoding="utf-8")

        self.assertIn('"evidence_class": "synthetic_derived"', summary)
        self.assertIn("Synthetic scenarios; verification and model-structure comparison only", figure)
        self.assertIn("M1 quasi-steady", figure)
        self.assertIn("M2 two-node", figure)


if __name__ == "__main__":
    unittest.main()
