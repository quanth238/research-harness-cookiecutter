# Baseline Protocol

## Canonical Baselines
| Baseline | Source | Config | Dataset/Split | Expected Range | Status |
|---|---|---|---|---|---|

## Reproduction Rules
- Baseline configs should be treated as locked unless a task explicitly changes them.
- Any deviation from an upstream paper, repository, or official benchmark must be recorded in `DECISIONS.md`.
- Baseline metrics must come from run manifests and metric files, not copied chat text.

## Verification Commands
- `make source-smoke`
- `make verify-metric`
