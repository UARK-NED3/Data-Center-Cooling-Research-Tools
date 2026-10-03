"""Create local-only summaries for the evidence-gated M100 stress test.

This module does not redistribute M100 data or assert a panel-to-rack mapping.
It summarizes measured PLC signals and conditional model outputs that a data
holder has generated locally.  The reported model errors are therefore
workflow diagnostics, not rack, RDHx, or cold-plate validation metrics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


OPERATING_COLUMNS = (
    "supply_temperature_c",
    "return_temperature_c",
    "active_flow_m3h",
    "temperature_rise_k",
    "derived_heat_transfer_kw",
)

MODEL_COLUMNS = (
    ("M0 quasi-steady", "m0_return_temperature_c"),
    ("M1 one-state", "m1_return_temperature_c"),
    ("M2 two-state", "m2_return_temperature_c"),
)


def _require_private_destination(output_dir: str | Path) -> Path:
    """Reject a result destination inside this public-source repository."""

    destination = Path(output_dir).resolve()
    repository_root = Path(__file__).resolve().parents[2]
    if destination == repository_root or repository_root in destination.parents:
        raise ValueError(
            "M100-derived outputs must be written outside the public repository "
            "until derivative-use and publication rights are confirmed"
        )
    return destination

SUMMARY_PREFIX = {
    "supply_temperature_c": "supply_temperature_c",
    "return_temperature_c": "return_temperature_c",
    "active_flow_m3h": "active_flow_m3h",
    "temperature_rise_k": "temperature_rise_k",
    "derived_heat_transfer_kw": "screening_heat_rate_kw",
}


def _require_columns(frame: pd.DataFrame, columns: set[str], context: str) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        raise ValueError(f"{context} is missing columns {sorted(missing)}")


def summarize_operating_statistics(frame: pd.DataFrame) -> pd.DataFrame:
    """Return per-panel descriptive statistics without pooling Q101 and Q102.

    The screening heat rate is supplied by the local intake as
    ``rho cp Vdot (Treturn - Tsupply)``.  It is deliberately retained as a
    derived diagnostic, not promoted to an independent calorimetric target.
    """

    _require_columns(frame, {"timestamp", "panel", *OPERATING_COLUMNS}, "PLC signal table")
    records: list[dict[str, object]] = []
    for panel, group in frame.groupby("panel", sort=True):
        ordered = group.sort_values("timestamp", kind="stable")
        record: dict[str, object] = {
            "panel": str(panel),
            "sample_count": int(len(ordered)),
            "start_utc": pd.to_datetime(ordered["timestamp"], utc=True).min().isoformat(),
            "end_utc": pd.to_datetime(ordered["timestamp"], utc=True).max().isoformat(),
        }
        for column in OPERATING_COLUMNS:
            values = pd.to_numeric(ordered[column], errors="coerce")
            label = SUMMARY_PREFIX[column]
            record[f"{label}_p05"] = float(values.quantile(0.05))
            record[f"{label}_p50"] = float(values.quantile(0.50))
            record[f"{label}_p95"] = float(values.quantile(0.95))
        flow = pd.to_numeric(ordered["active_flow_m3h"], errors="coerce")
        heat_rate = pd.to_numeric(ordered["derived_heat_transfer_kw"], errors="coerce")
        record["screening_heat_rate_flow_correlation"] = float(flow.corr(heat_rate))
        records.append(record)
    return pd.DataFrame.from_records(records)


def summarize_conditional_test_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    """Summarize only the untouched chronological test records by model class."""

    required = {"split", "return_temperature_c", *(column for _, column in MODEL_COLUMNS)}
    _require_columns(predictions, required, "prediction table")
    test = predictions.loc[predictions["split"] == "test"].copy()
    if test.empty:
        raise ValueError("prediction table has no records labelled 'test'")
    observed = pd.to_numeric(test["return_temperature_c"], errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(observed).all():
        raise ValueError("test observations must be finite")
    records: list[dict[str, object]] = []
    m0_rmse: float | None = None
    for name, column in MODEL_COLUMNS:
        predicted = pd.to_numeric(test[column], errors="coerce").to_numpy(dtype=float)
        if not np.isfinite(predicted).all():
            raise ValueError(f"test predictions for {name} must be finite")
        residual = predicted - observed
        rmse = float(np.sqrt(np.mean(np.square(residual))))
        if m0_rmse is None:
            m0_rmse = rmse
        records.append(
            {
                "model": name,
                "sample_count": int(len(test)),
                "mae_c": float(np.mean(np.abs(residual))),
                "rmse_c": rmse,
                "bias_c": float(np.mean(residual)),
                "max_absolute_error_c": float(np.max(np.abs(residual))),
                "rmse_change_from_m0_percent": float(100.0 * (rmse - m0_rmse) / m0_rmse)
                if m0_rmse > 0.0
                else float("nan"),
            }
        )
    return pd.DataFrame.from_records(records)


def _select_operating_window(
    signals: pd.DataFrame, panel: str, start: str | None, end: str | None
) -> pd.DataFrame:
    selected = signals.loc[signals["panel"] == panel].copy()
    if selected.empty:
        raise ValueError(f"no PLC signals were found for panel {panel}")
    selected["timestamp"] = pd.to_datetime(selected["timestamp"], utc=True)
    window_start = pd.Timestamp(start) if start else selected["timestamp"].min()
    if window_start.tzinfo is None:
        window_start = window_start.tz_localize("UTC")
    window_end = pd.Timestamp(end) if end else window_start + pd.Timedelta(days=1)
    if window_end.tzinfo is None:
        window_end = window_end.tz_localize("UTC")
    window = selected.loc[(selected["timestamp"] >= window_start) & (selected["timestamp"] <= window_end)]
    if window.empty:
        raise ValueError("the selected operating window contains no PLC records")
    return window.sort_values("timestamp", kind="stable")


def _plot_local_result_report(
    signals: pd.DataFrame,
    predictions: pd.DataFrame,
    test_metrics: pd.DataFrame,
    output_path: Path,
    *,
    panel: str,
    operating_start: str | None,
    operating_end: str | None,
    m2_at_candidate_bound: bool,
) -> None:
    """Render a three-part local diagnostic without writing source observations."""

    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError as exc:  # pragma: no cover - environment-specific guard.
        raise RuntimeError("figure generation requires matplotlib") from exc

    window = _select_operating_window(signals, panel, operating_start, operating_end)
    trace = window.set_index("timestamp").resample("5min").median(numeric_only=True)
    ordered_predictions = predictions.sort_values("time_bin", kind="stable").copy()
    ordered_predictions["time_bin"] = pd.to_datetime(ordered_predictions["time_bin"], utc=True)
    test = ordered_predictions.loc[ordered_predictions["split"] == "test"].copy()

    plt.rcParams.update({"font.family": "Arial", "font.size": 8, "savefig.dpi": 300})
    figure = plt.figure(figsize=(11.2, 3.55), constrained_layout=True)
    grid = figure.add_gridspec(1, 3, width_ratios=(1.0, 1.35, 0.85))

    axis_a = figure.add_subplot(grid[0, 0])
    axis_a.plot(trace.index, trace["supply_temperature_c"], color="#0072B2", label="Supply temperature")
    axis_a.plot(trace.index, trace["return_temperature_c"], color="#D55E00", label="Return temperature")
    axis_a.set_ylabel("Temperature (°C)")
    twin = axis_a.twinx()
    twin.plot(trace.index, trace["active_flow_m3h"], color="#009E73", linewidth=0.9, label="Active flow")
    twin.set_ylabel("Active flow (m$^3$ h$^{-1}$)", color="#007C5D")
    twin.tick_params(axis="y", colors="#007C5D")
    handles, labels = axis_a.get_legend_handles_labels()
    flow_handles, flow_labels = twin.get_legend_handles_labels()
    axis_a.legend(handles + flow_handles, labels + flow_labels, loc="upper left", ncol=1, frameon=False, fontsize=6.5)
    axis_a.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=5))
    axis_a.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))
    axis_a.set_title("(a) Measured PLC operating window", loc="left", fontweight="normal")

    axis_b = figure.add_subplot(grid[0, 1])
    axis_b.plot(test["time_bin"], test["return_temperature_c"], color="black", linewidth=1.0, label="Measured return")
    colors = ("#0072B2", "#E69F00", "#CC79A7")
    for (name, column), color in zip(MODEL_COLUMNS, colors):
        axis_b.plot(test["time_bin"], test[column], color=color, linewidth=0.75, label=name)
    axis_b.set_ylabel("Return temperature (°C)")
    axis_b.set_title("(b) Locked chronological test block", loc="left", fontweight="normal")
    axis_b.legend(loc="upper left", ncol=2, frameon=False, fontsize=6.5)

    axis_c = figure.add_subplot(grid[0, 2])
    bars = axis_c.bar(test_metrics["model"], test_metrics["rmse_c"], color=colors, width=0.62)
    axis_c.set_ylabel("Test RMSE (°C)")
    axis_c.set_ylim(0.0, max(0.1, float(test_metrics["rmse_c"].max()) * 1.30))
    axis_c.set_title("(c) Conditional prediction error", loc="left", fontweight="normal")
    axis_c.tick_params(axis="x", labelrotation=18, labelsize=7)
    for bar, value in zip(bars, test_metrics["rmse_c"]):
        axis_c.text(bar.get_x() + bar.get_width() / 2.0, float(value) + 0.02, f"{float(value):.3f}", ha="center", va="bottom", fontsize=8)
    if m2_at_candidate_bound:
        axis_c.text(
            0.99,
            0.96,
            "M2 includes a candidate-bound parameter",
            transform=axis_c.transAxes,
            ha="right",
            va="top",
            fontsize=7,
            color="0.25",
        )
    for axis in (axis_a, axis_b, axis_c):
        axis.grid(alpha=0.22)
    for suffix in (".png", ".pdf", ".svg"):
        figure.savefig(output_path.with_suffix(suffix), bbox_inches="tight")
    plt.close(figure)


def write_local_result_report(
    signals_csv: str | Path,
    predictions_csv: str | Path,
    model_summary_json: str | Path,
    output_dir: str | Path,
    *,
    panel: str = "Q101",
    operating_start: str | None = None,
    operating_end: str | None = None,
) -> dict[str, object]:
    """Write local CSV summaries, a figure, and a provenance-labelled report."""

    destination = _require_private_destination(output_dir)
    signals = pd.read_csv(signals_csv, parse_dates=["timestamp"])
    predictions = pd.read_csv(predictions_csv, parse_dates=["time_bin"])
    with Path(model_summary_json).open(encoding="utf-8") as stream:
        model_summary = json.load(stream)
    statistics = summarize_operating_statistics(signals)
    test_metrics = summarize_conditional_test_metrics(predictions)
    destination.mkdir(parents=True, exist_ok=True)
    statistics.to_csv(destination / "m100_plc_operating_statistics.csv", index=False)
    test_metrics.to_csv(destination / "m100_conditional_test_metrics.csv", index=False)
    figure_path = destination / "m100_conditional_stress_test.png"
    _plot_local_result_report(
        signals,
        predictions,
        test_metrics,
        figure_path,
        panel=panel,
        operating_start=operating_start,
        operating_end=operating_end,
        m2_at_candidate_bound=bool(model_summary.get("m2", {}).get("parameter_at_candidate_bound", False)),
    )
    provenance: dict[str, object] = {
        "analysis": "m100_rdhx_v0_1 conditional local result report",
        "panel": panel,
        "signals_csv": str(Path(signals_csv).resolve()),
        "predictions_csv": str(Path(predictions_csv).resolve()),
        "model_summary_json": str(Path(model_summary_json).resolve()),
        "evidence_class": "conditional_local_stress_test",
        "interpretation_limit": model_summary.get("interpretation_limit"),
        "output_files": [
            str((destination / "m100_plc_operating_statistics.csv").resolve()),
            str((destination / "m100_conditional_test_metrics.csv").resolve()),
            str(figure_path.resolve()),
            str(figure_path.with_suffix(".pdf").resolve()),
            str(figure_path.with_suffix(".svg").resolve()),
        ],
    }
    (destination / "m100_conditional_stress_test_provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )
    return provenance


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--signals-csv", type=Path, required=True)
    parser.add_argument("--predictions-csv", type=Path, required=True)
    parser.add_argument("--model-summary-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panel", choices=("Q101", "Q102"), default="Q101")
    parser.add_argument("--operating-start", default=None, help="Optional UTC ISO-8601 window start.")
    parser.add_argument("--operating-end", default=None, help="Optional UTC ISO-8601 window end.")
    arguments = parser.parse_args(argv)
    write_local_result_report(
        arguments.signals_csv,
        arguments.predictions_csv,
        arguments.model_summary_json,
        arguments.output_dir,
        panel=arguments.panel,
        operating_start=arguments.operating_start,
        operating_end=arguments.operating_end,
    )


if __name__ == "__main__":
    main()
