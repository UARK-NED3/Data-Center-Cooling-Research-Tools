"""Three explicitly different temperature-response model classes for RDHx data.

The models share supply temperature, coolant mass flow, and an externally
supplied thermal-load proxy.  A proxy is not evidence that its load belongs to
the PLC circuit.  The caller is responsible for recording that evidence class.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def _as_vector(name: str, values: Iterable[float]) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError(f"{name} must be a nonempty one-dimensional sequence")
    if not np.isfinite(vector).all():
        raise ValueError(f"{name} must contain finite values")
    return vector


def _validate_common_inputs(
    supply_temperature_c: Iterable[float],
    mass_flow_kg_s: Iterable[float],
    load_proxy_kw: Iterable[float],
    load_to_circuit_fraction: float,
    cp_j_kgk: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    supply = _as_vector("supply_temperature_c", supply_temperature_c)
    mass_flow = _as_vector("mass_flow_kg_s", mass_flow_kg_s)
    load_kw = _as_vector("load_proxy_kw", load_proxy_kw)
    if not (supply.size == mass_flow.size == load_kw.size):
        raise ValueError("supply, mass flow, and load proxy must have equal lengths")
    if (mass_flow <= 0.0).any():
        raise ValueError("mass_flow_kg_s must be positive")
    if (load_kw < 0.0).any():
        raise ValueError("load_proxy_kw must be nonnegative")
    if not 0.0 <= load_to_circuit_fraction <= 1.0:
        raise ValueError("load_to_circuit_fraction must be between zero and one")
    if not np.isfinite(cp_j_kgk) or cp_j_kgk <= 0.0:
        raise ValueError("cp_j_kgk must be positive and finite")
    return supply, mass_flow, load_kw


def predict_m0_quasisteady(
    supply_temperature_c: Iterable[float],
    mass_flow_kg_s: Iterable[float],
    load_proxy_kw: Iterable[float],
    *,
    load_to_circuit_fraction: float,
    cp_j_kgk: float = 4182.0,
) -> np.ndarray:
    """Predict return temperature from the zero-storage energy balance.

    M0 is the algebraic reference \(T_r=T_s+\eta Q/(\dot m c_p)\).  It is
    not an independently validated rack model unless ``load_proxy_kw`` has a
    documented physical mapping to the circuit control volume.
    """

    supply, mass_flow, load_kw = _validate_common_inputs(
        supply_temperature_c,
        mass_flow_kg_s,
        load_proxy_kw,
        load_to_circuit_fraction,
        cp_j_kgk,
    )
    heat_w = 1000.0 * load_to_circuit_fraction * load_kw
    return supply + heat_w / (mass_flow * cp_j_kgk)


def fit_m0_load_fraction(
    supply_temperature_c: Iterable[float],
    mass_flow_kg_s: Iterable[float],
    load_proxy_kw: Iterable[float],
    observed_return_temperature_c: Iterable[float],
    *,
    cp_j_kgk: float = 4182.0,
) -> float:
    """Fit the bounded load-to-circuit fraction for M0 on a training segment.

    A best fit at zero or one is reported as a boundary result.  It is a
    diagnostic of the proxy/control-volume match, not proof of a heat-path
    fraction.
    """

    supply, mass_flow, load_kw = _validate_common_inputs(
        supply_temperature_c, mass_flow_kg_s, load_proxy_kw, 0.0, cp_j_kgk
    )
    observed = _as_vector("observed_return_temperature_c", observed_return_temperature_c)
    if observed.size != supply.size:
        raise ValueError("observed return temperature must match input length")
    sensitivity_k = 1000.0 * load_kw / (mass_flow * cp_j_kgk)
    numerator = float(np.dot(sensitivity_k, observed - supply))
    denominator = float(np.dot(sensitivity_k, sensitivity_k))
    if denominator == 0.0:
        raise ValueError("load proxy must contain at least one positive value")
    return float(np.clip(numerator / denominator, 0.0, 1.0))


def split_contiguous_time_series(
    sample_count: int,
    *,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return disjoint chronological index blocks for train, validation, and test."""

    if sample_count < 5:
        raise ValueError("at least five samples are required for chronological splitting")
    if not 0.0 < train_fraction < 1.0 or not 0.0 < validation_fraction < 1.0:
        raise ValueError("split fractions must be between zero and one")
    train_end = int(sample_count * train_fraction)
    validation_end = train_end + int(sample_count * validation_fraction)
    if train_end < 1 or validation_end <= train_end or validation_end >= sample_count:
        raise ValueError("split fractions leave an empty train, validation, or test block")
    indices = np.arange(sample_count)
    return indices[:train_end], indices[train_end:validation_end], indices[validation_end:]


