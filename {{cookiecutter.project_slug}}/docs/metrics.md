# Metrics Protocol

## Primary Metric
- Name:
- Direction: higher is better / lower is better
- Script:
- Aggregation rule:
- Required splits:

## Secondary Metrics
| Metric | Purpose | Script | Aggregation |
|---|---|---|---|

## Known-Answer Checks
- Fixture:
- Expected output:
- Verification command: `make verify-metric`

## Claim Rules
- Do not claim an improvement unless baseline and candidate metrics use the same dataset version, split, preprocessing, and aggregation rule.
- Record run IDs, metric files, config hashes, and seeds for every reported comparison.
- Negative or inconclusive results should be recorded rather than omitted.
