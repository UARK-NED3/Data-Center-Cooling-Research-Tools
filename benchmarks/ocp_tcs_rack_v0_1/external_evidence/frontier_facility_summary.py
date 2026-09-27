"""Summarize the Frontier 2023 facility-loop record without redistributing it.

The source workbook contains one year of 10-minute secondary-loop records.  Its
subloop flow and supply/return temperatures are reported measurements, while
the subloop waste-heat fields are source-calculated quantities.  This adapter
keeps those evidence classes distinct and checks the algebraic identities that
are already encoded in the source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence


SOURCE_DOI = "https://doi.org/10.6084/m9.figshare.24391240.v4"
EXPECTED_COLUMNS = 18


def _finite(value: float, name: str) -> float:
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")
    return converted


def _summary(values: Iterable[float]) -> dict[str, float]:
    data = list(values)
    if not data:
        raise ValueError("cannot summarize an empty collection")
    return {
        "minimum": min(data),
        "mean": statistics.fmean(data),
        "maximum": max(data),
    }


def _median_step_s(timestamps: Sequence[datetime]) -> float | None:
    steps = [
        (later - earlier).total_seconds()
        for earlier, later in zip(timestamps, timestamps[1:])
        if later > earlier
    ]
    return statistics.median(steps) if steps else None


def _max_abs(values: Iterable[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def summarize_records(records: Iterable[dict[str, object]]) -> dict[str, object]:
    """Summarize normalized Frontier records and preserve evidence boundaries.

    A positive reported subloop duty requires positive flow and a positive
    return-minus-supply temperature rise.  Zero-duty outages are retained in
    the record count, but excluded from the source-factor calculation.
    """

    prepared = sorted(records, key=lambda row: row["timestamp"])
    if not prepared:
        raise ValueError("cannot summarize an empty Frontier record collection")

    factor_samples: list[float] = []
    subloop_sum_residuals: list[float] = []
    power_sum_residuals: list[float] = []
    pue_residuals: list[float] = []
    heat_values: list[float] = []
    compute_values: list[float] = []
    accessory_values: list[float] = []
    pue_values: list[float] = []
    timestamps: list[datetime] = []
    positive_duty_count = 0
    zero_or_negative_duty_count = 0

    for row in prepared:
        timestamp = row["timestamp"]
        if not isinstance(timestamp, datetime):
            raise ValueError("timestamp must be a datetime")
        timestamps.append(timestamp)

        flows = [_finite(value, "subloop flow") for value in row["subloop_flow_gpm"]]  # type: ignore[index]
        returns = [_finite(value, "subloop return temperature") for value in row["subloop_return_c"]]  # type: ignore[index]
        duties = [_finite(value, "subloop waste heat") for value in row["subloop_waste_heat_mw"]]  # type: ignore[index]
        if not (len(flows) == len(returns) == len(duties) == 3):
            raise ValueError("each Frontier record must contain three subloops")

        supply = _finite(row["supply_c"], "supply temperature")  # type: ignore[arg-type]
        for flow, returned, duty in zip(flows, returns, duties):
            delta_t = returned - supply
            if duty > 0:
                positive_duty_count += 1
                if flow <= 0:
                    raise ValueError("positive waste heat requires positive flow")
                if delta_t <= 0:
                    raise ValueError("positive waste heat requires positive temperature rise")
                factor_samples.append(duty / (flow * delta_t))
            else:
                zero_or_negative_duty_count += 1

        compute = _finite(row["compute_power_mw"], "compute power")  # type: ignore[arg-type]
        accessory = _finite(row["accessory_power_mw"], "accessory power")  # type: ignore[arg-type]
        total = _finite(row["total_power_mw"], "total power")  # type: ignore[arg-type]
        pue = _finite(row["pue"], "PUE")  # type: ignore[arg-type]
        if compute <= 0:
            raise ValueError("compute power must be positive for a reported PUE")

        subloop_sum_residuals.append(sum(duties) - _finite(row["overall_waste_heat_mw"], "overall waste heat"))  # type: ignore[arg-type]
        power_sum_residuals.append(compute + accessory - total)
        pue_residuals.append(total / compute - pue)
        heat_values.append(_finite(row["overall_waste_heat_mw"], "overall waste heat"))  # type: ignore[arg-type]
        compute_values.append(compute)
        accessory_values.append(accessory)
        pue_values.append(pue)

    return {
        "source": {
            "stable_identifier": SOURCE_DOI,
            "provider": "Oak Ridge National Laboratory / Figshare",
            "evidence_class": "third_party_measured_time_series_with_source_calculated_fields",
            "physical_scale": "facility_secondary_loop",
        },
        "record_count": len(prepared),
        "timestamp_coverage": {
            "start": timestamps[0].isoformat(timespec="minutes"),
            "end": timestamps[-1].isoformat(timespec="minutes"),
            "median_step_s": _median_step_s(timestamps),
        },
        "evidence_boundary": {
            "measured_source_fields": "subloop flow, subloop return temperature, supply temperature, and facility-power records",
            "source_calculated_fields": "subloop and overall waste heat; source documentation states these are calculated from each subloop flow and supply/return temperature",
            "excluded_claim": "This facility-secondary-loop dataset does not resolve rack branches, cold-plate pressure loss, or chip temperature.",
        },
        "source_calculated_waste_heat": {
            "positive_duty_sample_count": positive_duty_count,
            "zero_or_negative_duty_sample_count": zero_or_negative_duty_count,
            "factor_mw_per_gpm_k": statistics.fmean(factor_samples),
            "factor_spread_mw_per_gpm_k": max(factor_samples) - min(factor_samples),
            "interpretation": "A constant factor indicates that the reported waste-heat fields are algebraically derived from the reported flow and temperature records. It is not an independent calorimetric validation.",
        },
        "identity_checks": {
            "subloop_waste_heat_sum_max_abs_residual_mw": _max_abs(subloop_sum_residuals),
            "power_sum_max_abs_residual_mw": _max_abs(power_sum_residuals),
            "pue_max_abs_residual": _max_abs(pue_residuals),
        },
        "reported_operating_ranges": {
            "overall_waste_heat_mw": _summary(heat_values),
            "compute_power_mw": _summary(compute_values),
            "accessory_power_mw": _summary(accessory_values),
            "pue": _summary(pue_values),
        },
    }


def read_frontier_xlsx(path: Path) -> list[dict[str, object]]:
    """Load the documented ``Frontier2023`` worksheet by its stable column order."""

    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - exercised only when optional dependency is absent.
        raise RuntimeError("Frontier XLSX intake requires pandas and an Excel reader") from exc

    frame = pd.read_excel(path, sheet_name="Frontier2023", skiprows=[1])
    if len(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"{path.name}: expected {EXPECTED_COLUMNS} documented columns")
    records: list[dict[str, object]] = []
    for values in frame.itertuples(index=False, name=None):
        records.append(
            {
                "timestamp": values[0].to_pydatetime() if hasattr(values[0], "to_pydatetime") else values[0],
                "subloop_return_c": [values[1], values[3], values[5]],
                "subloop_flow_gpm": [values[2], values[4], values[6]],
                "supply_c": values[8],
                "subloop_waste_heat_mw": [values[10], values[11], values[12]],
                "overall_waste_heat_mw": values[13],
                "compute_power_mw": values[14],
                "accessory_power_mw": values[15],
                "total_power_mw": values[16],
                "pue": values[17],
            }
        )
    return records


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-xlsx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    result = summarize_records(read_frontier_xlsx(args.input_xlsx))
    result["source"]["input_file_name"] = args.input_xlsx.name  # type: ignore[index]
    result["source"]["input_file_sha256"] = _sha256(args.input_xlsx)  # type: ignore[index]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")


if __name__ == "__main__":
    main()
