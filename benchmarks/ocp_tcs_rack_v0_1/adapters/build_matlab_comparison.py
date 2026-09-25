"""Build a traceable cross-implementation comparison for the MATLAB adapter."""

import hashlib
import json
from pathlib import Path
import argparse


DEFAULT_TOLERANCE = 1e-10


def _read_json(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as input_file:
        return json.load(input_file)


def _sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_matlab_comparison(
    *,
    matlab_result_path: str | Path,
    baseline_result_path: str | Path,
    output_path: str | Path,
    tolerance: float = DEFAULT_TOLERANCE,
) -> dict:
    """Compare MATLAB and Python steady-state outputs and write a public record.

    Agreement is a cross-implementation check of the declared synthetic
    equation only. It does not establish model-form independence, calibration,
    or experimental validation.
    """
    resolved_matlab_path = Path(matlab_result_path)
    resolved_baseline_path = Path(baseline_result_path)
    resolved_output_path = Path(output_path)
    matlab_result = _read_json(resolved_matlab_path)
    baseline = _read_json(resolved_baseline_path)

    if matlab_result["case_id"] != baseline["case_id"]:
        raise ValueError("MATLAB and baseline result case IDs do not match")
    if matlab_result.get("evidence_class") != "synthetic_derived":
        raise ValueError("MATLAB result must declare synthetic_derived evidence")
    if tolerance < 0.0:
        raise ValueError("tolerance must be nonnegative")

    quantities = sorted(baseline["result"])
    differences = {}
    for quantity in quantities:
        if quantity not in matlab_result["result"]:
            raise ValueError(f"MATLAB result is missing {quantity}")
        differences[quantity] = abs(
            float(matlab_result["result"][quantity])
            - float(baseline["result"][quantity])
        )
    maximum_difference = max(differences.values(), default=0.0)
    comparison_state = (
        "agrees_within_tolerance"
        if maximum_difference <= tolerance
        else "disagrees"
    )
    comparison = {
        "case_id": baseline["case_id"],
        "case_sha256": baseline["case_sha256"],
        "comparison_state": comparison_state,
        "evidence_class": "synthetic_cross_implementation_check",
        "implementations": {
            "matlab": {
                "adapter_id": matlab_result["adapter_id"],
                "matlab_release": matlab_result.get("matlab_release", "unknown"),
                "result_sha256": _sha256(resolved_matlab_path),
            },
            "python": {
                "generator": baseline["generator"],
                "result_sha256": _sha256(resolved_baseline_path),
            },
        },
        "max_absolute_difference": maximum_difference,
        "per_quantity_absolute_difference": differences,
        "tolerance": tolerance,
        "use_limit": (
            "Cross-implementation consistency check for a shared synthetic steady "
            "energy balance only; not a calibrated or experimentally validated result."
        ),
    }
    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_output_path.write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return comparison


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare MATLAB and Python synthetic steady-state results."
    )
    parser.add_argument("matlab_result_path", type=Path)
    parser.add_argument("baseline_result_path", type=Path)
    parser.add_argument("output_path", type=Path)
    arguments = parser.parse_args()
    comparison = build_matlab_comparison(
        matlab_result_path=arguments.matlab_result_path,
        baseline_result_path=arguments.baseline_result_path,
        output_path=arguments.output_path,
    )
    print(json.dumps(comparison, indent=2, sort_keys=True))
