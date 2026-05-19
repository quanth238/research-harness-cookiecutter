# Testing Protocol

## Verification Hierarchy
1. Unit checks for pure functions, parsers, metrics, and config loading.
2. Integration checks for data loader, model forward path, evaluator, and artifact writing.
3. Smoke end-to-end checks on tiny data or a small fixture.
4. Full empirical verification only after cheaper gates pass.

## Standard Commands
- `make smoke`
- `make test`
- `make check`
- `make research-preflight`
- `make verify-data`
- `make verify-metric`
- `make verify-baseline`
- `make verify-novelty`
- `make verify-venue`
- `make verify-feature ID=R001`
- `make handoff-check`

## Agent-Oriented Failure Output
Verification scripts should explain:
- what failed,
- why it matters for the research claim,
- the likely file or config to inspect next.

## Completion Rule
Skipping a required verification level means the task is not complete. `make verify-feature ID=<TASK_ID>` is the normal state transition gate: it runs the registered commands, writes a verification log, and records evidence in `feature_list.json` when the commands pass.

If a check is too expensive, record the cheaper substitute and the remaining risk in `PROGRESS.md` or an optional evaluation report under `work/`. Keep the task `active` or `blocked` until the required empirical check is run or the human explicitly changes the completion standard.
