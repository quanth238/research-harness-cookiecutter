# Metrics Protocol

## Primary Metric
- Name: <metric name>
- Direction: <higher is better|lower is better|maximize|minimize>
- Script: <path>
- Aggregation rule: <aggregation rule>
- Required splits: <splits>

## Secondary Metrics
| Metric | Purpose | Script | Aggregation |
|---|---|---|---|

## Known-Answer Checks
- Fixture: <path>
- Expected output: <expected output>
- Verification command: <command that exits 0 only when fixture passes>

## Claim Rules
- Do not claim an improvement unless baseline and candidate metrics use the same dataset version, split, preprocessing, and aggregation rule.
- Record run IDs, metric files, config hashes, and seeds for every reported comparison.
- Negative or inconclusive results should be recorded rather than omitted.
