"""Tests for the measured M100 RDHx intake calculations.

The fixtures are synthetic.  They exercise scaling and conservation algebra
without redistributing third-party M100 observations.
"""

from __future__ import annotations

import unittest

import pandas as pd

from benchmarks.m100_rdhx_v0_1.analysis import (
    assemble_panel_signals,
    calculate_thermal_quantities,
)


class M100RdhxAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.timestamps = pd.to_datetime(
            ["2022-09-01T00:00:00Z", "2022-09-01T00:00:20Z"], utc=True
        )

    def test_assemble_decodes_documented_integer_scales(self):
        signals = {
            "active_flow_m3h": pd.DataFrame(
                {"timestamp": self.timestamps, "panel": ["Q101", "Q101"], "value": [1000, 1200]}
            ),
            "supply_temperature_c": pd.DataFrame(
                {"timestamp": self.timestamps, "panel": ["Q101", "Q101"], "value": [180, 190]}
            ),
            "return_temperature_c": pd.DataFrame(
                {"timestamp": self.timestamps, "panel": ["Q101", "Q101"], "value": [240, 250]}
            ),
            "reported_delta_temperature_c": pd.DataFrame(
                {"timestamp": self.timestamps, "panel": ["Q101", "Q101"], "value": [60, 60]}
            ),
        }

        result = assemble_panel_signals(signals)

        self.assertEqual(result["active_flow_m3h"].tolist(), [100.0, 120.0])
        self.assertEqual(result["supply_temperature_c"].tolist(), [18.0, 19.0])
        self.assertEqual(result["return_temperature_c"].tolist(), [24.0, 25.0])

    def test_thermal_quantity_uses_m3_per_hour_and_kelvin_consistently(self):
        frame = pd.DataFrame(
            {
                "active_flow_m3h": [100.0],
                "supply_temperature_c": [18.0],
                "return_temperature_c": [24.0],
                "reported_delta_temperature_c": [6.0],
            }
        )

        result = calculate_thermal_quantities(frame, density_kg_m3=1000.0, cp_j_kgk=4200.0)

        self.assertAlmostEqual(result.loc[0, "temperature_rise_k"], 6.0)
        self.assertAlmostEqual(result.loc[0, "derived_heat_transfer_kw"], 700.0)
        self.assertAlmostEqual(result.loc[0, "reported_minus_direct_delta_k"], 0.0)

    def test_assemble_rejects_duplicate_timestamp_panel_measurements(self):
        duplicate = pd.DataFrame(
            {
                "timestamp": [self.timestamps[0], self.timestamps[0]],
                "panel": ["Q101", "Q101"],
                "value": [1000, 1000],
            }
        )
        signals = {
            "active_flow_m3h": duplicate,
            "supply_temperature_c": duplicate,
            "return_temperature_c": duplicate,
            "reported_delta_temperature_c": duplicate,
        }

        with self.assertRaisesRegex(ValueError, "duplicate"):
            assemble_panel_signals(signals)


if __name__ == "__main__":
    unittest.main()
