"""Publication figures for the synthetic M1/M2/M3 benchmark (ITherm 2027).

Every figure is drawn at its printed IEEE size and reads only the declared
synthetic suites.  Each figure is written with the CSV of the plotted values,
and the scalar values quoted in the manuscript are collected in
``itherm_figure_metrics.json`` so that the text can be checked against the
code.  The curves are synthetic, NED3-authored derivatives; none is a
measurement of physical equipment.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from benchmarks.ocp_tcs_rack_v1_0.generate_artifacts import _simulate_transient
from benchmarks.ocp_tcs_rack_v1_0.model_suite import (
    load_suite as load_v1_0_suite,
    simulate_two_node_case,
    two_node_exact_state,
    two_node_rise_time,
    two_node_steady_state,
)
from benchmarks.publication_style import (
    DOUBLE_COLUMN_IN,
    ENTITY_STYLE,
    REFERENCE_GRAY,
    SINGLE_COLUMN_IN,
    panel_label,
    save_figure,
    use_style,
)


DEFAULT_OUTPUT_DIRECTORY = Path(__file__).with_name("results") / "itherm"
EVENT_TIMES_S = (300.0, 720.0, 960.0)
SENSITIVITY_FACTORS = (0.5, 2.0)
CONVERGENCE_STEPS_S = (0.25, 0.5, 1.0, 2.0, 4.0)
CONVERGENCE_TIME_S = 200.0
SHORT_CASE_NAMES = {"C1": "Balanced", "C2": "Nonuniform", "C3": "Hydraulic", "C4": "Coupled"}


def _write_rows(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def _two_node_parameters(suite: dict) -> dict[str, float]:
    baseline = suite["baseline"]
    parameters = suite["reduced_order_parameters"]
    return {
        "supply_temperature_c": baseline["supply_temperature_c"],
        "mass_flow_kg_s": baseline["mass_flow_kg_s"],
        "specific_heat_j_kg_k": suite["fluid"]["specific_heat_j_kg_k"],
        "liquid_heat_w": baseline["it_heat_w"] * baseline["liquid_capture_fraction"],
        "heat_capacity_hardware_j_k": parameters["heat_capacity_hardware_j_k"],
        "heat_capacity_coolant_j_k": parameters["heat_capacity_coolant_j_k"],
        "ua_w_k": parameters["ua_w_k"],
    }


# --------------------------------------------------------------------------
# Inputs and response (single column)
# --------------------------------------------------------------------------
def inputs_response_figure(stem: Path, suite: dict) -> tuple[dict[str, Path], list[dict]]:
    """Declared forcing functions and the resulting M1 and M2 responses."""
    use_style()
    rows = _simulate_transient(suite)
    time = [row["time_s"] for row in rows]
    fig = plt.figure(figsize=(SINGLE_COLUMN_IN, 3.9))
    grid = fig.add_gridspec(4, 1, height_ratios=(0.72, 0.72, 0.72, 2.1))
    axes = [fig.add_subplot(grid[0])]
    axes += [fig.add_subplot(grid[index], sharex=axes[0]) for index in (1, 2, 3)]

    inputs = (
        ("it_heat_w", 1.0e-3, "$Q_{IT}$\n(kW)", (0.0, 12.0)),
        ("supply_temperature_c", 1.0, "$T_s$\n(°C)", (29.0, 35.0)),
        ("mass_flow_kg_s", 1.0, "$\\dot m$\n(kg s$^{-1}$)", (0.3, 0.55)),
    )
    for axis, (key, scale, label, limits) in zip(axes, inputs):
        axis.step(time, [row[key] * scale for row in rows], where="post", color=REFERENCE_GRAY, linewidth=1.2)
        axis.set_ylabel(label)
        axis.set_ylim(*limits)
        axis.yaxis.set_major_locator(plt.MaxNLocator(2))
        axis.tick_params(labelbottom=False)

    response = axes[3]
    response.plot(time, [row["m1_return_temperature_c"] for row in rows], color=ENTITY_STYLE["M1"]["color"], linestyle="-", label=r"M1 return, $T_r$")
    response.plot(time, [row["m2_return_temperature_c"] for row in rows], color=ENTITY_STYLE["M2"]["color"], linestyle="--", label=r"M2 return, $T_r$")
    response.plot(time, [row["m2_hardware_temperature_c"] for row in rows], color=ENTITY_STYLE["M2"]["color"], linestyle="-", label=r"M2 hardware, $T_h$")
    response.set_ylabel(r"Temperature (°C)")
    response.set_xlabel("Time, $t$ (s)")
    response.set_xlim(0.0, 1200.0)
    response.legend(loc="lower right")

    for axis in axes:
        for event in EVENT_TIMES_S:
            axis.axvline(event, color="0.6", linestyle=(0, (3, 2)), linewidth=0.6, zorder=0)
    for axis, letter in zip(axes, "abcd"):
        axis.text(0.015, 0.93, f"({letter})", transform=axis.transAxes, fontweight="bold", va="top", ha="left")
    fig.align_ylabels(axes)
    data = [
        {
            "time_s": row["time_s"],
            "it_heat_w": row["it_heat_w"],
            "supply_temperature_c": row["supply_temperature_c"],
            "mass_flow_kg_s": row["mass_flow_kg_s"],
            "m1_return_temperature_c": row["m1_return_temperature_c"],
            "m2_return_temperature_c": row["m2_return_temperature_c"],
            "m2_hardware_temperature_c": row["m2_hardware_temperature_c"],
        }
        for row in rows
    ]
    return save_figure(fig, stem), data


# --------------------------------------------------------------------------
# Model-structure comparison (single column)
# --------------------------------------------------------------------------
def model_structure_figure(stem: Path, suite: dict, comparison: list[dict], branches: list[dict]) -> dict[str, Path]:
    """Mixed return and hidden hardware/branch states for M1-M3 at C1-C4."""
    use_style()
    codes = [row["case_code"] for row in comparison]
    positions = range(len(codes))
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(SINGLE_COLUMN_IN, 3.45), sharex=True, height_ratios=(1.25, 1.0))
    offsets = {"M1": -0.2, "M2": 0.0, "M3": 0.2}
    marker_size = 4.5
    for index, row in zip(positions, comparison):
        returns = {
            "M1": row["m1_mixed_return_temperature_c"],
            "M2": row["m2_mixed_return_temperature_c"],
            "M3": row["m3_mixed_return_temperature_c"],
        }
        for model, value in returns.items():
            style = ENTITY_STYLE[model]
            top.plot(index + offsets[model], value, linestyle="none", marker=style["marker"], markersize=marker_size, markerfacecolor="white", markeredgecolor=style["color"])
        for model, value in (("M2", row["m2_effective_hardware_temperature_c"]), ("M3", row["m3_peak_effective_hardware_temperature_c"])):
            style = ENTITY_STYLE[model]
            top.plot(index + offsets[model], value, linestyle="none", marker=style["marker"], markersize=marker_size, color=style["color"])
    top.set_ylabel(r"Temperature (°C)")
    top.set_ylim(32.5, 46.5)
    # Both marker-fill meanings sit together above the legend.
    top.text(-0.45, 45.35, r"Filled: hardware $T_h$", ha="left", va="center", fontsize=7)
    top.text(-0.45, 44.1, r"Open: mixed return $T_r$", ha="left", va="center", fontsize=7)
    handles = [
        Line2D([], [], linestyle="none", marker=ENTITY_STYLE["M1"]["marker"], color=ENTITY_STYLE["M1"]["color"], label="M1 whole rack"),
        Line2D([], [], linestyle="none", marker=ENTITY_STYLE["M2"]["marker"], color=ENTITY_STYLE["M2"]["color"], label="M2 lumped node"),
        Line2D([], [], linestyle="none", marker=ENTITY_STYLE["M3"]["marker"], color=ENTITY_STYLE["M3"]["color"], label=r"M3 hottest branch"),
    ]
    top.legend(handles=handles, loc="center left", bbox_to_anchor=(0.0, 0.6))

    nominal = suite["baseline"]["mass_flow_kg_s"] / 4.0
    bottom.axhline(nominal, color="0.55", linestyle=(0, (3, 2)), linewidth=0.7, zorder=0)
    bottom.text(-0.45, nominal + 0.003, r"$\dot m_{rack}/4$", fontsize=7, color="0.35", va="bottom")
    branch_offsets = (-0.24, -0.08, 0.08, 0.24)
    hottest = {row["case_code"]: row["m3_hottest_branch_id"] for row in comparison}
    for index, code in zip(positions, codes):
        rows = [row for row in branches if row["case_code"] == code]
        for offset, row in zip(branch_offsets, rows):
            filled = row["branch_id"] == hottest[code]
            bottom.plot(
                index + offset,
                row["mass_flow_kg_s"],
                linestyle="none",
                marker=ENTITY_STYLE["M3"]["marker"],
                markersize=marker_size,
                markeredgecolor=ENTITY_STYLE["M3"]["color"],
                markerfacecolor=ENTITY_STYLE["M3"]["color"] if filled else "white",
            )
    bottom.set_ylabel(r"Branch flow, $\dot m_i$ (kg s$^{-1}$)")
    bottom.set_ylim(0.06, 0.19)
    bottom.set_xticks(list(positions), [f"{code}\n{SHORT_CASE_NAMES.get(code, '')}" for code in codes])
    bottom.set_xlim(-0.55, len(codes) - 0.45)
    bottom.tick_params(axis="x", which="minor", bottom=False, top=False)
    top.tick_params(axis="x", which="minor", bottom=False, top=False)
    bottom.legend(
        handles=[
            Line2D([], [], linestyle="none", marker="^", markeredgecolor=ENTITY_STYLE["M3"]["color"], markerfacecolor="white", label="Branches B1–B4"),
            Line2D([], [], linestyle="none", marker="^", color=ENTITY_STYLE["M3"]["color"], label="Hottest branch"),
        ],
        loc="upper center",
        ncols=2,
    )
    panel_label(top, "a", x=-0.19)
    panel_label(bottom, "b", x=-0.19)
    fig.align_ylabels((top, bottom))
    return save_figure(fig, stem)


# --------------------------------------------------------------------------
# Sensitivity (single column)
# --------------------------------------------------------------------------
def sensitivity_rows(suite: dict) -> list[dict]:
    """Exact equilibrium hardware temperature and 98 % rise time per factor."""
    base = _two_node_parameters(suite)
    keys = (("ua_w_k", "UA"), ("heat_capacity_hardware_j_k", "C_h"), ("heat_capacity_coolant_j_k", "C_f"))
    rows = []
    for key, symbol in keys:
        for factor in (SENSITIVITY_FACTORS[0], 1.0, SENSITIVITY_FACTORS[1]):
            parameters = dict(base)
            parameters[key] *= factor
            steady = two_node_steady_state(
                supply_temperature_c=parameters["supply_temperature_c"],
                mass_flow_kg_s=parameters["mass_flow_kg_s"],
                specific_heat_j_kg_k=parameters["specific_heat_j_kg_k"],
                liquid_heat_w=parameters["liquid_heat_w"],
                ua_w_k=parameters["ua_w_k"],
            )
            rows.append(
                {
                    "parameter": symbol,
                    "multiplier": factor,
                    "steady_hardware_temperature_c": steady["hardware_temperature_c"],
                    "rise_time_98_s": two_node_rise_time(fraction=0.98, **parameters),
                }
            )
    return rows


def sensitivity_figure(stem: Path, rows: list[dict]) -> dict[str, Path]:
    use_style()
    fig, (left, right) = plt.subplots(1, 2, figsize=(SINGLE_COLUMN_IN, 1.75), sharey=True)
    parameters = ("UA", "C_h", "C_f")
    labels = {"UA": "$UA$", "C_h": "$C_h$", "C_f": "$C_f$"}
    color = ENTITY_STYLE["M2"]["color"]
    lookup = {(row["parameter"], row["multiplier"]): row for row in rows}
    baseline = lookup[("UA", 1.0)]
    for position, parameter in enumerate(parameters):
        y = len(parameters) - 1 - position
        for axis, key, reference in (
            (left, "steady_hardware_temperature_c", baseline["steady_hardware_temperature_c"]),
            (right, "rise_time_98_s", baseline["rise_time_98_s"]),
        ):
            low = lookup[(parameter, SENSITIVITY_FACTORS[0])][key] - (reference if axis is left else 0.0)
            high = lookup[(parameter, SENSITIVITY_FACTORS[1])][key] - (reference if axis is left else 0.0)
            axis.plot([low, high], [y, y], color=color, linewidth=3.0, solid_capstyle="butt", alpha=0.45)
            axis.plot(low, y, linestyle="none", marker="o", markerfacecolor="white", markeredgecolor=color)
            axis.plot(high, y, linestyle="none", marker="o", color=color)
    left.axvline(0.0, color=REFERENCE_GRAY, linewidth=0.7)
    right.axvline(baseline["rise_time_98_s"], color=REFERENCE_GRAY, linewidth=0.7)
    left.set_yticks(range(len(parameters)), [labels[name] for name in reversed(parameters)])
    left.set_ylim(-0.6, len(parameters) - 0.4)
    left.set_xlabel(r"$\Delta T_{h,\infty}$ (K)")
    right.set_xlabel(r"$t_{98}$ (s)")
    left.set_xlim(-1.4, 2.4)
    right.set_xlim(250.0, 1250.0)
    for axis in (left, right):
        axis.tick_params(axis="y", which="minor", left=False, right=False)
    right.legend(
        handles=[
            Line2D([], [], linestyle="none", marker="o", markerfacecolor="white", markeredgecolor=color, label=r"0.5$\times$"),
            Line2D([], [], linestyle="none", marker="o", color=color, label=r"2$\times$"),
        ],
        loc="lower right",
    )
    panel_label(left, "a", x=-0.3)
    panel_label(right, "b", x=-0.08)
    return save_figure(fig, stem)


# --------------------------------------------------------------------------
# Time-step convergence (single column)
# --------------------------------------------------------------------------
def convergence_rows(suite: dict) -> tuple[list[dict], dict]:
    parameters = _two_node_parameters(suite)
    exact = two_node_exact_state(time_s=CONVERGENCE_TIME_S, **parameters)
    rows = []
    for step in CONVERGENCE_STEPS_S:
        trajectory = simulate_two_node_case(duration_s=2.0 * CONVERGENCE_TIME_S, time_step_s=step, **parameters)
        state = trajectory[round(CONVERGENCE_TIME_S / step)]
        rows.append(
            {
                "time_step_s": step,
                "hardware_error_k": abs(state["hardware_temperature_c"] - exact["hardware_temperature_c"]),
                "return_error_k": abs(state["return_temperature_c"] - exact["return_temperature_c"]),
                "max_abs_residual_w": max(abs(row["energy_residual_w"]) for row in trajectory),
            }
        )
    log_steps = [math.log(row["time_step_s"]) for row in rows]
    log_errors = [math.log(row["hardware_error_k"]) for row in rows]
    mean_x = sum(log_steps) / len(log_steps)
    mean_y = sum(log_errors) / len(log_errors)
    order = sum((x - mean_x) * (y - mean_y) for x, y in zip(log_steps, log_errors)) / sum((x - mean_x) ** 2 for x in log_steps)
    summary = {
        "observed_order_hardware": order,
        "exact_hardware_temperature_200s_c": exact["hardware_temperature_c"],
        "slow_time_constant_s": exact["slow_time_constant_s"],
        "fast_time_constant_s": exact["fast_time_constant_s"],
        "forward_euler_stability_limit_s": 2.0 * exact["fast_time_constant_s"],
    }
    return rows, summary


def convergence_figure(stem: Path, rows: list[dict], summary: dict) -> dict[str, Path]:
    use_style()
    fig, axis = plt.subplots(figsize=(SINGLE_COLUMN_IN, 2.35))
    color = ENTITY_STYLE["M2"]["color"]
    steps = [row["time_step_s"] for row in rows]
    axis.loglog(steps, [row["hardware_error_k"] for row in rows], marker="s", color=color, linestyle="-", label=r"Hardware node, $T_h$")
    axis.loglog(steps, [row["return_error_k"] for row in rows], marker="s", color=color, markerfacecolor="white", linestyle="--", label=r"Return node, $T_r$")
    # First-order guide triangle below the data.
    x0, x1 = 0.5, 2.0
    y0 = rows[1]["return_error_k"] * 0.35
    axis.plot([x0, x1, x1, x0], [y0, y0, y0 * x1 / x0, y0], color=REFERENCE_GRAY, linewidth=0.7)
    axis.text(x1 * 1.08, y0 * math.sqrt(x1 / x0), "1", fontsize=7, va="center", color=REFERENCE_GRAY)
    axis.text(math.sqrt(x0 * x1), y0 * 0.72, "1", fontsize=7, ha="center", va="top", color=REFERENCE_GRAY)
    limit = summary["forward_euler_stability_limit_s"]
    axis.axvline(limit, color="0.55", linestyle=":", linewidth=0.9)
    axis.text(limit * 0.92, 2.0e-4, "Explicit\nstability\nlimit", fontsize=7, ha="right", va="bottom", color="0.35")
    axis.set_xlim(0.18, 9.0)
    axis.set_ylim(1.0e-4, 6.0e-2)
    axis.set_xlabel(r"Forward-Euler time step, $\Delta t$ (s)")
    axis.set_ylabel(r"$|T(200\ \mathrm{s}) - T_{exact}|$ (K)")
    axis.set_xticks(steps, [f"{step:g}" for step in steps])
    axis.tick_params(axis="x", which="minor", bottom=False, top=False)
    axis.text(0.04, 0.05, f"Observed order {summary['observed_order_hardware']:.2f}", transform=axis.transAxes, fontsize=7, va="bottom")
    axis.legend(loc="upper left")
    return save_figure(fig, stem)


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def generate_paper_figures(output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY) -> dict[str, Path]:
    """Write the synthetic ITherm figures, their data, and the quoted metrics."""
    from .generate_artifacts import evaluate_scenarios, load_suite as load_v1_1_suite

    destination = Path(output_directory)
    destination.mkdir(parents=True, exist_ok=True)
    v1_0 = load_v1_0_suite()
    v1_1 = load_v1_1_suite()
    outputs: dict[str, Path] = {}

    figure, data = inputs_response_figure(destination / "fig_inputs_response", v1_0)
    outputs["inputs_response_pdf"] = figure["pdf"]
    outputs["inputs_response_csv"] = _write_rows(destination / "fig_inputs_response.csv", data)

    comparison, branches = evaluate_scenarios(v1_1)
    figure = model_structure_figure(destination / "fig_model_structure", v1_1, comparison, branches)
    outputs["model_structure_pdf"] = figure["pdf"]
    outputs["model_structure_csv"] = _write_rows(destination / "fig_model_structure_branches.csv", branches)

    sensitivity = sensitivity_rows(v1_0)
    outputs["sensitivity_pdf"] = sensitivity_figure(destination / "fig_sensitivity", sensitivity)["pdf"]
    outputs["sensitivity_csv"] = _write_rows(destination / "fig_sensitivity.csv", sensitivity)

    convergence, convergence_summary = convergence_rows(v1_0)
    outputs["convergence_pdf"] = convergence_figure(destination / "fig_convergence", convergence, convergence_summary)["pdf"]
    outputs["convergence_csv"] = _write_rows(destination / "fig_convergence.csv", convergence)

    transient = _simulate_transient(v1_0)
    liquid_heat_max = max(row["it_heat_w"] for row in transient) * v1_0["baseline"]["liquid_capture_fraction"]
    max_residual = max(abs(row["m2_energy_residual_w"]) for row in transient)
    lookup = {(row["parameter"], row["multiplier"]): row for row in sensitivity}
    metrics = {
        "evidence_class": "synthetic_derived",
        "m2_transient_max_abs_residual_w": max_residual,
        "m2_transient_max_abs_residual_relative_to_liquid_heat": max_residual / liquid_heat_max,
        "convergence": convergence_summary,
        "sensitivity": {
            "baseline_steady_hardware_temperature_c": lookup[("UA", 1.0)]["steady_hardware_temperature_c"],
            "baseline_rise_time_98_s": lookup[("UA", 1.0)]["rise_time_98_s"],
            "rows": sensitivity,
        },
        "model_structure": comparison,
    }
    metrics_path = destination / "itherm_figure_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    outputs["metrics_json"] = metrics_path
    return outputs


if __name__ == "__main__":
    for name, path in generate_paper_figures().items():
        print(f"{name}: {path}")
