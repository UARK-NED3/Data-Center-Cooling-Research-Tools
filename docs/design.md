# Data Center Cooling Research Tools Design

## Goal

Create a breadth-first, awesome-style hub for data center cooling researchers. The repository should help readers discover credible tools and workflows across the full stack, not promote one model or one tool.

## Editorial Positioning

The repository is a curated library. It can include open-source repositories, commercial tools, standards, datasets, paper artifacts, and experimental workflows when they help researchers design, model, test, operate, or evaluate cooling systems.

The hub should remain cooling-centered. Broad data-center infrastructure belongs only when it affects cooling decisions, energy performance, telemetry, workload scheduling, carbon-aware operation, or hardware management for liquid-cooled systems.

## Organization

The primary organization is by physical scale:

1. Fundamental thermal-fluid mechanisms.
2. Chip, package, and server cooling.
3. Rack, CDU, and liquid loop systems.
4. Room, building, and campus modeling.
5. AI, control, digital twins, and operations.
6. System metrics, standards, and accounting.

Each entry should also carry implicit workflow and evidence context in its note.

## Discovery Strategy

Use a two-track GitHub discovery process:

- Primary: `data center cooling` repository search for cooling-specific candidates.
- Secondary: `data-center` topic page for adjacent DCIM, telemetry, simulation, operations, and sustainability tools.

Search-derived entries must be screened before inclusion. The README should prefer concise, useful annotations over exhaustive listing.

## Seed Examples

Initial seed examples include:

- `nuoaleon/Data-center-PUE-prediction-tool` for facility-scale PUE prediction and climate-dependent scenario analysis.
- `4g/dcool` for reinforcement-learning cooling control examples.
- `HewlettPackard/dc-rl` for SustainDC data center simulation and control environments.
- Cooling-specific search candidates such as rack planning, predictive cooling optimization, hybrid cooling, and Modelica smart cooling libraries.

## Maintenance Rules

The contribution rubric should protect the library from becoming a generic data-center repository list. Every resource needs a clear cooling, energy, sustainability, telemetry, control, or hardware-management link.

