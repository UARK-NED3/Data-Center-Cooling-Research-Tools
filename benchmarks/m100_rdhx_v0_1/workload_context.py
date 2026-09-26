"""Local-only visualization of M100 cluster workload and PLC circuit context.

This module deliberately does not fit a heat-load mapping.  It provides a
coverage-gated synchronization visual for deciding whether source topology is
sufficient to begin a physical model comparison.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def select_complete_power_windows(
    frame: pd.DataFrame, *, expected_nodes: int, minimum_fraction: float = 0.98
) -> pd.DataFrame:
    """Keep bins with declared near-complete node coverage and full 5-min samples."""

    required = {"mean_observed_cluster_power_kw", "mean_observed_node_count", "timestamp_count"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"power summary is missing columns {sorted(missing)}")
    if expected_nodes <= 0 or not 0 < minimum_fraction <= 1:
        raise ValueError("expected_nodes must be positive and minimum_fraction must be in (0, 1]")
    return frame.loc[
        (frame["mean_observed_node_count"] >= expected_nodes * minimum_fraction)
        & (frame["timestamp_count"] >= 15)
    ].copy()


def plot_workload_context(
    power_csv: str | Path,
    plc_csv: str | Path,
    output_path: str | Path,
    *,
    start: str,
    end: str,
    expected_nodes: int = 980,
) -> pd.DataFrame:
    """Create a protected system-context trace without assigning a loop load."""

    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - environment-specific guard.
        raise RuntimeError("figure generation requires matplotlib") from exc
    power = pd.read_csv(power_csv, parse_dates=["time_bin"])
    power["time_bin"] = pd.to_datetime(power["time_bin"], utc=True)
    power = select_complete_power_windows(power, expected_nodes=expected_nodes)
    power = power[(power["time_bin"] >= pd.Timestamp(start)) & (power["time_bin"] <= pd.Timestamp(end))]
    plc = pd.read_csv(plc_csv, parse_dates=["timestamp"])
    plc["timestamp"] = pd.to_datetime(plc["timestamp"], utc=True)
    plc = plc[(plc["timestamp"] >= pd.Timestamp(start)) & (plc["timestamp"] <= pd.Timestamp(end))]
    plc["time_bin"] = plc["timestamp"].dt.floor("5min")
    numeric_columns = plc.select_dtypes(include="number").columns.tolist()
    plc = (
        plc.groupby(["panel", "time_bin"], as_index=False)[numeric_columns]
        .median()
        .rename(columns={"time_bin": "timestamp"})
    )
    if power.empty or plc.empty:
        raise ValueError("requested context window has no complete power bins or PLC records")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "savefig.dpi": 300})
    colors = {"Q101": "#0072B2", "Q102": "#D55E00"}
    fig, axes = plt.subplots(3, 1, figsize=(7.1, 6.8), sharex=True)
    axes[0].plot(power["time_bin"], power["mean_observed_cluster_power_kw"], color="#222222", linewidth=1.2)
    axes[0].set_ylabel("Observed cluster power (kW)")
    for panel, group in plc.groupby("panel", sort=True):
        color = colors.get(panel, "0.25")
        axes[1].plot(group["timestamp"], group["derived_heat_transfer_kw"], color=color, label=f"{panel} screening heat rate")
        axes[2].plot(group["timestamp"], group["supply_temperature_c"], color=color, label=f"{panel} supply")
        axes[2].plot(group["timestamp"], group["return_temperature_c"], color=color, linestyle="--", label=f"{panel} return")
    axes[1].set_ylabel("Screening heat rate (kW)")
    axes[2].set_ylabel("Temperature (degC)")
    axes[2].set_xlabel("UTC time")
    for axis in axes:
        axis.grid(alpha=0.25)
    axes[1].legend(frameon=False, ncol=2)
    axes[2].legend(frameon=False, ncol=2)
    fig.text(
        0.01, 0.006,
        "Top: source-reported node power, retained only when at least 98% of 980 nodes are observed. Lower: PLC-circuit records. "
        "No panel-to-rack or power-to-loop assignment is assumed; screening heat rate is derived from PLC flow and temperatures.",
        ha="left", va="bottom", fontsize=7, wrap=True,
    )
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, bbox_inches="tight")
    plt.close(fig)
    return power


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--power-csv", type=Path, required=True)
    parser.add_argument("--plc-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--expected-nodes", type=int, default=980)
    args = parser.parse_args(argv)
    plot_workload_context(args.power_csv, args.plc_csv, args.output, start=args.start, end=args.end, expected_nodes=args.expected_nodes)


if __name__ == "__main__":
    main()
