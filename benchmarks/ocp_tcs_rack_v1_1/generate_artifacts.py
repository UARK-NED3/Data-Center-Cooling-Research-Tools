"""Generate traceable synthetic v1.1 multi-model comparison artifacts.

The artifacts compare declared model structures under NED3-authored synthetic
scenarios.  Every scenario, including its full branch table, is declared in
``suite.json``; this module only evaluates it.  The artifacts do not read,
reproduce, or infer results from third-party data, and they must not be
interpreted as empirical rack validation.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from benchmarks.ocp_tcs_rack_v1_0.model_suite import (
    evaluate_quasi_steady_case,
    simulate_two_node_case,
    two_node_steady_state,
)

from .model_suite import evaluate_multibranch_steady_case


DEFAULT_SUITE_PATH = Path(__file__).with_name("suite.json")
DEFAULT_OUTPUT_DIRECTORY = Path(__file__).with_name("results")

# Duration and step of the transient M2 run kept as a settling cross-check of
# the closed-form equilibrium used in the comparison.
M2_CHECK_DURATION_S = 1800.0
M2_CHECK_TIME_STEP_S = 0.5


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_suite(suite_path: str | Path = DEFAULT_SUITE_PATH) -> dict:
    """Load the v1.1 suite and check its evidence labels and scenario table."""
    suite = json.loads(Path(suite_path).read_text(encoding="utf-8"))
    if suite.get("evidence_class") != "synthetic_derived":
        raise ValueError("v1.1 suite must declare synthetic_derived evidence")
    if suite.get("validation_state") != "not_validated":
        raise ValueError("v1.1 suite must declare not_validated state")
    scenarios = suite.get("scenarios")
    if not scenarios or not all(isinstance(scenario, dict) for scenario in scenarios):
        raise ValueError("v1.1 suite must declare scenarios as objects with branch tables")
    identifiers = [scenario["scenario_id"] for scenario in scenarios]
    codes = [scenario["case_code"] for scenario in scenarios]
    if len(set(identifiers)) != len(identifiers) or len(set(codes)) != len(codes):
        raise ValueError("scenario_id and case_code values must be unique")
    return suite


def _aggregate_capture_fraction(branches: list[dict]) -> float:
    return sum(branch["it_heat_fraction"] * branch["liquid_capture_fraction"] for branch in branches)


def evaluate_scenarios(suite: dict) -> tuple[list[dict], list[dict]]:
    """Evaluate M1, M2, and M3 for every declared scenario.

    Returns one comparison row per scenario and one row per scenario branch.
    """
    baseline = suite["baseline"]
    fluid = suite["fluid"]
    comparison: list[dict] = []
    branch_rows: list[dict] = []
    for scenario in suite["scenarios"]:
        branches = scenario["branches"]
        m1 = evaluate_quasi_steady_case(
            it_heat_w=baseline["it_heat_w"],
            liquid_capture_fraction=_aggregate_capture_fraction(branches),
            supply_temperature_c=baseline["supply_temperature_c"],
            mass_flow_kg_s=baseline["mass_flow_kg_s"],
            specific_heat_j_kg_k=fluid["specific_heat_j_kg_k"],
        )
        ua_total = sum(branch["ua_w_k"] for branch in branches)
        m2 = two_node_steady_state(
            supply_temperature_c=baseline["supply_temperature_c"],
            mass_flow_kg_s=baseline["mass_flow_kg_s"],
            specific_heat_j_kg_k=fluid["specific_heat_j_kg_k"],
            liquid_heat_w=m1["liquid_heat_w"],
            ua_w_k=ua_total,
        )
        m2_transient = simulate_two_node_case(
            supply_temperature_c=baseline["supply_temperature_c"],
            mass_flow_kg_s=baseline["mass_flow_kg_s"],
            specific_heat_j_kg_k=fluid["specific_heat_j_kg_k"],
            liquid_heat_w=m1["liquid_heat_w"],
            heat_capacity_hardware_j_k=sum(branch["hardware_heat_capacity_j_k"] for branch in branches),
            heat_capacity_coolant_j_k=sum(branch["coolant_heat_capacity_j_k"] for branch in branches),
            ua_w_k=ua_total,
            duration_s=M2_CHECK_DURATION_S,
            time_step_s=M2_CHECK_TIME_STEP_S,
        )[-1]
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
        hardware = [branch["effective_hardware_temperature_c"] for branch in m3["branches"]]
        # A tie (balanced case) has no limiting branch; do not single one out.
        if max(hardware) - min(hardware) < 1.0e-9:
            hottest = "uniform"
        else:
            hottest = m3["branches"][hardware.index(max(hardware))]["branch_id"]
        comparison.append(
            {
                "scenario_id": scenario["scenario_id"],
                "case_code": scenario["case_code"],
                "m1_mixed_return_temperature_c": m1["return_temperature_c"],
                "m2_mixed_return_temperature_c": m2["return_temperature_c"],
                "m2_effective_hardware_temperature_c": m2["hardware_temperature_c"],
                "m2_return_temperature_at_1800s_c": m2_transient["return_temperature_c"],
                "m3_mixed_return_temperature_c": m3["mixed_return_temperature_c"],
                "m3_peak_effective_hardware_temperature_c": max(hardware),
                "m3_hottest_branch_id": hottest,
                "m3_min_branch_flow_kg_s": min(branch_flows),
                "m3_max_branch_flow_kg_s": max(branch_flows),
                "m3_pressure_drop_pa": m3["pressure_drop_pa"],
                "m3_pump_power_w": m3["pump_power_w"],
                "m3_energy_residual_w": m3["energy_residual_w"],
                "m3_mass_flow_residual_kg_s": m3["mass_flow_residual_kg_s"],
            }
        )
        for branch in m3["branches"]:
            branch_rows.append(
                {
                    "scenario_id": scenario["scenario_id"],
                    "case_code": scenario["case_code"],
                    "branch_id": branch["branch_id"],
                    "liquid_heat_w": branch["liquid_heat_w"],
                    "mass_flow_kg_s": branch["mass_flow_kg_s"],
                    "return_temperature_c": branch["return_temperature_c"],
                    "effective_hardware_temperature_c": branch["effective_hardware_temperature_c"],
                    "hydraulic_resistance_pa_s2_kg2": branch["hydraulic_resistance_pa_s2_kg2"],
                    "ua_w_k": branch["ua_w_k"],
                }
            )
    return comparison, branch_rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def generate_artifacts(output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY) -> dict[str, Path]:
    """Write deterministic synthetic results, the comparison figure, and a run summary."""
    from .paper_figures import model_structure_figure

    destination = Path(output_directory)
    destination.mkdir(parents=True, exist_ok=True)
    suite = load_suite()
    comparison_rows, branch_rows = evaluate_scenarios(suite)
    comparison_csv = destination / "synthetic_three_model_comparison.csv"
    branches_csv = destination / "synthetic_three_model_branches.csv"
    summary_json = destination / "synthetic_v1_1_run.json"
    _write_csv(comparison_csv, comparison_rows)
    _write_csv(branches_csv, branch_rows)
    figure_paths = model_structure_figure(destination / "synthetic_three_model_comparison", suite, comparison_rows, branch_rows)
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
        "maximum_absolute_m2_minus_m1_return_k": max(
            abs(row["m2_mixed_return_temperature_c"] - row["m1_mixed_return_temperature_c"]) for row in comparison_rows
        ),
        "maximum_absolute_m3_minus_m1_return_k": max(
            abs(row["m3_mixed_return_temperature_c"] - row["m1_mixed_return_temperature_c"]) for row in comparison_rows
        ),
        "maximum_absolute_m3_energy_residual_w": max(abs(row["m3_energy_residual_w"]) for row in comparison_rows),
        "maximum_absolute_m3_mass_flow_residual_kg_s": max(abs(row["m3_mass_flow_residual_kg_s"]) for row in comparison_rows),
        "use_limit": suite["use_limit"],
    }
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "comparison_csv": comparison_csv,
        "branches_csv": branches_csv,
        "comparison_svg": figure_paths["svg"],
        "comparison_png": figure_paths["png"],
        "comparison_pdf": figure_paths["pdf"],
        "summary_json": summary_json,
    }


if __name__ == "__main__":
    for name, path in generate_artifacts().items():
        print(f"{name}: {path}")
