# Repository Review Workflow

Use this workflow to review GitHub repositories before citing them in the main README.

## Purpose

The library should be broad, but it should not become an undifferentiated list of data-center links. Every included repository needs a clear relationship to data center cooling research, facility energy, thermal management, HVAC/control, liquid cooling, telemetry, sustainability, or hardware management.

## Search Streams

Use multiple search streams because each one finds a different slice of the landscape.

| Search stream | Role | Notes |
| --- | --- | --- |
| [`data center cooling`](https://github.com/search?q=data%20center%20cooling&type=repositories) | Primary cooling-specific mining stream | Finds AI control, chiller optimization, PUE, rack planning, hybrid cooling, digital twin, and educational examples. |
| [`datacenter cooling`](https://github.com/search?q=datacenter%20cooling&type=repositories) | Variant spelling stream | Finds duplicates, older repos, RL examples, and many Quora challenge false positives. |
| [`PUE data center`](https://github.com/search?q=PUE%20data%20center&type=repositories) | Facility metric stream | Finds PUE calculators, energy dashboards, and facility-level models. |
| [`data center liquid cooling`](https://github.com/search?q=data%20center%20liquid%20cooling&type=repositories) | Liquid-cooling stream | Finds vendor, market, and skills-oriented resources; screen carefully for technical substance. |
| [`data center CDU liquid cooling`](https://github.com/search?q=data%20center%20CDU%20liquid%20cooling&type=repositories) | Rack/CDU stream | Finds coolant distribution, leak-monitoring, and rack-liquid-loop resources. |
| [`liquid cooled data center control`](https://github.com/search?q=liquid%20cooled%20data%20center%20control&type=repositories) | Liquid-cooling control stream | Finds control, transient-loop, and benchmark candidates for liquid-cooled systems. |
| [`data center thermal management github`](https://github.com/search?q=data%20center%20thermal%20management%20github&type=repositories) | Thermal-management adjacent stream | Finds broad thermal-management resources; expect noise and screen carefully. |
| [`topic:data-center`](https://github.com/topics/data-center) | Broad adjacent stream | Finds DCIM, telemetry, workload scheduling, infrastructure, and data-center operations tools. Include only when cooling or energy relevance is explicit. |

The repeatable version of this search process is `scripts/discover_github_repos.py`. The weekly GitHub Actions workflow runs it and opens or updates a review issue with the latest candidate report.

## Review Fields

For each candidate, record:

- Repository name and URL.
- Search stream that found it.
- Short description from the repo and the reviewer.
- Scale: mechanism, chip, package, server, rack, CDU, loop, room, building, campus, operations, adjacent.
- Workflow: design, modeling, simulation, testing, data reduction, control, monitoring, optimization, accounting, due diligence.
- Evidence level: peer-reviewed artifact, validated model, benchmark, educational example, vendor/product material, emerging research, unclear.
- Validation basis: independent experiment, operational data, synthetic benchmark, standard/guideline, vendor claim, paper-only claim, none found, or unknown.
- Run status: locally run, CI-tested upstream, source inspected but not locally run, examples documented but not run, unavailable environment, no runnable artifact, or not applicable.
- Public data/code status: public code, public data, partial artifact, closed data, documentation only, or unknown.
- Maintenance signal: active, stale, archived, fork, empty/minimal, or unknown.
- Inclusion decision: include, candidate, screened low-confidence candidate, adjacent, educational, exclude.
- Rationale in one or two sentences.

## Inclusion Decisions

Use these labels consistently.

| Label | Meaning |
| --- | --- |
| Include | Strong fit for the main README now. |
| Candidate | Relevant but needs deeper review, README inspection, paper lookup, or validation check. |
| Screened low-confidence candidate | A dated first-pass review found some cooling relevance, but the public artifact is too thin, unrun, or weakly validated for promotion. |
| Adjacent | Useful for facility operations, DCIM, telemetry, scheduling, site selection, or energy analysis, but not directly a cooling tool. |
| Educational | Useful demo or student project, but not validated enough for main engineering use. |
| Exclude | Generic data-center infrastructure, unrelated challenge/problem solution, marketing-only page, abandoned empty repo, or no cooling/energy relevance. |

## Review Checklist

1. Open the README and confirm the repository actually contains usable material.
2. Check whether the work is code, data, documentation, paper artifact, skill, product page, or educational demo.
3. Identify the physical scale and workflow stage.
4. Look for validation evidence: paper, dataset, experiment, benchmark, or comparison.
5. Record whether the validation evidence is directly reusable, only described in a paper, or unavailable.
6. Check maintenance signals: latest update, archived flag, fork status, open issues, and whether examples run.
7. Decide whether it belongs in the main README, the candidate queue, an adjacent section, or should be excluded.
8. Write a concise note that does not overstate validation.

When a candidate has been inspected but should stay low-confidence, record the exact reason and date instead of leaving it as unreviewed. The generated reports reserve `unreviewed candidate` for first-pass work and use `screened low-confidence candidate` for dated candidates with thin public artifacts, missing validation, or no runnable example.

If a candidate row has no URL, treat source identification as the first validation task. Find the canonical repository, documentation, paper, or standards page before promoting it. If two dated searches fail to find a canonical source, move the item out of the main README and keep it only in `docs/candidate-repos.md` as a source-identification task until a source appears.

## Validation Language Rules

Use precise validation language because the generated evidence map reads the README tables.

| Situation | Preferred wording | Avoid |
| --- | --- | --- |
| Tool was source-inspected but not executed locally | "Run status: source inspected, local run not performed." | "Locally reviewed" or "validated" without command output. |
| Benchmark was source-inspected but not executed locally | "Run status: source inspected, local run not performed" plus "benchmark execution still required" in the queue/matrix. | Moving it to optional manual review before a command, config, and metrics are recorded. |
| Hardware or IoT prototype was source-inspected but not bench-tested | "Run status: source inspected, hardware-in-loop validation not performed." | "Ready for local code smoke test" when sensors, relays, or firmware upload are required. |
| Tool was not independently checked | "No independent validation is recorded in this catalog." | "Not a validated model" without context. |
| Tool has a paper but no reusable data/code | "Paper-described method; reusable artifact not found." | "Validated by paper" unless validation data are available. |
| Tool reports benchmark results | "Benchmark environment with reported results; rerun before using as evidence." | "Validated benchmark" unless reproduced. |
| Standard or specification | "Specification/guideline source; not a performance dataset." | "Validated design tool." |
| Vendor product page | "Vendor/product material; needs datasheet or test data before engineering citation." | "Validated hardware evidence." |

When an entry is promoted to the README, put compact metadata tokens at the end of the note so generated artifacts can preserve the curation basis:

```markdown
Validation basis: source documentation, benchmark, standard/guideline, paper artifact, operational data, no independent validation, or unknown; Run status: locally run, source inspected, local run not performed, source inspected, hardware-in-loop validation not performed, not run in catalog review, no runnable artifact, or not applicable; Artifact status: public code, public data, documentation only, public document, partial artifact, closed data, or unknown; Reviewed: YYYY-MM-DD.
```

Paper-described tools, benchmarks, or datasets should go on a watchlist first when public reusable artifacts are not confirmed. Cite them in the manuscript or trends as landscape signals only when the paper itself supports the point, and promote them to the README only after a public repository, model, dataset, or executable scenario is inspectable.

Hardware and IoT prototypes should be routed to hardware-in-loop/manual validation unless the repository includes a no-hardware simulator or test suite that can exercise the same control path. For these rows, closure evidence should name the bill of materials, firmware compile/upload result, sensor calibration state, relay or actuator safety checks, and any bench or field-test conditions.

After changing the README, first check local refresh prerequisites:

```bash
powershell -ExecutionPolicy Bypass -File scripts/check_runtime_prereqs.ps1
```

Then run both:

```bash
python scripts/build_catalog_assets.py
python scripts/check_catalog_quality.py
```

The build step also writes `docs/generated/validation_review_queue.md`, `docs/generated/validation_execution_matrix.md`, `docs/generated/validation_runbook.md`, `docs/generated/validation_next_actions.md`, and `docs/generated/validation_debt_report.md`. Use the queue, including its linked/unlinked counts plus `Reviewed` and `Age (days)` columns, to pick stale entries. Use the execution matrix to decide whether the next step is a local smoke test, notebook/data review, paper-artifact match, semantic validation, source-identification work, standard/version verification, vendor-claim follow-up, or benchmark execution that remains required after source inspection. Use the runbook to define the minimum evidence packet and to avoid closing benchmark, paper-artifact, semantic, or public-code workflow rows with README inspection alone. Use the next-actions report as the finite daily closure batch so recurring reviews close or reclassify at least one selected item before adding new candidates. Use the debt report to close at least one stale ready item before promoting another large batch of resources, or record why execution is blocked and demote, reclassify, or mark thermal validation as not applicable for the item.

If a stale ready item turns out to be a layout, visualization, documentation, or adjacent workflow rather than a thermal, airflow, hydraulic, energy, or control model, do not keep it in the queue as a failed validation target. Update the README note with the inspected source, state why thermal validation is not applicable, and keep only the evidence caveat that matches its actual role.

If the prerequisite check fails, record the blocked command, exit status, and interpreter or TeX problem in the dated review log. Do not update generated dates, counts, or manuscript snapshot numbers unless the generator actually ran or a manual generated-artifact edit is explicitly documented.

## Suggested Review Note

```markdown
| [repo/name](https://github.com/repo/name) | Candidate | Operations/control | Search: data center cooling. RL or predictive control example for cooling optimization; needs README and validation review before main inclusion. |
```

