# Initialization Contract

This file is the bootstrap contract for a fresh agent session. A generated project is ready for implementation only when every required condition below is satisfied.

## Required Startup Commands

```bash
./init.sh
make smoke
make source-status   # after a source repo has been added
```

## Required Verification Commands

```bash
make verify-feature ID=<TASK_ID>
make check
make handoff-check
```

## Bootstrap Conditions

- The harness root is readable from `AGENTS.md`.
- `./init.sh` runs without hidden manual steps.
- `feature_list.json` has at most one `active` task.
- Every feature has a behavior, verification command, and state.
- `PROGRESS.md`, `DECISIONS.md`, and `session-handoff.md` exist and are current enough for a fresh session.
- Source-specific checks are either configured or explicitly marked as not configured.

## Research Readiness Conditions

Before making empirical claims, the project must define:

- canonical dataset or input source,
- metric definitions and aggregation rules,
- baseline or comparison protocol,
- experiment run-record format,
- evidence artifact locations,
- clean-state exit routine.

## State Transition Rule

The agent may request verification, but it must not manually set a task to `passing`. `make verify-feature ID=<TASK_ID>` records evidence and updates the state only after all registered verification commands succeed.
