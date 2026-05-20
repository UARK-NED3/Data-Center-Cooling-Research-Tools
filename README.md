# Data Center Cooling Research Tools

A curated hub for researchers working on data center cooling, thermal management, liquid cooling, facility energy modeling, control, testing, and digital twins.

The goal is not to promote one model, one solver, or one lab codebase. This repository is meant to be a one-stop starting point for finding useful tools across the full cooling stack: from bubble and droplet physics to chip/package cooling, rack liquid loops, CDUs, facility simulation, PUE/WUE/ERE accounting, heat reuse, and AI-assisted operation.

## Scope

Included resources should help researchers design, model, test, monitor, optimize, or evaluate data center cooling systems. The library can include open-source repositories, commercial tools, standards, datasets, benchmark environments, papers with reusable artifacts, and practical workflows.

## Navigation

- [Fundamental Thermal-Fluid Mechanisms](#fundamental-thermal-fluid-mechanisms)
- [Chip, Package, And Server Cooling](#chip-package-and-server-cooling)
- [Rack, CDU, And Liquid Loop Systems](#rack-cdu-and-liquid-loop-systems)
- [Room, Building, And Campus Modeling](#room-building-and-campus-modeling)
- [AI, Control, Digital Twins, And Operations](#ai-control-digital-twins-and-operations)
- [System Metrics, Standards, And Accounting](#system-metrics-standards-and-accounting)
- [Skills, Agents, And Plugin Collections](#skills-agents-and-plugin-collections)
- [Discovery Sources](#discovery-sources)
- [Entry Format](#entry-format)

## Fundamental Thermal-Fluid Mechanisms

Tools and workflows for understanding the physics behind cooling technologies.

| Resource | Type | Scale | Notes |
| --- | --- | --- | --- |
| Bubble dynamics analysis | Research workflow | Bubble/boiling | High-speed imaging, segmentation, tracking, velocity, departure diameter, frequency, coalescence, and uncertainty analysis. |
| Droplet dynamics analysis | Research workflow | Spray/evaporation | Droplet impact, spreading, rebound, evaporation, spray cooling, and heat-transfer characterization. |
| Acoustic emission and flow visualization workflows | Experimental workflow | Boiling/two-phase | Useful for boiling regime identification, event detection, and multimodal diagnostics. |
| IR thermography workflows | Experimental workflow | Chip/surface | Useful for chip power maps, thermal maps, boiling surfaces, and validation of simulations. |

## Chip, Package, And Server Cooling

Tools for heat generation, spreading, conduction, cold plates, direct-to-chip cooling, and electro-thermal design.

| Resource | Type | Scale | Notes |
| --- | --- | --- | --- |
| Ansys Icepak | Commercial solver | Electronics/package/server | Electronics cooling CFD and thermal design workflows. Include examples only when tied to reproducible assumptions or validation data. |
| Ansys Fluent | Commercial solver | Component to facility | General CFD and conjugate heat transfer; useful for cold plates, immersion, airflows, and room-scale studies when validation is documented. |
| Chip power map workflows | Data/model workflow | Chip/package | Map power density to junction temperature, hotspot risk, cooling limits, and system-level energy implications. |
| Electro-thermal co-design workflows | Design workflow | Chip/server | Joint treatment of power delivery, thermal constraints, 800 VDC architectures, reliability, and cooling requirements. |
| Smart Cooling Library | Open-source candidate | Processor/rack | Modelica thermal modeling of processors, cooling systems, loops, and rack simulation; screen before full inclusion. |

## Rack, CDU, And Liquid Loop Systems

Tools for rack cooling hardware, hydraulic integration, liquid loops, CDUs, rear-door heat exchangers, and immersion systems.

| Resource | Type | Scale | Notes |
| --- | --- | --- | --- |
| CDU design and sizing workflows | Design workflow | Rack/loop | Pump curves, heat exchanger sizing, controls, redundancy, approach temperature, water quality, and failure modes. |
| Direct-to-chip liquid-cooling workflows | Design/modeling workflow | Server/rack | Cold plate selection, manifold design, pressure drop, flow balancing, quick disconnects, leak detection, and serviceability. |
| Immersion cooling workflows | Design/testing workflow | Server/rack/tank | Dielectric fluid selection, boiling/single-phase behavior, material compatibility, maintenance, and electrical reliability. |
| Rear-door heat exchanger workflows | Design/modeling workflow | Rack/room | Rack heat capture, air-liquid heat exchange, fan interaction, condensation risk, and controls. |
| 2listic/datacenter-planner | Open-source candidate | Rack/room | 3D planning for racks and cooling systems; useful as a visualization/planning candidate after screening. |

## Room, Building, And Campus Modeling

Tools for connecting component and rack innovations to facility energy use, water use, carbon, and heat reuse.

| Resource | Type | Scale | Notes |
| --- | --- | --- | --- |
| EnergyPlus | Open-source building simulator | Building/facility | Facility energy modeling, HVAC systems, weather files, economizers, heat recovery, and annual performance. |
| Modelica workflows | Modeling language/workflow | Component to facility | Useful for coupled thermal-fluid-energy systems, cooling loops, controls, and system dynamics. |
| Data-center room CFD workflows | CFD workflow | Room/facility | Air management, containment, recirculation, bypass, rack inlet temperatures, and CRAC/CRAH interactions. |
| [nuoaleon/Data-center-PUE-prediction-tool](https://github.com/nuoaleon/Data-center-PUE-prediction-tool) | Open notebooks | Facility/campus | Physics-based PUE prediction and sensitivity analysis for climate-dependent hyperscale data center cooling scenarios. |
| Heat reuse workflows | Design/accounting workflow | Facility/campus | Waste heat recovery, district heating, greenhouse/aquaculture uses, ERE accounting, economics, and temperature-grade constraints. |

## AI, Control, Digital Twins, And Operations

Tools for control, surrogate modeling, monitoring, data-driven optimization, and operational decision support.

| Resource | Type | Scale | Notes |
| --- | --- | --- | --- |
| [4g/dcool](https://github.com/4g/dcool) | Open-source example | Operations/control | Data center cooling with reinforcement learning; useful as a control research example rather than a universal validated controller. |
| [HewlettPackard/dc-rl](https://github.com/HewlettPackard/dc-rl) | Open-source environment | Operations/control | SustainDC environments for data center simulation and control, including cooling optimization, workload scheduling, battery management, and multi-agent RL. |
| Predictive cooling optimizer repositories | Open-source candidates | Operations/control | Temperature-aware predictive control and optimization examples from GitHub search results; screen for assumptions, data, and validation. |
| Digital twin workflows | Modeling/operations workflow | Rack/facility | Sensor fusion, reduced-order models, uncertainty, calibration, anomaly detection, control, and what-if analysis. |
| CFDTwin-style surrogate workflows | Research workflow | Component/facility | CFD automation, design of experiments, POD/reduced-order modeling, neural surrogate training, and validation. |

## System Metrics, Standards, And Accounting

Resources that connect cooling innovations to system-level outcomes.

| Resource | Type | Scale | Notes |
| --- | --- | --- | --- |
| PUE calculation workflows | Accounting workflow | Facility/campus | Include IT power, cooling power, power delivery, component-level innovation effects, weather, controls, and annualization. |
| WUE and water accounting | Accounting workflow | Facility/campus | Water-side economizers, evaporative cooling, cooling towers, regional water stress, and treatment requirements. |
| ERE and heat reuse accounting | Accounting workflow | Facility/campus | Captures useful exported heat and clarifies when heat reuse improves system performance. |
| ASHRAE thermal guidelines | Standard/guideline | IT/facility | Operating envelopes, allowable conditions, environmental classes, and data center thermal management guidance. |
| Reliability and serviceability metrics | Evaluation workflow | Component to facility | Leak risk, maintainability, redundancy, uptime, pump/fan failure, fouling, corrosion, and instrumentation drift. |

## Skills, Agents, And Plugin Collections

Agent skills and plugin collections can help researchers run literature reviews, screen data center opportunities, automate facility-control workflows, and preserve reproducible engineering reasoning. Include them when they support research work; do not treat them as substitutes for validated thermal-fluid models, calibrated experiments, or engineering judgment.

| Resource | Type | Scale | Notes |
| --- | --- | --- | --- |
| [Mechanical Engineering Research Skill](https://github.com/hanhuark/mechanical-engineering-research-skill) | Agent skill | Thermal-fluid research workflow | Source-aware workflow for heat transfer, fluid mechanics, HVAC, energy systems, CFD, experiments, AI/ML, research coding, proposals, and technical writing. Useful as a domain-specific research assistant for data center cooling studies. |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | Plugin/skill collection | Research workflow | Academic research skills for literature review, paper planning, writing, review, citation checking, and publication workflows. Useful for cooling researchers preparing reviews, manuscripts, and proposal background sections. |
| [Data Center Due Diligence Orchestrator](https://mcpmarket.com/tools/skills/data-center-due-diligence-orchestrator) | Agent skill | Site/facility/investment workflow | Coordinates multi-domain data center due diligence across power, connectivity, land, environmental, and commercial factors. Relevant for site selection, infrastructure risk, and early-stage facility cooling constraints. |
| [Sensibo Automation](https://mcpmarket.com/tools/skills/sensibo-automation) | Agent skill / MCP workflow | Building HVAC/control | Automates Sensibo-connected climate control and monitoring. Mostly adjacent to data centers, but relevant for building-level HVAC control experiments, small lab test spaces, and AI-driven climate-control workflow prototypes. |

## Discovery Sources

Use these sources to find candidate entries. Candidates should be screened before inclusion.

| Source | Why Use It | Screening Notes |
| --- | --- | --- |
| [GitHub search: data center cooling](https://github.com/search?q=data%20center%20cooling&type=repositories) | Cooling-targeted repository discovery; currently surfaces PUE, AI control, rack planning, hybrid cooling, and Modelica candidates. | Primary GitHub mining stream. Check documentation, maintenance, scope, validation, and cooling relevance. |
| [GitHub topic: data-center](https://github.com/topics/data-center) | Broad data-center repository discovery; includes DCIM, telemetry, simulators, workload scheduling, networking, and operations. | Secondary stream. Include only when the cooling, energy, sustainability, telemetry, or hardware-management link is explicit. |
| Paper artifact links | Reproducible research code and datasets. | Prefer papers with clear model assumptions, validation, and reusable data or scripts. |
| Standards and professional societies | High-confidence definitions and test guidance. | Include stable links and note whether access is open or paid. |
| Vendor examples and documentation | Practical workflows for commercial solvers and hardware. | Avoid marketing-only entries; prefer technical examples, manuals, or validation cases. |

## Entry Format

Use concise entries so the README remains scannable.

```markdown
| [Tool or resource](https://example.com) | Open-source/commercial/standard/dataset/workflow | Scale | What it is useful for, key inputs/outputs, and any validation caveat. |
```

Recommended tags:

- Scale: mechanism, chip, package, server, rack, CDU, loop, room, building, campus, operations.
- Workflow: design, modeling, simulation, testing, data reduction, control, monitoring, optimization, accounting.
- Evidence: standard, peer-reviewed, validated model, benchmark, educational example, commercial workflow, emerging research.
- Metrics: junction temperature, thermal resistance, HTC, CHF, pressure drop, pumping power, fan power, rack kW, PUE, WUE, ERE, TCO, carbon.

## Contributing

Contributions are welcome when they improve the usefulness of the hub for data center cooling researchers. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before adding entries.
