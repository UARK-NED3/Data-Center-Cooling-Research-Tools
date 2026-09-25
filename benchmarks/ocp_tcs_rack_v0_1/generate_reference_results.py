"""Generate traceable synthetic result artifacts for the v0.1 benchmark.

The generated baseline and sensitivity sweep are verification outputs of the
declared steady energy balance. They are not measurements, a calibration, or
an equipment-performance prediction.
"""

import csv
import hashlib
import json
from pathlib import Path

from .analytical_reference import DEFAULT_CASE_PATH, evaluate_case_file, evaluate_steady_case


DEFAULT_OUTPUT_DIRECTORY = Path(__file__).with_name("results")
FLOW_SWEEP_KG_S = (0.25, 0.50, 0.75, 1.00)


def _format_number(value: float) -> str:
    """Format a float compactly and deterministically for public artifacts."""
    return format(value, ".12g")


def _case_sha256(case_path: Path) -> str:
    return hashlib.sha256(case_path.read_bytes()).hexdigest()


def _flow_sensitivity_rows(case: dict) -> list[dict[str, float]]:
    rows = []
    for mass_flow_kg_s in FLOW_SWEEP_KG_S:
        result = evaluate_steady_case(
            it_heat_w=case["rack"]["it_heat_w"],
            liquid_capture_fraction=case["rack"]["liquid_capture_fraction"],
            tcs_supply_temperature_c=case["tcs"]["supply_temperature_c"],
            tcs_mass_flow_kg_s=mass_flow_kg_s,
            coolant_specific_heat_j_kg_k=case["fluid"]["specific_heat_j_kg_k"],
        )
        rows.append(
            {
                "mass_flow_kg_s": mass_flow_kg_s,
                "liquid_heat_w": result["liquid_heat_w"],
                "tcs_temperature_rise_k": result["tcs_temperature_rise_k"],
                "tcs_return_temperature_c": result["tcs_return_temperature_c"],
                "rack_energy_residual_w": result["rack_energy_residual_w"],
            }
        )
    return rows


