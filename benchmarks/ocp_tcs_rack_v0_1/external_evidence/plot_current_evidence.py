"""Create local, provenance-labelled figures from public third-party datasets.

The script deliberately writes outputs to a user-selected local directory. It
does not copy source measurements, PDF figures, or source workbooks into this
repository.  Frontier waste-heat values are labelled as source-calculated; NREL
cooling-power and temperature values retain their reported measurement label.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def _imports():
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - environment-specific guard.
        raise RuntimeError("Plot generation requires pandas and matplotlib") from exc
    return plt, pd


def _style(plt) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.labelsize": 10,
            "axes.titlesize": 11,
            "legend.fontsize": 9,
            "figure.dpi": 180,
            "savefig.dpi": 300,
        }
    )


def _save(fig, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for extension in ("svg", "png"):
        fig.savefig(output_dir / f"{stem}.{extension}", bbox_inches="tight")


def _frontier_monthly(path: Path):
    _, pd = _imports()
    frame = pd.read_excel(path, sheet_name="Frontier2023", skiprows=[1])
    frame = frame.rename(columns={frame.columns[0]: "timestamp"})
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    return (
        frame.set_index("timestamp")
        .resample("MS")
        .mean(numeric_only=True)
        .rename(columns={"Power Usage Effectiveness\u00a0": "pue"})
    )


def _nrel_monthly(input_dir: Path):
    _, pd = _imports()
    liquid_summary = input_dir / "HPCDC_Liquid_Monthly_Mean.csv"
    air_summary = input_dir / "HPCDC_Air_Monthly_Mean.csv"
    if liquid_summary.exists() and air_summary.exists():
        liquid = pd.read_csv(liquid_summary)
        air = pd.read_csv(air_summary)
        if len(liquid.columns) != 4 or len(air.columns) != 4:
            raise ValueError("NREL monthly-summary files must have four documented columns")
        liquid.columns = ["month", "liquid_heat_kw", "liquid_supply_c", "liquid_return_c"]
        air.columns = ["month", "air_heat_kw", "air_supply_c", "air_return_c"]
        liquid["month"] = pd.to_datetime(liquid["month"], format="%b-%y")
        air["month"] = pd.to_datetime(air["month"], format="%b-%y")
        return liquid.merge(air, on="month", validate="one_to_one").set_index("month").sort_index()

    files = sorted(input_dir.glob("NREL_HPCDC_*.csv"))
    if not files:
        raise FileNotFoundError(f"no NREL_HPCDC_*.csv files in {input_dir}")
    frames = []
    for path in files:
        frame = pd.read_csv(path)
        if len(frame.columns) != 7:
            raise ValueError(f"{path.name}: expected seven documented NREL columns")
        selected = frame.iloc[:, [0, 1, 2, 3, 4, 5, 6]].copy()
        selected.columns = [
            "timestamp",
            "air_heat_kw",
            "air_supply_c",
            "air_return_c",
            "liquid_heat_kw",
            "liquid_supply_c",
            "liquid_return_c",
        ]
        selected["timestamp"] = pd.to_datetime(selected["timestamp"])
        frames.append(selected)
    return pd.concat(frames, ignore_index=True).set_index("timestamp").sort_index().resample("MS").mean()


def plot_frontier_seasonal_control(frontier_xlsx: Path, output_dir: Path) -> None:
    plt, _ = _imports()
    _style(plt)
    data = _frontier_monthly(frontier_xlsx)
    delta_t = data["Overall-average Coolant Return Temp"] - data["Overall Coolant Supply Temp"]

    fig, axes = plt.subplots(3, 1, figsize=(8.0, 8.2), sharex=True)
    fig.suptitle("Frontier 2023 facility-secondary-loop seasonal operation")

    axes[0].plot(data.index, data["Overall_WasteHeat"], color="#0072B2", marker="o", label="Waste heat (source-calculated)")
    axes[0].plot(data.index, data["Frontier Compute Power"], color="#D55E00", marker="s", label="Compute power (reported)")
    axes[0].set_ylabel("Monthly mean (MW)")
    axes[0].legend(loc="upper right")

    flow_axis = axes[1]
    temperature_axis = flow_axis.twinx()
    flow_axis.plot(data.index, data["Overall Coolant FLow"] / 1000.0, color="#009E73", marker="o", label="Coolant flow")
    temperature_axis.plot(data.index, delta_t, color="#CC79A7", marker="s", label="Return minus supply")
    flow_axis.set_ylabel("Flow (10³ gpm)", color="#009E73")
    temperature_axis.set_ylabel("Temperature rise (K)", color="#CC79A7")
    lines = flow_axis.get_lines() + temperature_axis.get_lines()
    flow_axis.legend(lines, [line.get_label() for line in lines], loc="upper right")

    axes[2].plot(data.index, data["pue"], color="#000000", marker="o", label="PUE (reported)")
    axes[2].set_ylabel("PUE (-)")
    axes[2].set_ylim(1.02, max(1.08, data["pue"].max() + 0.005))
    axes[2].set_xlabel("Month in 2023")
    axes[2].grid(axis="y", alpha=0.25)
    for axis in axes[:2]:
        axis.grid(axis="y", alpha=0.25)
    fig.text(
        0.01,
        0.005,
        "Source: Grant et al., Frontier HPC & Facility Data (2024), Figshare DOI 10.6084/m9.figshare.24391240.v4. "
        "Facility-secondary-loop scope. Waste heat is source-calculated from subloop flow and temperature records.",
        ha="left",
        va="bottom",
        fontsize=7.5,
        wrap=True,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    _save(fig, output_dir, "frontier_seasonal_control")
    plt.close(fig)


def plot_frontier_subloop_sharing(frontier_xlsx: Path, output_dir: Path) -> None:
    plt, pd = _imports()
    _style(plt)
    frame = pd.read_excel(frontier_xlsx, sheet_name="Frontier2023", skiprows=[1])
    colors = ["#0072B2", "#D55E00", "#009E73"]
    fig, axis = plt.subplots(figsize=(7.2, 5.5))
    for index, color in zip((1, 2, 3), colors):
        flow_share = frame[f"SubLoop{index}-Coolant FLow"] / frame["Overall Coolant FLow"]
        heat_share = frame[f"SubLoop{index}_WasteHeat"] / frame["Overall_WasteHeat"]
        valid = (frame["Overall Coolant FLow"] > 0) & (frame["Overall_WasteHeat"] > 0)
        axis.scatter(flow_share[valid], heat_share[valid], s=4, alpha=0.045, color=color, label=f"Subloop {index}", rasterized=True)
        axis.scatter(flow_share[valid].mean(), heat_share[valid].mean(), s=65, color=color, edgecolor="white", linewidth=0.7, zorder=3)
    axis.plot([0, 1], [0, 1], color="0.25", linewidth=1.1, linestyle="--", label="Equal duty and flow fractions")
    axis.set_xlim(0, 0.65)
    axis.set_ylim(0, 0.9)
    axis.set_xlabel("Subloop fraction of total coolant flow (-)")
    axis.set_ylabel("Subloop fraction of total waste heat (-)")
    axis.set_title("Frontier 2023 subloop duty allocation")
    axis.grid(alpha=0.25)
    axis.legend(loc="upper left")
    fig.text(
        0.01,
        0.005,
        "Each point is a 10-minute record. Subloop waste heat is source-calculated, so this figure describes thermal-duty allocation rather than an independent heat-balance validation.",
        ha="left",
        va="bottom",
        fontsize=7.5,
        wrap=True,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    _save(fig, output_dir, "frontier_subloop_duty_allocation")
    plt.close(fig)


def plot_nrel_seasonality(nrel_input_dir: Path, output_dir: Path) -> None:
    plt, _ = _imports()
    _style(plt)
    data = _nrel_monthly(nrel_input_dir)
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.4), sharex=True)
    fig.suptitle("NREL ESIF HPC hybrid cooling-system seasonal operation")

    axes[0].plot(data.index, data["liquid_heat_kw"], color="#0072B2", marker="o", label="Liquid cooling power")
    axes[0].plot(data.index, data["air_heat_kw"], color="#E69F00", marker="s", label="Air cooling power")
    axes[0].set_ylabel("Monthly mean reported cooling power (kW)")
    axes[0].legend(loc="upper left")
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].plot(data.index, data["liquid_return_c"] - data["liquid_supply_c"], color="#CC79A7", marker="o", label="Liquid return minus supply")
    axes[1].plot(data.index, data["air_return_c"] - data["air_supply_c"], color="#009E73", marker="s", label="Air return minus supply")
    axes[1].set_ylabel("Monthly mean temperature rise (K)")
    axes[1].set_xlabel("Month")
    axes[1].legend(loc="upper left")
    axes[1].grid(axis="y", alpha=0.25)
    fig.text(
        0.01,
        0.005,
        "Source: NREL ESIF HPC Data Center Cooling System archive. Source-provided monthly averages of one-minute reported cooling-power and supply/return-temperature records. "
        "No branch flow, pressure, rack topology, or cold-plate temperature is available in this archive.",
        ha="left",
        va="bottom",
        fontsize=7.5,
        wrap=True,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    _save(fig, output_dir, "nrel_hybrid_cooling_seasonality")
    plt.close(fig)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-xlsx", type=Path, required=True)
    parser.add_argument("--nrel-input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    plot_frontier_seasonal_control(args.frontier_xlsx, args.output_dir)
    plot_frontier_subloop_sharing(args.frontier_xlsx, args.output_dir)
    plot_nrel_seasonality(args.nrel_input_dir, args.output_dir)


if __name__ == "__main__":
    main()
