"""Tests for the Frontier facility evidence intake summary."""

import unittest
from datetime import datetime

from benchmarks.ocp_tcs_rack_v0_1.external_evidence.frontier_facility_summary import (
    summarize_records,
)


class FrontierFacilitySummaryTests(unittest.TestCase):
    def test_identifies_source_calculated_waste_heat_and_power_identities(self):
        records = [
            {
                "timestamp": datetime(2023, 1, 1, 0, 0),
                "subloop_flow_gpm": [100.0, 200.0, 300.0],
                "subloop_return_c": [30.0, 30.0, 30.0],
                "supply_c": 20.0,
                "subloop_waste_heat_mw": [0.2340391666666667, 0.4680783333333334, 0.7021175],
                "overall_waste_heat_mw": 1.404235,
                "compute_power_mw": 10.0,
                "accessory_power_mw": 0.5,
                "total_power_mw": 10.5,
                "pue": 1.05,
            },
            {
                "timestamp": datetime(2023, 1, 1, 0, 10),
                "subloop_flow_gpm": [100.0, 200.0, 300.0],
                "subloop_return_c": [30.0, 30.0, 30.0],
                "supply_c": 20.0,
                "subloop_waste_heat_mw": [0.2340391666666667, 0.4680783333333334, 0.7021175],
                "overall_waste_heat_mw": 1.404235,
                "compute_power_mw": 10.0,
                "accessory_power_mw": 0.5,
                "total_power_mw": 10.5,
                "pue": 1.05,
            },
        ]

        summary = summarize_records(records)

        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(summary["timestamp_coverage"]["median_step_s"], 600.0)
        self.assertAlmostEqual(
            summary["source_calculated_waste_heat"]["factor_mw_per_gpm_k"],
            0.0002340391666666667,
        )
        self.assertAlmostEqual(
            summary["identity_checks"]["subloop_waste_heat_sum_max_abs_residual_mw"], 0.0
        )
        self.assertAlmostEqual(
            summary["identity_checks"]["power_sum_max_abs_residual_mw"], 0.0
        )
        self.assertAlmostEqual(
            summary["identity_checks"]["pue_max_abs_residual"], 0.0
        )

    def test_rejects_records_without_a_positive_temperature_rise_for_positive_duty(self):
        records = [
            {
                "timestamp": datetime(2023, 1, 1, 0, 0),
                "subloop_flow_gpm": [100.0, 200.0, 300.0],
                "subloop_return_c": [20.0, 30.0, 30.0],
                "supply_c": 20.0,
                "subloop_waste_heat_mw": [0.1, 0.4680783333333334, 0.7021175],
                "overall_waste_heat_mw": 1.2701958333333334,
                "compute_power_mw": 10.0,
                "accessory_power_mw": 0.5,
                "total_power_mw": 10.5,
                "pue": 1.05,
            }
        ]

        with self.assertRaisesRegex(ValueError, "positive temperature rise"):
            summarize_records(records)


if __name__ == "__main__":
    unittest.main()
