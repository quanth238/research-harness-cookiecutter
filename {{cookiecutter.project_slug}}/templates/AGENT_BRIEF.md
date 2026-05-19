# Agent Brief

## Role
<role>

## Task
<task-id>

## Inputs
- `feature_list.json`
- `docs/`
- task-specific files named by the orchestrator

## Constraints
- Work only on the assigned scope.
- Communicate through `work/agent_outbox/<task-id>/AGENT_RESULT.md`.
- Do not mark features passing.
- Do not claim research results without recorded evidence.

## Required Output
Write `AGENT_RESULT.md` with summary, files changed or inspected, evidence, blockers, and next action.
