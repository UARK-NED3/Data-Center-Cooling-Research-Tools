# Refresh Playbook

Use this playbook to keep the catalog current without turning GitHub search noise into unsupported evidence.

## Manual Refresh

Check local prerequisites before changing catalog inputs:

```bash
powershell -ExecutionPolicy Bypass -File scripts/check_runtime_prereqs.ps1
```

On Windows, a broken Microsoft Store Python launcher can make `py -3` exist while no usable Python process can start. Repair or install Python before regenerating catalog outputs, running citation checks, or launching GitHub discovery.

Run a candidate-mining pass:

```bash
python scripts/discover_github_repos.py --per-page 20
```

This writes:

- `docs/generated/latest-github-discovery.md`
- `data/discovery/latest-github-candidates.csv`

Refresh catalog tables and figures after changing `README.md`:

```bash
python scripts/build_catalog_assets.py
python scripts/check_catalog_quality.py
```

This writes:

- `docs/generated/catalog_summary.md`
- `docs/generated/catalog_resources.csv`
- `docs/generated/validation_review_queue.md`
- `docs/generated/validation_execution_matrix.md`
- `docs/generated/validation_runbook.md`
- `docs/generated/validation_next_actions.md`
- `docs/generated/validation_debt_report.md`
- `docs/generated/catalog_quality_report.md`
- `docs/assets/catalog_by_section.svg`
- `docs/assets/catalog_by_status.svg`
- `docs/assets/catalog_workflow_tags.svg`
- `docs/assets/catalog_evidence_map.svg`

For reproducible dated outputs, set:

```bash
python scripts/build_catalog_assets.py --generated-on 2026-06-22
python scripts/check_catalog_quality.py --generated-on 2026-06-22
```

## Weekly Automation

The [Weekly Tool Discovery](../.github/workflows/weekly-discovery.yml) workflow runs every Monday and can also be started manually from the GitHub Actions tab. It:

1. Runs `scripts/discover_github_repos.py`.
2. Uploads the Markdown and CSV discovery artifacts.
3. Opens a new review issue, or comments on the open weekly discovery issue.

The workflow does not commit changes or promote resources. That human review step is intentional.

## Search Streams

The discovery script currently searches:

| Query | Purpose |
| --- | --- |
| `data center cooling` | Primary cooling-specific stream |
| `datacenter cooling` | Variant spelling stream |
| `data center liquid cooling` | Liquid-cooling and hardware stream |
| `PUE data center` | Facility metric and accounting stream |
| `data center CDU liquid cooling` | Rack/CDU stream |
| `liquid cooled data center control` | Control stream for liquid-cooled systems |
| `data center thermal management github` | Broader thermal-management stream |

Add streams conservatively. Broad queries produce many unrelated infrastructure projects, while narrow queries miss newly named tools.

## Promotion Workflow

1. Put unreviewed resources in [candidate-repos.md](candidate-repos.md), not directly in the README.
2. Open a repository-review issue using the existing issue template.
3. Check documentation, inputs/outputs, assumptions, validation, maintenance, and evidence level.
4. Choose one decision: include, candidate, screened low-confidence candidate, adjacent, educational, or exclude.
5. Add a concise README row only if the resource is useful enough and the caveat is clear.
6. End the README note with explicit metadata: `Validation basis: ...; Run status: ...; Artifact status: ...; Reviewed: YYYY-MM-DD.`
7. Run `python scripts/build_catalog_assets.py`.
8. Run `python scripts/check_catalog_quality.py`.
9. Review `docs/generated/validation_review_queue.md`; use the linked/unlinked counts plus `Reviewed` and `Age (days)` columns to prioritize stale not-run items or source-missing candidates.
10. Review `docs/generated/validation_execution_matrix.md`; pick a `ready:` item for local or CI execution when possible, or record why the item remains `blocked:` or manual.
11. Review `docs/generated/validation_runbook.md`; use the probe template, evidence packet, and "Do not close with" column before deciding that source inspection is enough.
12. Review `docs/generated/validation_next_actions.md`; use the ranked daily closure batch to decide which stale ready item or blocker should be addressed before new catalog growth.
13. Review `docs/generated/validation_debt_report.md`; close at least one stale ready item before promoting another batch, or document why the item should be demoted, reclassified, marked thermal-validation-not-applicable, or left blocked.
14. Either close one queue item with observed evidence or record why it remains open; if the item is only layout, visualization, documentation, or adjacent workflow infrastructure, record why it is not a thermal-validation target.
15. When code or README inspection closes an educational/prototype scope question but no local command was run, use `Run status: source inspected, local run not performed` rather than `not run in catalog review`.
16. When an entry depends on sensors, relays, firmware upload, Arduino/ESP hardware, or physical actuation, use `Run status: source inspected, hardware-in-loop validation not performed` unless a bench test, firmware compile/upload, or simulator-backed control-path test is actually recorded.
17. When a benchmark, paper artifact, semantic workflow, or public-code workflow is source-inspected but not executed, keep it in a ready execution bucket until a command, configuration, and output metrics or pass/fail result are recorded.
18. If generation is blocked by missing local prerequisites, record the exact command and failure in the dated review log; do not update generated counts as if scripts ran.
19. Add a dated review log when a batch of entries is promoted or a recurring review cycle changes manuscript/repository evidence handling.

## Review Notes

- Do not treat stars, recent commits, or a polished README as validation.
- Do not cite vendor/product pages as engineering evidence unless they include technical documentation, test methods, or data.
- Prefer official standards, peer-reviewed papers, reproducible code, and validated benchmarks for manuscript claims.
- Treat `validation_basis`, `run_status`, and `artifact_status` as curation metadata, not as proof that the catalog maintainers validated the linked resource.
- Use `screened low-confidence candidate` when a dated first-pass review found a relevant but thin, unrun, or weakly validated artifact; reserve `unreviewed candidate` for items awaiting first-pass inspection.
- Use the validation review queue to choose runnable checks or source-identification tasks before promoting another wave of candidates.
- Use the validation execution matrix to distinguish runnable smoke tests from source-identification, vendor-evidence, paper-artifact, semantic-validation, and manual-review work.
- Use the validation runbook to record the minimum command, configuration, output, pass/fail result, blocking reason, or non-applicability evidence needed to close a queue item.
- Use the validation next-actions report as the finite daily closure target. It should prevent recurring reviews from spreading attention across the whole queue without closing at least one selected item.
- Use the validation debt report to track stale ready items across recurring reviews; repeated age without closure is evidence that the catalog entry needs execution, demotion, reclassification, a narrower caveat, or a documented non-applicability decision.
- Use `source inspected, local run not performed` for dated source-inspection closures. This reduces untouched not-run debt without implying local reproduction.
- Keep source-inspected benchmark rows execution-required until a minimal benchmark command, configuration, seed if relevant, and output metric are recorded.
- Use the hardware-in-loop/manual track for microcontroller, sensor, relay, or actuator prototypes; local software inspection alone should not become a Python-style smoke-test closure.
- Keep source-missing items out of the main README after two dated failed source searches; track them in `docs/candidate-repos.md` until a canonical source is found.
- Keep noisy repositories visible in the candidate queue only when they help future reviewers avoid rediscovering the same false positives.
