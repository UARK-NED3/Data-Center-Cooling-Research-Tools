"""Generate metadata-only admissibility and evidence-gap reports.

Usage:
    python -m benchmarks.evidence_gate_v0_1.generate_reports --output-dir results
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from benchmarks.evidence_gate_v0_1.contracts import (
    CONTRACT_DIRECTORY,
    build_gap_report,
    evaluate_case_contract,
    load_contract,
)


def build_registered_reports() -> list[dict[str, Any]]:
    """Evaluate every bundled contract in deterministic filename order."""

    reports: list[dict[str, Any]] = []
    for path in sorted(CONTRACT_DIRECTORY.glob("*.json")):
        contract = load_contract(path.name)
        decision = evaluate_case_contract(contract)
        reports.append(
            {
                "contract_file": path.name,
                "decision": decision,
                "gap_report": build_gap_report(contract, decision),
            }
        )
    return reports


def render_markdown(reports: list[dict[str, Any]]) -> str:
    """Render a compact human-readable view without raw or derived data."""

    lines = [
        "# Evidence-gated benchmark admissibility summary",
        "",
        "This generated report evaluates metadata contracts only. It contains no third-party observations, "
        "derived third-party results, or model-accuracy claims.",
        "",
        "| Case | Decision | Benchmark score | Claim ceiling | Reasons |",
        "| --- | --- | --- | --- | --- |",
    ]
    for report in reports:
        decision = report["decision"]
        reason_codes = ", ".join(reason["code"] for reason in decision["reasons"]) or "none"
        lines.append(
            "| {case_id} | {status} | {score} | {ceiling} | {reasons} |".format(
                case_id=decision["case_id"],
                status=decision["status"],
                score="permitted" if decision["benchmark_score_permitted"] else "not permitted",
                ceiling=decision["claim_ceiling"],
                reasons=reason_codes,
            )
        )
    lines.extend(["", "## Minimum actions for blocked or conditional cases", ""])
    for report in reports:
        decision = report["decision"]
        gap_report = report["gap_report"]
        lines.append(f"### {decision['case_id']}")
        actions = gap_report["minimum_actions"]
        if actions:
            lines.extend(f"- `{action}`" for action in actions)
        else:
            lines.append("- No additional evidence action is registered for the stated verification scope.")
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    arguments = parser.parse_args()

    reports = build_registered_reports()
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = arguments.output_dir / "admissibility_summary.json"
    markdown_path = arguments.output_dir / "admissibility_summary.md"
    json_path.write_text(json.dumps(reports, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(reports) + "\n", encoding="utf-8")
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")


if __name__ == "__main__":
    main()
