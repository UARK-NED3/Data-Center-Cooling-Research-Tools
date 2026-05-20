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
- The note explains what the resource is useful for without overstating validation.

## Suggested Entry Style

Use one compact table row:

```markdown
| [Resource name](https://example.com) | Open-source candidate | Rack/loop | One sentence on use case, key inputs/outputs, and validation caveat. |
```

Avoid vague descriptions such as "cool tool" or "AI for data centers." Say what the resource does and where it fits.

## Screening Search-Derived Repositories

GitHub search results can be noisy. For repositories found through searches such as `data center cooling` or the `data-center` topic:

1. Confirm the repository is actually relevant to cooling, energy, sustainability, telemetry, control, or hardware management.
2. Check whether it is an implementation, benchmark, dataset, paper artifact, educational demo, or planning tool.
3. Note if it is unvalidated, inactive, incomplete, or mainly educational.
4. Place adjacent resources in an "Adjacent Infrastructure" section only when they help cooling research.

