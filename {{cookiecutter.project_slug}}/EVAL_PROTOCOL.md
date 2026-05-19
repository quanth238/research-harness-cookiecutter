# Evaluation Protocol

## Primary Metrics
- Verified Completion Rate: verified tasks / attempted tasks.
- False Completion Rate: tasks claimed done but rejected by independent verification.
- Human Review Time: minutes to accept or reject a task.
- Cost per Verified Task: time/tokens/cost divided by verified completions.

## Research-Specific Metric
- Claim-Evidence Alignment: every written conclusion must point to a log, metric, figure, table, dataset checksum, or citation.
- Run-Record Completeness: accepted empirical runs have a manifest that passes `make check-run-record FILE=...`.

## Completion Rule
A task is complete only when:
1. Its verification command passes.
2. Required artifacts are stored under `experiments/`, `results/`, `artifacts/`, or `work/`.
3. `PROGRESS.md` records commands and outcomes.
4. Any manual review outcome or human override is recorded when verification is incomplete or ambiguous.
5. Any empirical claim has run IDs, config, seed, metric path, and artifact paths recorded.
6. Failed, negative, or unstable empirical outcomes are recorded in `docs/failure-log.md`.
