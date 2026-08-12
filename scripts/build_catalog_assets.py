"""Build generated catalog tables and figures from README.md.

The repository intentionally keeps the main catalog human-readable in README.md.
This script parses those Markdown tables and emits lightweight CSV/Markdown/SVG
artifacts that help readers see coverage and trends without maintaining a
second source of truth.
"""

from __future__ import annotations

import argparse
import csv
import html
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
GENERATED_DIR = ROOT / "docs" / "generated"
ASSETS_DIR = ROOT / "docs" / "assets"

CATALOG_SECTIONS = {
    "Fundamental Thermal-Fluid Mechanisms",
    "Chip, Package, And Server Cooling",
    "Rack, CDU, And Liquid Loop Systems",
    "Room, Building, And Campus Modeling",
    "AI, Control, Digital Twins, And Operations",
    "System Metrics, Standards, And Accounting",
    "Sustainability: Life Cycle, Water, Carbon, And Heat Reuse",
    "Skills, Agents, And Plugin Collections",
}

SECTION_ORDER = [
    "Fundamental Thermal-Fluid Mechanisms",
    "Chip, Package, And Server Cooling",
    "Rack, CDU, And Liquid Loop Systems",
    "Room, Building, And Campus Modeling",
    "AI, Control, Digital Twins, And Operations",
    "System Metrics, Standards, And Accounting",
    "Sustainability: Life Cycle, Water, Carbon, And Heat Reuse",
    "Skills, Agents, And Plugin Collections",
]

STATUS_ORDER = [
    "standard/guideline",
    "commercial",
    "included",
    "workflow",
    "benchmark",
    "paper artifact",
    "educational",
    "prototype",
    "vendor/material",
    "candidate",
]

VALIDATION_SIGNAL_ORDER = [
    "standard/guideline",
    "explicit validation claim",
    "reported benchmark",
    "paper artifact",
    "documentation-only basis",
    "commercial workflow caveat",
    "vendor evidence caveat",
    "educational/prototype caveat",
    "explicit validation caveat",
    "screened low-confidence candidate",
    "unreviewed candidate",
    "not specified",
]

VALIDATION_TRACK_ORDER = [
    "source identification",
    "benchmark smoke test",
    "paper artifact matching",
    "semantic validation",
    "hardware-in-loop/manual check",
    "local code smoke test",
    "notebook/data review",
    "educational/prototype scope check",
    "vendor evidence follow-up",
    "independent validation search",
    "documented example/manual check",
]

VALIDATION_STALE_DAYS = 7
VALIDATION_NEXT_ACTION_LIMIT = 8

METADATA_LABELS = {
    "validation basis": "validation_basis",
    "run status": "run_status",
    "artifact status": "artifact_status",
    "reviewed": "reviewed_on",
}

NEGATED_VALIDATION_PATTERNS = [
    r"\bnot\s+(?:a\s+|an\s+)?(?:universal\s+)?validated\b",
    r"\bnot\s+(?:a\s+|an\s+)?(?:[\w-]+\s+){0,4}validated\b",
    r"\bnot\s+(?:a\s+|an\s+)?(?:[\w-]+-){0,4}validated\b",
    r"\bnot\s+validated\b",
    r"\bno\s+(?:independent\s+)?validation\b",
    r"\bwithout\s+(?:independent\s+)?validation\b",
    r"\bneeds?\s+(?:deeper\s+|detailed\s+)?validation\b",
    r"\bpending\s+validation\b",
    r"\bpending\s+(?:detailed\s+)?(?:model\s+)?review\b",
    r"\bvalidation\s+caveats?\b",
    r"\brather\s+than\s+(?:a\s+|an\s+)?(?:universal\s+)?validated\b",
]

EXPLICIT_VALIDATION_PATTERNS = [
    r"\bvalidated\s+through\b",
    r"\bvalidated\s+against\b",
    r"\bvalidation\s+data\b",
    r"\bvalidated\s+model\b",
    r"\bcalibrated\b",
    r"\bashrae\s+guideline\s+14\b",
]

NEGATED_DATASET_PATTERNS = [
    r"\bnot\s+(?:a\s+|an\s+)?(?:public\s+)?(?:performance\s+)?datasets?\b",
    r"\bnot\s+as\s+(?:a\s+|an\s+)?(?:public\s+)?(?:performance\s+)?datasets?\b",
    r"\bnot\s+(?:a\s+|an\s+)?(?:[\w-]+\s+){0,4}datasets?\b",
    r"\bnot\s+as\s+(?:a\s+|an\s+)?(?:[\w-]+\s+){0,4}datasets?\b",
    r"\bno\s+(?:public\s+|reusable\s+)?(?:validation\s+|performance\s+)?(?:data|datasets?)\b",
    r"\bno\b.{0,120}\b(?:public|reusable|facility|operational|validation|performance)\b.{0,40}\b(?:data|datasets?)\b",
    r"\bwithout\s+(?:public\s+|reusable\s+)?(?:validation\s+|performance\s+)?(?:data|datasets?)\b",
    r"\bdid\s+not\s+surface\b.{0,120}\bdatasets?\b",
    r"\bdid\s+not\s+find\b.{0,120}\bdatasets?\b",
]

NEGATED_BENCHMARK_PATTERNS = [
    r"\bno\b.{0,80}\bbenchmark\b",
    r"\bwithout\b.{0,80}\bbenchmark\b",
    r"\bnot\s+(?:a\s+|an\s+)?(?:reproducible\s+)?benchmark\b",
    r"\bbenchmark\b.{0,80}\bnot\s+(?:recorded|available|visible|confirmed)\b",
]


def has_negated_validation(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in NEGATED_VALIDATION_PATTERNS)


def has_explicit_validation_signal(text: str) -> bool:
    if has_negated_validation(text):
        return False
    return any(re.search(pattern, text) for pattern in EXPLICIT_VALIDATION_PATTERNS)


def has_negated_dataset_signal(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in NEGATED_DATASET_PATTERNS)


def has_negated_benchmark_signal(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in NEGATED_BENCHMARK_PATTERNS)


@dataclass(frozen=True)
class Resource:
    name: str
    url: str
    section: str
    resource_type: str
    scale: str
    notes: str
    status: str
    evidence_level: str
    validation_basis: str
    run_status: str
    artifact_status: str
    reviewed_on: str
    validation_signal: str
    review_priority: str
    workflow_tags: str


def today_string() -> str:
    return os.environ.get("CATALOG_DATE") or datetime.now(timezone.utc).date().isoformat()


def split_markdown_row(line: str) -> list[str]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return cells


def is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def parse_link(cell: str) -> tuple[str, str]:
    match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", cell)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return re.sub(r"\s+", " ", cell).strip(), ""


def extract_note_metadata(notes: str) -> dict[str, str]:
    metadata = {
        "validation_basis": "not specified",
        "run_status": "not specified",
        "artifact_status": "not specified",
        "reviewed_on": "",
    }
    pattern = re.compile(
        r"(?i)\b(validation basis|run status|artifact status|reviewed):\s*(.*?)(?=;\s*(?:validation basis|run status|artifact status|reviewed):|$)"
    )
    for match in pattern.finditer(notes):
        key = METADATA_LABELS[match.group(1).lower()]
        metadata[key] = match.group(2).strip().rstrip(".")
    return metadata


