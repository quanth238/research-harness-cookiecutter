# Experiment Protocol

## Standard Run Record
Every experiment should record:
- Git commit
- Config file
- Dataset version
- Seed
- Command
- Hardware/runtime notes
- Logs path
- Output artifacts

## Cheap Gates Before Expensive Runs
1. Import/config check
2. Data fixture check
3. One-batch, one-scene, or one-episode run
4. Metric sanity check
5. Full run only after cheap gates pass

## Verification Commands
- `make smoke`
- `make test`
- `make verify-metric`
- `make verify-one-scene`

