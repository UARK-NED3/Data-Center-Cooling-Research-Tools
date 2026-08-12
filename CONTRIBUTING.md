# Contributing

Thank you for helping build a useful hub for data center cooling research tools.

## What Belongs

Add resources that help researchers design, model, test, monitor, optimize, benchmark, or evaluate data center cooling systems.

Good candidates include:

- Cooling and thermal-fluid tools for chips, packages, servers, racks, CDUs, loops, rooms, buildings, and campuses.
- PUE, WUE, ERE, TCO, carbon, water, and heat-reuse accounting tools.
- CFD, EnergyPlus, Modelica, reduced-order modeling, digital twin, and surrogate modeling workflows.
- Experimental tools for boiling, droplets, cold plates, immersion, direct-to-chip cooling, and rack/facility testing.
- AI, reinforcement learning, control, telemetry, and operations tools with a clear cooling or energy connection.
- Standards, datasets, benchmark environments, and peer-reviewed paper artifacts.

## What Usually Does Not Belong

Do not add generic data-center infrastructure unless the cooling or energy connection is explicit.

Usually exclude:

- Generic networking tools.
- Generic deployment or cloud infrastructure tooling.
- Asset inventory tools with no thermal, energy, telemetry, or hardware-management connection.
- Marketing pages without technical detail.
- Repositories with unclear scope, no usable documentation, or no meaningful relation to cooling research.

## Entry Checklist

Before adding an entry, check:

- The link is stable and public.
- The resource has enough documentation for a researcher to understand its use.
- The scale is clear: mechanism, chip, package, server, rack, CDU, loop, room, building, campus, or operations.
- The workflow is clear: design, modeling, simulation, testing, data reduction, control, monitoring, optimization, or accounting.
- The evidence level is clear: standard, peer-reviewed model, validated model, benchmark, educational example, commercial workflow, or emerging research.
- The validation basis is clear: independent data, standard/guideline, reported benchmark, vendor claim, paper-only claim, no validation found, or unknown.
- The README note ends with metadata tokens: `Validation basis: ...; Run status: ...; Artifact status: ...; Reviewed: YYYY-MM-DD.`
- The note explains what the resource is useful for without overstating validation.

## Update Workflow

`README.md` is the source of truth for the curated catalog. Files under `docs/generated/` and the catalog SVGs under `docs/assets/catalog_*.svg` are generated from the README.

When you add, remove, or reclassify catalog entries:

1. Add unreviewed resources to `docs/candidate-repos.md` first.
2. Apply `docs/repo-review-workflow.md` before promotion.
3. Edit the relevant README table.
4. Check local prerequisites, especially on Windows:

```bash
powershell -ExecutionPolicy Bypass -File scripts/check_runtime_prereqs.ps1
```

5. Run:

```bash
python scripts/build_catalog_assets.py
python scripts/check_catalog_quality.py
```

6. Check `docs/generated/catalog_summary.md`, `docs/generated/catalog_quality_report.md`, and the figures in `docs/assets/`.
7. Check `docs/generated/validation_next_actions.md` before adding more candidates; close or reclassify at least one selected stale item when practical.
8. Add a dated review log for substantial refreshes. If Python or TeX is unavailable, record the exact blocked command and do not claim regenerated or compiled artifacts.

To mine new GitHub candidates without editing the catalog, run:

```bash
python scripts/discover_github_repos.py
```

This produces a Markdown report and CSV under `docs/generated/` and `data/discovery/`.

## Suggested Entry Style

Use one compact table row:

```markdown
| [Resource name](https://example.com) | Open-source candidate | Rack/loop | One sentence on use case, key inputs/outputs, and validation caveat. Validation basis: source documentation; Run status: not run in catalog review; Artifact status: public code; Reviewed: YYYY-MM-DD. |
```

Avoid vague descriptions such as "cool tool" or "AI for data centers." Say what the resource does and where it fits.

## Screening Search-Derived Repositories

GitHub search results can be noisy. For repositories found through searches such as `data center cooling` or the `data-center` topic:

1. Confirm the repository is actually relevant to cooling, energy, sustainability, telemetry, control, or hardware management.
2. Check whether it is an implementation, benchmark, dataset, paper artifact, educational demo, or planning tool.
3. Note if it is unvalidated, inactive, incomplete, or mainly educational.
4. Prefer wording such as "No independent validation is recorded in this catalog" over ambiguous phrases that can be misread as validation.
5. Place adjacent resources in an "Adjacent Infrastructure" section only when they help cooling research.

