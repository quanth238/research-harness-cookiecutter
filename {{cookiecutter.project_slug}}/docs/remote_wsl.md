# Remote WSL GPU Runner

This harness can use a remote WSL2 Ubuntu environment as the execution machine
for AutoResearchClaw and GPU experiments. The local machine remains the review
and coordination surface; the harness gates still decide whether ARC outputs are
accepted.

## Roles

- WSL/GPU runs AutoResearchClaw, Codex CLI, experiment code, and raw ARC runs.
- The harness owns task state, run records, evidence gates, citation checks, and
  final paper acceptance.
- The local reviewer inspects imported manifests, paper artifacts, and final
  gate records before committing accepted outputs.

## Defaults

```bash
REMOTE_SSH={{ cookiecutter.remote_wsl_ssh_host }}
WSL_DISTRO={{ cookiecutter.remote_wsl_distro }}
REMOTE_ROOT={{ cookiecutter.remote_wsl_root }}
REMOTE_ARC_PYTHON=python3
```

Override these Make variables when the generated project lives somewhere else
inside WSL.

## First Setup In WSL

SSH to the Windows host, enter WSL, and install the required runtime:

```bash
ssh {{ cookiecutter.remote_wsl_ssh_host }}
wsl -d {{ cookiecutter.remote_wsl_distro }}
sudo apt-get update
sudo apt-get install -y git make build-essential python3 python3-venv python3-pip nodejs npm
sudo npm i -g @openai/codex
```

Codex auth must be available inside WSL because ARC calls `codex exec` inside
that environment. Prefer `codex --login` inside WSL. If the operator explicitly
approves syncing local Codex auth, run:

```bash
make remote-wsl-sync-auth
```

This copies only `auth.json` and `config.toml` into WSL `~/.codex`, never prints
their contents, and keeps the files out of the repository.

## Create Or Place The Harness In WSL

The remote targets expect the generated harness project to exist at
`REMOTE_ROOT`.

```bash
mkdir -p ~/code_space
cd ~/code_space
git clone https://github.com/quanth238/research-harness-cookiecutter.git research-harness-cookiecutter-autoresearchclaw
cd research-harness-cookiecutter-autoresearchclaw
git switch codex/autoresearchclaw-managed-backend
python3 -m pip install --user cookiecutter
python3 -m cookiecutter . --no-input project_name="{{ cookiecutter.project_name }}" source_repo_name="{{ cookiecutter.source_repo_name }}"
```

## Remote Checks

From the local harness checkout:

```bash
make remote-wsl-doctor
make remote-wsl-arc-doctor
make remote-wsl-bootstrap
make remote-wsl-arc-doctor
```

`remote-wsl-doctor` checks SSH, WSL, GPU visibility, Git, Python, Node/npm,
Codex CLI, Codex login, disk, and optional Docker/LaTeX.

`remote-wsl-bootstrap` creates `.arc/venv` for AutoResearchClaw and `.venv` for
ARC sandbox experiment execution inside WSL.

## Remote ARC Run And Gate

Run ARC in WSL:

```bash
make remote-wsl-run TOPIC="your research topic"
```

Then gate the run, still inside WSL:

```bash
make remote-wsl-import RUN_DIR=artifacts/arc-runs/<run_id>
make remote-wsl-verify RUN_DIR=artifacts/arc-runs/<run_id>
make remote-wsl-paper-gate RUN_DIR=artifacts/arc-runs/<run_id>
```

Raw ARC output remains candidate output. Final paper acceptance requires
`arc-verify` and `arc-paper-gate` to pass.

## Commit Policy

Commit only lightweight accepted artifacts: manifests, summaries, paper files,
and docs. Do not commit raw `artifacts/arc-runs/`, `.arc/`, virtual
environments, or `external/AutoResearchClaw/`.
