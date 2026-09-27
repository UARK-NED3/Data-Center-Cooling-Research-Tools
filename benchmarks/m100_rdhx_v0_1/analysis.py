"""Traceable reductions for measured M100 RDHx PLC signals.

The M100 Schneider stream reports integer-coded PLC values for two HMI
panels.  The conversions in ``SIGNAL_SCALES`` are source-documentation
metadata, not inferred calibration coefficients.  ``derived_heat_transfer_kw``
is a screening quantity at the PLC temperature-and-flow control volume.  It is
not a rack heat load, a cold-plate duty, or an independently validated value.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


SIGNAL_SCALES: dict[str, float] = {
    "active_flow_m3h": 10.0,
    "supply_temperature_c": 10.0,
    "return_temperature_c": 10.0,
    "reported_delta_temperature_c": 10.0,
    "flow_sensor_1_m3h": 50.0,
    "flow_sensor_2_m3h": 50.0,
    "pump_pid_output": 1.0,
    "valve_1_position_percent": 100.0,
    "valve_2_position_percent": 100.0,
    "temperature_setpoint_c": 10.0,
}

REQUIRED_THERMAL_SIGNALS = (
    "active_flow_m3h",
    "supply_temperature_c",
    "return_temperature_c",
    "reported_delta_temperature_c",
)


def _validate_long_signal(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    required_columns = {"timestamp", "panel", "value"}
    missing = required_columns.difference(frame.columns)
    if missing:
        raise ValueError(f"{name}: missing required columns {sorted(missing)}")
    selected = frame.loc[:, ["timestamp", "panel", "value"]].copy()
    selected["timestamp"] = pd.to_datetime(selected["timestamp"], utc=True)
    if selected[["timestamp", "panel"]].duplicated().any():
        raise ValueError(f"{name}: duplicate timestamp-panel measurements")
    if selected["panel"].isna().any():
        raise ValueError(f"{name}: panel identifiers are required for an unambiguous join")
    return selected


def assemble_panel_signals(signals: Mapping[str, pd.DataFrame]) -> pd.DataFrame:
    """Inner-join decoded signals on timestamp and HMI panel.

    Joining on timestamp alone is invalid because Q101 and Q102 report at the
    same times.  The inner join deliberately records only synchronized rows;
    upstream code must report the resulting coverage rather than silently
    forward-filling gaps.
    """

    missing = set(REQUIRED_THERMAL_SIGNALS).difference(signals)
    if missing:
        raise ValueError(f"missing required signals {sorted(missing)}")
    result: pd.DataFrame | None = None
    for name, frame in signals.items():
        if name not in SIGNAL_SCALES:
            raise ValueError(f"no documented scale is registered for {name}")
        decoded = _validate_long_signal(name, frame).rename(columns={"value": name})
        decoded[name] = pd.to_numeric(decoded[name], errors="coerce") / SIGNAL_SCALES[name]
        if result is None:
            result = decoded
        else:
            result = result.merge(decoded, on=["timestamp", "panel"], how="inner", validate="one_to_one")
    assert result is not None
    return result.sort_values(["panel", "timestamp"], kind="stable").reset_index(drop=True)


def calculate_thermal_quantities(
    frame: pd.DataFrame,
    *,
    density_kg_m3: float = 997.0,
    cp_j_kgk: float = 4182.0,
) -> pd.DataFrame:
    """Calculate PLC-control-volume temperature rise and screening heat rate.

    ``rho`` and ``cp`` are explicit assumptions.  The function does not imply
    that the circuit fluid is pure water or that this control volume contains
    all facility or rack heat loads.
    """

    required = {
        "active_flow_m3h",
        "supply_temperature_c",
        "return_temperature_c",
        "reported_delta_temperature_c",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"missing thermal columns {sorted(missing)}")
    if density_kg_m3 <= 0 or cp_j_kgk <= 0:
        raise ValueError("density and specific heat must be positive")
    result = frame.copy()
    result["temperature_rise_k"] = result["return_temperature_c"] - result["supply_temperature_c"]
    result["reported_minus_direct_delta_k"] = (
        result["reported_delta_temperature_c"] - result["temperature_rise_k"]
    )
    result["mass_flow_kg_s"] = density_kg_m3 * result["active_flow_m3h"] / 3600.0
    result["derived_heat_transfer_kw"] = (
        result["mass_flow_kg_s"] * cp_j_kgk * result["temperature_rise_k"] / 1000.0
    )
    return result


def summarize_signal_quality(frame: pd.DataFrame) -> pd.DataFrame:
    """Return non-destructive per-panel signal checks for a decoded table."""

    if not {"timestamp", "panel"}.issubset(frame.columns):
        raise ValueError("timestamp and panel are required")
    records: list[dict[str, object]] = []
    for panel, group in frame.groupby("panel", sort=True):
        group = group.sort_values("timestamp", kind="stable")
        cadence = group["timestamp"].diff().dt.total_seconds()
        record: dict[str, object] = {
            "panel": panel,
            "synchronized_rows": len(group),
            "start_utc": group["timestamp"].min().isoformat(),
            "end_utc": group["timestamp"].max().isoformat(),
            "median_cadence_s": cadence.dropna().median(),
            "gaps_over_60_s": int((cadence > 60.0).sum()),
        }
        for column in group.columns:
            if column not in {"timestamp", "panel"}:
                record[f"{column}_missing_fraction"] = float(group[column].isna().mean())
        records.append(record)
    return pd.DataFrame.from_records(records)