def _flow_sensitivity_svg(rows: list[dict[str, float]]) -> str:
    """Return a self-contained SVG plot with explicit synthetic-result labels."""
    left, top, width, height = 125, 78, 740, 340
    x_min, x_max = FLOW_SWEEP_KG_S[0], FLOW_SWEEP_KG_S[-1]
    y_min, y_max = 30.0, 38.0

    def x_coordinate(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * width

    def y_coordinate(value: float) -> float:
        return top + (y_max - value) / (y_max - y_min) * height

    points = " ".join(
        f"{x_coordinate(row['mass_flow_kg_s']):.2f},{y_coordinate(row['tcs_return_temperature_c']):.2f}"
        for row in rows
    )
    grid_lines = []
    labels = []
    for temperature in range(30, 39, 2):
        y_value = y_coordinate(float(temperature))
        grid_lines.append(
            f'<line x1="{left}" y1="{y_value:.2f}" x2="{left + width}" y2="{y_value:.2f}" class="grid"/>'
        )
        labels.append(
            f'<text x="{left - 14}" y="{y_value + 5:.2f}" class="tick" text-anchor="end">{temperature}</text>'
        )
    for flow in FLOW_SWEEP_KG_S:
        x_value = x_coordinate(flow)
        grid_lines.append(
            f'<line x1="{x_value:.2f}" y1="{top}" x2="{x_value:.2f}" y2="{top + height}" class="grid"/>'
        )
        labels.append(
            f'<text x="{x_value:.2f}" y="{top + height + 30}" class="tick" text-anchor="middle">{_format_number(flow)}</text>'
        )
    markers = "".join(
        f'<circle cx="{x_coordinate(row["mass_flow_kg_s"]):.2f}" cy="{y_coordinate(row["tcs_return_temperature_c"]):.2f}" r="5" class="marker"/>'
        for row in rows
    )
    baseline = next(row for row in rows if row["mass_flow_kg_s"] == 0.5)
    baseline_x = x_coordinate(baseline["mass_flow_kg_s"])
    baseline_y = y_coordinate(baseline["tcs_return_temperature_c"])

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="560" viewBox="0 0 960 560" role="img" aria-labelledby="title description">
  <title id="title">Technology-cooling-system flow sensitivity</title>
  <desc id="description">Synthetic steady-state coolant return temperature for the v0.1 rack verification case as a function of total TCS mass flow rate.</desc>
  <style>
    .title {{ font: 700 25px Arial, sans-serif; fill: #102a43; }}
    .subtitle {{ font: 15px Arial, sans-serif; fill: #486581; }}
    .axis {{ stroke: #243b53; stroke-width: 1.5; }}
    .grid {{ stroke: #d9e2ec; stroke-width: 1; }}
    .tick {{ font: 14px Arial, sans-serif; fill: #486581; }}
    .label {{ font: 16px Arial, sans-serif; fill: #243b53; }}
    .series {{ fill: none; stroke: #0b7285; stroke-width: 4; }}
    .marker {{ fill: #0b7285; stroke: white; stroke-width: 2; }}
    .baseline {{ font: 700 14px Arial, sans-serif; fill: #087f5b; }}
    .note {{ font: 13px Arial, sans-serif; fill: #627d98; }}
  </style>
  <rect width="960" height="560" fill="white"/>
  <text x="70" y="36" class="title">Technology-cooling-system flow sensitivity</text>
  <text x="70" y="59" class="subtitle">10 kW IT heat, 80% liquid capture, 30 °C supply, cₚ = 4180 J/(kg·K)</text>
  {''.join(grid_lines)}
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + height}" class="axis"/>
  <line x1="{left}" y1="{top + height}" x2="{left + width}" y2="{top + height}" class="axis"/>
  {''.join(labels)}
  <polyline points="{points}" class="series"/>
  {markers}
  <text x="{baseline_x + 12:.2f}" y="{baseline_y - 14:.2f}" class="baseline">Baseline: 33.83 °C</text>
  <text x="{left + width / 2:.2f}" y="{top + height + 66}" class="label" text-anchor="middle">Total TCS mass flow rate, ṁ [kg/s]</text>
  <text x="32" y="{top + height / 2:.2f}" class="label" text-anchor="middle" transform="rotate(-90 32 {top + height / 2:.2f})">TCS return temperature [°C]</text>
  <text x="70" y="520" class="note">Synthetic verification only; no pressure drop, component thermal resistance, CDU, pump, or facility model is included.</text>
</svg>
'''


def generate_reference_results(
    case_path: str | Path = DEFAULT_CASE_PATH,
    output_directory: str | Path = DEFAULT_OUTPUT_DIRECTORY,
) -> dict[str, Path]:
    """Generate the baseline JSON, flow-sensitivity CSV, and SVG figure."""
    resolved_case_path = Path(case_path)
    resolved_output_directory = Path(output_directory)
    resolved_output_directory.mkdir(parents=True, exist_ok=True)
    with resolved_case_path.open(encoding="utf-8") as case_file:
        case = json.load(case_file)

    baseline = evaluate_case_file(resolved_case_path)
    flow_rows = _flow_sensitivity_rows(case)
    baseline_path = resolved_output_directory / "canonical_steady_state_result.json"
    flow_csv_path = resolved_output_directory / "flow_sensitivity.csv"
    flow_svg_path = resolved_output_directory / "flow_sensitivity.svg"

    baseline_payload = {
        "case_id": case["case_id"],
        "case_sha256": _case_sha256(resolved_case_path),
        "evidence_class": "synthetic_derived",
        "generator": "benchmarks.ocp_tcs_rack_v0_1.generate_reference_results",
        "result": baseline,
        "use_limit": "Verification output only; not a calibrated or experimentally validated rack result.",
    }
    baseline_path.write_text(
        json.dumps(baseline_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with flow_csv_path.open("w", newline="", encoding="utf-8") as result_file:
        writer = csv.DictWriter(result_file, fieldnames=list(flow_rows[0]))
        writer.writeheader()
        for row in flow_rows:
            writer.writerow({key: _format_number(value) for key, value in row.items()})
    flow_svg_path.write_text(_flow_sensitivity_svg(flow_rows), encoding="utf-8")

    return {
        "baseline_json": baseline_path,
        "flow_csv": flow_csv_path,
        "flow_svg": flow_svg_path,
    }


if __name__ == "__main__":
    for artifact_name, artifact_path in generate_reference_results().items():
        print(f"{artifact_name}: {artifact_path}")
