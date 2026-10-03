"""Tests for locally generated, evidence-gated M100 summary outputs."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from benchmarks.m100_rdhx_v0_1.local_result_report import (
    summarize_conditional_test_metrics,
    summarize_operating_statistics,
    write_local_result_report,
)


class M100LocalResultReportTests(unittest.TestCase):
    def test_operating_statistics_preserve_panel_separation_and_report_quantiles(self):
        frame = pd.DataFrame(
            {
                "timestamp": pd.date_range("2022-09-01", periods=4, freq="20s", tz="UTC"),
                "panel": ["Q101", "Q101", "Q102", "Q102"],
                "supply_temperature_c": [16.0, 17.0, 16.0, 17.0],
                "return_temperature_c": [22.0, 23.0, 22.0, 23.0],
                "active_flow_m3h": [100.0, 120.0, 110.0, 130.0],
                "temperature_rise_k": [6.0, 6.0, 6.0, 6.0],
                "derived_heat_transfer_kw": [700.0, 840.0, 770.0, 910.0],
            }
        )

        summary = summarize_operating_statistics(frame)

        self.assertEqual(summary["panel"].tolist(), ["Q101", "Q102"])
        self.assertEqual(summary.loc[0, "sample_count"], 2)
        self.assertAlmostEqual(summary.loc[0, "screening_heat_rate_kw_p50"], 770.0)
        self.assertAlmostEqual(summary.loc[0, "screening_heat_rate_flow_correlation"], 1.0)

    def test_conditional_test_metrics_use_only_the_locked_test_block(self):
        predictions = pd.DataFrame(
            {
                "split": ["train", "test", "test"],
                "return_temperature_c": [20.0, 20.0, 22.0],
                "m0_return_temperature_c": [20.0, 21.0, 23.0],
                "m1_return_temperature_c": [20.0, 20.5, 22.5],
                "m2_return_temperature_c": [20.0, 20.0, 22.0],
            }
        )

        summary = summarize_conditional_test_metrics(predictions)

        self.assertEqual(summary["model"].tolist(), ["M0 quasi-steady", "M1 one-state", "M2 two-state"])
        self.assertEqual(summary.loc[0, "sample_count"], 2)
        self.assertAlmostEqual(summary.loc[0, "rmse_c"], 1.0)
        self.assertAlmostEqual(summary.loc[2, "rmse_c"], 0.0)
        self.assertAlmostEqual(summary.loc[2, "rmse_change_from_m0_percent"], -100.0)

    def test_local_report_writes_vector_and_raster_figures_outside_the_repository(self):
        timestamps = pd.date_range("2022-09-01", periods=4, freq="5min", tz="UTC")
        signals = pd.DataFrame(
            {
                "timestamp": timestamps,
                "panel": "Q101",
                "supply_temperature_c": [16.0, 16.0, 16.2, 16.2],
                "return_temperature_c": [22.0, 22.1, 22.3, 22.2],
                "active_flow_m3h": [100.0, 101.0, 102.0, 103.0],
                "temperature_rise_k": [6.0, 6.1, 6.1, 6.0],
                "derived_heat_transfer_kw": [700.0, 710.0, 720.0, 725.0],
            }
        )
        predictions = pd.DataFrame(
            {
                "time_bin": timestamps,
                "split": ["train", "test", "test", "test"],
                "return_temperature_c": [22.0, 22.1, 22.3, 22.2],
                "m0_return_temperature_c": [22.0, 22.5, 22.6, 22.7],
                "m1_return_temperature_c": [22.0, 22.2, 22.4, 22.3],
                "m2_return_temperature_c": [22.0, 22.1, 22.3, 22.2],
            }
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            signals_csv = root / "signals.csv"
            predictions_csv = root / "predictions.csv"
            summary_json = root / "summary.json"
            signals.to_csv(signals_csv, index=False)
            predictions.to_csv(predictions_csv, index=False)
            summary_json.write_text(json.dumps({"m2": {"parameter_at_candidate_bound": True}}), encoding="utf-8")

            write_local_result_report(signals_csv, predictions_csv, summary_json, root / "report")

            self.assertTrue((root / "report" / "m100_conditional_stress_test.png").exists())
            self.assertTrue((root / "report" / "m100_conditional_stress_test.pdf").exists())
            self.assertTrue((root / "report" / "m100_conditional_stress_test.svg").exists())

    def test_local_report_rejects_a_destination_inside_the_public_repository(self):
        repository_root = Path(__file__).resolve().parents[1]

        with self.assertRaisesRegex(ValueError, "outside the public repository"):
            write_local_result_report(
                "does-not-need-to-exist.csv",
                "does-not-need-to-exist.csv",
                "does-not-need-to-exist.json",
                repository_root / "m100-derived-output",
            )


if __name__ == "__main__":
    unittest.main()
