"""Generate publication-facing SVG figures for the synthetic v1.0 suite.

All numerical curves in this module are derived from the NED3-authored,
synthetic suite.  The dataset-readiness matrix is a metadata audit based on
the cited companion papers, not a reuse or reanalysis of third-party records.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from .generate_artifacts import _scenario_input, _simulate_transient, _steady_sweep
from .model_suite import load_suite, simulate_two_node_case


DEFAULT_OUTPUT_DIRECTORY = Path(__file__).with_name("results")
COLORS = {"input": "#1f77b4", "liquid": "#d95f02", "hardware": "#6a3d9a", "air": "#6b7280", "grid": "#d9e2ec"}


def _style():
    plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 10, "legend.fontsize": 8, "svg.fonttype": "none"})


def _save(fig, path: Path) -> Path:
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return path


def _label(ax, label: str) -> None:
    ax.text(-0.12, 1.06, label, transform=ax.transAxes, fontweight="bold", va="bottom")


def _control_volume(path: Path, suite: dict) -> Path:
    _style()
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    ax.set_axis_off()
    rack = FancyBboxPatch((0.33, 0.18), 0.34, 0.62, boxstyle="round,pad=0.02", linewidth=1.5, edgecolor="#243b53", facecolor="#f8fafc")
    ax.add_patch(rack)
    ax.text(0.50, 0.74, "Declared rack TCS control volume", ha="center", va="center", weight="bold", color="#102a43")
    ax.text(0.50, 0.51, r"$Q_{IT}$", ha="center", va="center", fontsize=13)
    ax.text(0.50, 0.40, r"$Q_\ell=f_\ell Q_{IT}$     $Q_a=(1-f_\ell)Q_{IT}$", ha="center", va="center")
    ax.text(0.50, 0.28, "M1: no storage; M2: effective hardware and coolant storage", ha="center", va="center", fontsize=8)
    arrows = [
        ((0.06, 0.57), (0.32, 0.57), COLORS["input"], "TCS supply\n$T_s$, $\\dot m$, $c_p$"),
        ((0.68, 0.57), (0.94, 0.57), COLORS["liquid"], "TCS return\n$T_r$"),
        ((0.50, 0.98), (0.50, 0.81), "#111827", "IT heat input\n$Q_{IT}$"),
        ((0.50, 0.17), (0.50, 0.02), COLORS["air"], "Residual-air path\n$Q_a$"),
    ]
    for start, end, color, text in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, linewidth=2, color=color))
        x, y = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        if start[0] == end[0]: x += 0.07
        else: y += 0.10
        ax.text(x, y, text, ha="center", va="center", color=color, fontsize=8)
    ax.text(0.50, -0.15, "Synthetic v1.0 boundary. CDU, facility heat rejection, air recirculation, pump power, and branch maldistribution are excluded.", ha="center", fontsize=8, color="#4b5563")
    return _save(fig, path)


def _input_schedule(path: Path, suite: dict) -> Path:
    _style(); rows = _simulate_transient(suite)
    keys = [("it_heat_w", "IT heat [kW]", 1e-3), ("supply_temperature_c", "Supply temperature [°C]", 1.0), ("mass_flow_kg_s", "Mass flow [kg/s]", 1.0)]
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 5.4), sharex=True, layout="constrained")
    for i, (key, ylabel, scale) in enumerate(keys):
        ax = axes[i]; ax.step([r["time_s"] for r in rows], [r[key] * scale for r in rows], where="post", color=COLORS["input"], linewidth=2)
        for event in (300, 720, 960): ax.axvline(event, color="#94a3b8", linestyle="--", linewidth=0.9)
        ax.set_ylabel(ylabel); ax.grid(axis="y", color=COLORS["grid"]); _label(ax, f"({chr(97+i)})")
    axes[-1].set_xlabel("Time [s]")
    fig.suptitle("Declared synthetic forcing functions applied identically to each implemented model", fontweight="bold")
    return _save(fig, path)


def _steady_reference(path: Path, suite: dict) -> Path:
    _style(); rows = _steady_sweep(suite); baseline = suite["baseline"]
    flow = [r["mass_flow_kg_s"] for r in rows]; rise = [r["temperature_rise_k"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), layout="constrained")
    axes[0].plot(flow, rise, "o-", color=COLORS["liquid"], linewidth=2); axes[0].set(xlabel="Mass flow [kg/s]", ylabel="M1 return temperature rise [K]")
    axes[0].grid(color=COLORS["grid"]); _label(axes[0], "(a)")
    labels = ["Liquid path", "Residual-air path"]; values = [baseline["liquid_capture_fraction"] * baseline["it_heat_w"] / 1000, baseline["residual_air_heat_fraction"] * baseline["it_heat_w"] / 1000]
    bars = axes[1].bar(labels, values, color=[COLORS["liquid"], COLORS["air"]]); axes[1].set(ylabel="Heat partition [kW]", ylim=(0, 9)); axes[1].grid(axis="y", color=COLORS["grid"]); _label(axes[1], "(b)")
    for bar, value in zip(bars, values): axes[1].text(bar.get_x()+bar.get_width()/2, value+.2, f"{value:.1f}", ha="center")
    fig.suptitle("Analytical M1 reference for the declared 10 kW, 80% liquid-capture case", fontweight="bold")
    return _save(fig, path)


def _sensitivity(path: Path, suite: dict) -> Path:
    _style(); p = suite["reduced_order_parameters"]; b = suite["baseline"]; cp = suite["fluid"]["specific_heat_j_kg_k"]; q = b["it_heat_w"] * b["liquid_capture_fraction"]
    factors = [0.5, 1.0, 2.0]; names = [("ua_w_k", "Effective $UA$", "#d95f02"), ("heat_capacity_hardware_j_k", "Hardware capacitance", "#6a3d9a"), ("heat_capacity_coolant_j_k", "Coolant capacitance", "#1f77b4")]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1), layout="constrained"); metric_rows=[]
    for key, name, color in names:
        peaks=[]; settling=[]
        for factor in factors:
            params=p.copy(); params[key] *= factor
            rows=simulate_two_node_case(supply_temperature_c=b["supply_temperature_c"], mass_flow_kg_s=b["mass_flow_kg_s"], specific_heat_j_kg_k=cp, liquid_heat_w=q, heat_capacity_hardware_j_k=params["heat_capacity_hardware_j_k"], heat_capacity_coolant_j_k=params["heat_capacity_coolant_j_k"], ua_w_k=params["ua_w_k"], duration_s=800, time_step_s=1)
            peak=max(r["hardware_temperature_c"] for r in rows); final=rows[-1]["hardware_temperature_c"]; threshold=b["supply_temperature_c"]+0.98*(final-b["supply_temperature_c"])
            tnext=next(r["time_s"] for r in rows if r["hardware_temperature_c"] >= threshold)
            peaks.append(peak); settling.append(tnext); metric_rows.append((key,factor,peak,tnext))
        axes[0].plot(factors, peaks, "o-", label=name, color=color); axes[1].plot(factors, settling, "o-", label=name, color=color)
    for ax, ylabel, label in zip(axes, ["Peak effective hardware temperature [°C]", "98% hardware-rise time [s]"], ["(a)", "(b)"]):
        ax.set(xlabel="Parameter multiplier relative to v1.0", ylabel=ylabel, xlim=(0.4, 2.1)); ax.set_xticks(factors, ["0.5", "1", "2"]); ax.grid(color=COLORS["grid"]); _label(ax, label)
    axes[1].legend(loc="best", frameon=False)
    fig.suptitle("Synthetic parameter sensitivity identifies which measurements would constrain M2", fontweight="bold")
    return _save(fig, path)


def _verification(path: Path, suite: dict) -> Path:
    _style(); p=suite["reduced_order_parameters"]; b=suite["baseline"]; cp=suite["fluid"]["specific_heat_j_kg_k"]; q=b["it_heat_w"]*b["liquid_capture_fraction"]
    dts=[0.25,0.5,1.0,2.0,4.0]; trajectories=[]
    for dt in dts:
        rows=simulate_two_node_case(supply_temperature_c=b["supply_temperature_c"], mass_flow_kg_s=b["mass_flow_kg_s"], specific_heat_j_kg_k=cp, liquid_heat_w=q, heat_capacity_hardware_j_k=p["heat_capacity_hardware_j_k"], heat_capacity_coolant_j_k=p["heat_capacity_coolant_j_k"], ua_w_k=p["ua_w_k"], duration_s=400, time_step_s=dt)
        trajectories.append(rows)
    reference=trajectories[0]; ref_at_200=reference[int(200/dts[0])]["hardware_temperature_c"]
    errors=[abs(rows[int(200/dt)]["hardware_temperature_c"]-ref_at_200) for rows,dt in zip(trajectories,dts)]
    residuals=[max(abs(r["energy_residual_w"]) for r in rows) for rows in trajectories]
    fig, axes=plt.subplots(1,2,figsize=(7.2,3.1),layout="constrained")
    axes[0].loglog(dts, errors, "o-", color=COLORS["hardware"]); axes[0].set(xlabel="Forward-Euler step [s]", ylabel="|$T_h$(200 s) − reference| [K]"); axes[0].grid(which="both", color=COLORS["grid"]); _label(axes[0],"(a)")
    axes[1].semilogy(dts, residuals, "o-", color=COLORS["liquid"]); axes[1].set(xlabel="Forward-Euler step [s]", ylabel="Maximum algebraic balance residual [W]"); axes[1].grid(which="both", color=COLORS["grid"]); _label(axes[1],"(b)")
    fig.suptitle("Numerical checks for the constant-input M2 reference case", fontweight="bold")
    return _save(fig,path)


def _data_readiness(path: Path, suite: dict) -> Path:
    _style(); columns=["Topology", "Load\nallocation", "Liquid flow", "Supply/return\nsensors", "Coolant\nproperties", "Time\nalignment", "Uncertainty", "Validation\nstatus"]
    rows=["M100 ExaData", "OLCF Summit", "Kuzay et al. 2022"]
    values=[[0,0,0,0,0,1,0,0],[1,0,0,0,0,1,0,0],[1,1,0,0,0,1,1,0]]
    cmap=matplotlib.colors.ListedColormap(["#e5e7eb", "#fbbf24", "#2563eb"])
    fig,ax=plt.subplots(figsize=(7.2,2.8)); im=ax.imshow(values,cmap=cmap,vmin=0,vmax=2,aspect="auto")
    ax.set_xticks(range(len(columns)),columns,rotation=0); ax.set_yticks(range(len(rows)),rows)
    for i,row in enumerate(values):
        for j,value in enumerate(row): ax.text(j,i,["N", "P", "D"][value],ha="center",va="center",fontsize=10, color="#111827", fontweight="bold")
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.set_title("Published-metadata readiness for direct liquid rack-model validation\nD documented   P partial   N not documented for the rack TCS boundary",fontweight="bold",pad=14)
    return _save(fig,path)


def generate_itherm_figures(output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY) -> dict[str, Path]:
    """Generate six SVG assets that complete the planned main-figure set."""
    destination=Path(output_directory); destination.mkdir(parents=True,exist_ok=True); suite=load_suite()
    return {
        "control_volume": _control_volume(destination / "fig1_rack_control_volume.svg",suite),
        "input_schedule": _input_schedule(destination / "fig3_synthetic_input_schedule.svg",suite),
        "steady_reference": _steady_reference(destination / "fig4_m1_steady_reference.svg",suite),
        "sensitivity": _sensitivity(destination / "fig6_synthetic_sensitivity.svg",suite),
        "verification": _verification(destination / "fig7_numerical_verification.svg",suite),
        "data_readiness": _data_readiness(destination / "fig8_data_readiness.svg",suite),
    }


if __name__ == "__main__":
    for name,path in generate_itherm_figures().items(): print(f"{name}: {path}")
