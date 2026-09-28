"""Behavioral tests for evidence-gated benchmark admission decisions.

All case fixtures are synthetic metadata. They contain no third-party
observations or derived third-party results.
"""

from __future__ import annotations

import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

from benchmarks.evidence_gate_v0_1.contracts import (
    build_gap_report,
    build_run_record,
    evaluate_case_contract,
    load_contract,
)


def matching_contract() -> dict[str, object]:
    return {
        "case_id": "synthetic_matching_case",
        "purpose": "cross_implementation_verification",
        "prediction": {
            "quantity": "coolant_return_temperature",
            "unit": "degC",
            "time_basis": "steady_state",
            "control_volume": "rack_tcs_outlet",
        },
        "measurement": {
            "quantity": "coolant_return_temperature",
            "unit": "degC",
            "time_basis": "steady_state",
            "control_volume": "rack_tcs_outlet",
            "uncertainty_status": "not_applicable_synthetic",
        },
        "inputs": [
            {"name": "rack_heat_load", "evidence_status": "documented", "target_leakage": False}
        ],
        "topology_links": [
            {"name": "rack_heat_to_tcs_outlet", "status": "documented"}
        ],
        "provenance": {
            "source_id": "ned3_synthetic_case",
            "rights_status": "ned3_authored",
            "raw_data_in_repository": False,
        },
        "run": {"execution_state": "completed", "validation_state": "verification_only"},
    }


class EvidenceGateTests(unittest.TestCase):
    def test_matching_completed_contract_is_admitted_for_verification(self):
        decision = evaluate_case_contract(matching_contract())

        self.assertEqual(decision["status"], "admit")
        self.assertTrue(decision["benchmark_score_permitted"])
        self.assertEqual(decision["claim_ceiling"], "verification")
        self.assertEqual(decision["reasons"], [])

    def test_control_volume_mismatch_blocks_a_numerical_score(self):
        contract = matching_contract()
        contract["measurement"]["control_volume"] = "facility_water_loop"  # type: ignore[index]

        decision = evaluate_case_contract(contract)

        self.assertEqual(decision["status"], "block")
        self.assertFalse(decision["benchmark_score_permitted"])
        self.assertIn("control_volume_mismatch", {reason["code"] for reason in decision["reasons"]})

    def test_unassigned_power_proxy_is_conditional_not_validation(self):
        contract = matching_contract()
        contract["purpose"] = "local_stress_test"
        contract["inputs"] = [
            {"name": "facility_power_proxy", "evidence_status": "proxy", "target_leakage": False}
        ]
        contract["run"]["validation_state"] = "not_validated"  # type: ignore[index]

        decision = evaluate_case_contract(contract)

        self.assertEqual(decision["status"], "conditional")
        self.assertFalse(decision["benchmark_score_permitted"])
        self.assertTrue(decision["diagnostic_metric_permitted"])
        self.assertIn("unassigned_input_proxy", {reason["code"] for reason in decision["reasons"]})

    def test_target_leakage_blocks_the_comparison(self):
        contract = matching_contract()
        contract["inputs"] = [
            {"name": "future_return_temperature", "evidence_status": "documented", "target_leakage": True}
        ]

        decision = evaluate_case_contract(contract)

        self.assertEqual(decision["status"], "block")
        self.assertIn("target_leakage", {reason["code"] for reason in decision["reasons"]})

    def test_gap_report_turns_a_block_into_a_minimum_evidence_request(self):
        contract = matching_contract()
        contract["topology_links"] = [{"name": "power_to_panel", "status": "unknown"}]

        report = build_gap_report(contract, evaluate_case_contract(contract))

        self.assertEqual(report["status"], "block")
        self.assertIn("document_power_to_panel_mapping", report["minimum_actions"])

    def test_run_record_has_a_deterministic_hash_and_preserves_rights_boundary(self):
        contract = matching_contract()
        decision = evaluate_case_contract(contract)
        record = build_run_record(
            contract,
            decision,
            model={"model_id": "analytical_reference", "model_class": "analytical"},
            inputs={"case.json": "abc123"},
            outputs={"result.json": "def456"},
            environment={"python": "3.10"},
        )

        self.assertEqual(record["record_hash"], build_run_record(
            contract,
            decision,
            model={"model_id": "analytical_reference", "model_class": "analytical"},
            inputs={"case.json": "abc123"},
            outputs={"result.json": "def456"},
            environment={"python": "3.10"},
        )["record_hash"])
        self.assertFalse(record["provenance"]["raw_data_in_repository"])

    def test_registered_contracts_preserve_their_declared_claim_boundaries(self):
        expected = {
            "ocp_tcs_rack_v0_1.json": "admit",
            "m100_rdhx_q101_stress_test.json": "conditional",
            "retrofit_openfoam_smoke_test.json": "block",
        }
        for filename, expected_status in expected.items():
            with self.subTest(filename=filename):
                contract = load_contract(filename)
                self.assertEqual(evaluate_case_contract(contract)["status"], expected_status)

    def test_module_command_writes_metadata_only_decisions_and_gap_reports(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_directory = Path(temporary_directory) / "generated"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "benchmarks.evidence_gate_v0_1.generate_reports",
                    "--output-dir",
                    str(output_directory),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("wrote", completed.stdout)
            summary = (output_directory / "admissibility_summary.json").read_text(encoding="utf-8")
            self.assertIn('"m100_rdhx_q101_stress_test"', summary)
            self.assertIn('"conditional"', summary)
            self.assertTrue((output_directory / "admissibility_summary.md").is_file())


if __name__ == "__main__":
    unittest.main()
