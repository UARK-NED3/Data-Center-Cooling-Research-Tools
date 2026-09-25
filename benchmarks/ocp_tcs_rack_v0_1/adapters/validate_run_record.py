"""Validate traceability requirements for external-model adapter records."""

import json
from pathlib import Path
import re
from typing import Any


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_EXECUTION_STATES = {"planned", "completed", "failed", "not_run"}
_COMPARISON_STATES = {"not_compared", "compared", "not_applicable"}


def _require_mapping(record: dict[str, Any], key: str) -> dict[str, Any]:
    value = record.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _require_string(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(_SHA256_PATTERN.fullmatch(value))


def validate_run_record(record_path: str | Path) -> dict[str, Any]:
    """Load and validate an adapter record without requiring a JSON-schema package.

    A completed external run must bind its output to a particular source revision
    and hashes of the supplied canonical-case input and produced output. Planned
    records intentionally permit those fields to be null because no run occurred.
    """
    with Path(record_path).open(encoding="utf-8") as record_file:
        record = json.load(record_file)

    if record.get("record_type") != "external_model_run":
        raise ValueError("record_type must be external_model_run")
    _require_string(record, "schema_version")
    _require_string(record, "case_id")
    _require_string(record, "adapter_id")

    execution_state = record.get("execution_state")
    if execution_state not in _EXECUTION_STATES:
        raise ValueError(f"execution_state must be one of {sorted(_EXECUTION_STATES)}")

    model = _require_mapping(record, "model")
    _require_string(model, "provider")
    _require_string(model, "source_url")
    environment = _require_mapping(record, "environment")
    _require_string(environment, "runtime")
    _require_string(environment, "runtime_release")
    if not isinstance(environment.get("products"), list):
        raise ValueError("environment.products must be an array")

    input_record = _require_mapping(record, "input")
    output_record = _require_mapping(record, "output")
    comparison = _require_mapping(record, "comparison")
    if comparison.get("state") not in _COMPARISON_STATES:
        raise ValueError(f"comparison.state must be one of {sorted(_COMPARISON_STATES)}")

    if execution_state == "completed":
        revision = model.get("revision")
        if not isinstance(revision, str) or revision in {"", "not_recorded"}:
            raise ValueError("completed records require model.revision")
        if not _is_sha256(input_record.get("case_sha256")):
            raise ValueError("completed records require input.case_sha256 as a SHA-256")
        if not _is_sha256(output_record.get("output_sha256")):
            raise ValueError("completed records require output.output_sha256 as a SHA-256")

    return record
