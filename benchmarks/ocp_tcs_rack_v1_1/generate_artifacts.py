"""Generate traceable synthetic v1.1 multi-model comparison artifacts.

The artifacts compare declared model structures under NED3-authored synthetic
scenarios.  They do not read, reproduce, or infer results from third-party
data, and they must not be interpreted as empirical rack validation.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from benchmarks.ocp_tcs_rack_v1_0.model_suite import evaluate_quasi_steady_case, simulate_two_node_case

from .model_suite import evaluate_multibranch_steady_case


DEFAULT_SUITE_PATH = Path(__file__).with_name("suite.json")
DEFAULT_OUTPUT_DIRECTORY = Path(__file__).with_name("results")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_suite() -> dict:
    suite = json.loads(DEFAULT_SUITE_PATH.read_text(encoding="utf-8"))
    if suite.get("evidence_class") != "synthetic_derived":
        raise ValueError("v1.1 suite must declare synthetic_derived evidence")
    if suite.get("validation_state") != "not_validated":
        raise ValueError("v1.1 suite must declare not_validated state")
    return suite


def _balanced_branches(suite: dict) -> list[dict]:
    """Build the M3 limiting case that must reduce to the whole-rack balance."""
    prototype = copy.deepcopy(suite["branches"][0])
    result: list[dict] = []
    for index in range(1, 5):
        branch = copy.deepcopy(prototype)
        branch.update(
            {
                "branch_id": f"B{index}",
                "it_heat_fraction": 0.25,
                "hydraulic_resistance_pa_s2_kg2": 1.0e6,
                "ua_w_k": 1000.0,
                "hardware_heat_capacity_j_k": 5.0e4,
                "coolant_heat_capacity_j_k": 5.0e3,
            }
        )
        result.append(branch)
    return result


def _scenario_branches(suite: dict) -> dict[str, list[dict]]:
    """Return mechanism-focused cases, rather than an exhaustive parameter grid."""
    balanced = _balanced_branches(suite)
    hydraulic_imbalance = copy.deepcopy(balanced)
    hydraulic_imbalance[-1]["hydraulic_resistance_pa_s2_kg2"] = 4.0e6
    coupled_stress = copy.deepcopy(suite["branches"])
    coupled_stress[0]["it_heat_fraction"] = 0.55
    coupled_stress[1]["it_heat_fraction"] = 0.20
    coupled_stress[2]["it_heat_fraction"] = 0.15
    coupled_stress[3]["it_heat_fraction"] = 0.10
    coupled_stress[0]["hydraulic_resistance_pa_s2_kg2"] *= 3.0
    return {
        "balanced_reference": balanced,
        "nominal_nonuniform": copy.deepcopy(suite["branches"]),
        "hydraulic_imbalance": hydraulic_imbalance,
        "coupled_load_hydraulic_stress": coupled_stress,
    }


def _aggregate_capture_fraction(branches: list[dict]) -> float:
    return sum(branch["it_heat_fraction"] * branch["liquid_capture_fraction"] for branch in branches)


def _model_comparison_rows(suite: dict) -> list[dict]:
    baseline = suite["baseline"]
    fluid = suite["fluid"]
    rows: list[dict] = []
    for scenario_id, branches in _scenario_branches(suite).items():
        capture_fraction = _aggregate_capture_fraction(branches)
        m1 = evaluate_quasi_steady_case(
            it_heat_w=baseline["it_heat_w"],
            liquid_capture_fraction=capture_fraction,
            supply_temperature_c=baseline["supply_temperature_c"],
            mass_flow_kg_s=baseline["mass_flow_kg_s"],
            specific_heat_j_kg_k=fluid["specific_heat_j_kg_k"],
        )
        m2_rows = simulate_two_node_case(
            supply_temperature_c=baseline["supply_temperature_c"],
            mass_flow_kg_s=baseline["mass_flow_kg_s"],
            specific_heat_j_kg_k=fluid["specific_heat_j_kg_k"],
            liquid_heat_w=m1["liquid_heat_w"],
            heat_capacity_hardware_j_k=sum(branch["hardware_heat_capacity_j_k"] for branch in branches),
            heat_capacity_coolant_j_k=sum(branch["coolant_heat_capacity_j_k"] for branch in branches),
            ua_w_k=sum(branch["ua_w_k"] for branch in branches),
            duration_s=1800.0,
            time_step_s=0.5,
        )
        m2 = m2_rows[-1]
        m3 = evaluate_multibranch_steady_case(
            it_heat_w=baseline["it_heat_w"],
            supply_temperature_c=baseline["supply_temperature_c"],
            mass_flow_kg_s=baseline["mass_flow_kg_s"],
            specific_heat_j_kg_k=fluid["specific_heat_j_kg_k"],
            density_kg_m3=fluid["density_kg_m3"],
            pump_efficiency=baseline["pump_efficiency"],
            branches=branches,
        )
        branch_flows = [branch["mass_flow_kg_s"] for branch in m3["branches"]]
        branch_hardware_temperatures = [branch["effective_hardware_temperature_c"] for branch in m3["branches"]]
        rows.append(
            {
                "scenario_id": scenario_id,
                "m1_mixed_return_temperature_c": m1["return_temperature_c"],
                "m2_mixed_return_temperature_c": m2["return_temperature_c"],
                "m2_effective_hardware_temperature_c": m2["hardware_temperature_c"],
                "m3_mixed_return_temperature_c": m3["mixed_return_temperature_c"],
                "m3_peak_effective_hardware_temperature_c": max(branch_hardware_temperatures),
                "m3_min_branch_flow_kg_s": min(branch_flows),
                "m3_max_branch_flow_kg_s": max(branch_flows),
                "m3_pressure_drop_pa": m3["pressure_drop_pa"],
                "m3_pump_power_w": m3["pump_power_w"],
                "m3_energy_residual_w": m3["energy_residual_w"],
                "m3_mass_flow_residual_kg_s": m3["mass_flow_residual_kg_s"],
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _comparison_figure(path: Path, rows: list[dict]) -> None:
    plt.rcParams.update({"font.family": "Arial", "font.size": 9, "svg.fonttype": "none"})
    labels = [row["scenario_id"].replace("_", "\n") for row in rows]
    index = list(range(len(rows)))
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.25), layout="constrained")
    colors = {"M1": "#007C91", "M2": "#D95F02", "M3": "#6A3D9A"}

    reference = [row["m1_mixed_return_temperature_c"] for row in rows]
    axes[0].plot(index, [0.0 for _ in rows], "o-", color=colors["M1"], label="M1 whole-rack")
    axes[0].plot(index, [(row["m2_mixed_return_temperature_c"] - ref) * 1000.0 for row, ref in zip(rows, reference)], "s--", color=colors["M2"], label="M2 mixed-node")
    axes[0].plot(index, [(row["m3_mixed_return_temperature_c"] - ref) * 1000.0 for row, ref in zip(rows, reference)], "^:", color=colors["M3"], linewidth=2.2, label="M3 multi-branch")
    axes[0].set(ylabel="Mixed-return difference from M1 [mK]", xticks=index, xticklabels=labels)
    axes[0].grid(axis="y", color="#D9E2EC")
    axes[0].legend(frameon=False, fontsize=7)

    axes[1].plot(index, [row["m2_effective_hardware_temperature_c"] for row in rows], "s--", color=colors["M2"], label="M2 effective hardware")
    axes[1].plot(index, [row["m3_peak_effective_hardware_temperature_c"] for row in rows], "^:", color=colors["M3"], linewidth=2.2, label="M3 branch peak")
    axes[1].set(ylabel="Effective hardware temperature [°C]", xticks=index, xticklabels=labels)
    axes[1].grid(axis="y", color="#D9E2EC")
    axes[1].legend(frameon=False, fontsize=7)

    minimum = [row["m3_min_branch_flow_kg_s"] for row in rows]
    maximum = [row["m3_max_branch_flow_kg_s"] for row in rows]
    axes[2].vlines(index, minimum, maximum, color=colors["M3"], linewidth=4, label="M3 branch-flow range")
    axes[2].plot(index, minimum, "v", color=colors["M3"])
    axes[2].plot(index, maximum, "^", color=colors["M3"])
    axes[2].set(ylabel="Branch mass flow [kg/s]", xticks=index, xticklabels=labels)
    axes[2].grid(axis="y", color="#D9E2EC")
    axes[2].legend(frameon=False, fontsize=7)

    for axis, label in zip(axes, ("(a)", "(b)", "(c)")):
        axis.text(-0.15, 1.05, label, transform=axis.transAxes, fontweight="bold")
    fig.suptitle("Synthetic model-structure comparison under common rack-manifold boundary conditions", fontweight="bold")
    fig.text(
        0.5,
        -0.03,
        "All curves are NED3-authored synthetic derivatives. Agreement in mixed return temperature does not validate branch-level predictions.",
        ha="center",
        fontsize=8,
        color="#475569",
    )
    fig.savefig(path, format="svg", bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=240, bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)
    # Matplotlib's SVG backend retains alignment whitespace in path rows. Strip
    # it so the committed vector artifact passes repository whitespace checks.
    path.write_text(
        "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )


def generate_artifacts(output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY) -> dict[str, Path]:
    """Write deterministic synthetic results, a comparison figure, and a run summary."""
    destination = Path(output_directory)
    destination.mkdir(parents=True, exist_ok=True)
    suite = _load_suite()
    comparison_rows = _model_comparison_rows(suite)
    comparison_csv = destination / "synthetic_three_model_comparison.csv"
    comparison_svg = destination / "synthetic_three_model_comparison.svg"
    comparison_png = destination / "synthetic_three_model_comparison.png"
    comparison_pdf = destination / "synthetic_three_model_comparison.pdf"
    summary_json = destination / "synthetic_v1_1_run.json"
    _write_csv(comparison_csv, comparison_rows)
    _comparison_figure(comparison_svg, comparison_rows)
    summary = {
        "suite_id": suite["suite_id"],
        "suite_sha256": _sha256(DEFAULT_SUITE_PATH),
        "evidence_class": suite["evidence_class"],
        "validation_state": suite["validation_state"],
        "model_levels": {
            "M1": "quasi_steady_whole_rack_energy_balance",
            "M2": "two_node_mixed_thermal_network",
            "M3": "multi_branch_thermal_hydraulic_network",
        },
        "scenario_count": len(comparison_rows),
        "maximum_absolute_m3_energy_residual_w": max(abs(row["m3_energy_residual_w"]) for row in comparison_rows),
        "maximum_absolute_m3_mass_flow_residual_kg_s": max(abs(row["m3_mass_flow_residual_kg_s"]) for row in comparison_rows),
        "use_limit": suite["use_limit"],
    }
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "comparison_csv": comparison_csv,
        "comparison_svg": comparison_svg,
        "comparison_png": comparison_png,
        "comparison_pdf": comparison_pdf,
        "summary_json": summary_json,
    }


if __name__ == "__main__":
    for name, path in generate_artifacts().items():
        print(f"{name}: {path}")
