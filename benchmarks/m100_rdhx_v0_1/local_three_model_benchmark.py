"""Local-only chronological comparison of three RDHx thermal model classes.

This module deliberately treats facility-wide IPMI power as an *unassigned load
proxy*.  It may support a stress test of model workflow, but it cannot validate
an RDHx, row, or rack model until the physical mapping is supplied.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from benchmarks.m100_rdhx_v0_1.model_comparison import (
    fit_m0_load_fraction,
    predict_m0_quasisteady,
    simulate_m1_lumped,
    simulate_m2_two_state,
    split_contiguous_time_series,
)


CP_J_KGK = 4182.0
TIME_STEP_S = 300.0
M1_CAPACITANCE_CANDIDATES_J_K = (1.0e8, 3.0e8, 1.0e9, 3.0e9, 1.0e10, 3.0e10)
M2_LOAD_CAPACITANCE_CANDIDATES_J_K = (3.0e8, 1.0e9, 3.0e9, 1.0e10, 3.0e10)
M2_FLUID_CAPACITANCE_CANDIDATES_J_K = (1.0e9, 3.0e9, 1.0e10, 3.0e10)
M2_CONDUCTANCE_CANDIDATES_W_K = (2.0e4, 1.0e5, 5.0e5)


def build_panel_comparison_frame(
    plc_signals: pd.DataFrame,
    cluster_power: pd.DataFrame,
    *,
    panel: str,
    minimum_node_count: float,
) -> pd.DataFrame:
    """Synchronize one PLC panel with complete five-minute power intervals.

    PLC values are mean-resampled within a five-minute bin.  The method does
    not infer a physical panel-to-node mapping; it only creates a time-aligned
    conditional comparison dataset.
    """

    plc_required = {
        "timestamp",
        "panel",
        "supply_temperature_c",
        "return_temperature_c",
        "mass_flow_kg_s",
    }
    power_required = {
        "time_bin",
        "mean_observed_cluster_power_kw",
        "mean_observed_node_count",
        "timestamp_count",
    }
    missing_plc = plc_required.difference(plc_signals.columns)
    missing_power = power_required.difference(cluster_power.columns)
    if missing_plc:
        raise ValueError(f"PLC table is missing columns {sorted(missing_plc)}")
    if missing_power:
        raise ValueError(f"power table is missing columns {sorted(missing_power)}")
    if minimum_node_count <= 0.0:
        raise ValueError("minimum_node_count must be positive")

    selected = plc_signals.loc[plc_signals["panel"] == panel, list(plc_required)].copy()
    if selected.empty:
        raise ValueError(f"no PLC records were found for panel {panel}")
    selected["timestamp"] = pd.to_datetime(selected["timestamp"], utc=True)
    selected["time_bin"] = selected["timestamp"].dt.floor("5min")
    resampled = (
        selected.groupby(["time_bin", "panel"], as_index=False, sort=True)[
            ["supply_temperature_c", "return_temperature_c", "mass_flow_kg_s"]
        ]
        .mean()
    )

    power = cluster_power.loc[:, list(power_required)].copy()
    power["time_bin"] = pd.to_datetime(power["time_bin"], utc=True)
    complete_power = power.loc[
        (power["mean_observed_node_count"] >= minimum_node_count)
        & (power["timestamp_count"] > 0)
    ].copy()
    joined = resampled.merge(complete_power, on="time_bin", how="inner", validate="one_to_one")
    if joined.empty:
        raise ValueError("no synchronized PLC and complete power bins remain after filtering")
    if (joined["mass_flow_kg_s"] <= 0.0).any():
        raise ValueError("nonpositive mass flow remains after synchronization")
    return joined.sort_values("time_bin", kind="stable").reset_index(drop=True)


def calculate_error_metrics(predicted_c: np.ndarray, observed_c: np.ndarray) -> dict[str, float | int]:
    """Return temperature metrics with bias defined as predicted minus observed."""

    prediction = np.asarray(predicted_c, dtype=float)
    observed = np.asarray(observed_c, dtype=float)
    if prediction.ndim != 1 or observed.ndim != 1 or prediction.size != observed.size:
        raise ValueError("predicted and observed temperatures must be equally sized vectors")
    if prediction.size == 0 or not np.isfinite(prediction).all() or not np.isfinite(observed).all():
        raise ValueError("temperature vectors must be finite and nonempty")
    residual = prediction - observed
    return {
        "sample_count": int(prediction.size),
        "mae_c": float(np.mean(np.abs(residual))),
        "rmse_c": float(np.sqrt(np.mean(np.square(residual)))),
        "bias_c": float(np.mean(residual)),
        "max_absolute_error_c": float(np.max(np.abs(residual))),
    }


def _validation_score(prediction: np.ndarray, observed: np.ndarray, validation_indices: np.ndarray) -> float:
    return float(calculate_error_metrics(prediction[validation_indices], observed[validation_indices])["rmse_c"])


def _at_candidate_bound(value: float, candidates: tuple[float, ...]) -> bool:
    return bool(np.isclose(value, min(candidates)) or np.isclose(value, max(candidates)))


def _select_m1_capacitance(
    supply: np.ndarray,
    mass_flow: np.ndarray,
    load_proxy: np.ndarray,
    observed: np.ndarray,
    validation_indices: np.ndarray,
    load_fraction: float,
) -> tuple[float, np.ndarray]:
    best: tuple[float, float, np.ndarray] | None = None
    for capacitance in M1_CAPACITANCE_CANDIDATES_J_K:
        prediction = simulate_m1_lumped(
            supply,
            mass_flow,
            load_proxy,
            initial_return_temperature_c=float(observed[0]),
            load_to_circuit_fraction=load_fraction,
            thermal_capacitance_j_k=capacitance,
            time_step_s=TIME_STEP_S,
            cp_j_kgk=CP_J_KGK,
        )
        candidate = (_validation_score(prediction, observed, validation_indices), capacitance, prediction)
        if best is None or candidate[0] < best[0]:
            best = candidate
    assert best is not None
    return best[1], best[2]


def _select_m2_parameters(
    supply: np.ndarray,
    mass_flow: np.ndarray,
    load_proxy: np.ndarray,
    observed: np.ndarray,
    validation_indices: np.ndarray,
    load_fraction: float,
) -> tuple[dict[str, float], np.ndarray]:
    best: tuple[float, dict[str, float], np.ndarray] | None = None
    for load_capacitance in M2_LOAD_CAPACITANCE_CANDIDATES_J_K:
        for fluid_capacitance in M2_FLUID_CAPACITANCE_CANDIDATES_J_K:
            for conductance in M2_CONDUCTANCE_CANDIDATES_W_K:
                prediction = simulate_m2_two_state(
                    supply,
                    mass_flow,
                    load_proxy,
                    initial_return_temperature_c=float(observed[0]),
                    initial_load_temperature_c=float(observed[0]),
                    load_to_circuit_fraction=load_fraction,
                    load_thermal_capacitance_j_k=load_capacitance,
                    fluid_thermal_capacitance_j_k=fluid_capacitance,
                    heat_exchange_conductance_w_k=conductance,
                    time_step_s=TIME_STEP_S,
                    cp_j_kgk=CP_J_KGK,
                )
                parameters = {
                    "load_thermal_capacitance_j_k": load_capacitance,
                    "fluid_thermal_capacitance_j_k": fluid_capacitance,
                    "heat_exchange_conductance_w_k": conductance,
                }
                candidate = (_validation_score(prediction, observed, validation_indices), parameters, prediction)
                if best is None or candidate[0] < best[0]:
                    best = candidate
    assert best is not None
    return best[1], best[2]


def run_three_model_comparison(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Fit M0 on training data and select M1/M2 capacity from a later holdout.

    The final chronological block remains untouched until evaluation.  Each
    dynamic simulation uses only the first observed return temperature to
    initialize its state, then advances solely from the declared inputs.
    """

    required = {
        "time_bin",
        "panel",
        "supply_temperature_c",
        "return_temperature_c",
        "mass_flow_kg_s",
        "mean_observed_cluster_power_kw",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"comparison frame is missing columns {sorted(missing)}")
    if frame.empty:
        raise ValueError("comparison frame is empty")
    panel_values = frame["panel"].dropna().unique()
    if len(panel_values) != 1:
        raise ValueError("comparison frame must contain one panel only")

    ordered = frame.sort_values("time_bin", kind="stable").reset_index(drop=True).copy()
    supply = ordered["supply_temperature_c"].to_numpy(dtype=float)
    observed = ordered["return_temperature_c"].to_numpy(dtype=float)
    mass_flow = ordered["mass_flow_kg_s"].to_numpy(dtype=float)
    load_proxy = ordered["mean_observed_cluster_power_kw"].to_numpy(dtype=float)
    train_indices, validation_indices, test_indices = split_contiguous_time_series(len(ordered))

    m0_fraction = fit_m0_load_fraction(
        supply[train_indices],
        mass_flow[train_indices],
        load_proxy[train_indices],
        observed[train_indices],
        cp_j_kgk=CP_J_KGK,
    )
    m0_prediction = predict_m0_quasisteady(
        supply, mass_flow, load_proxy, load_to_circuit_fraction=m0_fraction, cp_j_kgk=CP_J_KGK
    )
    m1_capacitance, m1_prediction = _select_m1_capacitance(
        supply, mass_flow, load_proxy, observed, validation_indices, m0_fraction
    )
    m2_parameters, m2_prediction = _select_m2_parameters(
        supply, mass_flow, load_proxy, observed, validation_indices, m0_fraction
    )

    split_name = np.full(len(ordered), "test", dtype=object)
    split_name[train_indices] = "train"
    split_name[validation_indices] = "validation"
    output = ordered.loc[:, ["time_bin", "panel", "supply_temperature_c", "return_temperature_c", "mass_flow_kg_s", "mean_observed_cluster_power_kw"]].copy()
    output["split"] = split_name
    output["m0_return_temperature_c"] = m0_prediction
    output["m1_return_temperature_c"] = m1_prediction
    output["m2_return_temperature_c"] = m2_prediction

    summary: dict[str, object] = {
        "panel": str(panel_values[0]),
        "evidence_class": "conditional_local_stress_test",
        "time_step_s": TIME_STEP_S,
        "specific_heat_j_kgk": CP_J_KGK,
        "load_proxy": "facility-wide IPMI cluster power; no documented mapping to the PLC panel",
        "load_fraction_fitted_on": "earliest chronological training block only",
        "m0": {
            "load_to_circuit_fraction": m0_fraction,
            "fraction_at_physical_bound": bool(np.isclose(m0_fraction, 0.0) or np.isclose(m0_fraction, 1.0)),
        },
        "m1": {
            "thermal_capacitance_j_k": m1_capacitance,
            "parameter_at_candidate_bound": _at_candidate_bound(
                m1_capacitance, M1_CAPACITANCE_CANDIDATES_J_K
            ),
        },
        "m2": {
            **m2_parameters,
            "parameter_at_candidate_bound": any(
                (
                    _at_candidate_bound(
                        m2_parameters["load_thermal_capacitance_j_k"],
                        M2_LOAD_CAPACITANCE_CANDIDATES_J_K,
                    ),
                    _at_candidate_bound(
                        m2_parameters["fluid_thermal_capacitance_j_k"],
                        M2_FLUID_CAPACITANCE_CANDIDATES_J_K,
                    ),
                    _at_candidate_bound(
                        m2_parameters["heat_exchange_conductance_w_k"],
                        M2_CONDUCTANCE_CANDIDATES_W_K,
                    ),
                )
            ),
        },
        "metrics": {
            model: {
                split: calculate_error_metrics(
                    output.loc[output["split"] == split, column].to_numpy(),
                    output.loc[output["split"] == split, "return_temperature_c"].to_numpy(),
                )
                for split in ("train", "validation", "test")
            }
            for model, column in (
                ("m0_quasisteady", "m0_return_temperature_c"),
                ("m1_lumped", "m1_return_temperature_c"),
                ("m2_two_state", "m2_return_temperature_c"),
            )
        },
        "interpretation_limit": (
            "The comparison tests computational behavior under an unassigned system-power proxy. "
            "It cannot validate any panel, RDHx, row, rack, or cold-plate model."
        ),
    }
    return output, summary