def infer_status(resource_type: str, notes: str) -> str:
    text = f"{resource_type} {notes}".lower()
    if "standard" in text or "guideline" in text or "specification" in text:
        return "standard/guideline"
    if "commercial" in text:
        return "commercial"
    if (
        "low-confidence" in text
        or "newly surfaced candidate" in text
        or "keep as a candidate" in text
        or "needs validation review" in text
        or "needs deeper validation review" in text
        or "pending detailed model review" in text
    ):
        return "candidate"
    if "benchmark" in text and not has_negated_benchmark_signal(text):
        return "benchmark"
    if "paper artifact" in text or "peer-reviewed" in text:
        return "paper artifact"
    if "educational" in text:
        return "educational"
    if "prototype" in text:
        return "prototype"
    if "vendor/product" in text or "vendor material" in text or "product material" in text:
        return "vendor/material"
    if "candidate" in text:
        return "candidate"
    if "workflow" in text:
        return "workflow"
    return "included"


def infer_evidence_level(resource_type: str, notes: str) -> str:
    text = f"{resource_type} {notes}".lower()
    checks = [
        ("standard", "standard/guideline"),
        ("guideline", "standard/guideline"),
        ("specification", "standard/guideline"),
        ("candidate", "candidate"),
        ("low-confidence", "candidate"),
        ("needs validation", "candidate"),
        ("pending detailed model review", "candidate"),
        ("validated", "validated model"),
        ("peer-reviewed", "peer-reviewed artifact"),
        ("paper artifact", "paper artifact"),
        ("benchmark", "benchmark"),
        ("commercial", "commercial workflow"),
        ("vendor", "vendor/product material"),
        ("educational", "educational example"),
        ("prototype", "prototype"),
        ("candidate", "candidate"),
        ("workflow", "workflow"),
        ("open-source", "open-source implementation"),
    ]
    for token, label in checks:
        if label == "validated model" and has_negated_validation(text):
            continue
        if label == "benchmark" and has_negated_benchmark_signal(text):
            continue
        if token in text:
            return label
    return "curated resource"


def infer_validation_signal(
    resource_type: str,
    notes: str,
    status: str,
    evidence_level: str,
    validation_basis: str = "not specified",
) -> str:
    text = f"{resource_type} {notes}".lower()
    basis = validation_basis.lower()
    if status == "standard/guideline":
        return "standard/guideline"
    if status == "candidate":
        if basis and basis != "not specified" and not any(
            token in basis for token in ["candidate", "needs review", "unreviewed", "unknown"]
        ):
            return "screened low-confidence candidate"
        return "unreviewed candidate"
    if basis and basis != "not specified":
        if any(token in basis for token in ["standard", "guideline", "specification", "metric guidance"]):
            return "standard/guideline"
        if any(token in basis for token in ["candidate", "needs review", "unreviewed"]):
            return "unreviewed candidate"
        if any(token in basis for token in ["no independent", "none found", "not independently checked"]):
            return "explicit validation caveat"
        if any(token in basis for token in ["operational data", "measured data", "validated", "calibrated"]):
            return "explicit validation claim"
        if "benchmark" in basis:
            return "reported benchmark"
        if "paper" in basis:
            return "paper artifact"
        if "vendor" in basis:
            return "vendor evidence caveat"
        if any(token in basis for token in ["educational", "prototype"]):
            return "educational/prototype caveat"
        if any(token in basis for token in ["documentation", "source", "library", "lab workflow", "protocol"]):
            return "documentation-only basis"
    if has_negated_validation(text):
        return "explicit validation caveat"
    if evidence_level == "validated model" or has_explicit_validation_signal(text):
        return "explicit validation claim"
    if status in {"educational", "prototype"}:
        return "educational/prototype caveat"
    if status == "vendor/material":
        return "vendor evidence caveat"
    if status == "commercial":
        return "commercial workflow caveat"
    if status == "paper artifact":
        return "paper artifact"
    return "not specified"


def infer_review_priority(status: str, validation_signal: str) -> str:
    if status == "candidate":
        return "high"
    if validation_signal in {
        "explicit validation caveat",
        "unreviewed candidate",
        "vendor evidence caveat",
        "educational/prototype caveat",
        "screened low-confidence candidate",
    }:
        return "high"
    if status in {"standard/guideline", "benchmark", "paper artifact"}:
        return "medium"
    if validation_signal in {"reported benchmark", "documentation-only basis"}:
        return "medium"
    if status == "commercial":
        return "medium"
    return "normal"


def infer_workflow_tags(resource_type: str, notes: str) -> str:
    text = f"{resource_type} {notes}".lower()
    tags = []
    keyword_tags = [
        ("simulation", "simulation"),
        ("energyplus", "simulation"),
        ("model", "modeling"),
        ("cfd", "CFD"),
        ("control", "control"),
        ("rl", "control"),
        ("reinforcement", "control"),
        ("monitor", "monitoring"),
        ("telemetry", "monitoring"),
        ("optimization", "optimization"),
        ("sizing", "design"),
        ("design", "design"),
        ("test", "testing"),
        ("experiment", "testing"),
        ("account", "accounting"),
        ("pue", "accounting"),
        ("wue", "accounting"),
        ("ere", "accounting"),
        ("heat reuse", "heat reuse"),
        ("dataset", "dataset"),
        ("trace", "dataset"),
        ("benchmark", "benchmark"),
        ("planning", "planning"),
        ("workflow", "workflow"),
        ("standard", "standard"),
        ("ontology", "semantic metadata"),
        ("shacl", "semantic metadata"),
        ("brick", "semantic metadata"),
        ("semantic", "semantic metadata"),
    ]
    for keyword, tag in keyword_tags:
        if tag == "dataset" and has_negated_dataset_signal(text):
            continue
        if tag == "benchmark" and has_negated_benchmark_signal(text):
            continue
        if keyword in text and tag not in tags:
            tags.append(tag)
    return "; ".join(tags) if tags else "reference"


def validation_queue_resources(resources: list[Resource]) -> list[Resource]:
    queued = [
        resource
        for resource in resources
        if not (resource.status == "standard/guideline" and resource.run_status == "not applicable")
        and (
            resource.review_priority == "high"
            or resource.status in {"benchmark", "paper artifact"}
            or source_inspected_execution_required(resource)
            or (
                resource.run_status == "not run in catalog review"
                and resource.validation_signal
                in {
                    "documentation-only basis",
                    "reported benchmark",
                    "paper artifact",
                    "explicit validation caveat",
                }
            )
        )
    ]
    priority_order = {"high": 0, "medium": 1, "normal": 2}
    status_order = {status: idx for idx, status in enumerate(STATUS_ORDER)}
    signal_order = {signal: idx for idx, signal in enumerate(VALIDATION_SIGNAL_ORDER)}
    return sorted(
        queued,
        key=lambda resource: (
            priority_order.get(resource.review_priority, 9),
            status_order.get(resource.status, 99),
            signal_order.get(resource.validation_signal, 99),
            resource.section,
            resource.name.lower(),
        ),
    )