def simulate_m1_lumped(
    supply_temperature_c: Iterable[float],
    mass_flow_kg_s: Iterable[float],
    load_proxy_kw: Iterable[float],
    *,
    initial_return_temperature_c: float,
    load_to_circuit_fraction: float,
    thermal_capacitance_j_k: float,
    time_step_s: float,
    cp_j_kgk: float = 4182.0,
) -> np.ndarray:
    """Simulate a one-state liquid control volume with forward Euler time steps.

    The governing model is \(C dT_r/dt=\eta Q-\dot m c_p(T_r-T_s)\).
    ``thermal_capacitance_j_k`` is an effective parameter, not a measured mass
    unless the control-volume inventory and materials are documented.
    """

    supply, mass_flow, load_kw = _validate_common_inputs(
        supply_temperature_c,
        mass_flow_kg_s,
        load_proxy_kw,
        load_to_circuit_fraction,
        cp_j_kgk,
    )
    if not np.isfinite(initial_return_temperature_c):
        raise ValueError("initial_return_temperature_c must be finite")
    if not np.isfinite(thermal_capacitance_j_k) or thermal_capacitance_j_k <= 0.0:
        raise ValueError("thermal_capacitance_j_k must be positive and finite")
    if not np.isfinite(time_step_s) or time_step_s <= 0.0:
        raise ValueError("time_step_s must be positive and finite")
    if np.max(time_step_s * mass_flow * cp_j_kgk / thermal_capacitance_j_k) > 1.0:
        raise ValueError("time step is unstable for the requested M1 capacitance")

    predicted = np.empty_like(supply)
    predicted[0] = initial_return_temperature_c
    heat_w = 1000.0 * load_to_circuit_fraction * load_kw
    for index in range(1, predicted.size):
        heat_removed_w = mass_flow[index - 1] * cp_j_kgk * (predicted[index - 1] - supply[index - 1])
        predicted[index] = predicted[index - 1] + time_step_s * (
            heat_w[index - 1] - heat_removed_w
        ) / thermal_capacitance_j_k
    return predicted


def simulate_m2_two_state(
    supply_temperature_c: Iterable[float],
    mass_flow_kg_s: Iterable[float],
    load_proxy_kw: Iterable[float],
    *,
    initial_return_temperature_c: float,
    initial_load_temperature_c: float,
    load_to_circuit_fraction: float,
    load_thermal_capacitance_j_k: float,
    fluid_thermal_capacitance_j_k: float,
    heat_exchange_conductance_w_k: float,
    time_step_s: float,
    cp_j_kgk: float = 4182.0,
) -> np.ndarray:
    """Simulate a load-to-liquid, two-state thermal network with forward Euler.

    M2 represents a heat-producing thermal mass coupled by \(UA\) to a liquid
    control volume.  The reported output is the liquid return temperature.
    It needs topology, inventory, and heat-path evidence before its fitted
    parameters can receive a component-level physical interpretation.
    """

    supply, mass_flow, load_kw = _validate_common_inputs(
        supply_temperature_c,
        mass_flow_kg_s,
        load_proxy_kw,
        load_to_circuit_fraction,
        cp_j_kgk,
    )
    positive_parameters = {
        "load_thermal_capacitance_j_k": load_thermal_capacitance_j_k,
        "fluid_thermal_capacitance_j_k": fluid_thermal_capacitance_j_k,
        "heat_exchange_conductance_w_k": heat_exchange_conductance_w_k,
        "time_step_s": time_step_s,
    }
    for name, value in positive_parameters.items():
        if not np.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be positive and finite")
    if not np.isfinite(initial_return_temperature_c) or not np.isfinite(initial_load_temperature_c):
        raise ValueError("initial temperatures must be finite")

    fluid_stability = time_step_s * (heat_exchange_conductance_w_k + np.max(mass_flow) * cp_j_kgk)
    load_stability = time_step_s * heat_exchange_conductance_w_k
    if fluid_stability / fluid_thermal_capacitance_j_k > 1.0 or load_stability / load_thermal_capacitance_j_k > 1.0:
        raise ValueError("time step is unstable for the requested M2 parameters")

    return_temperature = np.empty_like(supply)
    load_temperature = float(initial_load_temperature_c)
    return_temperature[0] = initial_return_temperature_c
    heat_w = 1000.0 * load_to_circuit_fraction * load_kw
    for index in range(1, return_temperature.size):
        prior_return = return_temperature[index - 1]
        transfer_w = heat_exchange_conductance_w_k * (load_temperature - prior_return)
        removed_w = mass_flow[index - 1] * cp_j_kgk * (prior_return - supply[index - 1])
        load_temperature += time_step_s * (heat_w[index - 1] - transfer_w) / load_thermal_capacitance_j_k
        return_temperature[index] = prior_return + time_step_s * (transfer_w - removed_w) / fluid_thermal_capacitance_j_k
    return return_temperature
