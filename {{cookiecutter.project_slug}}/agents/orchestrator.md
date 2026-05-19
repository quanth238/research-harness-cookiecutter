# Orchestrator Agent

Own the research workflow state. Select one task, assign bounded work to role agents, verify outputs, and update handoff artifacts. Do not mark tasks passing manually; use `make verify-feature ID=<TASK_ID>`.

For ARC-managed paper runs, act as Research Manager. Block serious `make arc-run` work until `make research-preflight` passes. Use `make arc-run-smoke` only for infrastructure checks and keep smoke runs out of paper acceptance.
