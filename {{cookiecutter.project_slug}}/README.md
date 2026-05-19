# {{ cookiecutter.project_name }}

{{ cookiecutter.research_goal }}

This workspace wraps a source repository under `src/{{ cookiecutter.source_repo_name }}/` and keeps research harness artifacts at the root. The harness is designed as a general empirical-research operating pattern: one task, one verification path, recorded evidence, and clean handoff.

## Start

```bash
./init.sh
make verify-feature ID=R001
make source-status
```

For a newly generated wrapper before the source repo is present, use:

```bash
./init.sh
make handoff-check
```

## Add A Source Repository

{% if cookiecutter.upstream_repo_url %}
```bash
git clone {{ cookiecutter.upstream_repo_url }} src/{{ cookiecutter.source_repo_name }}
```
{% else %}
```bash
git clone <upstream-repo-url> src/{{ cookiecutter.source_repo_name }}
```
{% endif %}

## Agent Workflow

1. Read `AGENTS.md` and `INITIALIZATION_CONTRACT.md`.
2. Read `PROGRESS.md`, `DECISIONS.md`, and `feature_list.json`.
3. Select exactly one task.
4. Read the docs relevant to that task.
5. Implement only the selected scope.
6. Verify with `make verify-feature ID=<TASK_ID>`.
7. Record evidence and update progress.
8. Run `make clean-session` before ending.

## Harness Checks

The template enforces a small strict core:

- `make smoke` validates harness structure and feature-list state.
- `make verify-feature ID=...` runs registered verification commands, writes logs under `work/verification_logs/`, and records task evidence.
- `make handoff-check` validates continuity files before ending a session.

Research-specific checks remain flexible. Replace placeholder targets such as `source-smoke`, `verify-protocol`, `verify-data`, `verify-metric`, and `verify-one-scene` with commands that fit the wrapped project.

## Research Protocol Docs

- `docs/research_question.md` - hypothesis and claim boundaries.
- `docs/data.md` - data sources, versions, checksums, splits, invariants.
- `docs/metrics.md` - metrics, aggregation, known-answer checks.
- `docs/baselines.md` - baselines and comparison protocol.
- `docs/experiments.md` - run records and experiment gates.
- `docs/testing.md` - verification hierarchy and required checks.
- `docs/artifacts.md` - logs, manifests, figures, tables, checkpoints, and submissions.
- `docs/paper.md` - paper claims, figures, tables, and evidence links.
- `docs/failure-log.md` - negative, failed, or unstable runs.
- `docs/auto_research.md` - managed AutoResearchClaw backend workflow and gates.
- `docs/remote_wsl.md` - remote WSL/GPU execution runbook for ARC.

## Evidence Rule

A result is not accepted because it looks plausible. It is accepted only when the command, config, seed, log, metric file, artifact path, and verification result are recorded in repo artifacts.

For AutoResearchClaw-managed runs, `make arc-import RUN_DIR=...` records candidate output as inconclusive, and `make arc-paper-gate RUN_DIR=...` must pass before the final paper can be treated as accepted evidence.

`make arc-bootstrap` creates `.arc/venv` for AutoResearchClaw and `.venv` for ARC sandbox experiment execution.

The default ARC auth mode is `ARC_AUTH=codex`, which uses the existing Codex CLI login through `codex exec`. The harness never reads `~/.codex/auth.json`. Codex calls default to `CODEX_MODEL=gpt-5.5` and `CODEX_REASONING_EFFORT=xhigh`; override those Make variables if your account or environment needs a different model. To use API-key auth instead, set `ARC_AUTH=openai ARC_CONFIG=configs/researchclaw.openai.yaml`.

For GPU execution on the configured WSL runner, read `docs/remote_wsl.md` and start with `make remote-wsl-doctor`. Auth sync to WSL is explicit via `make remote-wsl-sync-auth`; the sync script copies only Codex CLI auth files and never prints their contents.

For larger projects, the optional files under `roles/` and `templates/` can support planner/generator/evaluator style handoffs. They are not required for the default workflow.
