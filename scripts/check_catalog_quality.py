"""Check generated catalog labels for evidence and validation consistency."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[0]
sys.path.insert(0, str(SCRIPT_DIR))

from build_catalog_assets import (  # noqa: E402
    README,
    GENERATED_DIR,
    VALIDATION_STALE_DAYS,
    execution_readiness,
    has_negated_benchmark_signal,
    has_source_inspection,
    has_hardware_dependency,
    has_negated_dataset_signal,
    has_negated_validation,
    parse_resources,
    review_age_days,
    source_inspected_execution_required,
    validation_queue_resources,
    validation_track,
)


def today_string() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def combined_text(resource) -> str:
    return f"{resource.resource_type} {resource.scale} {resource.notes}".lower()


def has_explicit_metadata(value: str) -> bool:
    return bool(value and value.strip().lower() != "not specified")


def check_resources(resources) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []

    for resource in resources:
        text = combined_text(resource)
        label = f"{resource.name} ({resource.section})"

        if resource.evidence_level == "validated model" and has_negated_validation(text):
            failures.append(f"{label}: negated validation text produced `validated model`.")

        if "dataset" in resource.workflow_tags.split("; ") and has_negated_dataset_signal(text):
            failures.append(f"{label}: negated dataset text produced a `dataset` workflow tag.")

        if "benchmark" in resource.workflow_tags.split("; ") and has_negated_benchmark_signal(text):
            failures.append(f"{label}: negated benchmark text produced a `benchmark` workflow tag.")

        if resource.status == "benchmark" and has_negated_benchmark_signal(text):
            failures.append(f"{label}: negated benchmark text produced benchmark status.")

        if resource.status == "candidate" and resource.evidence_level in {
            "validated model",
            "standard/guideline",
            "commercial workflow",
        }:
            failures.append(
                f"{label}: candidate status conflicts with evidence level `{resource.evidence_level}`."
            )

        if resource.status in {"educational", "prototype", "vendor/material"} and resource.evidence_level == "validated model":
            failures.append(
                f"{label}: low-evidence status conflicts with `validated model` evidence."
            )

        if resource.status == "standard/guideline" and resource.validation_signal != "standard/guideline":
            failures.append(f"{label}: standard/guideline status lacks matching validation signal.")

        if resource.status == "candidate" and resource.review_priority != "high":
            failures.append(f"{label}: candidate entry should be high review priority.")

        if resource.status == "candidate" and resource.validation_signal not in {
            "unreviewed candidate",
            "screened low-confidence candidate",
        }:
            failures.append(
                f"{label}: candidate entry has unexpected validation signal `{resource.validation_signal}`."
            )

        if resource.reviewed_on and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", resource.reviewed_on):
            failures.append(f"{label}: reviewed date `{resource.reviewed_on}` should use YYYY-MM-DD.")

        if resource.evidence_level == "validated model" and not has_explicit_metadata(resource.validation_basis):
            warnings.append(f"{label}: validated-model label has no explicit validation basis.")

        if resource.url and not has_explicit_metadata(resource.validation_basis) and resource.status in {
            "included",
            "workflow",
            "benchmark",
        }:
            warnings.append(f"{label}: no explicit validation basis in catalog note.")

        if resource.url and not has_explicit_metadata(resource.run_status) and resource.review_priority in {"high", "medium"}:
            warnings.append(f"{label}: high/medium-priority entry lacks run status metadata.")

        if resource.url and not has_explicit_metadata(resource.artifact_status) and resource.review_priority in {"high", "medium"}:
            warnings.append(f"{label}: high/medium-priority entry lacks artifact status metadata.")

    return failures, warnings


def write_report(resources, failures: list[str], warnings: list[str], path: Path, generated_on: str) -> None:
    status_counts = Counter(resource.status for resource in resources)
    signal_counts = Counter(resource.validation_signal for resource in resources)
    priority_counts = Counter(resource.review_priority for resource in resources)
    queued = validation_queue_resources(resources)
    readiness_counts = Counter(execution_readiness(resource) for resource in queued)
    track_counts = Counter(validation_track(resource) for resource in queued)
    review_ages = {resource.name: review_age_days(resource, generated_on) for resource in queued}
    explicit_validation_basis = sum(has_explicit_metadata(resource.validation_basis) for resource in resources)
    explicit_run_status = sum(has_explicit_metadata(resource.run_status) for resource in resources)
    explicit_artifact_status = sum(has_explicit_metadata(resource.artifact_status) for resource in resources)
    reviewed_dates = sum(bool(resource.reviewed_on) for resource in resources)
    unlinked_high_priority = sum(
        not resource.url and resource.review_priority == "high" for resource in resources
    )
    stale_queued = sum(
        age is not None and age >= VALIDATION_STALE_DAYS for age in review_ages.values()
    )
    stale_ready = sum(
        review_ages[resource.name] is not None
        and review_ages[resource.name] >= VALIDATION_STALE_DAYS
        and execution_readiness(resource).startswith("ready:")
        for resource in queued
    )
    unlinked_queued = sum(not resource.url for resource in queued)
    source_inspected_queued = sum(has_source_inspection(resource) for resource in queued)
    source_inspected_execution_required_count = sum(
        source_inspected_execution_required(resource) for resource in queued
    )
    hardware_manual_queued = sum(has_hardware_dependency(resource) for resource in queued)

    lines = [
        "# Catalog Quality Report",
        "",
        f"Generated on {generated_on} from `README.md`.",
        "",
        "## Summary",
        "",
        "| Check | Count |",
        "| --- | ---: |",
        f"| Parsed resources | {len(resources)} |",
        f"| Failures | {len(failures)} |",
        f"| Warnings | {len(warnings)} |",
        f"| Candidate entries | {status_counts.get('candidate', 0)} |",
        f"| Unreviewed candidate signals | {signal_counts.get('unreviewed candidate', 0)} |",
        f"| Screened low-confidence candidate signals | {signal_counts.get('screened low-confidence candidate', 0)} |",
        f"| Explicit validation caveats | {signal_counts.get('explicit validation caveat', 0)} |",
        f"| High-priority review entries | {priority_counts.get('high', 0)} |",
        f"| Unlinked high-priority entries | {unlinked_high_priority} |",
        f"| Explicit validation-basis fields | {explicit_validation_basis} |",
        f"| Explicit run-status fields | {explicit_run_status} |",
        f"| Explicit artifact-status fields | {explicit_artifact_status} |",
        f"| Rows with reviewed dates | {reviewed_dates} |",
        f"| Validation-queue resources | {len(queued)} |",
        f"| Ready execution or inspection items | {sum(count for label, count in readiness_counts.items() if label.startswith('ready:'))} |",
        f"| Blocked validation items | {sum(count for label, count in readiness_counts.items() if label.startswith('blocked:'))} |",
        f"| Source-inspected queued resources | {source_inspected_queued} |",
        f"| Source-inspected resources still requiring execution | {source_inspected_execution_required_count} |",
        f"| Hardware/manual validation queued resources | {hardware_manual_queued} |",
        f"| Stale queued resources ({VALIDATION_STALE_DAYS}+ days) | {stale_queued} |",
        f"| Stale ready items ({VALIDATION_STALE_DAYS}+ days) | {stale_ready} |",
        f"| Queued resources without URLs | {unlinked_queued} |",
        f"| Benchmark smoke-test track items | {track_counts.get('benchmark smoke test', 0)} |",
        f"| Hardware-in-loop/manual check track items | {track_counts.get('hardware-in-loop/manual check', 0)} |",
        f"| Local code smoke-test track items | {track_counts.get('local code smoke test', 0)} |",
        "",
        "## Failures",
        "",
    ]
    if failures:
        lines.extend(f"- {failure}" for failure in failures)
    else:
        lines.append("No blocking catalog-quality failures were found.")

    lines.extend(["", "## Warnings", ""])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("No warnings were found.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report checks internal consistency only. It does not prove that any linked tool is physically validated, maintained, or suitable for a specific facility.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=README)
    parser.add_argument("--output", type=Path, default=GENERATED_DIR / "catalog_quality_report.md")
    parser.add_argument("--generated-on", default="")
    args = parser.parse_args()

    resources = parse_resources(args.readme)
    failures, warnings = check_resources(resources)
    generated_on = args.generated_on or today_string()
    write_report(resources, failures, warnings, args.output, generated_on)

    print(f"Checked {len(resources)} resources.")
    print(f"Failures: {len(failures)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Wrote {args.output}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
