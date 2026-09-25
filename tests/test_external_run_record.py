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
    def test_simscape_inspection_utility_is_non_destructive(self):
        source = (ADAPTERS_DIRECTORY / "inspect_simscape_liquid_model.m").read_text(
            encoding="utf-8"
        )

        self.assertIn("load_system", source)
        self.assertIn("find_system", source)
        self.assertIn("close_system(modelName, 0)", source)
        self.assertNotIn("sim(", source)
        self.assertNotIn("save_system", source)

    def test_simscape_inspection_filters_paths_relative_to_the_model_root(self):
        source = (ADAPTERS_DIRECTORY / "inspect_simscape_liquid_model.m").read_text(
            encoding="utf-8"
        )

        self.assertIn("relativePaths = extractAfter(blockPaths, strlength(modelName));", source)
        self.assertIn("contains(lower(relativePaths), keywords)", source)

    def test_simscape_inspection_records_one_representative_server_mask(self):
        source = (ADAPTERS_DIRECTORY / "inspect_simscape_liquid_model.m").read_text(
            encoding="utf-8"
        )

        self.assertIn("report.representative_server_unit", source)
        self.assertIn('get_param(blockPath, "MaskValues")', source)

    def test_matlab_steady_state_reference_has_no_hidden_simscape_execution(self):
        source = (ADAPTERS_DIRECTORY / "matlab_steady_state_reference.m").read_text(
            encoding="utf-8"
        )

        self.assertIn("jsondecode", source)
        self.assertIn("tcs_return_temperature_c", source)
        self.assertIn("report.method = strjoin", source)
        self.assertIn("report.use_limit = strjoin", source)
        self.assertNotIn("sim(", source)
        self.assertNotIn("load_system", source)

    def test_matlab_preflight_binds_ver_output_before_reading_product_names(self):
        source = (ADAPTERS_DIRECTORY / "matlab_preflight.m").read_text(
            encoding="utf-8"
        )

        self.assertIn("installedProductInfo = ver;", source)
        self.assertIn("{installedProductInfo.Name}", source)

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
