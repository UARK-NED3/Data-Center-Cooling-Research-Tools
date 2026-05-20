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
| [`topic:data-center`](https://github.com/topics/data-center) | Broad adjacent stream | Finds DCIM, telemetry, workload scheduling, infrastructure, and data-center operations tools. Include only when cooling or energy relevance is explicit. |

## Review Fields

For each candidate, record:

- Repository name and URL.
- Search stream that found it.
- Short description from the repo and the reviewer.
- Scale: mechanism, chip, package, server, rack, CDU, loop, room, building, campus, operations, adjacent.
- Workflow: design, modeling, simulation, testing, data reduction, control, monitoring, optimization, accounting, due diligence.
- Evidence level: peer-reviewed artifact, validated model, benchmark, educational example, vendor/product material, emerging research, unclear.
- Maintenance signal: active, stale, archived, fork, empty/minimal, or unknown.
- Inclusion decision: include, candidate, adjacent, educational, exclude.
- Rationale in one or two sentences.

## Inclusion Decisions

Use these labels consistently.

| Label | Meaning |
| --- | --- |
| Include | Strong fit for the main README now. |
| Candidate | Relevant but needs deeper review, README inspection, paper lookup, or validation check. |
| Adjacent | Useful for facility operations, DCIM, telemetry, scheduling, site selection, or energy analysis, but not directly a cooling tool. |
| Educational | Useful demo or student project, but not validated enough for main engineering use. |
| Exclude | Generic data-center infrastructure, unrelated challenge/problem solution, marketing-only page, abandoned empty repo, or no cooling/energy relevance. |

## Review Checklist

1. Open the README and confirm the repository actually contains usable material.
2. Check whether the work is code, data, documentation, paper artifact, skill, product page, or educational demo.
3. Identify the physical scale and workflow stage.
4. Look for validation evidence: paper, dataset, experiment, benchmark, or comparison.
5. Check maintenance signals: latest update, archived flag, fork status, open issues, and whether examples run.
6. Decide whether it belongs in the main README, the candidate queue, an adjacent section, or should be excluded.
7. Write a concise note that does not overstate validation.

## Suggested Review Note

```markdown
| [repo/name](https://github.com/repo/name) | Candidate | Operations/control | Search: data center cooling. RL or predictive control example for cooling optimization; needs README and validation review before main inclusion. |
```

