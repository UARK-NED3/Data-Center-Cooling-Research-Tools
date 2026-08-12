# Generated Catalog Summary

Generated on 2026-08-11 from `README.md`.

## Snapshot

| Metric | Count |
| --- | ---: |
| Total resources | 82 |
| Sections | 8 |
| Candidate or low-confidence entries | 3 |
| Standards/guidelines | 6 |
| Explicit validation caveats | 1 |
| High-priority review entries | 20 |
| Educational/prototype entries | 14 |
| Entries with explicit validation basis | 61 |
| Entries in validation review queue | 49 |

## Resources By Cooling-Stack Section

| Section | Count |
| --- | ---: |
| Fundamental Thermal-Fluid Mechanisms | 8 |
| Chip, Package, And Server Cooling | 5 |
| Rack, CDU, And Liquid Loop Systems | 12 |
| Room, Building, And Campus Modeling | 11 |
| AI, Control, Digital Twins, And Operations | 25 |
| System Metrics, Standards, And Accounting | 11 |
| Sustainability: Life Cycle, Water, Carbon, And Heat Reuse | 5 |
| Skills, Agents, And Plugin Collections | 5 |

## Inferred Status Mix

| Status | Count |
| --- | ---: |
| standard/guideline | 6 |
| commercial | 3 |
| included | 16 |
| workflow | 30 |
| benchmark | 3 |
| paper artifact | 4 |
| educational | 10 |
| prototype | 4 |
| vendor/material | 3 |
| candidate | 3 |

## Validation Signals

| Validation signal | Count |
| --- | ---: |
| standard/guideline | 8 |
| explicit validation claim | 1 |
| reported benchmark | 4 |
| paper artifact | 5 |
| documentation-only basis | 23 |
| commercial workflow caveat | 1 |
| vendor evidence caveat | 3 |
| educational/prototype caveat | 13 |
| explicit validation caveat | 1 |
| screened low-confidence candidate | 3 |
| not specified | 20 |

## Metadata Completeness

| Metadata field | Explicit rows |
| --- | ---: |
| validation_basis | 61 |
| run_status | 61 |
| artifact_status | 61 |
| reviewed_on | 61 |

## Review Priority

| Priority | Count |
| --- | ---: |
| high | 20 |
| medium | 39 |
| normal | 23 |

## Common Workflow Tags

| Workflow tag | Count |
| --- | ---: |
| workflow | 36 |
| modeling | 29 |
| control | 23 |
| accounting | 20 |
| testing | 17 |
| design | 15 |
| simulation | 14 |
| monitoring | 11 |
| CFD | 7 |
| optimization | 5 |
| dataset | 4 |
| reference | 4 |
| benchmark | 3 |
| planning | 3 |
| standard | 3 |
| heat reuse | 1 |
| semantic metadata | 1 |

## Generated Files

- `docs/generated/catalog_resources.csv`
- `docs/assets/catalog_by_section.svg`
- `docs/assets/catalog_by_status.svg`
- `docs/assets/catalog_workflow_tags.svg`
- `docs/assets/catalog_evidence_map.svg`
- `docs/generated/validation_review_queue.md`
- `docs/generated/validation_execution_matrix.md`
- `docs/generated/validation_runbook.md`
- `docs/generated/validation_next_actions.md`
- `docs/generated/validation_debt_report.md`
- `docs/generated/catalog_quality_report.md` after running `scripts/check_catalog_quality.py`

Regenerate with:

```bash
python scripts/build_catalog_assets.py
```
