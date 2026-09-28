"""Validate benchmark metadata before treating a numerical metric as evidence.

The module intentionally evaluates metadata, not numerical model accuracy. A
matching error metric is meaningful only after the prediction target,
measurement target, inputs, topology, provenance, and execution state have
been declared. The contracts contain no third-party observations.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


CONTRACT_DIRECTORY = Path(__file__).with_name("contracts")

_TARGET_FIELDS = ("quantity", "unit", "time_basis", "control_volume")
_PURPOSES = {"cross_implementation_verification", "local_stress_test", "measured_validation"}
_INPUT_EVIDENCE = {"documented", "proxy", "unknown"}
_LINK_STATUSES = {"documented", "assumed", "unknown"}
_EXECUTION_STATES = {"not_run", "smoke_test", "completed", "completed_local"}
_VALIDATION_STATES = {"verification_only", "not_validated", "validated"}


def _as_mapping(name: str, value: object) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _require_nonempty_string(mapping: Mapping[str, Any], field: str, parent: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{parent}.{field} must be a nonempty string")
    return value


def _validate_target(name: str, value: object) -> Mapping[str, Any]:
    target = _as_mapping(name, value)
    for field in _TARGET_FIELDS:
        _require_nonempty_string(target, field, name)
    return target


def validate_case_contract(contract: Mapping[str, Any]) -> None:
    """Raise ``ValueError`` if a contract is structurally incomplete.

    Structural validity is separate from admissibility. A structurally valid
    contract may still be blocked because it declares incompatible control
    volumes or missing topology evidence.
    """

    _require_nonempty_string(contract, "case_id", "contract")
    purpose = _require_nonempty_string(contract, "purpose", "contract")
    if purpose not in _PURPOSES:
        raise ValueError(f"contract.purpose must be one of {sorted(_PURPOSES)}")

    _validate_target("prediction", contract.get("prediction"))
    measurement = _validate_target("measurement", contract.get("measurement"))
    uncertainty_status = _require_nonempty_string(measurement, "uncertainty_status", "measurement")
    if uncertainty_status not in {"documented", "unknown", "not_applicable_synthetic"}:
        raise ValueError("measurement.uncertainty_status is not recognized")

    inputs = contract.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("contract.inputs must be a nonempty list")
    for index, value in enumerate(inputs):
        item = _as_mapping(f"inputs[{index}]", value)
        _require_nonempty_string(item, "name", f"inputs[{index}]")
        status = _require_nonempty_string(item, "evidence_status", f"inputs[{index}]")
        if status not in _INPUT_EVIDENCE:
            raise ValueError(f"inputs[{index}].evidence_status is not recognized")
        if not isinstance(item.get("target_leakage"), bool):
            raise ValueError(f"inputs[{index}].target_leakage must be boolean")

    links = contract.get("topology_links")
    if not isinstance(links, list) or not links:
        raise ValueError("contract.topology_links must be a nonempty list")
    for index, value in enumerate(links):
        item = _as_mapping(f"topology_links[{index}]", value)
        _require_nonempty_string(item, "name", f"topology_links[{index}]")
        status = _require_nonempty_string(item, "status", f"topology_links[{index}]")
        if status not in _LINK_STATUSES:
            raise ValueError(f"topology_links[{index}].status is not recognized")

    provenance = _as_mapping("provenance", contract.get("provenance"))
    _require_nonempty_string(provenance, "source_id", "provenance")
    _require_nonempty_string(provenance, "rights_status", "provenance")
    if not isinstance(provenance.get("raw_data_in_repository"), bool):
        raise ValueError("provenance.raw_data_in_repository must be boolean")

    run = _as_mapping("run", contract.get("run"))
    execution_state = _require_nonempty_string(run, "execution_state", "run")
    validation_state = _require_nonempty_string(run, "validation_state", "run")
    if execution_state not in _EXECUTION_STATES:
        raise ValueError(f"run.execution_state must be one of {sorted(_EXECUTION_STATES)}")
    if validation_state not in _VALIDATION_STATES:
        raise ValueError(f"run.validation_state must be one of {sorted(_VALIDATION_STATES)}")


def _reason(code: str, severity: str, detail: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "detail": detail}


def _claim_ceiling(purpose: str, validation_state: str) -> str:
    if validation_state == "validated" and purpose == "measured_validation":
        return "validation"
    if validation_state == "verification_only" or purpose == "cross_implementation_verification":
        return "verification"
    return "demonstration"


def evaluate_case_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Return an evidence-based decision for a structurally valid contract.

    ``admit`` permits a benchmark score for the stated claim ceiling.
    ``conditional`` permits diagnostic metrics, but not a benchmark accuracy
    claim. ``block`` permits neither until the listed issue is resolved.
    """

    validate_case_contract(contract)
    prediction = _as_mapping("prediction", contract["prediction"])
    measurement = _as_mapping("measurement", contract["measurement"])
    run = _as_mapping("run", contract["run"])
    reasons: list[dict[str, str]] = []

    for field, code in (
        ("quantity", "quantity_mismatch"),
        ("unit", "unit_mismatch"),
        ("time_basis", "time_basis_mismatch"),
        ("control_volume", "control_volume_mismatch"),
    ):
        if prediction[field] != measurement[field]:
            reasons.append(
                _reason(
                    code,
                    "block",
                    f"prediction.{field}={prediction[field]!r} does not match measurement.{field}={measurement[field]!r}",
                )
            )

    for item in contract["inputs"]:
        input_item = _as_mapping("input", item)
        if input_item["target_leakage"]:
            reasons.append(
                _reason("target_leakage", "block", f"input {input_item['name']!r} contains target information")
            )
        elif input_item["evidence_status"] == "unknown":
            reasons.append(
                _reason("unknown_input_evidence", "block", f"input {input_item['name']!r} lacks provenance")
            )
        elif input_item["evidence_status"] == "proxy":
            reasons.append(
                _reason(
                    "unassigned_input_proxy",
                    "conditional",
                    f"input {input_item['name']!r} is a declared proxy, not a documented assignment",
                )
            )

    for item in contract["topology_links"]:
        link = _as_mapping("topology_link", item)
        if link["status"] != "documented":
            reasons.append(
                _reason(
                    "undocumented_topology",
                    "block",
                    f"topology link {link['name']!r} is {link['status']!r}, not documented",
                )
            )

    if run["execution_state"] in {"not_run", "smoke_test"}:
        reasons.append(
            _reason(
                "incomplete_run",
                "block",
                f"execution state {run['execution_state']!r} cannot support a scored comparison",
            )
        )
    if measurement["uncertainty_status"] == "unknown":
        reasons.append(
            _reason(
                "measurement_uncertainty_unknown",
                "conditional",
                "measurement uncertainty is unavailable for interpretation of an error metric",
            )
        )

    has_block = any(reason["severity"] == "block" for reason in reasons)
    has_conditional = any(reason["severity"] == "conditional" for reason in reasons)
    status = "block" if has_block else "conditional" if has_conditional else "admit"
    return {
        "case_id": contract["case_id"],
        "status": status,
        "benchmark_score_permitted": status == "admit",
        "diagnostic_metric_permitted": not has_block,
        "claim_ceiling": _claim_ceiling(contract["purpose"], run["validation_state"]),
        "reasons": reasons,
    }


