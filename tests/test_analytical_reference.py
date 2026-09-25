"""Tests for the OCP-aligned synthetic rack verification reference."""

import json
import subprocess
import sys
import unittest

from benchmarks.ocp_tcs_rack_v0_1.analytical_reference import (
    evaluate_case_file,
    evaluate_steady_case,
)


class AnalyticalReferenceTests(unittest.TestCase):
    def test_closes_rack_energy_balance_for_liquid_and_air_heat_paths(self):
        result = evaluate_steady_case(
            it_heat_w=10_000.0,
            liquid_capture_fraction=0.80,
            tcs_supply_temperature_c=30.0,
            tcs_mass_flow_kg_s=0.50,
            coolant_specific_heat_j_kg_k=4_180.0,
        )

        self.assertAlmostEqual(result["liquid_heat_w"], 8_000.0)
        self.assertAlmostEqual(result["air_heat_w"], 2_000.0)
        self.assertAlmostEqual(result["tcs_return_temperature_c"], 33.8277511962)
        self.assertAlmostEqual(result["rack_energy_residual_w"], 0.0)

    def test_rejects_nonphysical_liquid_capture_fraction(self):
        with self.assertRaises(ValueError):
            evaluate_steady_case(
                it_heat_w=10_000.0,
                liquid_capture_fraction=1.01,
                tcs_supply_temperature_c=30.0,
                tcs_mass_flow_kg_s=0.50,
                coolant_specific_heat_j_kg_k=4_180.0,
            )

    def test_rejects_nonpositive_tcs_mass_flow(self):
        with self.assertRaises(ValueError):
            evaluate_steady_case(
                it_heat_w=10_000.0,
                liquid_capture_fraction=0.80,
                tcs_supply_temperature_c=30.0,
                tcs_mass_flow_kg_s=0.0,
                coolant_specific_heat_j_kg_k=4_180.0,
            )

    def test_canonical_case_file_closes_its_energy_balance(self):
        result = evaluate_case_file()

        self.assertEqual(result["it_heat_w"], 10_000.0)
        self.assertEqual(result["liquid_heat_w"], 8_000.0)
        self.assertEqual(result["air_heat_w"], 2_000.0)
        self.assertAlmostEqual(result["rack_energy_residual_w"], 0.0)

    def test_module_command_emits_machine_readable_canonical_result(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "benchmarks.ocp_tcs_rack_v0_1.analytical_reference",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result = json.loads(completed.stdout)
        self.assertEqual(result["liquid_heat_w"], 8_000.0)
        self.assertAlmostEqual(result["rack_energy_residual_w"], 0.0)


if __name__ == "__main__":
    unittest.main()
