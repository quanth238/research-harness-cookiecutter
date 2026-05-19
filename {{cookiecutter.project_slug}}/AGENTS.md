# Research Harness Instructions

## Project
{{ cookiecutter.research_goal }}

This repository is an empirical research harness. The agent's job is not to work on the project broadly; it must execute one bounded task from `feature_list.json`, verify it, record evidence, and leave a clean handoff.

## Source Repository
- Primary source path: `src/{{ cookiecutter.source_repo_name }}`
- Upstream URL: `{{ cookiecutter.upstream_repo_url }}`
- If this harness wraps an external repository, inspect source code under `src/{{ cookiecutter.source_repo_name }}/`.
- Keep harness files at the workspace root unless a task explicitly asks to modify the source repository itself.

## Start Every Session
1. Read `AGENTS.md` and `INITIALIZATION_CONTRACT.md`.
2. Read `PROGRESS.md`, `DECISIONS.md`, and `feature_list.json`.
3. Run `./init.sh` or `make smoke`.
4. Inspect source repo status with `make source-status` when source work is in scope.
5. Select exactly one task with state `active` or `not_started`.
6. Read the topic docs relevant to that task before editing files.

## Task State Rules
- Allowed task states: `not_started`, `active`, `blocked`, `passing`.
- At most one task may be `active` at a time.
- Do not start another task while one task is `active`.
- Do not manually mark a task `passing`.
- To verify a task, run `make verify-feature ID=<TASK_ID>`.
- If verification passes, the verification script records evidence and updates task state.
- If verification fails, keep the task `active` or mark it `blocked` with a concrete reason.

## Hard Constraints
- Do not change dataset splits, evaluation metrics, or reported baseline numbers without recording the reason in `DECISIONS.md`.
- Do not claim an experiment result unless the command, config, seed, logs, metric file, and output artifact are recorded.
- Do not compare results unless the metric definition, dataset split, and aggregation rule are compatible.
- Prefer cheap proxy validation before expensive GPU training, rendering, or robotics simulation.
- Keep implementation changes separate from paper-writing and result-interpretation changes unless the task explicitly combines them.
- Record negative results and failed runs; do not hide them by only reporting successful runs.

## Commands
- `make setup` prepares harness directories.
- `make smoke` runs cheap checks that should finish quickly.
- `make test` runs local harness tests.
- `make check` runs the normal harness verification gate.
- `make verify-feature ID=R001` runs the verification commands registered for one feature and records evidence.
- `make source-status` checks the wrapped source repository status.
- `make handoff-check` validates end-of-session continuity artifacts.
- `make check-run-record FILE=...` validates a research run manifest.
- `make arc-check` validates the static AutoResearchClaw managed backend scaffold.
- `make arc-bootstrap` clones and installs the pinned AutoResearchClaw backend.
- `make arc-doctor` validates the selected ARC auth mode. Default `ARC_AUTH=codex` uses Codex CLI login, not `OPENAI_API_KEY`.
- `make arc-doctor-live` optionally spends a tiny Codex call to verify live model access.
- `make arc-run TOPIC="..."` runs AutoResearchClaw under harness-controlled output paths.
- `make arc-import RUN_DIR=...`, `make arc-verify RUN_DIR=...`, and `make arc-paper-gate RUN_DIR=...` import and gate ARC outputs.
- `make agent-run ROLE=... TASK=...` launches a bounded Codex CLI worker using file-based handoff.
- `make remote-wsl-doctor` checks the configured WSL/GPU runner without mutating it.
- `make remote-wsl-sync-auth` explicitly syncs local Codex CLI auth files into WSL when the operator has approved it.
- `make remote-wsl-arc-doctor`, `make remote-wsl-bootstrap`, `make remote-wsl-run`, `make remote-wsl-import`, `make remote-wsl-verify`, and `make remote-wsl-paper-gate` dispatch ARC work to the configured WSL project root.
- `make clean-session` performs the end-of-session cleanup routine.
- Research-specific placeholder targets such as `make verify-protocol`, `make source-smoke`, `make verify-data`, `make verify-metric`, `make verify-one-scene`, and `make verify-figure` must be replaced before their tasks can pass.

## Topic Docs
- Read `docs/research_question.md` before changing the hypothesis, method, or claims.
- Read `docs/data.md` before touching datasets, preprocessing, labels, splits, or calibration.
- Read `docs/metrics.md` before changing metrics, aggregation, or claim comparisons.
- Read `docs/baselines.md` before changing or evaluating baselines.
- Read `docs/experiments.md` before changing training, evaluation, sweeps, logging, or seeds.
- Read `docs/testing.md` before adding or changing verification commands.
- Read `docs/artifacts.md` before writing logs, run manifests, figures, tables, checkpoints, or submissions.
- Read `docs/paper.md` before changing figures, tables, text, or result claims.
- Read `docs/source_repo.md` before changing or wrapping upstream source code.
- Read `docs/failure-log.md` before repeating a failed experiment family.
- Read `docs/auto_research.md` before running or accepting AutoResearchClaw-managed outputs.
- Read `docs/remote_wsl.md` before dispatching ARC work to WSL.

## AutoResearchClaw Managed Backend
- Treat AutoResearchClaw as an optional backend, not the source of truth.
- Default ARC auth uses `codex exec` through `scripts/codex_acp_shim.py`; do not read or copy `~/.codex/auth.json`.
- ARC Codex calls and `make agent-run` default to `CODEX_MODEL=gpt-5.5` and `CODEX_REASONING_EFFORT=xhigh`.
- To use API-key auth, pass `ARC_AUTH=openai ARC_CONFIG=configs/researchclaw.openai.yaml`.
- Raw ARC runs live under `artifacts/arc-runs/` and remain unaccepted until imported and verified.
- A final paper requires `make arc-paper-gate RUN_DIR=...`; draft paper files alone are not sufficient.
- The ARC Codex backend is read-only text generation. Codex worker agents may write outputs under `work/agent_outbox/`, but only verification scripts may mark work passing.
- WSL/GPU is an execution target only. Remote ARC outputs still require the same import, verify, and paper-gate checks.

## Optional Reports
- For simple tasks, update `feature_list.json`, `PROGRESS.md`, and `session-handoff.md`.
- For larger tasks, use the templates in `templates/` to write a task spec, implementation report, or evaluation report under `work/`.

## Session Exit
Before ending a session:
1. Run the relevant verification command or document why it could not run.
2. Update `PROGRESS.md` with commands, outcomes, evidence paths, and next action.
3. Update `DECISIONS.md` if any research assumption changed.
4. Update `docs/failure-log.md` for failed, negative, or unstable runs.
5. Run `make clean-session`.