def _action_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def build_gap_report(contract: Mapping[str, Any], decision: Mapping[str, Any]) -> dict[str, Any]:
    """Turn each decision reason into the minimum evidence-gathering action."""

    validate_case_contract(contract)
    if decision.get("case_id") != contract["case_id"]:
        raise ValueError("decision.case_id must match contract.case_id")
    actions: list[str] = []
    for reason in decision.get("reasons", []):
        code = _as_mapping("reason", reason).get("code")
        if code == "control_volume_mismatch":
            actions.append("define_common_prediction_and_measurement_control_volume")
        elif code == "quantity_mismatch":
            actions.append("define_common_prediction_and_measurement_quantity")
        elif code == "unit_mismatch":
            actions.append("define_and_apply_traceable_unit_conversion")
        elif code == "time_basis_mismatch":
            actions.append("align_sampling_and_aggregation_time_basis")
        elif code == "target_leakage":
            actions.append("remove_target_or_future_information_from_model_inputs")
        elif code == "unknown_input_evidence":
            actions.append("document_input_source_and_transformation")
        elif code == "unassigned_input_proxy":
            actions.append("document_proxy_to_target_heat_or_load_mapping")
        elif code == "undocumented_topology":
            for link in contract["topology_links"]:
                link_mapping = _as_mapping("topology_link", link)
                if link_mapping["status"] != "documented":
                    actions.append(f"document_{_action_slug(str(link_mapping['name']))}_mapping")
        elif code == "incomplete_run":
            actions.append("complete_measurement_aligned_model_run")
        elif code == "measurement_uncertainty_unknown":
            actions.append("document_measurement_calibration_and_uncertainty")
    return {
        "case_id": contract["case_id"],
        "status": decision.get("status"),
        "minimum_actions": list(dict.fromkeys(actions)),
        "rights_boundary": contract["provenance"]["rights_status"],
    }


def build_run_record(
    contract: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    model: Mapping[str, Any],
    inputs: Mapping[str, str],
    outputs: Mapping[str, str],
    environment: Mapping[str, str],
) -> dict[str, Any]:
    """Build a canonical, hash-addressed local run record from declared metadata."""

    validate_case_contract(contract)
    if decision.get("case_id") != contract["case_id"]:
        raise ValueError("decision.case_id must match contract.case_id")
    _require_nonempty_string(model, "model_id", "model")
    _require_nonempty_string(model, "model_class", "model")
    for collection_name, collection in (("inputs", inputs), ("outputs", outputs), ("environment", environment)):
        if not isinstance(collection, Mapping) or not collection:
            raise ValueError(f"{collection_name} must be a nonempty mapping")
        if not all(isinstance(key, str) and isinstance(value, str) and value for key, value in collection.items()):
            raise ValueError(f"{collection_name} must map nonempty strings to nonempty strings")
    record: dict[str, Any] = {
        "case_id": contract["case_id"],
        "model": dict(model),
        "decision": dict(decision),
        "inputs": dict(sorted(inputs.items())),
        "outputs": dict(sorted(outputs.items())),
        "environment": dict(sorted(environment.items())),
        "provenance": dict(contract["provenance"]),
    }
    serialized = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    record["record_hash"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return record


def load_contract(filename: str) -> dict[str, Any]:
    """Load a bundled contract while preventing paths outside this package."""

    candidate = Path(filename)
    if candidate.name != filename or candidate.suffix != ".json":
        raise ValueError("filename must be a JSON filename without directory components")
    with (CONTRACT_DIRECTORY / candidate).open(encoding="utf-8") as handle:
        contract = json.load(handle)
    if not isinstance(contract, dict):
        raise ValueError("contract JSON root must be an object")
    validate_case_contract(contract)
    return contract