def validation_action(resource: Resource) -> str:
    if not resource.url:
        return "Find and record the canonical source URL before deciding whether to screen, promote, or remove this entry."
    if "no runnable artifact" in resource.run_status.lower() or "no runnable artifact" in resource.artifact_status.lower():
        return "Record the missing runnable entry point, demote or retain as blocked, and revisit only if source files or examples appear."
    if has_hardware_dependency(resource):
        if has_source_inspection(resource):
            return "Keep the hardware/prototype caveat; record bench, compile/upload, sensor-calibration, or field-test evidence before claiming validation."
        return "Inspect hardware requirements, safety limits, sensor calibration, and code path before deciding whether hardware-in-loop validation is feasible."
    if has_source_inspection(resource) and resource.status in {"educational", "prototype"}:
        return "Keep the educational/prototype caveat; run locally only if executable output evidence is needed."
    text = f"{resource.resource_type} {resource.notes}".lower()
    if any(token in text for token in ["ontology", "shacl", "brick schema", "semantic"]):
        return "Run the documented SHACL or ontology validation command on a minimal instance graph and record constraints checked."
    if resource.status == "candidate":
        if resource.validation_signal == "screened low-confidence candidate":
            return "Run or inspect enough of the artifact to either promote, demote, or retain a dated low-confidence caveat."
        return "Screen README, examples, tests, physical assumptions, and data provenance before promoting."
    if resource.status == "benchmark" or resource.validation_signal == "reported benchmark":
        return "Run the smallest documented benchmark and record observations, actions, constraints, rewards, and output metrics."
    if resource.status == "paper artifact" or resource.validation_signal == "paper artifact":
        return "Match code or data to the cited paper, run a minimal reproduction, and record reproducibility limits."
    if resource.status in {"educational", "prototype"}:
        return "Confirm teaching/prototype scope, identify missing validation, and avoid engineering-evidence language."
    if resource.status == "vendor/material" or resource.validation_signal == "vendor evidence caveat":
        return "Locate datasheets, test methods, or independent reports before citing performance claims."
    if resource.validation_signal == "explicit validation caveat":
        return "Find independent validation evidence or keep the row explicitly marked as unvalidated."
    if resource.validation_signal == "documentation-only basis":
        return "Run a documented example if feasible; otherwise mark why execution is unavailable."
    return "Inspect source documentation and record the next reproducible validation step."


def has_public_code_artifact(resource: Resource) -> bool:
    artifact = resource.artifact_status.lower()
    return "public" in artifact and "code" in artifact


def has_source_inspection(resource: Resource) -> bool:
    run_status = resource.run_status.lower()
    return "source inspected" in run_status or "source-inspected" in run_status


def is_validation_not_applicable(resource: Resource) -> bool:
    text = f"{resource.run_status} {resource.notes}".lower()
    return (
        "thermal validation not applicable" in text
        or "thermal-validation not applicable" in text
        or "thermal validation is not applicable" in text
        or "validation not applicable" in text
    )


def has_hardware_dependency(resource: Resource) -> bool:
    text = f"{resource.resource_type} {resource.scale} {resource.notes}".lower()
    hardware_patterns = [
        r"\bhardware prototype\b",
        r"\bhardware-in-loop\b",
        r"\besp8266\b",
        r"\besp32\b",
        r"\barduino\b",
        r"\bnodemcu\b",
        r"\brelays?\b",
        r"\bsensors?\b",
        r"\boled\b",
        r"\bbuzzer\b",
        r"\bmicrocontroller\b",
    ]
    return any(re.search(pattern, text) for pattern in hardware_patterns)


def validation_track(resource: Resource) -> str:
    if not resource.url:
        return "source identification"
    text = f"{resource.resource_type} {resource.scale} {resource.notes}".lower()
    if resource.status == "benchmark" or resource.validation_signal == "reported benchmark":
        return "benchmark smoke test"
    if resource.status == "paper artifact" or resource.validation_signal == "paper artifact":
        return "paper artifact matching"
    if any(token in text for token in ["ontology", "shacl", "brick schema", "semantic"]):
        return "semantic validation"
    if resource.status == "vendor/material" or resource.validation_signal == "vendor evidence caveat":
        return "vendor evidence follow-up"
    if has_hardware_dependency(resource):
        return "hardware-in-loop/manual check"
    if resource.status in {"educational", "prototype"} or resource.validation_signal == "educational/prototype caveat":
        return "educational/prototype scope check"
    if resource.validation_signal == "explicit validation caveat":
        return "independent validation search"
    if "notebook" in text or "colab" in text or "weather files" in text:
        return "notebook/data review"
    if has_public_code_artifact(resource):
        return "local code smoke test"
    return "documented example/manual check"


def execution_readiness(resource: Resource) -> str:
    if not resource.url:
        return "blocked: source missing"
    if is_validation_not_applicable(resource):
        return "manual: thermal validation not applicable"
    artifact = resource.artifact_status.lower()
    run_status = resource.run_status.lower()
    text = f"{resource.resource_type} {resource.scale} {resource.notes}".lower()
    track = validation_track(resource)
    if "no runnable artifact" in artifact or "no runnable artifact" in run_status:
        return "blocked: no runnable artifact found"
    if resource.status == "vendor/material" or resource.validation_signal == "vendor evidence caveat":
        return "blocked: needs datasheet or test method"
    if has_hardware_dependency(resource):
        if has_source_inspection(resource):
            return "manual: source-inspected hardware validation not run"
        return "manual: hardware-in-loop validation required"
    if has_source_inspection(resource):
        if track == "benchmark smoke test":
            return "ready: benchmark execution still required"
        if track == "paper artifact matching":
            return "ready: artifact reproduction still required"
        if track == "semantic validation":
            return "ready: semantic validation command"
        if track == "local code smoke test":
            return "ready: source-inspected smoke test still required"
        return "manual: source-inspected, local execution optional"
    if has_public_code_artifact(resource) and "not run" in run_status:
        if "docker" in text or "compose" in text:
            return "ready: container or service smoke test"
        if "test" in text or "tests" in text:
            return "ready: test-suite or example smoke test"
        if "notebook" in text or "colab" in text:
            return "ready: notebook review or execution"
        return "ready: local code smoke test"
    if "public ontology" in artifact or "shacl" in text:
        return "ready: semantic validation command"
    if "weather files" in artifact or "public data" in artifact:
        return "ready: data provenance and notebook check"
    if "public document" in artifact or "documentation only" in artifact:
        return "manual: document or standard review"
    if resource.status == "candidate":
        return "manual: candidate source inspection"
    return "manual: evidence review"


def source_inspected_execution_required(resource: Resource) -> bool:
    return (
        has_source_inspection(resource)
        and not is_validation_not_applicable(resource)
        and execution_readiness(resource).startswith("ready:")
    )


def closure_evidence(resource: Resource) -> str:
    track = validation_track(resource)
    if execution_readiness(resource) == "blocked: no runnable artifact found":
        return "Dated missing-entry or no-runnable-artifact evidence plus demotion, reclassification, or retained-blocked decision."
    if track == "source identification":
        return "Canonical URL plus include, demote, or remove decision."
    if track == "benchmark smoke test":
        return "Command, version/config, seed if used, output metrics, and failure notes."
    if track == "paper artifact matching":
        return "Paper-to-code/data mapping, minimal reproduction command, and mismatch notes."
    if track == "semantic validation":
        return "Validation command, shapes or instance graph, pass/fail result, and constraints checked."
    if track == "hardware-in-loop/manual check":
        if has_source_inspection(resource):
            return "Source inspection plus hardware bill of materials; bench test, compile/upload result, sensor calibration, relay safety, or field trial still needed."
        return "Hardware bill of materials, compile/upload or bench-test result, sensor/actuator checks, and safety limits."
    if track == "vendor evidence follow-up":
        return "Datasheet, test method, independent report, or explicit vendor-only caveat."
    if track == "educational/prototype scope check":
        if has_source_inspection(resource):
            return "Source-inspection evidence recorded; local run remains optional for deeper reproducibility."
        return "Small run or code inspection showing assumptions, limits, and teaching/prototype scope."
    if track == "independent validation search":
        return "Independent validation source or retained unvalidated label with dated search note."
    if track == "notebook/data review":
        return "Notebook/data provenance check, assumptions, units, and reproducible output note."
    if track == "local code smoke test":
        return "Smoke-test command, environment, observed output, and unresolved errors."
    return "Documented example result or reason execution remains unavailable."


