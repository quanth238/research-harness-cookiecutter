# Baseline Protocol

## Canonical Baselines
| Baseline | Source | Config | Dataset/Split | Expected Range | Status |
|---|---|---|---|---|---|

## Accepted Baseline Runs
Source of accepted numbers: <own-run|our-run|harness-run|local-run>

| Baseline | Run Record | Metrics Path | Config Path | Dataset/Split | Seed | Status |
|---|---|---|---|---|---|---|

## Reproduction Rules
- Baseline configs should be treated as locked unless a task explicitly changes them.
- Any deviation from an upstream paper, repository, or official benchmark must be recorded in `DECISIONS.md`.
- Baseline metrics must come from run manifests and metric files, not copied chat text.
- Upstream paper numbers are reference context only; accepted baseline numbers must come from harness run records.

## Verification Commands
- `make source-smoke`
- `make verify-metric`
- `make verify-baseline`
