"""Synthetic multi-branch liquid-rack reference model for benchmark v1.1.

The model represents a rack-manifold technology-cooling-system control volume.
Parallel branches share a common pressure drop and carry declared portions of
the IT heat.  All branch properties are synthetic, illustrative quantities.
The model supports conservation and model-structure checks; it is not a
calibrated cold-plate, rack, or facility prediction.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


REQUIRED_BRANCH_FIELDS = (
    "branch_id",
    "it_heat_fraction",
    "liquid_capture_fraction",
    "hydraulic_resistance_pa_s2_kg2",
    "ua_w_k",
    "hardware_heat_capacity_j_k",
    "coolant_heat_capacity_j_k",
)


def _validate_common_inputs(
    *,
    it_heat_w: float,
    mass_flow_kg_s: float,
    specific_heat_j_kg_k: float,
    density_kg_m3: float,
    pump_efficiency: float,
) -> None:
    if it_heat_w < 0.0:
        raise ValueError("it_heat_w must be nonnegative")
    if mass_flow_kg_s <= 0.0:
        raise ValueError("mass_flow_kg_s must be positive")
    if specific_heat_j_kg_k <= 0.0:
        raise ValueError("specific_heat_j_kg_k must be positive")
    if density_kg_m3 <= 0.0:
        raise ValueError("density_kg_m3 must be positive")
    if not 0.0 < pump_efficiency <= 1.0:
        raise ValueError("pump_efficiency must be in (0, 1]")


def _validated_branch_copies(branches: Sequence[dict]) -> list[dict]:
    if not branches:
        raise ValueError("at least one branch is required")
    copies: list[dict] = []
    identifiers: set[str] = set()
    for branch in branches:
        missing = [field for field in REQUIRED_BRANCH_FIELDS if field not in branch]
        if missing:
            raise ValueError(f"branch is missing required fields: {', '.join(missing)}")
        copy = dict(branch)
        branch_id = str(copy["branch_id"])
        if not branch_id or branch_id in identifiers:
            raise ValueError("branch_id values must be nonempty and unique")
        identifiers.add(branch_id)
        copy["branch_id"] = branch_id
        if copy["it_heat_fraction"] < 0.0:
            raise ValueError("it_heat_fraction must be nonnegative")
        if not 0.0 <= copy["liquid_capture_fraction"] <= 1.0:
            raise ValueError("liquid_capture_fraction must be between 0 and 1")
        for field in (
            "hydraulic_resistance_pa_s2_kg2",
            "ua_w_k",
            "hardware_heat_capacity_j_k",
            "coolant_heat_capacity_j_k",
        ):
            if copy[field] <= 0.0:
                raise ValueError(f"{field} must be positive")
        copies.append(copy)
    if not math.isclose(sum(branch["it_heat_fraction"] for branch in copies), 1.0, abs_tol=1.0e-12):
        raise ValueError("branch it_heat_fraction values must sum to one")
    return copies


def _hydraulic_split(branches: Sequence[dict], mass_flow_kg_s: float) -> tuple[float, dict[str, float]]:
    """Return common parallel-branch pressure drop and branch mass flows.

    Each branch follows ``Delta p = K m_dot^2``.  The equation is an assumed
    synthetic closure for this benchmark, not a replacement for a calibrated
    component pressure-drop correlation.
    """
    conductance_sum = sum(1.0 / math.sqrt(branch["hydraulic_resistance_pa_s2_kg2"]) for branch in branches)
    pressure_drop_pa = (mass_flow_kg_s / conductance_sum) ** 2
    flows = {
        branch["branch_id"]: math.sqrt(pressure_drop_pa / branch["hydraulic_resistance_pa_s2_kg2"])
        for branch in branches
    }
    return pressure_drop_pa, flows


def evaluate_multibranch_steady_case(
    *,
    it_heat_w: float,
    supply_temperature_c: float,
    mass_flow_kg_s: float,
    specific_heat_j_kg_k: float,
    density_kg_m3: float,
    pump_efficiency: float,
    branches: Sequence[dict],
) -> dict:
    """Evaluate the declared multi-branch steady liquid-network model.

    ``T_return,i = T_supply + Q_liquid,i/(m_dot_i c_p)`` defines each branch
    outlet.  The reported mixed return is the mass-flow-weighted branch outlet.
    Hardware temperatures are effective states defined by
    ``T_h,i = T_return,i + Q_liquid,i/UA_i``.  They are model outputs, not
    measured device temperatures.
    """
    _validate_common_inputs(
        it_heat_w=it_heat_w,
        mass_flow_kg_s=mass_flow_kg_s,
        specific_heat_j_kg_k=specific_heat_j_kg_k,
        density_kg_m3=density_kg_m3,
        pump_efficiency=pump_efficiency,
    )
    branch_list = _validated_branch_copies(branches)
    pressure_drop_pa, branch_flows = _hydraulic_split(branch_list, mass_flow_kg_s)
    branch_rows: list[dict[str, float | str]] = []
    total_liquid_heat_w = 0.0
    total_residual_air_heat_w = 0.0
    heat_removed_by_liquid_w = 0.0
    mixed_temperature_numerator = 0.0
    for branch in branch_list:
        branch_id = branch["branch_id"]
        branch_heat_w = it_heat_w * branch["it_heat_fraction"]
        liquid_heat_w = branch_heat_w * branch["liquid_capture_fraction"]
        residual_air_heat_w = branch_heat_w - liquid_heat_w
        branch_flow_kg_s = branch_flows[branch_id]
        return_temperature_c = supply_temperature_c + liquid_heat_w / (branch_flow_kg_s * specific_heat_j_kg_k)
        effective_hardware_temperature_c = return_temperature_c + liquid_heat_w / branch["ua_w_k"]
        liquid_removed_w = branch_flow_kg_s * specific_heat_j_kg_k * (return_temperature_c - supply_temperature_c)
        total_liquid_heat_w += liquid_heat_w
        total_residual_air_heat_w += residual_air_heat_w
        heat_removed_by_liquid_w += liquid_removed_w
        mixed_temperature_numerator += branch_flow_kg_s * return_temperature_c
        branch_rows.append(
            {
                "branch_id": branch_id,
                "it_heat_w": branch_heat_w,
                "liquid_heat_w": liquid_heat_w,
                "residual_air_heat_w": residual_air_heat_w,
                "mass_flow_kg_s": branch_flow_kg_s,
                "return_temperature_c": return_temperature_c,
                "effective_hardware_temperature_c": effective_hardware_temperature_c,
                "hydraulic_resistance_pa_s2_kg2": branch["hydraulic_resistance_pa_s2_kg2"],
                "ua_w_k": branch["ua_w_k"],
            }
        )
    mixed_return_temperature_c = mixed_temperature_numerator / mass_flow_kg_s
    volumetric_flow_m3_s = mass_flow_kg_s / density_kg_m3
    pump_power_w = pressure_drop_pa * volumetric_flow_m3_s / pump_efficiency
    return {
        "it_heat_w": it_heat_w,
        "total_liquid_heat_w": total_liquid_heat_w,
        "total_residual_air_heat_w": total_residual_air_heat_w,
        "supply_temperature_c": supply_temperature_c,
        "mass_flow_kg_s": mass_flow_kg_s,
        "mixed_return_temperature_c": mixed_return_temperature_c,
        "pressure_drop_pa": pressure_drop_pa,
        "pump_power_w": pump_power_w,
        "energy_residual_w": total_liquid_heat_w - heat_removed_by_liquid_w,
        "mass_flow_residual_kg_s": mass_flow_kg_s - sum(branch_flows.values()),
        "branches": branch_rows,
    }


def simulate_multibranch_case(
    *,
    it_heat_w: float,
    supply_temperature_c: float,
    mass_flow_kg_s: float,
    specific_heat_j_kg_k: float,
    density_kg_m3: float,
    pump_efficiency: float,
    branches: Sequence[dict],
    duration_s: float,
    time_step_s: float,
) -> list[dict]:
    """Integrate independent effective branch states under constant inputs.

    The liquid network recalculates a parallel hydraulic split from the declared
    resistance coefficients.  Each branch integrates effective hardware and
    coolant states with forward Euler.  The residual is a model-equation check,
    not a measurement uncertainty estimate.
    """
    _validate_common_inputs(
        it_heat_w=it_heat_w,
        mass_flow_kg_s=mass_flow_kg_s,
        specific_heat_j_kg_k=specific_heat_j_kg_k,
        density_kg_m3=density_kg_m3,
        pump_efficiency=pump_efficiency,
    )
    if duration_s <= 0.0 or time_step_s <= 0.0:
        raise ValueError("duration_s and time_step_s must be positive")
    step_count = round(duration_s / time_step_s)
    if not math.isclose(step_count * time_step_s, duration_s, abs_tol=1.0e-12):
        raise ValueError("duration_s must be an integer multiple of time_step_s")

    branch_list = _validated_branch_copies(branches)
    pressure_drop_pa, branch_flows = _hydraulic_split(branch_list, mass_flow_kg_s)
    hardware_temperature_c = {branch["branch_id"]: supply_temperature_c for branch in branch_list}
    return_temperature_c = {branch["branch_id"]: supply_temperature_c for branch in branch_list}
    pump_power_w = pressure_drop_pa * (mass_flow_kg_s / density_kg_m3) / pump_efficiency
    rows: list[dict] = []
    for index in range(step_count + 1):
        branch_states: list[dict[str, float | str]] = []
        residual_w = 0.0
        liquid_heat_total_w = 0.0
        mixed_return_numerator = 0.0
        for branch in branch_list:
            branch_id = branch["branch_id"]
            liquid_heat_w = it_heat_w * branch["it_heat_fraction"] * branch["liquid_capture_fraction"]
            branch_flow_kg_s = branch_flows[branch_id]
            heat_transfer_w = branch["ua_w_k"] * (hardware_temperature_c[branch_id] - return_temperature_c[branch_id])
            liquid_rejection_w = branch_flow_kg_s * specific_heat_j_kg_k * (return_temperature_c[branch_id] - supply_temperature_c)
            hardware_rate_k_s = (liquid_heat_w - heat_transfer_w) / branch["hardware_heat_capacity_j_k"]
            coolant_rate_k_s = (heat_transfer_w - liquid_rejection_w) / branch["coolant_heat_capacity_j_k"]
            residual_w += (
                liquid_heat_w
                - liquid_rejection_w
                - branch["hardware_heat_capacity_j_k"] * hardware_rate_k_s
                - branch["coolant_heat_capacity_j_k"] * coolant_rate_k_s
            )
            liquid_heat_total_w += liquid_heat_w
            mixed_return_numerator += branch_flow_kg_s * return_temperature_c[branch_id]
            branch_states.append(
                {
                    "branch_id": branch_id,
                    "mass_flow_kg_s": branch_flow_kg_s,
                    "hardware_temperature_c": hardware_temperature_c[branch_id],
                    "return_temperature_c": return_temperature_c[branch_id],
                    "liquid_heat_w": liquid_heat_w,
                    "heat_transfer_w": heat_transfer_w,
                    "liquid_rejection_w": liquid_rejection_w,
                }
            )
            hardware_temperature_c[branch_id] += hardware_rate_k_s * time_step_s
            return_temperature_c[branch_id] += coolant_rate_k_s * time_step_s
        rows.append(
            {
                "time_s": index * time_step_s,
                "mixed_return_temperature_c": mixed_return_numerator / mass_flow_kg_s,
                "peak_hardware_temperature_c": max(state["hardware_temperature_c"] for state in branch_states),
                "liquid_heat_w": liquid_heat_total_w,
                "pressure_drop_pa": pressure_drop_pa,
                "pump_power_w": pump_power_w,
                "energy_residual_w": residual_w,
                "mass_flow_residual_kg_s": mass_flow_kg_s - sum(branch_flows.values()),
                "branches": branch_states,
            }
        )
    return rows
