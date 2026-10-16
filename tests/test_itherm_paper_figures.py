"""Tests for the exact two-node reference and the ITherm publication figures.

The figures are synthetic, NED3-authored derivatives.  These tests check the
numerical references behind them and the printed-size conventions, not any
claim about physical equipment.
"""

import json
import math
import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from benchmarks.ocp_tcs_rack_v1_0.model_suite import (
    simulate_two_node_case,
    two_node_exact_state,
    two_node_rise_time,
    two_node_steady_state,
)
from benchmarks.ocp_tcs_rack_v1_1.paper_figures import generate_paper_figures
from benchmarks.publication_style import save_figure, use_style


BASELINE = {
    "supply_temperature_c": 30.0,
    "mass_flow_kg_s": 0.5,
    "specific_heat_j_kg_k": 4180.0,
    "liquid_heat_w": 8000.0,
    "heat_capacity_hardware_j_k": 2.0e5,
    "heat_capacity_coolant_j_k": 2.0e4,
    "ua_w_k": 4000.0,
}


class ExactTwoNodeReferenceTests(unittest.TestCase):
    def test_equilibrium_matches_the_declared_balance_and_ignores_capacitance(self):
        steady = two_node_steady_state(
            supply_temperature_c=30.0, mass_flow_kg_s=0.5, specific_heat_j_kg_k=4180.0, liquid_heat_w=8000.0, ua_w_k=4000.0
        )
        self.assertAlmostEqual(steady["return_temperature_c"], 33.8277511962)
        self.assertAlmostEqual(steady["hardware_temperature_c"], 35.8277511962)
        late = two_node_exact_state(time_s=1.0e5, **BASELINE)
        self.assertAlmostEqual(late["hardware_temperature_c"], steady["hardware_temperature_c"], places=9)

    def test_exact_solution_starts_at_the_initial_state_and_satisfies_the_ode(self):
        start = two_node_exact_state(time_s=0.0, **BASELINE)
        self.assertAlmostEqual(start["hardware_temperature_c"], 30.0, places=12)
        self.assertAlmostEqual(start["return_temperature_c"], 30.0, places=12)
        step = 1.0e-3
        before = two_node_exact_state(time_s=100.0 - step, **BASELINE)
        after = two_node_exact_state(time_s=100.0 + step, **BASELINE)
        now = two_node_exact_state(time_s=100.0, **BASELINE)
        hardware_rate = (after["hardware_temperature_c"] - before["hardware_temperature_c"]) / (2.0 * step)
        expected = (BASELINE["liquid_heat_w"] - BASELINE["ua_w_k"] * (now["hardware_temperature_c"] - now["return_temperature_c"])) / BASELINE["heat_capacity_hardware_j_k"]
        self.assertAlmostEqual(hardware_rate, expected, places=8)

    def test_forward_euler_converges_to_the_exact_solution_at_first_order(self):
        exact = two_node_exact_state(time_s=200.0, **BASELINE)["hardware_temperature_c"]
        errors = []
        for step in (0.5, 1.0, 2.0):
            rows = simulate_two_node_case(duration_s=200.0, time_step_s=step, **BASELINE)
            errors.append(abs(rows[-1]["hardware_temperature_c"] - exact))
        for finer, coarser in zip(errors, errors[1:]):
            self.assertAlmostEqual(math.log2(coarser / finer), 1.0, delta=0.05)

    def test_rise_time_is_consistent_with_the_exact_trajectory(self):
        rise = two_node_rise_time(fraction=0.98, **BASELINE)
        steady = two_node_steady_state(
            supply_temperature_c=30.0, mass_flow_kg_s=0.5, specific_heat_j_kg_k=4180.0, liquid_heat_w=8000.0, ua_w_k=4000.0
        )["hardware_temperature_c"]
        at_rise = two_node_exact_state(time_s=rise, **BASELINE)["hardware_temperature_c"]
        self.assertAlmostEqual(at_rise, 30.0 + 0.98 * (steady - 30.0), places=6)


class PublicationFigureTests(unittest.TestCase):
    def test_paper_figures_are_written_at_printed_size_with_metrics(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            outputs = generate_paper_figures(Path(temporary_directory))
            metrics = json.loads(outputs["metrics_json"].read_text(encoding="utf-8"))
            for key in ("inputs_response_pdf", "model_structure_pdf", "sensitivity_pdf", "convergence_pdf"):
                self.assertTrue(outputs[key].is_file(), key)
        self.assertEqual(metrics["evidence_class"], "synthetic_derived")
        self.assertAlmostEqual(metrics["convergence"]["observed_order_hardware"], 1.0, delta=0.05)
        self.assertLess(metrics["m2_transient_max_abs_residual_relative_to_liquid_heat"], 1.0e-14)
        rows = {(row["parameter"], row["multiplier"]): row for row in metrics["sensitivity"]["rows"]}
        baseline = metrics["sensitivity"]["baseline_steady_hardware_temperature_c"]
        self.assertAlmostEqual(rows[("C_h", 2.0)]["steady_hardware_temperature_c"], baseline)
        self.assertAlmostEqual(rows[("C_f", 0.5)]["steady_hardware_temperature_c"], baseline)
        self.assertGreater(rows[("UA", 0.5)]["steady_hardware_temperature_c"], baseline)

    def test_save_figure_rejects_text_below_the_printed_minimum(self):
        use_style()
        figure, axis = plt.subplots(figsize=(3.5, 2.0))
        axis.set_xlabel("too small", fontsize=5)
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(ValueError, "below the printed minimum"):
                save_figure(figure, Path(temporary_directory) / "bad")
        plt.close(figure)


if __name__ == "__main__":
    unittest.main()
