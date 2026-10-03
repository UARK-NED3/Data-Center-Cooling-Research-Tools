"""Specification tests for the synthetic v1.1 multi-branch rack model.

These tests intentionally cover a model that is physically distinct from the
whole-rack M1 balance and the mixed-node M2 model.  All quantities are
synthetic and therefore support verification and model-structure comparison,
not empirical rack validation.
"""

import unittest
from pathlib import Path
import tempfile

from benchmarks.ocp_tcs_rack_v1_1.generate_artifacts import generate_artifacts
from benchmarks.ocp_tcs_rack_v1_1.model_suite import (
    evaluate_multibranch_steady_case,
    simulate_multibranch_case,
)


def _balanced_branches():
    return [
        {
            "branch_id": f"B{index}",
            "it_heat_fraction": 0.25,
            "liquid_capture_fraction": 0.8,
            "hydraulic_resistance_pa_s2_kg2": 1.0e6,
            "ua_w_k": 1000.0,
            "hardware_heat_capacity_j_k": 5.0e4,
            "coolant_heat_capacity_j_k": 5.0e3,
        }
        for index in range(1, 5)
    ]


class MultibranchSuiteTests(unittest.TestCase):
    def test_balanced_network_reduces_to_the_declared_whole_rack_energy_balance(self):
        result = evaluate_multibranch_steady_case(
            it_heat_w=10_000.0,
            supply_temperature_c=30.0,
            mass_flow_kg_s=0.5,
            specific_heat_j_kg_k=4180.0,
            density_kg_m3=997.0,
            pump_efficiency=0.6,
            branches=_balanced_branches(),
        )

        self.assertAlmostEqual(result["mixed_return_temperature_c"], 33.8277511962)
        self.assertAlmostEqual(result["energy_residual_w"], 0.0)
        self.assertAlmostEqual(sum(branch["mass_flow_kg_s"] for branch in result["branches"]), 0.5)
        self.assertTrue(all(abs(branch["mass_flow_kg_s"] - 0.125) < 1.0e-12 for branch in result["branches"]))

    def test_hydraulic_imbalance_changes_branch_temperature_without_changing_total_energy_closure(self):
        branches = _balanced_branches()
        branches[-1]["hydraulic_resistance_pa_s2_kg2"] = 4.0e6
        result = evaluate_multibranch_steady_case(
            it_heat_w=10_000.0,
            supply_temperature_c=30.0,
            mass_flow_kg_s=0.5,
            specific_heat_j_kg_k=4180.0,
            density_kg_m3=997.0,
            pump_efficiency=0.6,
            branches=branches,
        )

        branch_by_id = {branch["branch_id"]: branch for branch in result["branches"]}
        self.assertLess(branch_by_id["B4"]["mass_flow_kg_s"], branch_by_id["B1"]["mass_flow_kg_s"])
        self.assertGreater(branch_by_id["B4"]["return_temperature_c"], branch_by_id["B1"]["return_temperature_c"])
        self.assertAlmostEqual(result["energy_residual_w"], 0.0)

    def test_dynamic_multibranch_model_relaxes_toward_the_steady_network_solution(self):
        branches = _balanced_branches()
        steady = evaluate_multibranch_steady_case(
            it_heat_w=10_000.0,
            supply_temperature_c=30.0,
            mass_flow_kg_s=0.5,
            specific_heat_j_kg_k=4180.0,
            density_kg_m3=997.0,
            pump_efficiency=0.6,
            branches=branches,
        )
        rows = simulate_multibranch_case(
            it_heat_w=10_000.0,
            supply_temperature_c=30.0,
            mass_flow_kg_s=0.5,
            specific_heat_j_kg_k=4180.0,
            density_kg_m3=997.0,
            pump_efficiency=0.6,
            branches=branches,
            duration_s=1800.0,
            time_step_s=0.5,
        )

        self.assertAlmostEqual(rows[-1]["mixed_return_temperature_c"], steady["mixed_return_temperature_c"], places=3)
        self.assertLess(max(abs(row["energy_residual_w"]) for row in rows), 1.0e-8)

    def test_artifact_generator_writes_three_model_comparison_with_traceability_metadata(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifacts = generate_artifacts(Path(temporary_directory))
            summary = artifacts["summary_json"].read_text(encoding="utf-8")
            comparison = artifacts["comparison_csv"].read_text(encoding="utf-8")
            figure = artifacts["comparison_svg"].read_text(encoding="utf-8")
            preview = artifacts["comparison_png"]
            publication_figure = artifacts["comparison_pdf"]
            self.assertTrue(preview.is_file())
            self.assertTrue(publication_figure.is_file())

        self.assertIn('"evidence_class": "synthetic_derived"', summary)
        self.assertIn('"M3": "multi_branch_thermal_hydraulic_network"', summary)
        self.assertIn("scenario_id,m1_mixed_return_temperature_c", comparison)
        self.assertIn("Synthetic model-structure comparison", figure)


if __name__ == "__main__":
    unittest.main()
