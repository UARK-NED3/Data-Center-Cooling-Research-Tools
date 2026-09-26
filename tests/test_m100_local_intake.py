"""Tests for local-only M100 RDHx file-intake conventions."""

from __future__ import annotations

import unittest

from benchmarks.m100_rdhx_v0_1.local_intake import METRIC_DIRECTORIES, source_file_for_metric


class M100LocalIntakeTests(unittest.TestCase):
    def test_required_thermal_metrics_have_source_directories(self):
        self.assertEqual(METRIC_DIRECTORIES["active_flow_m3h"], "PLC_PLC_Q101.Portata_attiva")
        self.assertEqual(METRIC_DIRECTORIES["supply_temperature_c"], "PLC_PLC_Q101.Temp_mandata")
        self.assertEqual(METRIC_DIRECTORIES["return_temperature_c"], "PLC_PLC_Q101.Temp_ritorno")

    def test_source_file_preserves_partitioned_m100_path(self):
        path = source_file_for_metric("D:/selected", "22-09", "active_flow_m3h")
        self.assertEqual(
            path.as_posix(),
            "D:/selected/year_month=22-09/plugin=schneider_pub/metric=PLC_PLC_Q101.Portata_attiva/a_0.parquet",
        )


if __name__ == "__main__":
    unittest.main()
