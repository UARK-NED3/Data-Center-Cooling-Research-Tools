# ITherm Figure Architecture: Evidence-Gated Rack-Model Benchmark

This figure architecture is for the ITherm manuscript on an executable,
evidence-gated benchmark for liquid-cooled data-center rack models.  It is a
publication plan, not a claim that every planned capability has already been
executed. The public v1.1 results are synthetic and unvalidated. The M3
parallel-branch network is implemented in Python; a Simscape adapter remains
planned. M100, Summit, and Kuzay are reviewed
only at the level supported by their published metadata and the locally held
records; no protected raw data or derivatives are included in the repository.

## Narrative sequence

The paper should answer the following questions in order.

1. What physical rack-level prediction is being compared?
2. Why cannot two nominally similar models be compared without a common case
   and evidence contract?
3. What inputs and model levels does the executable v1.1 suite declare?
4. What do the implemented models predict under identical synthetic tests?
5. Which conclusions are numerical verification or model-structure findings,
   and which would require a fully specified experiment?
6. Which available records can be promoted to that experiment and which
   metadata are still missing?

The resulting argument uses eight main figures.  Figures S1 and S2 are useful
audit artifacts and should remain supplementary unless a future M3 run or
benchmark-ready field record makes them central.

| ID | Manuscript role and question | Proposed content and source | Evidence class and claim boundary | Status |
| --- | --- | --- | --- | --- |
| Fig. 1 | **Physical target.** What is included in a rack thermal control volume? | User-authored rack-manifold schematic showing IT heat, liquid capture, residual air heat, TCS supply and return, and excluded CDU/facility paths. | Conceptual representation of the declared v1.0 boundary.  It does not depict a measured topology or commercial rack. | To generate |
| Fig. 2 | **Benchmark logic.** How does the framework prevent an unsupported comparison? | Existing evidence-gated architecture: case contract, evidence gate, M1/M2/M3, common outputs, and permissible claim tier. | Framework design. M1/M2/M3 are implemented as synthetic models; a Simscape adapter remains planned. | Generated |
| Fig. 3 | **Case definition.** What synthetic disturbances are applied to every implemented model? | Time histories of IT heat, TCS supply temperature, and mass flow from `suite.json` and the declared 1,200 s schedule. | NED3-authored synthetic test inputs; not field measurements or operating recommendations. | To generate |
| Fig. 4 | **Steady baseline.** What conservation trend must every compatible model reproduce? | M1 temperature rise versus mass flow, together with liquid and residual-air heat partitions at the 10 kW baseline. | Analytical, derived result for the declared control volume.  This is code/conservation verification, not rack validation. | To generate |
| Fig. 5 | **Three-model comparison.** What model-form difference emerges at a common rack manifold? | M1/M2/M3 mixed-return difference, M2 effective hardware state versus the M3 branch peak, and M3 branch-flow ranges under four mechanism-focused cases. | Synthetic model-structure comparison. M3 hydraulic resistances and thermal parameters are declared inputs, not measured hardware properties. | Generated |
| Fig. 6 | **Sensitivity and identifiability.** Which declared effective parameters change the response, and which observables would identify them? | Parameter sweep of $UA$, hardware capacitance, and coolant capacitance.  Report return-temperature rise, effective-hardware peak temperature, and settling time. | Synthetic sensitivity analysis.  It identifies data needs for calibration; it does not estimate physical parameters. | To generate |
| Fig. 7 | **Verification evidence.** Does the numerical implementation close the stated energy balance and converge in time step? | Energy-residual trace and time-step sensitivity for M2 under the declared disturbances. | Numerical verification of the implementation only.  It cannot establish physical accuracy. | To generate |
| Fig. 8 | **Field-data readiness.** Can available public records support a rack-model validation claim? | Curated matrix for M100, Summit, and Kuzay against topology, load allocation, flow, supply/return sensor locations, coolant properties, synchronization, uncertainty, and rights/provenance. | Literature/dataset metadata synthesis.  Each entry is traceable to a cited source and is not a reanalysis of restricted records. | To generate |

| Supplement | Role | Proposed content and source | Evidence class and claim boundary | Status |
| --- | --- | --- | --- | --- |
| Fig. S1 | **Run-record traceability.** What must an implementation report for replay? | Case-to-code-to-output provenance diagram and a compact excerpt of the run-record schema. | Documentation of the public synthetic suite. | To generate |
| Fig. S2 | **Claim escalation.** What additional measurements move a case from verification to validation? | Evidence ladder showing the required physical metadata and resulting permitted comparisons. | Framework guidance, not a result. | To generate |

## Placement and figure-to-section mapping

| Manuscript section | Figures | Job in the argument |
| --- | --- | --- |
| Introduction and motivation | Fig. 1, Fig. 8 | Define the physical target and demonstrate the evidence gap that prevents direct reuse of available records as a validation case. |
| Framework and case definition | Fig. 2, Fig. 3 | Specify the benchmark contract and the common synthetic forcing functions. |
| Models and verification | Fig. 4, Fig. 7 | Establish the analytical reference and numerical implementation checks before interpretation. |
| Results and interpretation | Fig. 5, Fig. 6 | Show model-form differences and identify the measurements required to distinguish model behavior. |
| Supplement | Fig. S1, Fig. S2 | Preserve traceability and decision logic without interrupting the main physical narrative. |

## Design rules

- Use vector SVG/PDF for all schematics and line plots.  Use Arial in exported
  figures, with at least 8 pt text at final two-column width.
- Use a consistent semantic palette: TCS supply/flow inputs in blue,
  liquid-path heat and return temperature in orange, effective hardware state
  in purple, residual-air heat in gray, and unexecuted/planned work in a
  gray dashed treatment.  Do not use color as the sole encoding.
- Use normal `(a)`, `(b)`, and so forth outside axes.  Each subfigure label
  must be unique and aligned.
- Each caption must identify the quantity, units, data source, calculation,
  and evidence boundary.  No figure may imply that synthetic cases are
  measured rack results.
- Keep Fig. 7 numerical detail in the main paper only if the venue page limit
  allows it.  If space is constrained, move it to the supplement and retain
  the numerical-verification statement in the methods.

## Promotion criteria

The implemented M3 result augments Fig. 5, but it does not validate M3. A
future Simscape implementation can be added only after its input/output
mapping, solver settings, version, and run record are captured. A field-data comparison may enter the main
results only when the selected record documents the model boundary, power-to-
loop allocation, supply and return sensor positions, flow, time alignment,
coolant properties, uncertainty or quality flags, and rights for the intended
use.  Otherwise it remains a conditional diagnostic or a data-readiness item.
