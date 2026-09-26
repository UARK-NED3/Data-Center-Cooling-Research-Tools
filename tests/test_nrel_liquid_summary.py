"""Tests for the external NREL liquid-loop evidence intake adapter."""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.ocp_tcs_rack_v0_1.external_evidence.nrel_liquid_summary import (
    summarize_directory,
)


class NrelLiquidSummaryTests(unittest.TestCase):
    def _write_month(self, directory: Path, name: str, rows: list[list[str]]) -> None:
        with (directory / name).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                [
                    "Time",
                    "Q_flow,in,air [kW]",
                    "T_supply [°C]",
                    "T_return [°C]",
                    "Q_flow,in,liquidg [kW]",
                    "T_supply [°C]",
                    "T_return [°C]",
                ]
            )
            writer.writerows(rows)

    def test_summarizes_duplicate_temperature_headers_by_documented_position(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_month(
                root,
                "NREL_HPCDC_201609.csv",
                [
                    ["09/01/2016 00:00", "150", "20", "30", "500", "24", "34"],
                    ["09/01/2016 00:01", "151", "20", "30", "510", "24", "35"],
                ],
            )

            summary = summarize_directory(root)

        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(summary["source_file_count"], 1)
        self.assertEqual(summary["liquid_heat_kw"]["minimum"], 500.0)
        self.assertEqual(summary["liquid_heat_kw"]["maximum"], 510.0)
        self.assertAlmostEqual(summary["liquid_delta_t_k"]["mean"], 10.5)
        self.assertAlmostEqual(
            summary["inferred_capacity_rate_kw_per_k"]["mean"], 48.1818181818
        )
        self.assertEqual(summary["timestamp_coverage"]["median_step_s"], 60.0)

    def test_rejects_rows_without_positive_liquid_temperature_rise(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_month(
                root,
                "NREL_HPCDC_201609.csv",
                [["09/01/2016 00:00", "150", "20", "30", "500", "34", "34"]],
            )

            with self.assertRaisesRegex(ValueError, "positive liquid temperature rise"):
                summarize_directory(root)

    def test_flags_nonpositive_reported_heat_without_silently_dropping_the_row(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_month(
                root,
                "NREL_HPCDC_201609.csv",
                [
                    ["09/01/2016 00:00", "150", "20", "30", "500", "24", "34"],
                    ["09/01/2016 00:01", "150", "20", "30", "-50", "24", "34"],
                ],
            )

            summary = summarize_directory(root)

        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(summary["positive_heat_record_count"], 1)
        self.assertEqual(summary["quality_flags"]["nonpositive_liquid_heat_record_count"], 1)
        self.assertEqual(summary["liquid_heat_kw"]["mean"], 500.0)

    def test_cli_writes_machine_readable_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_month(
                root,
                "NREL_HPCDC_201609.csv",
                [["09/01/2016 00:00", "150", "20", "30", "500", "24", "34"]],
            )
            destination = root / "summary.json"

            from benchmarks.ocp_tcs_rack_v0_1.external_evidence.nrel_liquid_summary import main

            main(["--input-dir", str(root), "--output", str(destination)])
            with destination.open(encoding="utf-8") as stream:
                payload = json.load(stream)

        self.assertEqual(payload["record_count"], 1)
        self.assertEqual(payload["liquid_heat_kw"]["mean"], 500.0)


if __name__ == "__main__":
    unittest.main()