def validation_probe(resource: Resource) -> str:
    track = validation_track(resource)
    readiness = execution_readiness(resource)
    text = f"{resource.resource_type} {resource.scale} {resource.notes}".lower()
    if track == "source identification":
        return "Search for a canonical repository, paper, standard, or vendor page before any catalog promotion."
    if track == "benchmark smoke test":
        return "Run the smallest documented reset/step, training, evaluation, or notebook example; capture config, seed, constraint status, reward or energy metrics, and errors."
    if track == "paper artifact matching":
        return "Map the cited paper claim to repository files, then run the smallest notebook or script path against included, cited, or synthetic data."
    if track == "semantic validation":
        return "Run the documented ontology or SHACL validation command on the smallest included graph and record constraints checked."
    if track == "hardware-in-loop/manual check":
        return "Compile or upload firmware, run a simulator-backed control path if provided, or record hardware bill of materials, calibration, electrical safety, and bench conditions."
    if track == "vendor evidence follow-up":
        return "Collect datasheets, qualification methods, public test data, or independent reports; otherwise keep the entry as vendor context only."
    if track == "educational/prototype scope check":
        if has_source_inspection(resource):
            return "No default execution required for scope closure; run only if the row will be used as reproducible evidence."
        return "Inspect files or run the smallest demo to identify equations, inputs, assumptions, outputs, and validation gaps."
    if track == "independent validation search":
        return "Search papers, issues, releases, and third-party uses for independent validation; retain an unvalidated label if none is found."
    if track == "notebook/data review":
        return "Open the notebook or data files, check provenance and units, and run a minimal cell path when dependencies are available."
    if track == "local code smoke test":
        if "docker" in text or "compose" in text or "container" in text:
            return "Start the documented container or compose stack, capture service health, endpoint response, logs, and a sample metric or UI/API check."
        if "test" in text or "tests" in text:
            return "Install in an isolated environment and run the smallest documented test, example, or quickstart command."
        return "Install documented dependencies and run the smallest CLI, script, notebook, or import check that exercises the advertised workflow."
    if readiness.startswith("blocked:"):
        return "Record the blocking condition with dated evidence and demote, reclassify, or leave blocked until the artifact changes."
    return "Run a documented example if one exists; otherwise record why execution is unavailable or not applicable."


def non_closure_condition(resource: Resource) -> str:
    track = validation_track(resource)
    if track == "benchmark smoke test":
        return "README/source inspection alone; a benchmark needs command, config, and metrics."
    if track == "paper artifact matching":
        return "Citation or paper title alone; artifact-to-result mapping must be checked."
    if track == "semantic validation":
        return "Ontology file presence alone; at least one validation command or graph check is needed."
    if track == "hardware-in-loop/manual check":
        return "Software review alone when sensors, relays, firmware, or physical actuation are part of the claim."
    if track == "vendor evidence follow-up":
        return "Marketing copy without datasheet, test method, or explicit vendor-only caveat."
    if track == "local code smoke test":
        return "A public repository link alone; capture an import, service, test, or example result."
    if track == "notebook/data review":
        return "Notebook existence alone; record data provenance, units, and executable status."
    if track == "educational/prototype scope check":
        return "Engineering-evidence language; keep teaching/prototype caveats unless reproduced and validated."
    if track == "independent validation search":
        return "Uncited claims of validation; record the search result or keep the unvalidated label."
    if track == "source identification":
        return "A name-only row without a canonical source URL."
    return "Undated judgment without source, command, output, or non-applicability reason."


def validation_reason(resource: Resource) -> str:
    reasons = []
    if not resource.url:
        reasons.append("no source URL recorded")
    if resource.review_priority == "high":
        reasons.append("high priority")
    if resource.status == "candidate":
        reasons.append("candidate")
    if resource.validation_signal in {
        "explicit validation caveat",
        "unreviewed candidate",
        "screened low-confidence candidate",
        "vendor evidence caveat",
        "educational/prototype caveat",
    }:
        reasons.append(resource.validation_signal)
    if resource.run_status == "not run in catalog review":
        reasons.append("not run")
    if has_source_inspection(resource):
        reasons.append("source inspected")
    if has_public_code_artifact(resource):
        reasons.append("public code available")
    return "; ".join(dict.fromkeys(reasons))


def parse_resources(readme_path: Path) -> list[Resource]:
    resources: list[Resource] = []
    current_section = ""

    for line in readme_path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current_section = heading.group(1)
            continue
        if current_section not in CATALOG_SECTIONS:
            continue
        if not line.strip().startswith("|"):
            continue

        cells = split_markdown_row(line)
        if len(cells) < 4 or is_separator_row(cells):
            continue
        if cells[0].lower() in {"resource", "source"}:
            continue

        name, url = parse_link(cells[0])
        resource_type = cells[1]
        scale = cells[2]
        notes = cells[3]
        metadata = extract_note_metadata(notes)
        status = infer_status(resource_type, notes)
        evidence_level = infer_evidence_level(resource_type, notes)
        validation_signal = infer_validation_signal(
            resource_type,
            notes,
            status,
            evidence_level,
            metadata["validation_basis"],
        )
        resources.append(
            Resource(
                name=name,
                url=url,
                section=current_section,
                resource_type=resource_type,
                scale=scale,
                notes=notes,
                status=status,
                evidence_level=evidence_level,
                validation_basis=metadata["validation_basis"],
                run_status=metadata["run_status"],
                artifact_status=metadata["artifact_status"],
                reviewed_on=metadata["reviewed_on"],
                validation_signal=validation_signal,
                review_priority=infer_review_priority(status, validation_signal),
                workflow_tags=infer_workflow_tags(resource_type, notes),
            )
        )
    return resources


def ordered_counter(counter: Counter[str], preferred_order: Iterable[str] = ()) -> list[tuple[str, int]]:
    preferred = [(label, counter[label]) for label in preferred_order if counter.get(label)]
    remaining = sorted(
        ((label, value) for label, value in counter.items() if label not in set(preferred_order)),
        key=lambda item: (-item[1], item[0].lower()),
    )
    return preferred + remaining


