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

# Display names use D0-D2 so the local diagnostic variants cannot be confused
# with the public synthetic benchmark models M1-M3.  The CSV column names keep
# the original m0/m1/m2 prefixes for compatibility with existing local runs.
MODEL_COLUMNS = (
    ("D0 quasi-steady", "m0_return_temperature_c"),
    ("D1 one-state", "m1_return_temperature_c"),
    ("D2 two-state", "m2_return_temperature_c"),
)
MODEL_STYLE_KEYS = ("D0", "D1", "D2")


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
        bias = float(np.mean(residual))
        records.append(
            {
                "model": name,
                "sample_count": int(len(test)),
                "mae_c": float(np.mean(np.abs(residual))),
                "rmse_c": rmse,
                "bias_c": bias,
                # RMSE^2 = bias^2 + error_sd^2 (population SD of the residual).
                "error_sd_c": float(np.std(residual)),
                "bias_share_of_mse": float(bias * bias / (rmse * rmse)) if rmse > 0.0 else float("nan"),
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
    """Render a three-part local diagnostic without writing source observations.

    The figure is drawn at IEEE double-column width.  Panel (a) shows one
    measured PLC window, (b) hourly means over the locked test block, and (c)
    splits each test RMSE into its mean bias and bias-removed spread.
    """

    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.lines import Line2D
    except ImportError as exc:  # pragma: no cover - environment-specific guard.
        raise RuntimeError("figure generation requires matplotlib") from exc
    from benchmarks.publication_style import DOUBLE_COLUMN_IN, ENTITY_STYLE, panel_label, save_figure, use_style

    window = _select_operating_window(signals, panel, operating_start, operating_end)
    trace = window.set_index("timestamp").resample("5min").median(numeric_only=True)
    hours = (trace.index - trace.index[0]).total_seconds() / 3600.0
    ordered_predictions = predictions.sort_values("time_bin", kind="stable").copy()
    ordered_predictions["time_bin"] = pd.to_datetime(ordered_predictions["time_bin"], utc=True)
    test = ordered_predictions.loc[ordered_predictions["split"] == "test"].copy()
    hourly = test.set_index("time_bin").resample("1h").mean(numeric_only=True)
    plotted_columns = ["return_temperature_c", *(column for _, column in MODEL_COLUMNS)]

    use_style()
    figure = plt.figure(figsize=(DOUBLE_COLUMN_IN, 2.55))
    grid = figure.add_gridspec(2, 3, width_ratios=(1.0, 1.5, 0.95))

    axis_t = figure.add_subplot(grid[0, 0])
    axis_f = figure.add_subplot(grid[1, 0], sharex=axis_t)
    axis_t.plot(hours, trace["supply_temperature_c"], color=ENTITY_STYLE["supply"]["color"], linewidth=1.0, label="Supply")
    axis_t.plot(hours, trace["return_temperature_c"], color=ENTITY_STYLE["return"]["color"], linewidth=1.0, label="Return")
    axis_t.set_ylabel("$T$ (°C)")
    axis_t.legend(loc="center right")
    axis_t.tick_params(labelbottom=False)
    axis_f.plot(hours, trace["active_flow_m3h"], color=ENTITY_STYLE["measured"]["color"], linewidth=0.9)
    axis_f.set_ylabel("$\\dot V$ (m$^3$ h$^{-1}$)")
    axis_f.set_xlabel(f"Hours from {trace.index[0]:%d %b %Y} 00:00 UTC")
    span = max(float(hours[-1]), 1.0)
    axis_f.set_xlim(0.0, span)
    if span >= 23.0:
        axis_f.set_xticks((0, 6, 12, 18, 24))
    figure.align_ylabels((axis_t, axis_f))

    axis_b = figure.add_subplot(grid[:, 1])
    axis_b.plot(hourly.index, hourly["return_temperature_c"], color=ENTITY_STYLE["measured"]["color"], linewidth=1.1, label="Measured", zorder=4)
    for (name, column), key in zip(MODEL_COLUMNS, MODEL_STYLE_KEYS):
        style = ENTITY_STYLE[key]
        axis_b.plot(hourly.index, hourly[column], color=style["color"], linestyle=style["linestyle"], linewidth=1.0, label=name.split()[0])
    axis_b.set_ylabel("Return temperature (°C)")
    axis_b.xaxis.set_major_locator(mdates.DayLocator())
    axis_b.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    axis_b.xaxis.set_minor_locator(mdates.HourLocator(byhour=(6, 12, 18)))
    axis_b.set_xlabel("Locked test block, 2022 (hourly means)")
    axis_b.legend(loc="upper center", ncols=4, handlelength=1.6, columnspacing=0.8)
    values = hourly[plotted_columns].to_numpy(dtype=float)
    low = float(np.nanmin(values))
    high = float(np.nanmax(values))
    axis_b.set_ylim(low - 0.15, high + 0.45 * (high - low) + 0.15)

    axis_c = figure.add_subplot(grid[:, 2])
    names = [str(name).split()[0] for name in test_metrics["model"]]
    rows = list(range(len(names)))[::-1]
    for y, (_, metric), key in zip(rows, test_metrics.iterrows(), MODEL_STYLE_KEYS):
        color = ENTITY_STYLE[key]["color"]
        axis_c.plot([0.0, metric["rmse_c"]], [y, y], color=color, linewidth=0.8, alpha=0.6)
        axis_c.plot(abs(metric["bias_c"]), y, linestyle="none", marker="o", markerfacecolor="white", markeredgecolor=color)
        axis_c.plot(metric["error_sd_c"], y, linestyle="none", marker="x", color=color)
        axis_c.plot(metric["rmse_c"], y, linestyle="none", marker="o", color=color)
        axis_c.text(metric["rmse_c"] + 0.04, y, f"{metric['rmse_c']:.2f}", va="center", fontsize=7)
    labels = [f"{name}*" if name == "D2" and m2_at_candidate_bound else name for name in names]
    axis_c.set_yticks(rows, labels)
    axis_c.tick_params(axis="y", which="minor", left=False, right=False)
    axis_c.set_ylim(-1.1, len(names) - 0.4)
    axis_c.set_xlim(0.0, max(1.1, float(test_metrics["rmse_c"].max()) + 0.3))
    axis_c.set_xlabel("Test error (°C)")
    axis_c.legend(
        handles=[
            Line2D([], [], linestyle="none", marker="o", color="0.3", label="RMSE"),
            Line2D([], [], linestyle="none", marker="o", markerfacecolor="white", markeredgecolor="0.3", label="|Bias|"),
            Line2D([], [], linestyle="none", marker="x", color="0.3", label="SD"),
        ],
        loc="lower right",
        ncols=3,
        handletextpad=0.2,
        columnspacing=0.6,
    )
    if m2_at_candidate_bound:
        axis_c.text(0.03, 0.97, "* parameter at\ncandidate bound", transform=axis_c.transAxes, fontsize=7, va="top")

    panel_label(axis_t, "a", x=-0.34, y=1.04)
    panel_label(axis_b, "b", x=-0.14, y=1.02)
    panel_label(axis_c, "c", x=-0.2, y=1.02)
    save_figure(figure, output_path.with_suffix(""))


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
