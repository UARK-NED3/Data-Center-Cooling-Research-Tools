"""Summarize the NREL liquid-loop archive without copying source measurements.

The NREL monthly CSV files have duplicate temperature headings.  This adapter
therefore maps the seven documented columns by position, preserves source-file
identities, and reports only aggregate quantities in the requested JSON output.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Iterable


EXPECTED_COLUMN_COUNT = 7
NREL_FILE_GLOB = "NREL_HPCDC_*.csv"


def _parse_timestamp(value: str) -> datetime:
    for pattern in ("%m/%d/%Y %H:%M", "%m/%d/%y %H:%M"):
        try:
            return datetime.strptime(value.strip(), pattern)
        except ValueError:
            continue
    raise ValueError(f"unrecognized NREL timestamp: {value!r}")


def _summary(values: Iterable[float]) -> dict[str, float]:
    data = list(values)
    if not data:
        raise ValueError("cannot summarize an empty collection")
    return {
        "minimum": min(data),
        "mean": statistics.fmean(data),
        "maximum": max(data),
    }


def _read_month(path: Path) -> list[tuple[datetime, float, float, float]]:
    rows: list[tuple[datetime, float, float, float]] = []
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.reader(stream)
        header = next(reader, None)
        if header is None or len(header) != EXPECTED_COLUMN_COUNT:
            raise ValueError(f"{path.name}: expected seven documented NREL columns")
        if header[0].strip() != "Time" or "liquid" not in header[4].lower():
            raise ValueError(f"{path.name}: unexpected NREL column order")

        for line_number, row in enumerate(reader, start=2):
            if not row:
                continue
            if len(row) != EXPECTED_COLUMN_COUNT:
                raise ValueError(f"{path.name}:{line_number}: expected seven values")
            timestamp = _parse_timestamp(row[0])
            liquid_heat_kw = float(row[4])
            liquid_supply_c = float(row[5])
            liquid_return_c = float(row[6])
            liquid_delta_t_k = liquid_return_c - liquid_supply_c
            if liquid_delta_t_k <= 0:
                raise ValueError(
                    f"{path.name}:{line_number}: expected positive liquid temperature rise"
                )
            rows.append((timestamp, liquid_heat_kw, liquid_delta_t_k, liquid_heat_kw / liquid_delta_t_k))
    return rows


def summarize_directory(input_dir: Path) -> dict[str, object]:
    """Return a source-traceable aggregate for NREL monthly liquid-loop files.

    ``inferred_capacity_rate_kw_per_k`` is a derived Q/delta-T quantity.  It is
    numerically equivalent to m-dot*c_p only if the reported heat-flow and
    supply/return temperature measurements share the same liquid control volume.
    The NREL archive does not provide branch flow or pressure measurements.
    """

    source_files = sorted(input_dir.glob(NREL_FILE_GLOB))
    if not source_files:
        raise FileNotFoundError(f"no {NREL_FILE_GLOB} files found in {input_dir}")

    records = [record for path in source_files for record in _read_month(path)]
    if not records:
        raise ValueError("NREL source files contained no records")
    records.sort(key=lambda record: record[0])
    positive_heat_records = [record for record in records if record[1] > 0]
    if not positive_heat_records:
        raise ValueError("NREL source files contained no positive liquid-heat records")

    timestamps = [record[0] for record in records]
    steps_s = [
        (later - earlier).total_seconds()
        for earlier, later in zip(timestamps, timestamps[1:])
        if later > earlier
    ]
    return {
        "source": {
            "provider": "NREL ESIF HPC data center",
            "evidence_class": "third_party_measured_time_series",
            "source_file_glob": NREL_FILE_GLOB,
            "source_files": [path.name for path in source_files],
            "redistribution_status": "not assessed by this adapter",
        },
        "record_count": len(records),
        "positive_heat_record_count": len(positive_heat_records),
        "source_file_count": len(source_files),
        "quality_flags": {
            "nonpositive_liquid_heat_record_count": len(records) - len(positive_heat_records),
            "positive_heat_screen": "Only rows with reported liquid heat greater than zero are included in the aggregate thermal statistics.",
        },
        "timestamp_coverage": {
            "start": timestamps[0].isoformat(timespec="minutes"),
            "end": timestamps[-1].isoformat(timespec="minutes"),
            "median_step_s": statistics.median(steps_s) if steps_s else None,
        },
        "liquid_heat_kw": _summary(record[1] for record in positive_heat_records),
        "liquid_delta_t_k": _summary(record[2] for record in positive_heat_records),
        "inferred_capacity_rate_kw_per_k": _summary(record[3] for record in positive_heat_records),
        "limitations": [
            "The source archive reports cooling power and supply/return temperature, not branch flow or pressure.",
            "Rows with nonpositive reported liquid heat are retained in record_count and flagged, but excluded from positive-heat aggregate statistics.",
            "The inferred capacity rate is a derived screening quantity, not a measured mass-flow record.",
            "This summary does not establish rack topology or cold-plate-level behavior.",
        ],
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    result = summarize_directory(args.input_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
