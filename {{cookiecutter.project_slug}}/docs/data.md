# Data Protocol

## Canonical Data Sources
- Dataset name: <dataset name>
- Version: <dataset version>
- Location: <source URL or local path>
- Checksum or manifest: <checksum or manifest path>

## Splits
- Train: <train split identifier>
- Validation: <validation split identifier>
- Test: <test split identifier>

## Invariants
- No train/test leakage.
- Preprocessing is deterministic or records seeds.
- Any filtered samples are logged.
- Leakage check: <passed|verified|clean>

## Verification Commands
- `make verify-data`

## Evidence
- Data manifest path: <path>
- Split manifest path: <path>
- Preprocessing config path: <path>
- Last verification log: <path>
