"""Validate the repository's source-only external-dataset catalog."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


REQUIRED_COLUMNS = (
    "dataset_id",
    "dataset_name",
    "source_url",
    "companion_url",
    "primary_record_id",
    "record_type",
    "system_scale",
    "cooling_architecture",
    "spatial_linkage",
    "time_coverage",
    "time_resolution",
    "primary_modalities",
    "thermal_benchmark_role",
    "benchmark_readiness",
    "rights_status",
    "redistribution_note",
    "catalog_review_basis",
    "reviewed_on",
)

ALLOWED_BENCHMARK_ROLES = {
    "airflow_cfd_validation_candidate",
    "facility_or_loop_behavior_candidate",
    "node_telemetry_modeling_candidate",
    "rack_or_room_validation_candidate",
    "workload_context_only",
}


def validate_catalog(catalog_path: Path) -> list[dict[str, str]]:
    """Return catalog rows after checking identity, provenance, and review fields."""
    with catalog_path.open(newline="", encoding="utf-8") as catalog_file:
        reader = csv.DictReader(catalog_file)
        if reader.fieldnames is None:
            raise ValueError("catalog has no header")

        missing_columns = [
            column for column in REQUIRED_COLUMNS if column not in reader.fieldnames
        ]
        if missing_columns:
            raise ValueError(f"catalog is missing required columns: {missing_columns}")

        rows = list(reader)

    if not rows:
        raise ValueError("catalog contains no dataset records")

    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        missing_values = [
            column for column in REQUIRED_COLUMNS if not (row.get(column) or "").strip()
        ]
        if missing_values:
            raise ValueError(
                f"row {row_number} has empty required values: {', '.join(missing_values)}"
            )

        dataset_id = row["dataset_id"]
        if dataset_id in seen_ids:
            raise ValueError(f"duplicate dataset_id: {dataset_id}")
        seen_ids.add(dataset_id)

        if not row["source_url"].startswith(("https://", "http://")):
            raise ValueError(f"row {row_number} source_url is not an HTTP(S) URL")

        if row["thermal_benchmark_role"] not in ALLOWED_BENCHMARK_ROLES:
            raise ValueError(
                f"row {row_number} has unknown thermal_benchmark_role: "
                f"{row['thermal_benchmark_role']}"
            )

        try:
            date.fromisoformat(row["reviewed_on"])
        except ValueError as error:
            raise ValueError(f"row {row_number} reviewed_on is not ISO-8601") from error

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "catalog_path",
        nargs="?",
        type=Path,
        default=Path("data/dataset_catalog.csv"),
        help="path to the CSV catalog (default: data/dataset_catalog.csv)",
    )
    arguments = parser.parse_args()
    rows = validate_catalog(arguments.catalog_path)
    print(f"dataset catalog valid: {len(rows)} records")


if __name__ == "__main__":
    main()
