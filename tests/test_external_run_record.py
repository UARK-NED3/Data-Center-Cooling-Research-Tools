"""Tests for external-model adapter run-record validation."""

import json
from pathlib import Path
import tempfile
import unittest

from benchmarks.ocp_tcs_rack_v0_1.adapters.validate_run_record import (
    validate_run_record,
)


ADAPTERS_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "benchmarks"
    / "ocp_tcs_rack_v0_1"
    / "adapters"
)


class ExternalRunRecordTests(unittest.TestCase):
    def test_planned_template_is_a_valid_nonexecution_record(self):
        result = validate_run_record(ADAPTERS_DIRECTORY / "run_record.template.json")

        self.assertEqual(result["execution_state"], "planned")
        self.assertEqual(result["comparison"]["state"], "not_compared")

    def test_completed_record_requires_traceable_input_and_output_hashes(self):
        with (ADAPTERS_DIRECTORY / "run_record.template.json").open(encoding="utf-8") as file:
            record = json.load(file)
        record["execution_state"] = "completed"
        record["model"]["revision"] = "6bafcf54315b59ffe41f30f5da276db48a0e4965"

        with tempfile.TemporaryDirectory() as temporary_directory:
            record_path = Path(temporary_directory) / "completed.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "sha256"):
                validate_run_record(record_path)


if __name__ == "__main__":
    unittest.main()
