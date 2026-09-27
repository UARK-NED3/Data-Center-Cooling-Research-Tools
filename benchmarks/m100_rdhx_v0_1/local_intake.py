"""Run a local-only quality-controlled intake of selected M100 PLC signals.

The source root is intentionally outside the Git checkout.  This module writes
only derived tables, figures, and a provenance record to an explicitly supplied
local output directory.  It does not upload, copy, or redistribute the source
archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from .analysis import assemble_panel_signals, calculate_thermal_quantities, summarize_signal_quality


METRIC_DIRECTORIES = {
    "active_flow_m3h": "PLC_PLC_Q101.Portata_attiva",
    "supply_temperature_c": "PLC_PLC_Q101.Temp_mandata",
    "return_temperature_c": "PLC_PLC_Q101.Temp_ritorno",
    "reported_delta_temperature_c": "PLC_PLC_Q101.Delta_temp",
    "flow_sensor_1_m3h": "PLC_PLC_Q101.Portata_1",
    "flow_sensor_2_m3h": "PLC_PLC_Q101.Portata_2",
    "pump_pid_output": "PLC_PLC_Q101.Out_pid_pompe",
    "valve_1_position_percent": "PLC_PLC_Q101.Pos_valvola1",
    "valve_2_position_percent": "PLC_PLC_Q101.Pos_valvola_2",
    "temperature_setpoint_c": "PLC_PLC_Q101.Set_temperatura",
}


def source_file_for_metric(source_root: str | Path, period: str, signal: str) -> Path:
    """Return the canonical partition path for one M100 Schneider signal."""

    try:
        metric = METRIC_DIRECTORIES[signal]
    except KeyError as exc:
        raise ValueError(f"unknown M100 signal {signal!r}") from exc
    return (
        Path(source_root)
        / f"year_month={period}"
        / "plugin=schneider_pub"
        / f"metric={metric}"
        / "a_0.parquet"
    )


def _read_signal(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"required M100 signal partition not found: {path}")
    frame = pd.read_parquet(path)
    return frame


def load_signals(source_root: str | Path, period: str, signals: Iterable[str] | None = None) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    """Load selected source partitions and return their SHA-256 identities."""

    selected = list(signals or METRIC_DIRECTORIES)
    frames: dict[str, pd.DataFrame] = {}
    checksums: dict[str, str] = {}
    for signal in selected:
        path = source_file_for_metric(source_root, period, signal)
        frames[signal] = _read_signal(path)
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        checksums[signal] = digest.hexdigest()
    return frames, checksums


def _plot_intake(frame: pd.DataFrame, output_dir: Path, start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    """Create local, provenance-labelled figures from synchronized PLC records."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - environment-specific guard.
        raise RuntimeError("figure generation requires matplotlib") from exc
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "savefig.dpi": 300})
    selected = frame[(frame["timestamp"] >= start) & (frame["timestamp"] <= end)].copy()
    if selected.empty:
        raise ValueError("the requested plot window contains no synchronized records")
    outputs: list[str] = []
    colors = {"Q101": "#0072B2", "Q102": "#D55E00"}

    fig, axes = plt.subplots(4, 1, figsize=(7.2, 8.2), sharex=True)
    for panel, group in selected.groupby("panel", sort=True):
        grouped = group.set_index("timestamp").resample("5min").median(numeric_only=True)
        color = colors.get(panel, "0.25")
        axes[0].plot(grouped.index, grouped["supply_temperature_c"], color=color, label=f"{panel} supply")
        axes[0].plot(grouped.index, grouped["return_temperature_c"], color=color, linestyle="--", label=f"{panel} return")
        axes[1].plot(grouped.index, grouped["active_flow_m3h"], color=color, label=panel)
        axes[2].plot(grouped.index, grouped["temperature_rise_k"], color=color, label=panel)
        axes[3].plot(grouped.index, grouped["derived_heat_transfer_kw"], color=color, label=panel)
    axes[0].set_ylabel("Temperature (degC)")
    axes[1].set_ylabel("Active flow (m3/h)")
    axes[2].set_ylabel("Return minus supply (K)")
    axes[3].set_ylabel("Screening heat rate (kW)")
    axes[3].set_xlabel("UTC time")
    axes[0].legend(ncol=2, frameon=False)
    axes[1].legend(frameon=False)
    for axis in axes:
        axis.grid(alpha=0.25)
    fig.text(
        0.01, 0.006,
        "M100 Dataset 12 Schneider PLC records. Measured temperatures and flow; heat rate is derived as rho cp Vdot (Treturn - Tsupply) using stated water-property assumptions. "
        "Q101 and Q102 are shown separately; topology and rack mapping are unresolved.",
        ha="left", va="bottom", fontsize=7, wrap=True,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    for suffix in ("png", "svg"):
        path = output_dir / f"m100_rdhx_operating_trace.{suffix}"
        fig.savefig(path, bbox_inches="tight")
        outputs.append(str(path))
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.35))
    for panel, group in selected.groupby("panel", sort=True):
        color = colors.get(panel, "0.25")
        axes[0].scatter(group["active_flow_m3h"], group["flow_sensor_1_m3h"], s=1, alpha=0.08, color=color, label=panel, rasterized=True)
        axes[1].scatter(group["temperature_rise_k"], group["reported_delta_temperature_c"], s=1, alpha=0.08, color=color, label=panel, rasterized=True)
    for axis, label in zip(axes, ("Flow-sensor consistency", "Temperature-difference consistency")):
        lower, upper = axis.get_xlim()
        axis.plot([lower, upper], [lower, upper], color="0.2", linestyle="--", linewidth=0.8, label="One-to-one")
        axis.set_title(label)
        axis.grid(alpha=0.25)
        axis.legend(frameon=False, markerscale=4)
    axes[0].set_xlabel("Active flow (m3/h)")
    axes[0].set_ylabel("Flow sensor 1 (m3/h)")
    axes[1].set_xlabel("Direct return minus supply (K)")
    axes[1].set_ylabel("Reported Delta temp (K)")
    fig.tight_layout()
    for suffix in ("png", "svg"):
        path = output_dir / f"m100_rdhx_sensor_consistency.{suffix}"
        fig.savefig(path, bbox_inches="tight")
        outputs.append(str(path))
    plt.close(fig)
    return outputs


