"""Regression checks for the curated external-dataset catalog."""

import csv
from pathlib import Path
import tempfile
import unittest

from scripts.check_dataset_catalog import REQUIRED_COLUMNS, validate_catalog


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPOSITORY_ROOT / "data" / "dataset_catalog.csv"


class DatasetCatalogTests(unittest.TestCase):
    def test_repository_catalog_is_valid_and_contains_cooling_records(self):
        rows = validate_catalog(CATALOG_PATH)

        self.assertGreaterEqual(len(rows), 8)
        self.assertTrue(
            any(row["thermal_benchmark_role"] != "workload_context_only" for row in rows)
        )
        self.assertTrue(
            any(row["thermal_benchmark_role"] == "workload_context_only" for row in rows)
        )

    def test_duplicate_identifiers_are_rejected(self):
        row = {column: "example" for column in REQUIRED_COLUMNS}
        row.update(
            {
                "dataset_id": "duplicate",
                "dataset_name": "Example dataset",
                "source_url": "https://example.org/dataset",
                "primary_record_id": "none",
                "record_type": "measured_operational_telemetry",
                "system_scale": "server_or_node",
                "cooling_architecture": "not_reported",
                "spatial_linkage": "unknown_or_not_reported",
                "time_coverage": "not_reported",
                "time_resolution": "not_reported",
                "thermal_benchmark_role": "workload_context_only",
                "rights_status": "not_reported_verify_before_reuse",
                "catalog_review_basis": "source_record",
                "reviewed_on": "2026-09-26",
            }
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            catalog_path = Path(temporary_directory) / "catalog.csv"
            with catalog_path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=REQUIRED_COLUMNS)
                writer.writeheader()
                writer.writerow(row)
                writer.writerow(row)

            with self.assertRaisesRegex(ValueError, "duplicate dataset_id"):
                validate_catalog(catalog_path)


if __name__ == "__main__":
    unittest.main()
