# Experiment Protocol

## Standard Run Record
Every experiment should record:
- Git commit
- Config file
- Config hash when practical
- Dataset version
- Seed
- Command
- Hardware/runtime notes
- Logs path
- Output artifacts
- Run manifest under `experiments/manifests/`

## Cheap Gates Before Expensive Runs
1. Import/config check
2. Data fixture check
3. One-batch, one-scene, or one-episode run
4. Metric sanity check
5. Full run only after cheap gates pass

## Verification Commands
- `make smoke`
- `make test`
- `make verify-protocol`
- `make verify-metric`
- `make verify-one-scene`
- `make check-run-record FILE=experiments/manifests/<run_id>.json`

## Run Status Values
Use `planned`, `running`, `passed`, `failed`, `blocked`, `inconclusive`, or `unstable`. Failed and unstable runs should also be summarized in `docs/failure-log.md`.
