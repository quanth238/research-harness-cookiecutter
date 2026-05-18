# Research Harness Instructions

## Project
{{ cookiecutter.research_goal }}

## Source Repository
- Primary source path: `src/{{ cookiecutter.source_repo_name }}`
- Upstream URL: `{{ cookiecutter.upstream_repo_url }}`
- If this harness wraps an external repository, inspect source code under `src/{{ cookiecutter.source_repo_name }}/`.
- Keep harness files at the workspace root unless a task explicitly asks to modify the source repository itself.

## Start Every Session
1. Read `AGENTS.md`.
2. Read `PROGRESS.md` and `DECISIONS.md`.
3. Inspect `feature_list.json`.
4. Run `./init.sh` or `make smoke`.
5. Inspect source repo status with `make source-status`.
6. Work on exactly one active task unless the human explicitly changes scope.

## Hard Constraints
- Do not change dataset splits, evaluation metrics, or reported baseline numbers without recording the reason in `DECISIONS.md`.
- Do not claim an experiment result unless the command, config, seed, logs, and output artifact are recorded.
- Do not mark a task complete manually. Completion requires the registered verification command to pass.
- Prefer cheap proxy validation before expensive GPU training, rendering, or robotics simulation.
- Keep implementation changes separate from paper-writing and result-interpretation changes unless the task explicitly combines them.

## Commands
- `make setup` prepares the environment.
- `make smoke` runs cheap checks that should finish quickly.
- `make test` runs local tests.
- `make check` runs the normal verification gate.
- `make verify-feature ID=R001` runs the verification command registered for one feature.
- `make source-status` checks the wrapped source repository status.

## Topic Docs
- Read `docs/research_question.md` before changing the hypothesis, method, or claims.
- Read `docs/data.md` before touching datasets, preprocessing, labels, splits, or calibration.
- Read `docs/experiments.md` before changing training, evaluation, sweeps, logging, or seeds.
- Read `docs/paper.md` before changing figures, tables, text, or result claims.
- Read `docs/source_repo.md` before changing or wrapping upstream source code.

## Role Protocol
- Planner writes `work/TASK_SPEC.md` and does not edit implementation code.
- Generator implements only the approved task and writes `work/IMPLEMENTATION_REPORT.md`.
- Evaluator independently checks the diff, logs, outputs, and rubric, then writes `work/EVALUATION_REPORT.md`.

