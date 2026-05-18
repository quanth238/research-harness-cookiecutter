# Evaluator Rubric

Score each dimension 0-2.

## Empirical Correctness
- 2: Claim is supported by correct metric files, logs, and protocol.
- 1: Partial evidence exists, but caveats remain.
- 0: Claim is unsupported or contradicted.

## Reproducibility
- 2: Run can be reproduced from command, config, commit, seed, and data version.
- 1: Mostly reproducible, but some metadata is missing.
- 0: Cannot reproduce from repo artifacts.

## Verification Discipline
- 2: Required checks were run and evidence was recorded.
- 1: Some checks were run, but evidence is incomplete.
- 0: Relies on inspection or confidence.

## Scope Discipline
- 2: Stayed within the selected task.
- 1: Minor extra changes.
- 0: Changed unrelated code, experiments, or claims.

## Handoff Readiness
- 2: Next session can continue from repo artifacts alone.
- 1: Some context is missing.
- 0: Requires human explanation outside the repo.

## Decision
accept | repair_required | reject

