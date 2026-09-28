"""Generate deterministic, public artifacts for the v1.0 synthetic suite."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .model_suite import DEFAULT_SUITE_PATH, evaluate_quasi_steady_case, load_suite, simulate_two_node_case


DEFAULT_OUTPUT_DIRECTORY = Path(__file__).with_name("results")


def _number(value: float) -> str:
    return format(value, ".12g")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scenario_input(time_s: float, baseline: dict) -> tuple[float, float, float]:
    """Return synthetic IT heat, supply temperature, and flow for a 20-min test.

    The first 300 s establish a low-load state. Subsequent changes separately
    exercise IT-load, supply-temperature, and flow response. Values are test
    stimuli, not measurements or recommended equipment operating points.
    """
    it_heat_w = 2_500.0 if time_s < 300.0 else baseline["it_heat_w"]
    supply_temperature_c = baseline["supply_temperature_c"] if time_s < 720.0 else 34.0
    mass_flow_kg_s = baseline["mass_flow_kg_s"] if time_s < 960.0 else 0.35
    return it_heat_w, supply_temperature_c, mass_flow_kg_s


def _simulate_transient(suite: dict, *, duration_s: float = 1200.0, time_step_s: float = 2.0) -> list[dict[str, float]]:
    baseline = suite["baseline"]
    parameters = suite["reduced_order_parameters"]
    cp = suite["fluid"]["specific_heat_j_kg_k"]
    liquid_fraction = baseline["liquid_capture_fraction"]
    hardware_temperature_c = baseline["supply_temperature_c"]
    return_temperature_c = baseline["supply_temperature_c"]
    rows: list[dict[str, float]] = []
    count = round(duration_s / time_step_s)
    for index in range(count + 1):
        time_s = index * time_step_s
        it_heat_w, supply_temperature_c, mass_flow_kg_s = _scenario_input(time_s, baseline)
        steady = evaluate_quasi_steady_case(
            it_heat_w=it_heat_w,
            liquid_capture_fraction=liquid_fraction,
            supply_temperature_c=supply_temperature_c,
            mass_flow_kg_s=mass_flow_kg_s,
            specific_heat_j_kg_k=cp,
        )
        liquid_heat_w = steady["liquid_heat_w"]
        capacity_rate_w_k = mass_flow_kg_s * cp
        heat_transfer_w = parameters["ua_w_k"] * (hardware_temperature_c - return_temperature_c)
        liquid_rejection_w = capacity_rate_w_k * (return_temperature_c - supply_temperature_c)
        hardware_rate_k_s = (liquid_heat_w - heat_transfer_w) / parameters["heat_capacity_hardware_j_k"]
        coolant_rate_k_s = (heat_transfer_w - liquid_rejection_w) / parameters["heat_capacity_coolant_j_k"]
        residual_w = (
            liquid_heat_w
            - liquid_rejection_w
            - parameters["heat_capacity_hardware_j_k"] * hardware_rate_k_s
            - parameters["heat_capacity_coolant_j_k"] * coolant_rate_k_s
        )
        rows.append(
            {
                "time_s": time_s,
                "it_heat_w": it_heat_w,
                "supply_temperature_c": supply_temperature_c,
                "mass_flow_kg_s": mass_flow_kg_s,
                "m1_return_temperature_c": steady["return_temperature_c"],
                "m2_hardware_temperature_c": hardware_temperature_c,
                "m2_return_temperature_c": return_temperature_c,
                "m2_energy_residual_w": residual_w,
            }
        )
        hardware_temperature_c += hardware_rate_k_s * time_step_s
        return_temperature_c += coolant_rate_k_s * time_step_s
    return rows


def _steady_sweep(suite: dict) -> list[dict[str, float]]:
    baseline = suite["baseline"]
    cp = suite["fluid"]["specific_heat_j_kg_k"]
    rows: list[dict[str, float]] = []
    for flow in (0.25, 0.35, 0.5, 0.75, 1.0):
        result = evaluate_quasi_steady_case(
            it_heat_w=baseline["it_heat_w"],
            liquid_capture_fraction=baseline["liquid_capture_fraction"],
            supply_temperature_c=baseline["supply_temperature_c"],
            mass_flow_kg_s=flow,
            specific_heat_j_kg_k=cp,
        )
        rows.append(
            {
                "mass_flow_kg_s": flow,
                "return_temperature_c": result["return_temperature_c"],
                "temperature_rise_k": result["temperature_rise_k"],
                "liquid_heat_w": result["liquid_heat_w"],
            }
        )
    return rows


def _polyline(rows: list[dict[str, float]], x_key: str, y_key: str, *, left: float, top: float, width: float, height: float, x_min: float, x_max: float, y_min: float, y_max: float) -> str:
    return " ".join(
        f"{left + (row[x_key] - x_min) / (x_max - x_min) * width:.2f},{top + (y_max - row[y_key]) / (y_max - y_min) * height:.2f}"
        for row in rows
    )


def _transient_svg(rows: list[dict[str, float]]) -> str:
    """Draw a two-panel vector figure without a plotting dependency."""
    left, top, width, height = 110, 115, 435, 305
    right_left = 685
    x_min, x_max = 0.0, 1200.0
    y_min, y_max = 29.0, 43.0
    x = lambda value, origin: origin + (value - x_min) / (x_max - x_min) * width
    y = lambda value: top + (y_max - value) / (y_max - y_min) * height
    grid = []
    ticks = []
    for value in range(30, 44, 2):
        for origin in (left, right_left):
            grid.append(f'<line x1="{origin}" y1="{y(value):.2f}" x2="{origin + width}" y2="{y(value):.2f}" class="grid"/>')
            ticks.append(f'<text x="{origin - 11}" y="{y(value) + 5:.2f}" class="tick" text-anchor="end">{value}</text>')
    for value in range(0, 1201, 300):
        for origin in (left, right_left):
            grid.append(f'<line x1="{x(value, origin):.2f}" y1="{top}" x2="{x(value, origin):.2f}" y2="{top + height}" class="grid"/>')
            ticks.append(f'<text x="{x(value, origin):.2f}" y="{top + height + 27}" class="tick" text-anchor="middle">{value}</text>')
    event_lines = "".join(
        f'<line x1="{x(event, left):.2f}" y1="{top}" x2="{x(event, left):.2f}" y2="{top + height}" class="event"/>'
        + f'<line x1="{x(event, right_left):.2f}" y1="{top}" x2="{x(event, right_left):.2f}" y2="{top + height}" class="event"/>'
        for event in (300.0, 720.0, 960.0)
    )
    m1 = _polyline(rows, "time_s", "m1_return_temperature_c", left=left, top=top, width=width, height=height, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
    m2 = _polyline(rows, "time_s", "m2_return_temperature_c", left=left, top=top, width=width, height=height, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
    hardware = _polyline(rows, "time_s", "m2_hardware_temperature_c", left=right_left, top=top, width=width, height=height, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
    coolant = _polyline(rows, "time_s", "m2_return_temperature_c", left=right_left, top=top, width=width, height=height, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="630" viewBox="0 0 1260 630" role="img" aria-labelledby="title description">
  <title id="title">Synthetic liquid-cooled rack transient model comparison</title>
  <desc id="description">The left plot contrasts quasi-steady and two-node predicted TCS return temperature. The right plot shows the two-node effective hardware and coolant states. Vertical dotted lines mark independent synthetic input changes.</desc>
  <style>
    .title {{ font: 700 25px Arial, sans-serif; fill: #102a43; }} .subtitle {{ font: 15px Arial, sans-serif; fill: #486581; }}
    .axis {{ stroke: #243b53; stroke-width: 1.5; }} .grid {{ stroke: #d9e2ec; stroke-width: 1; }} .event {{ stroke: #829ab1; stroke-width: 1.3; stroke-dasharray: 6 5; }}
    .tick {{ font: 13px Arial, sans-serif; fill: #486581; }} .label {{ font: 15px Arial, sans-serif; fill: #243b53; }} .note {{ font: 13px Arial, sans-serif; fill: #627d98; }}
    .mone {{ fill: none; stroke: #0b7285; stroke-width: 3.3; }} .mtwo {{ fill: none; stroke: #d9480f; stroke-width: 3.3; }} .hardware {{ fill: none; stroke: #7048e8; stroke-width: 3.3; }}
  </style>
  <rect width="1260" height="630" fill="white"/>
  <text x="68" y="38" class="title">Synthetic liquid-cooled rack response to declared disturbances</text>
  <text x="68" y="63" class="subtitle">10 kW maximum IT heat, 80% liquid capture, water cₚ = 4180 J/(kg·K); no hardware measurements or calibration</text>
  <text x="110" y="93" class="label">(a) Return-temperature response</text>
  <text x="685" y="93" class="label">(b) Two-node internal states</text>
  {''.join(grid)}
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + height}" class="axis"/><line x1="{left}" y1="{top + height}" x2="{left + width}" y2="{top + height}" class="axis"/>
  <line x1="{right_left}" y1="{top}" x2="{right_left}" y2="{top + height}" class="axis"/><line x1="{right_left}" y1="{top + height}" x2="{right_left + width}" y2="{top + height}" class="axis"/>
  {''.join(ticks)}{event_lines}
  <polyline points="{m1}" class="mone"/><polyline points="{m2}" class="mtwo"/><polyline points="{hardware}" class="hardware"/><polyline points="{coolant}" class="mtwo"/>
  <line x1="128" y1="462" x2="158" y2="462" class="mone"/><text x="166" y="467" class="tick">M1 quasi-steady return</text>
  <line x1="335" y1="462" x2="365" y2="462" class="mtwo"/><text x="373" y="467" class="tick">M2 two-node return</text>
  <line x1="703" y1="462" x2="733" y2="462" class="hardware"/><text x="741" y="467" class="tick">M2 effective hardware</text>
  <line x1="925" y1="462" x2="955" y2="462" class="mtwo"/><text x="963" y="467" class="tick">M2 return</text>
  <text x="{left + width / 2}" y="{top + height + 62}" class="label" text-anchor="middle">Time [s]</text><text x="{right_left + width / 2}" y="{top + height + 62}" class="label" text-anchor="middle">Time [s]</text>
  <text x="33" y="{top + height / 2}" class="label" text-anchor="middle" transform="rotate(-90 33 {top + height / 2})">Temperature [°C]</text><text x="608" y="{top + height / 2}" class="label" text-anchor="middle" transform="rotate(-90 608 {top + height / 2})">Temperature [°C]</text>
  <text x="110" y="506" class="note">Dashed events: 2.5→10 kW IT load at 300 s; 30→34 °C supply at 720 s; 0.50→0.35 kg/s flow at 960 s.</text>
  <text x="110" y="534" class="note">Synthetic scenarios; verification and model-structure comparison only. Differences arise from declared thermal storage, not measured rack behavior.</text>
</svg>'''


def _write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows([{key: _number(value) for key, value in row.items()} for row in rows])


def generate_artifacts(output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY) -> dict[str, Path]:
    """Build deterministic synthetic results, an SVG figure, and traceability JSON."""
    destination = Path(output_directory)
    destination.mkdir(parents=True, exist_ok=True)
    suite = load_suite()
    transient_rows = _simulate_transient(suite)
    steady_rows = _steady_sweep(suite)
    transient_csv = destination / "synthetic_transient_response.csv"
    steady_csv = destination / "synthetic_steady_flow_sweep.csv"
    transient_svg = destination / "synthetic_transient_model_comparison.svg"
    summary_json = destination / "synthetic_suite_run.json"
    _write_csv(transient_csv, transient_rows)
    _write_csv(steady_csv, steady_rows)
    transient_svg.write_text(_transient_svg(transient_rows), encoding="utf-8")
    summary = {
        "suite_id": suite["suite_id"],
        "suite_sha256": _sha256(DEFAULT_SUITE_PATH),
        "evidence_class": suite["evidence_class"],
        "validation_state": suite["validation_state"],
        "model_levels": {
            "M1": "quasi_steady_energy_balance",
            "M2": "two_node_reduced_order_model",
            "M3": "component_network_adapter_planned_not_executed"
        },
        "transient_rows": len(transient_rows),
        "maximum_absolute_m2_energy_residual_w": max(abs(row["m2_energy_residual_w"]) for row in transient_rows),
        "use_limit": suite["use_limit"],
    }
    summary_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "transient_csv": transient_csv,
        "steady_csv": steady_csv,
        "transient_svg": transient_svg,
        "summary_json": summary_json,
    }


if __name__ == "__main__":
    for name, path in generate_artifacts().items():
        print(f"{name}: {path}")
