"""Regression tests for presentable synthetic benchmark result artifacts."""

import csv
import json
from pathlib import Path
import tempfile
import unittest

from benchmarks.ocp_tcs_rack_v0_1.generate_reference_results import (
    generate_reference_results,
)
from benchmarks.ocp_tcs_rack_v0_1.adapters.build_matlab_comparison import (
    build_matlab_comparison,
)


BENCHMARK_DIRECTORY = Path(__file__).resolve().parents[1] / "benchmarks" / "ocp_tcs_rack_v0_1"


class ReferenceResultsTests(unittest.TestCase):
    def test_matlab_comparison_records_zero_difference_for_matching_results(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            generated = generate_reference_results(output_directory=temporary_path / "results")
            baseline = json.loads(generated["baseline_json"].read_text(encoding="utf-8"))
            matlab_result = {
                "adapter_id": "matlab-steady-state-reference-v0.1",
                "case_id": baseline["case_id"],
                "evidence_class": "synthetic_derived",
                "matlab_release": "2025b",
                "result": baseline["result"],
            }
            matlab_path = temporary_path / "matlab_result.json"
            matlab_path.write_text(json.dumps(matlab_result), encoding="utf-8")

            comparison_path = temporary_path / "matlab_comparison.json"
            comparison = build_matlab_comparison(
                matlab_result_path=matlab_path,
                baseline_result_path=generated["baseline_json"],
                output_path=comparison_path,
            )

            self.assertEqual(comparison["max_absolute_difference"], 0.0)
            self.assertEqual(comparison["comparison_state"], "agrees_within_tolerance")
            self.assertTrue(comparison_path.is_file())

    def test_generator_writes_traceable_baseline_and_flow_sensitivity_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory) / "results"
            generated = generate_reference_results(output_directory=output_directory)

            baseline = json.loads(generated["baseline_json"].read_text(encoding="utf-8"))
            self.assertEqual(baseline["evidence_class"], "synthetic_derived")
            self.assertEqual(baseline["result"]["liquid_heat_w"], 8_000.0)
            self.assertAlmostEqual(
                baseline["result"]["tcs_return_temperature_c"], 33.8277511962
            )
            self.assertEqual(len(baseline["case_sha256"]), 64)

            with generated["flow_csv"].open(newline="", encoding="utf-8") as result_file:
                rows = list(csv.DictReader(result_file))
            self.assertEqual([row["mass_flow_kg_s"] for row in rows], ["0.25", "0.5", "0.75", "1"])
            temperatures = [float(row["tcs_return_temperature_c"]) for row in rows]
            self.assertEqual(temperatures, sorted(temperatures, reverse=True))

            figure = generated["flow_svg"].read_text(encoding="utf-8")
            self.assertIn("Technology-cooling-system flow sensitivity", figure)
            self.assertIn("Synthetic verification only", figure)


if __name__ == "__main__":
    unittest.main()
