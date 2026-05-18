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
├── feature_list.json
├── PROGRESS.md
├── DECISIONS.md
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

## Core Principle

Do not ask the agent to "work on the research project."

Ask it to execute one task from `feature_list.json`, using the relevant docs, with verification commands and evidence artifacts recorded in the repo.

## Local Validation

```bash
python3 scripts/smoke_test_template.py
```