def write_csv(resources: list[Resource], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "name",
        "url",
        "section",
        "resource_type",
        "scale",
        "status",
        "evidence_level",
        "validation_basis",
        "run_status",
        "artifact_status",
        "reviewed_on",
        "validation_signal",
        "review_priority",
        "workflow_tags",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for resource in resources:
            writer.writerow({field: getattr(resource, field) for field in fields})


def svg_text(text: str) -> str:
    return html.escape(text, quote=False)


def write_bar_svg(title: str, rows: list[tuple[str, int]], path: Path, color: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 980
    row_height = 34
    top = 72
    left = 330
    right = 40
    height = top + row_height * max(len(rows), 1) + 42
    max_value = max((value for _, value in rows), default=1)
    bar_width = width - left - right - 70

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="32" y="38" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#1f2937">{svg_text(title)}</text>',
        '<text x="32" y="60" font-family="Arial, sans-serif" font-size="13" fill="#6b7280">Generated from README.md resource tables</text>',
    ]
    for idx, (label, value) in enumerate(rows):
        y = top + idx * row_height
        width_px = int((value / max_value) * bar_width)
        parts.extend(
            [
                f'<text x="32" y="{y + 20}" font-family="Arial, sans-serif" font-size="14" fill="#374151">{svg_text(label)}</text>',
                f'<rect x="{left}" y="{y + 5}" width="{bar_width}" height="18" rx="3" fill="#e5e7eb"/>',
                f'<rect x="{left}" y="{y + 5}" width="{width_px}" height="18" rx="3" fill="{color}"/>',
                f'<text x="{left + bar_width + 18}" y="{y + 20}" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#111827">{value}</text>',
            ]
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_heatmap_svg(resources: list[Resource], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = STATUS_ORDER
    matrix: dict[tuple[str, str], int] = defaultdict(int)
    for resource in resources:
        matrix[(resource.section, resource.status)] += 1

    cell = 58
    label_width = 280
    top = 122
    width = label_width + len(columns) * cell + 40
    height = top + len(SECTION_ORDER) * cell + 50
    max_value = max(matrix.values(), default=1)

    def fill(value: int) -> str:
        if value == 0:
            return "#f3f4f6"
        intensity = 0.25 + 0.75 * (value / max_value)
        # Blue-green ramp with constant high readability.
        r = int(224 - 136 * intensity)
        g = int(242 - 92 * intensity)
        b = int(241 - 89 * intensity)
        return f"#{r:02x}{g:02x}{b:02x}"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="32" y="38" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#1f2937">Catalog Evidence Map</text>',
        '<text x="32" y="60" font-family="Arial, sans-serif" font-size="13" fill="#6b7280">Rows are cooling-stack sections; columns are inferred status/evidence labels.</text>',
    ]
    for idx, col in enumerate(columns):
        x = label_width + idx * cell + cell / 2
        parts.append(
            f'<text x="{x}" y="104" font-family="Arial, sans-serif" font-size="11" fill="#374151" text-anchor="end" transform="rotate(-35 {x} 104)">{svg_text(col)}</text>'
        )
    for row_idx, section in enumerate(SECTION_ORDER):
        y = top + row_idx * cell
        parts.append(
            f'<text x="32" y="{y + 34}" font-family="Arial, sans-serif" font-size="13" fill="#374151">{svg_text(section)}</text>'
        )
        for col_idx, col in enumerate(columns):
            x = label_width + col_idx * cell
            value = matrix[(section, col)]
            parts.extend(
                [
                    f'<rect x="{x}" y="{y}" width="{cell - 4}" height="{cell - 4}" rx="4" fill="{fill(value)}" stroke="#ffffff"/>',
                    f'<text x="{x + (cell - 4) / 2}" y="{y + 34}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#111827" text-anchor="middle">{value if value else ""}</text>',
                ]
            )
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_summary_markdown(resources: list[Resource], path: Path, generated_on: str) -> None:
    section_counts = Counter(resource.section for resource in resources)
    status_counts = Counter(resource.status for resource in resources)
    validation_counts = Counter(resource.validation_signal for resource in resources)
    priority_counts = Counter(resource.review_priority for resource in resources)
    explicit_validation_basis = sum(resource.validation_basis != "not specified" for resource in resources)
    explicit_run_status = sum(resource.run_status != "not specified" for resource in resources)
    explicit_artifact_status = sum(resource.artifact_status != "not specified" for resource in resources)
    reviewed_dates = sum(bool(resource.reviewed_on) for resource in resources)
    validation_queue_count = len(validation_queue_resources(resources))
    workflow_counts: Counter[str] = Counter()
    for resource in resources:
        for tag in resource.workflow_tags.split("; "):
            workflow_counts[tag] += 1

    lines = [
        "# Generated Catalog Summary",
        "",
        f"Generated on {generated_on} from `README.md`.",
        "",
        "## Snapshot",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Total resources | {len(resources)} |",
        f"| Sections | {len(section_counts)} |",
        f"| Candidate or low-confidence entries | {status_counts.get('candidate', 0)} |",
        f"| Standards/guidelines | {status_counts.get('standard/guideline', 0)} |",
        f"| Explicit validation caveats | {validation_counts.get('explicit validation caveat', 0)} |",
        f"| High-priority review entries | {priority_counts.get('high', 0)} |",
        f"| Educational/prototype entries | {status_counts.get('educational', 0) + status_counts.get('prototype', 0)} |",
        f"| Entries with explicit validation basis | {explicit_validation_basis} |",
        f"| Entries in validation review queue | {validation_queue_count} |",
        "",
        "## Resources By Cooling-Stack Section",
        "",
        "| Section | Count |",
        "| --- | ---: |",
    ]
    for section, count in ordered_counter(section_counts, SECTION_ORDER):
        lines.append(f"| {section} | {count} |")

    lines.extend(
        [
            "",
            "## Inferred Status Mix",
            "",
            "| Status | Count |",
            "| --- | ---: |",
        ]
    )
    for status, count in ordered_counter(status_counts, STATUS_ORDER):
        lines.append(f"| {status} | {count} |")

    lines.extend(
        [
            "",
            "## Validation Signals",
            "",
            "| Validation signal | Count |",
            "| --- | ---: |",
        ]
    )
    for signal, count in ordered_counter(validation_counts, VALIDATION_SIGNAL_ORDER):
        lines.append(f"| {signal} | {count} |")

    lines.extend(
        [
            "",
            "## Metadata Completeness",
            "",
            "| Metadata field | Explicit rows |",
            "| --- | ---: |",
            f"| validation_basis | {explicit_validation_basis} |",
            f"| run_status | {explicit_run_status} |",
            f"| artifact_status | {explicit_artifact_status} |",
            f"| reviewed_on | {reviewed_dates} |",
            "",
            "## Review Priority",
            "",
            "| Priority | Count |",
            "| --- | ---: |",
        ]
    )
    for priority, count in ordered_counter(priority_counts, ["high", "medium", "normal"]):
        lines.append(f"| {priority} | {count} |")

    lines.extend(
        [
            "",
            "## Common Workflow Tags",
            "",
            "| Workflow tag | Count |",
            "| --- | ---: |",
        ]
    )
    for tag, count in ordered_counter(workflow_counts):
        lines.append(f"| {tag} | {count} |")

    lines.extend(
        [
            "",
            "## Generated Files",
            "",
            "- `docs/generated/catalog_resources.csv`",
            "- `docs/assets/catalog_by_section.svg`",
            "- `docs/assets/catalog_by_status.svg`",
            "- `docs/assets/catalog_workflow_tags.svg`",
            "- `docs/assets/catalog_evidence_map.svg`",
            "- `docs/generated/validation_review_queue.md`",
            "- `docs/generated/validation_execution_matrix.md`",
            "- `docs/generated/validation_runbook.md`",
            "- `docs/generated/validation_next_actions.md`",
            "- `docs/generated/validation_debt_report.md`",
            "- `docs/generated/catalog_quality_report.md` after running `scripts/check_catalog_quality.py`",
            "",
            "Regenerate with:",
            "",
            "```bash",
            "python scripts/build_catalog_assets.py",
            "```",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def table_cell(value: str) -> str:
    return value.replace("|", "\\|")


def parse_iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def review_age_days(resource: Resource, generated_on: str) -> int | None:
    reviewed = parse_iso_date(resource.reviewed_on)
    generated = parse_iso_date(generated_on)
    if not reviewed or not generated:
        return None
    return max((generated - reviewed).days, 0)


def validation_age_bucket(age: int | None) -> str:
    if age is None:
        return "undated"
    if age <= 2:
        return "0-2 days"
    if age <= 6:
        return "3-6 days"
    if age <= 13:
        return "7-13 days"
    return "14+ days"


def write_validation_queue_markdown(resources: list[Resource], path: Path, generated_on: str) -> None:
    queued = validation_queue_resources(resources)
    priority_counts = Counter(resource.review_priority for resource in queued)
    signal_counts = Counter(resource.validation_signal for resource in queued)
    linked_count = sum(bool(resource.url) for resource in queued)
    review_ages = [
        age for resource in queued if (age := review_age_days(resource, generated_on)) is not None
    ]
    lines = [
        "# Validation Review Queue",
        "",
        f"Generated on {generated_on} from `README.md` metadata.",
        "",
        "This queue turns catalog caveats into concrete follow-up work. It does not mean every listed resource is weak; it identifies entries where execution, artifact inspection, independent data, or tighter evidence language would most improve reproducibility. The review-age column is computed from each entry's `Reviewed` date relative to the generated date so repeated automation runs can prioritize stale open work.",
        "",
        "## Queue Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Queued resources | {len(queued)} |",
        f"| Queued linked resources | {linked_count} |",
        f"| Queued unlinked resources | {len(queued) - linked_count} |",
        f"| High-priority queued resources | {priority_counts.get('high', 0)} |",
        f"| Medium-priority queued resources | {priority_counts.get('medium', 0)} |",
        f"| Candidate entries | {sum(resource.status == 'candidate' for resource in queued)} |",
        f"| Unreviewed candidate signals | {signal_counts.get('unreviewed candidate', 0)} |",
        f"| Screened low-confidence candidates | {signal_counts.get('screened low-confidence candidate', 0)} |",
        f"| Vendor or product-material caveats | {sum(resource.status == 'vendor/material' for resource in queued)} |",
        f"| Reported benchmark signals | {signal_counts.get('reported benchmark', 0)} |",
        f"| Paper artifacts | {signal_counts.get('paper artifact', 0)} |",
        f"| Not-run queued resources | {sum(resource.run_status == 'not run in catalog review' for resource in queued)} |",
        f"| Source-inspected queued resources | {sum(has_source_inspection(resource) for resource in queued)} |",
        f"| Source-inspected resources still requiring execution | {sum(source_inspected_execution_required(resource) for resource in queued)} |",
        f"| Queued resources with review dates | {len(review_ages)} |",
        f"| Oldest queued review age | {max(review_ages, default=0)} days |",
        "",
        "## Immediate Validation Queue",
        "",
        "| Priority | Resource | Section | Status | Signal | Reviewed | Age (days) | Reason | Suggested next validation step |",
        "| --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for resource in queued:
        age = review_age_days(resource, generated_on)
        resource_cell = (
            f"[{table_cell(resource.name)}]({resource.url})"
            if resource.url
            else f"{table_cell(resource.name)} (no source URL recorded)"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    table_cell(resource.review_priority),
                    resource_cell,
                    table_cell(resource.section),
                    table_cell(resource.status),
                    table_cell(resource.validation_signal),
                    table_cell(resource.reviewed_on or "not recorded"),
                    str(age) if age is not None else "",
                    table_cell(validation_reason(resource)),
                    table_cell(validation_action(resource)),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## How To Close A Queue Item",
            "",
            "1. Run the smallest documented example, inspect the cited paper or standard, or document why execution is unavailable.",
            "2. Update the README note with the observed validation basis, run status, artifact status, and review date.",
            "3. Regenerate `docs/generated/catalog_resources.csv`, this queue, the catalog summary, figures, and the quality report.",
            "4. Record the decision in the next dated review log.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_validation_execution_matrix_markdown(resources: list[Resource], path: Path, generated_on: str) -> None:
    queued = validation_queue_resources(resources)
    readiness_values = [execution_readiness(resource) for resource in queued]
    track_counts = Counter(validation_track(resource) for resource in queued)
    readiness_counts = Counter(readiness_values)
    ready_count = sum(readiness.startswith("ready:") for readiness in readiness_values)
    blocked_count = sum(readiness.startswith("blocked:") for readiness in readiness_values)

    lines = [
        "# Validation Execution Matrix",
        "",
        f"Generated on {generated_on} from `README.md` metadata.",
        "",
        "This matrix splits the validation queue into executable tracks. It is a planning artifact, not evidence that any queued resource has been reproduced.",
        "",
        "## Execution Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Queued resources | {len(queued)} |",
        f"| Ready execution or inspection items | {ready_count} |",
        f"| Blocked items | {blocked_count} |",
        f"| Manual evidence-review items | {len(queued) - ready_count - blocked_count} |",
        f"| Source-inspected queued resources | {sum(has_source_inspection(resource) for resource in queued)} |",
        f"| Source-inspected resources still requiring execution | {sum(source_inspected_execution_required(resource) for resource in queued)} |",
        "",
        "## By Validation Track",
        "",
        "| Track | Count |",
        "| --- | ---: |",
    ]
    for track, count in ordered_counter(track_counts, VALIDATION_TRACK_ORDER):
        lines.append(f"| {track} | {count} |")

    lines.extend(
        [
            "",
            "## By Execution Readiness",
            "",
            "| Readiness | Count |",
            "| --- | ---: |",
        ]
    )
    for readiness, count in ordered_counter(readiness_counts):
        lines.append(f"| {readiness} | {count} |")

    lines.extend(
        [
            "",
            "## Queue Execution Plan",
            "",
            "| Track | Readiness | Resource | Reviewed | Age (days) | Closure evidence required |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for resource in queued:
        age = review_age_days(resource, generated_on)
        resource_cell = (
            f"[{table_cell(resource.name)}]({resource.url})"
            if resource.url
            else f"{table_cell(resource.name)} (no source URL recorded)"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    table_cell(validation_track(resource)),
                    table_cell(execution_readiness(resource)),
                    resource_cell,
                    table_cell(resource.reviewed_on or "not recorded"),
                    str(age) if age is not None else "",
                    table_cell(closure_evidence(resource)),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## How To Use This Matrix",
            "",
            "1. Start with `ready:` items when the goal is to reduce not-run validation debt.",
            "2. Use `blocked:` items for source-identification, datasheet, or artifact-availability work.",
            "3. Record the exact command, input data, output metric, or reason execution remains unavailable in the next dated review log.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_validation_runbook_markdown(resources: list[Resource], path: Path, generated_on: str) -> None:
    queued = validation_queue_resources(resources)
    readiness_by_name = {resource.name: execution_readiness(resource) for resource in queued}
    age_by_name = {resource.name: review_age_days(resource, generated_on) for resource in queued}

    def readiness_rank(resource: Resource) -> int:
        readiness = readiness_by_name[resource.name]
        if readiness.startswith("ready:"):
            return 0
        if readiness.startswith("blocked:"):
            return 1
        return 2

    def priority_rank(resource: Resource) -> int:
        return {"high": 0, "medium": 1, "normal": 2}.get(resource.review_priority, 9)

    ordered = sorted(
        queued,
        key=lambda resource: (
            readiness_rank(resource),
            -(age_by_name[resource.name] or 0),
            priority_rank(resource),
            validation_track(resource),
            resource.name.lower(),
        ),
    )

    ready_items = sum(readiness.startswith("ready:") for readiness in readiness_by_name.values())
    blocked_items = sum(readiness.startswith("blocked:") for readiness in readiness_by_name.values())
    source_execution_required = sum(source_inspected_execution_required(resource) for resource in queued)

    lines = [
        "# Validation Runbook",
        "",
        f"Generated on {generated_on} from `README.md` metadata.",
        "",
        "This runbook turns validation debt into evidence packets. It is not proof of reproduction; it states what must be captured before a row can move from a caveated catalog entry toward reproducible engineering evidence.",
        "",
        "## Runbook Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Queued resources | {len(queued)} |",
        f"| Ready execution or inspection items | {ready_items} |",
        f"| Blocked items | {blocked_items} |",
        f"| Manual evidence-review items | {len(queued) - ready_items - blocked_items} |",
        f"| Source-inspected resources still requiring execution | {source_execution_required} |",
        "",
        "## Evidence Packet Runbook",
        "",
        "| Readiness | Resource | Track | Reviewed | Age (days) | Probe template | Evidence packet | Do not close with |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]

    for resource in ordered:
        age = age_by_name[resource.name]
        resource_cell = (
            f"[{table_cell(resource.name)}]({resource.url})"
            if resource.url
            else f"{table_cell(resource.name)} (no source URL recorded)"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    table_cell(readiness_by_name[resource.name]),
                    resource_cell,
                    table_cell(validation_track(resource)),
                    table_cell(resource.reviewed_on or "not recorded"),
                    str(age) if age is not None else "",
                    table_cell(validation_probe(resource)),
                    table_cell(closure_evidence(resource)),
                    table_cell(non_closure_condition(resource)),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Minimum Evidence Rule",
            "",
            "A queue item is not closed by source inspection alone unless its catalog role is explicitly educational, prototype, adjacent, documentation-only, vendor-context, or thermal-validation-not-applicable. Benchmark, paper-artifact, semantic-validation, and public-code workflow rows need a command, configuration, output, pass/fail result, or dated blocking reason.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def next_action_reason(resource: Resource, age: int | None) -> str:
    readiness = execution_readiness(resource)
    reasons = []
    if age is not None and age >= VALIDATION_STALE_DAYS:
        reasons.append("stale queue item")
    if readiness.startswith("ready:"):
        reasons.append("ready for closure evidence")
    if resource.run_status == "not run in catalog review":
        reasons.append("untouched not-run row")
    if has_source_inspection(resource) and source_inspected_execution_required(resource):
        reasons.append("source inspection did not close execution debt")
    if resource.review_priority == "high":
        reasons.append("high-priority caveat")
    if readiness.startswith("blocked:"):
        reasons.append("blocker needs demotion or retained-blocked evidence")
    return "; ".join(reasons) if reasons else "queue item needs dated evidence"


def validation_next_action_resources(
    resources: list[Resource],
    generated_on: str,
    limit: int = VALIDATION_NEXT_ACTION_LIMIT,
) -> list[Resource]:
    queued = validation_queue_resources(resources)

    def priority_rank(resource: Resource) -> int:
        return {"high": 0, "medium": 1, "normal": 2}.get(resource.review_priority, 9)

    def readiness_rank(resource: Resource) -> int:
        readiness = execution_readiness(resource)
        age = review_age_days(resource, generated_on) or 0
        if readiness.startswith("ready:") and age >= VALIDATION_STALE_DAYS:
            return 0
        if readiness.startswith("ready:"):
            return 1
        if readiness.startswith("blocked:") and age >= VALIDATION_STALE_DAYS:
            return 2
        if readiness.startswith("blocked:"):
            return 3
        return 4

    return sorted(
        queued,
        key=lambda resource: (
            readiness_rank(resource),
            priority_rank(resource),
            -(review_age_days(resource, generated_on) or 0),
            validation_track(resource),
            resource.name.lower(),
        ),
    )[:limit]


def write_validation_next_actions_markdown(resources: list[Resource], path: Path, generated_on: str) -> None:
    queued = validation_queue_resources(resources)
    selected = validation_next_action_resources(resources, generated_on)
    readiness_by_name = {resource.name: execution_readiness(resource) for resource in selected}
    age_by_name = {resource.name: review_age_days(resource, generated_on) for resource in selected}
    track_counts = Counter(validation_track(resource) for resource in selected)
    ready_selected = sum(readiness_by_name[resource.name].startswith("ready:") for resource in selected)
    blocked_selected = sum(readiness_by_name[resource.name].startswith("blocked:") for resource in selected)
    stale_selected = sum(
        age_by_name[resource.name] is not None
        and age_by_name[resource.name] >= VALIDATION_STALE_DAYS
        for resource in selected
    )

    lines = [
        "# Validation Next Actions",
        "",
        f"Generated on {generated_on} from `README.md` metadata.",
        "",
        "This report converts the validation queue into a finite daily closure batch. It favors stale `ready:` rows, high-priority caveats, and blockers that need demotion, reclassification, or retained-blocked evidence. It is a planning artifact, not reproduction evidence.",
        "",
        "## Batch Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Queued resources | {len(queued)} |",
        f"| Selected next-action resources | {len(selected)} |",
        f"| Selected ready items | {ready_selected} |",
        f"| Selected blocked items | {blocked_selected} |",
        f"| Selected stale items ({VALIDATION_STALE_DAYS}+ days) | {stale_selected} |",
        f"| Selected high-priority items | {sum(resource.review_priority == 'high' for resource in selected)} |",
        "",
        "## Selected Validation Closure Batch",
        "",
        "| Rank | Resource | Track | Readiness | Reviewed | Age (days) | Why this now | Probe template | Evidence packet |",
        "| ---: | --- | --- | --- | --- | ---: | --- | --- | --- |",
    ]

    for rank, resource in enumerate(selected, start=1):
        age = age_by_name[resource.name]
        resource_cell = (
            f"[{table_cell(resource.name)}]({resource.url})"
            if resource.url
            else f"{table_cell(resource.name)} (no source URL recorded)"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    resource_cell,
                    table_cell(validation_track(resource)),
                    table_cell(readiness_by_name[resource.name]),
                    table_cell(resource.reviewed_on or "not recorded"),
                    str(age) if age is not None else "",
                    table_cell(next_action_reason(resource, age)),
                    table_cell(validation_probe(resource)),
                    table_cell(closure_evidence(resource)),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Selected Tracks",
            "",
            "| Track | Count |",
            "| --- | ---: |",
        ]
    )
    for track, count in ordered_counter(track_counts, VALIDATION_TRACK_ORDER):
        lines.append(f"| {track} | {count} |")

    lines.extend(
        [
            "",
            "## Daily Closure Rule",
            "",
            "Close at least one selected `ready:` row with command/output evidence, or convert one selected blocked row into a dated demotion, reclassification, non-applicability, or retained-blocked decision before adding new catalog candidates.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_validation_debt_report_markdown(resources: list[Resource], path: Path, generated_on: str) -> None:
    queued = validation_queue_resources(resources)
    readiness_by_name = {resource.name: execution_readiness(resource) for resource in queued}
    age_by_name = {resource.name: review_age_days(resource, generated_on) for resource in queued}
    age_counts = Counter(validation_age_bucket(age_by_name[resource.name]) for resource in queued)
    ready_count = sum(readiness_by_name[resource.name].startswith("ready:") for resource in queued)
    blocked_count = sum(readiness_by_name[resource.name].startswith("blocked:") for resource in queued)
    stale_queued = [
        resource
        for resource in queued
        if (age_by_name[resource.name] is not None and age_by_name[resource.name] >= VALIDATION_STALE_DAYS)
    ]
    stale_ready = [
        resource
        for resource in stale_queued
        if readiness_by_name[resource.name].startswith("ready:")
    ]
    stale_high_priority = [
        resource
        for resource in stale_queued
        if resource.review_priority == "high"
    ]
    actionable = [
        resource
        for resource in stale_ready
        if resource.run_status == "not run in catalog review"
    ]
    blockers = [
        resource
        for resource in queued
        if readiness_by_name[resource.name].startswith("blocked:")
    ]

    def priority_rank(resource: Resource) -> int:
        return {"high": 0, "medium": 1, "normal": 2}.get(resource.review_priority, 9)

    def sorted_by_age(items: list[Resource]) -> list[Resource]:
        return sorted(
            items,
            key=lambda resource: (
                -(age_by_name[resource.name] or 0),
                priority_rank(resource),
                resource.section,
                resource.name.lower(),
            ),
        )

    lines = [
        "# Validation Debt Report",
        "",
        f"Generated on {generated_on} from `README.md` metadata.",
        "",
        "This report tracks unresolved validation debt by age and execution readiness. It does not prove that a tool has been reproduced; it identifies where the catalog has carried the same open caveat long enough to need closure evidence or a demotion decision.",
        "",
        "## Debt Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Queued resources | {len(queued)} |",
        f"| Not-run queued resources | {sum(resource.run_status == 'not run in catalog review' for resource in queued)} |",
        f"| Ready execution or inspection items | {ready_count} |",
        f"| Blocked items | {blocked_count} |",
        f"| Manual evidence-review items | {len(queued) - ready_count - blocked_count} |",
        f"| Source-inspected queued resources | {sum(has_source_inspection(resource) for resource in queued)} |",
        f"| Source-inspected resources still requiring execution | {sum(source_inspected_execution_required(resource) for resource in queued)} |",
        f"| Stale queued resources ({VALIDATION_STALE_DAYS}+ days) | {len(stale_queued)} |",
        f"| Stale ready items ({VALIDATION_STALE_DAYS}+ days) | {len(stale_ready)} |",
        f"| Stale high-priority items ({VALIDATION_STALE_DAYS}+ days) | {len(stale_high_priority)} |",
        f"| Queued resources without URLs | {sum(not resource.url for resource in queued)} |",
        "",
        "## Age Buckets",
        "",
        "| Review age | Count |",
        "| --- | ---: |",
    ]
    for bucket in ["0-2 days", "3-6 days", "7-13 days", "14+ days", "undated"]:
        if age_counts.get(bucket):
            lines.append(f"| {bucket} | {age_counts[bucket]} |")

    lines.extend(
        [
            "",
            "## Oldest Ready Items",
            "",
            "| Priority | Resource | Track | Readiness | Reviewed | Age (days) | Closure evidence required |",
            "| --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for resource in sorted_by_age(actionable)[:15]:
        age = age_by_name[resource.name]
        resource_cell = f"[{table_cell(resource.name)}]({resource.url})" if resource.url else table_cell(resource.name)
        lines.append(
            "| "
            + " | ".join(
                [
                    table_cell(resource.review_priority),
                    resource_cell,
                    table_cell(validation_track(resource)),
                    table_cell(readiness_by_name[resource.name]),
                    table_cell(resource.reviewed_on or "not recorded"),
                    str(age) if age is not None else "",
                    table_cell(closure_evidence(resource)),
                ]
            )
            + " |"
        )
    if not actionable:
        lines.append("|  | No stale ready not-run items found. |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Current Blockers",
            "",
            "| Resource | Track | Readiness | Reviewed | Age (days) | Blocking condition |",
            "| --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for resource in sorted_by_age(blockers):
        age = age_by_name[resource.name]
        resource_cell = f"[{table_cell(resource.name)}]({resource.url})" if resource.url else table_cell(resource.name)
        lines.append(
            "| "
            + " | ".join(
                [
                    resource_cell,
                    table_cell(validation_track(resource)),
                    table_cell(readiness_by_name[resource.name]),
                    table_cell(resource.reviewed_on or "not recorded"),
                    str(age) if age is not None else "",
                    table_cell(closure_evidence(resource)),
                ]
            )
            + " |"
        )
    if not blockers:
        lines.append("| No blocked queue items found. |  |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Closure Rule For Recurring Reviews",
            "",
            f"Before promoting another batch of candidates, close at least one stale ready item ({VALIDATION_STALE_DAYS}+ days) with observed evidence, or record why execution is blocked and demote/reclassify the entry if the artifact cannot support its catalog role.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build(args: argparse.Namespace) -> None:
    resources = parse_resources(args.readme)
    generated_on = args.generated_on or today_string()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    write_csv(resources, GENERATED_DIR / "catalog_resources.csv")
    write_summary_markdown(resources, GENERATED_DIR / "catalog_summary.md", generated_on)
    write_validation_queue_markdown(resources, GENERATED_DIR / "validation_review_queue.md", generated_on)
    write_validation_execution_matrix_markdown(
        resources,
        GENERATED_DIR / "validation_execution_matrix.md",
        generated_on,
    )
    write_validation_runbook_markdown(
        resources,
        GENERATED_DIR / "validation_runbook.md",
        generated_on,
    )
    write_validation_next_actions_markdown(
        resources,
        GENERATED_DIR / "validation_next_actions.md",
        generated_on,
    )
    write_validation_debt_report_markdown(
        resources,
        GENERATED_DIR / "validation_debt_report.md",
        generated_on,
    )

    section_counts = Counter(resource.section for resource in resources)
    status_counts = Counter(resource.status for resource in resources)
    workflow_counts: Counter[str] = Counter()
    for resource in resources:
        for tag in resource.workflow_tags.split("; "):
            workflow_counts[tag] += 1

    write_bar_svg(
        "Resources By Cooling-Stack Section",
        ordered_counter(section_counts, SECTION_ORDER),
        ASSETS_DIR / "catalog_by_section.svg",
        "#2563eb",
    )
    write_bar_svg(
        "Inferred Catalog Status Mix",
        ordered_counter(status_counts, STATUS_ORDER),
        ASSETS_DIR / "catalog_by_status.svg",
        "#059669",
    )
    write_bar_svg(
        "Common Workflow Tags",
        ordered_counter(workflow_counts),
        ASSETS_DIR / "catalog_workflow_tags.svg",
        "#7c3aed",
    )
    write_heatmap_svg(resources, ASSETS_DIR / "catalog_evidence_map.svg")

    print(f"Parsed {len(resources)} resources from {args.readme}")
    print(f"Wrote generated outputs under {GENERATED_DIR} and {ASSETS_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=README)
    parser.add_argument("--generated-on", default="")
    args = parser.parse_args()
    build(args)


if __name__ == "__main__":
    main()
