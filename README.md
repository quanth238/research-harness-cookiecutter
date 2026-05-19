# Research Harness Cookiecutter

Cookiecutter template for creating an empirical research harness around any existing code repository.

The generated workspace is intentionally a wrapper:

- harness files live at the project root,
- the implementation repo lives under `src/<source_repo_name>/`,
- users clone or copy their own source repo into `src/`,
- Codex or another coding agent works from repository artifacts, not chat memory.

This is useful for projects such as 3D Gaussian Splatting, VLA robotics, computer vision, empirical ML, and paper-reproduction workflows where "done" means auditable evidence exists.

## Install

```bash
pipx install cookiecutter
```

Or:

```bash
python3 -m pip install --user cookiecutter
```

## Generate A Harness

From a local checkout of this template:

```bash
cookiecutter research-harness-cookiecutter
```

From GitHub after publishing:

```bash
cookiecutter gh:quanth238/research-harness-cookiecutter
```

## Clone Your Source Repo

After generation:

```bash
cd my-research-harness
git clone https://github.com/graphdeco-inria/gaussian-splatting.git src/gaussian-splatting
./init.sh
make source-status
```

## Generated Layout

```text
my-research-harness/
├── AGENTS.md
├── Makefile
├── init.sh
├── INITIALIZATION_CONTRACT.md
├── feature_list.json
├── PROGRESS.md
├── DECISIONS.md
├── EVAL_PROTOCOL.md
├── docs/
├── roles/
├── templates/
├── scripts/
├── work/
├── experiments/
├── artifacts/
├── paper/
└── src/
    └── <source_repo_name>/
```

`roles/` and report templates are optional aids for larger projects; the default workflow only requires the feature list, verification commands, progress notes, and handoff checks.

## Core Principle

Do not ask the agent to "work on the research project."

Ask it to execute one task from `feature_list.json`, using the relevant docs, with verification commands and evidence artifacts recorded in the repo.

The generated template keeps a strict harness core while leaving research methods flexible:

- strict: one active task, evidence before passing, logged verification, clean session checks,
- flexible: source setup, metrics, data checks, experiment runners, and paper artifact workflows are project-defined.

## AutoResearchClaw Managed Backend

Generated projects include an optional managed AutoResearchClaw backend. The harness remains the source of truth for task state, evidence, run records, gates, multi-agent roles, and handoff; AutoResearchClaw produces candidate artifacts that must be imported and verified. The default backend auth uses the existing Codex CLI login through `codex exec`, without reading `~/.codex/auth.json`. Codex calls default to `CODEX_MODEL=gpt-5.5` and `CODEX_REASONING_EFFORT=xhigh`.

```bash
make arc-check
make arc-bootstrap
make arc-doctor
make arc-run TOPIC="your research topic"
make arc-import RUN_DIR=artifacts/arc-runs/<run_id>
make arc-verify RUN_DIR=artifacts/arc-runs/<run_id>
make arc-paper-gate RUN_DIR=artifacts/arc-runs/<run_id>
```

For OpenAI-compatible API-key auth, use `ARC_AUTH=openai ARC_CONFIG=configs/researchclaw.openai.yaml`.

The final paper gate is strict: simulated experiments, missing metrics, missing run records, or missing citation verification block final paper acceptance.

The template also includes an initialization contract, failure log, run-record schema, and CI smoke test so a fresh generated harness can prove that its basic workflow is runnable before source-specific research work starts.

## Local Validation

```bash
python3 scripts/smoke_test_template.py
```