def run_local_intake(source_root: str | Path, output_dir: str | Path, *, period: str = "22-09", plot_start: str | None = None, plot_end: str | None = None) -> dict[str, object]:
    """Read, audit, derive, and locally render selected M100 PLC signals."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    frames, checksums = load_signals(source_root, period)
    synchronized = calculate_thermal_quantities(assemble_panel_signals(frames))
    quality = summarize_signal_quality(synchronized)
    synchronized.to_csv(destination / "m100_rdhx_synchronized_signals.csv", index=False)
    quality.to_csv(destination / "m100_rdhx_signal_quality.csv", index=False)
    start = pd.Timestamp(plot_start, tz="UTC") if plot_start else synchronized["timestamp"].min()
    end = pd.Timestamp(plot_end, tz="UTC") if plot_end else min(start + pd.Timedelta(days=1), synchronized["timestamp"].max())
    figure_paths = _plot_intake(synchronized, destination, start, end)
    provenance = {
        "analysis": "m100_rdhx_v0_1 local intake",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(Path(source_root).resolve()),
        "period": period,
        "source_partition_sha256": checksums,
        "source_record": "10.5281/zenodo.7590583",
        "time_basis": "UTC",
        "join_keys": ["timestamp", "panel"],
        "property_assumptions": {"density_kg_m3": 997.0, "cp_j_kgk": 4182.0},
        "derived_output": "rho cp (Vdot/3600) (T_return - T_supply)",
        "scope_limit": "RDHx PLC control volume; not an individual-rack or cold-plate result",
        "figure_window_utc": {"start": start.isoformat(), "end": end.isoformat()},
        "outputs": figure_paths,
    }
    (destination / "m100_rdhx_provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return provenance


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True, help="Local directory containing year_month=<period> source partitions.")
    parser.add_argument("--output-dir", type=Path, required=True, help="Local output directory outside the public Git checkout.")
    parser.add_argument("--period", default="22-09")
    parser.add_argument("--plot-start", default=None, help="UTC ISO-8601 start time.")
    parser.add_argument("--plot-end", default=None, help="UTC ISO-8601 end time.")
    args = parser.parse_args(argv)
    run_local_intake(args.source_root, args.output_dir, period=args.period, plot_start=args.plot_start, plot_end=args.plot_end)


if __name__ == "__main__":
    main()