def _plot_predictions(output: pd.DataFrame, output_path: Path) -> None:
    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(11, 4.2), constrained_layout=True)
    axis.plot(output["time_bin"], output["return_temperature_c"], color="black", linewidth=1.2, label="Measured return")
    axis.plot(output["time_bin"], output["m0_return_temperature_c"], linewidth=0.8, label="M0 quasi-steady")
    axis.plot(output["time_bin"], output["m1_return_temperature_c"], linewidth=0.8, label="M1 one-state")
    axis.plot(output["time_bin"], output["m2_return_temperature_c"], linewidth=0.8, label="M2 two-state")
    axis.set_xlabel("UTC time")
    axis.set_ylabel("Return temperature (°C)")
    axis.set_title("Conditional local stress test; facility power is an unassigned proxy")
    axis.legend(ncol=4, fontsize=8)
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plc-signals", type=Path, required=True)
    parser.add_argument("--cluster-power", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--panel", choices=("Q101", "Q102"), required=True)
    parser.add_argument("--minimum-node-count", type=float, default=961.0)
    arguments = parser.parse_args()

    frame = build_panel_comparison_frame(
        pd.read_csv(arguments.plc_signals),
        pd.read_csv(arguments.cluster_power),
        panel=arguments.panel,
        minimum_node_count=arguments.minimum_node_count,
    )
    output, summary = run_three_model_comparison(frame)
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    output.to_csv(arguments.output_dir / f"{arguments.panel.lower()}_three_model_predictions.csv", index=False)
    with (arguments.output_dir / f"{arguments.panel.lower()}_three_model_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    _plot_predictions(output, arguments.output_dir / f"{arguments.panel.lower()}_three_model_predictions.png")


if __name__ == "__main__":
    main()
