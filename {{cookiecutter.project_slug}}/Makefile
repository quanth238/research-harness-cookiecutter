SRC_DIR ?= src/{{ cookiecutter.source_repo_name }}
PYTHON ?= {{ cookiecutter.python_command }}
ARC_PYTHON ?= {{ cookiecutter.arc_python_command }}
ARC_REPO_URL ?= {{ cookiecutter.autoresearchclaw_repo_url }}
ARC_REF ?= {{ cookiecutter.autoresearchclaw_ref }}
ARC_DIR ?= external/AutoResearchClaw
ARC_VENV ?= .arc/venv
ARC_SANDBOX_VENV ?= .venv
ARC_OPTIONAL_PACKAGES ?= matplotlib
ARC_AUTH ?= codex
ARC_CONFIG ?= configs/researchclaw.codex.yaml
ARC_RUN_ROOT ?= artifacts/arc-runs
CODEX_CLI ?= codex
CODEX_MODEL ?= gpt-5.5
CODEX_REASONING_EFFORT ?= xhigh
REMOTE_SSH ?= {{ cookiecutter.remote_wsl_ssh_host }}
WSL_DISTRO ?= {{ cookiecutter.remote_wsl_distro }}
REMOTE_ROOT ?= {{ cookiecutter.remote_wsl_root }}
REMOTE_ARC_PYTHON ?= python3

.PHONY: setup smoke test check verify-feature clean-session source-status source-smoke \
	verify-protocol verify-data verify-metric verify-baseline verify-novelty verify-venue research-preflight \
	verify-one-scene verify-figure handoff-check check-run-record \
	arc-bootstrap arc-doctor arc-doctor-live arc-check arc-run arc-run-smoke arc-resume arc-import arc-verify arc-paper-gate agent-run \
	remote-wsl-doctor remote-wsl-sync-auth remote-wsl-arc-doctor remote-wsl-bootstrap remote-wsl-run \
	remote-wsl-run-smoke remote-wsl-import remote-wsl-verify remote-wsl-paper-gate

setup:
	@mkdir -p work/verification_logs work/agent_runs work/agent_inbox work/agent_outbox work/locks experiments/manifests experiments/runs logs/verification results/manifests tests docs/kb/questions docs/kb/literature docs/kb/experiments docs/kb/findings docs/kb/decisions docs/kb/reviews roles templates scripts configs evals artifacts/figures artifacts/tables artifacts/checkpoints artifacts/arc-runs paper src external .arc agents
	@echo "Harness directories ready."

smoke:
	@$(PYTHON) scripts/validate_harness.py

test:
	@$(PYTHON) scripts/validate_harness.py

check: smoke test
	@echo "Normal harness verification gate passed. Add source-specific checks as the project matures."

verify-feature:
	@test -n "$(ID)" || (echo "Usage: make verify-feature ID=R001" && exit 2)
	@$(PYTHON) scripts/verify_feature.py "$(ID)"

handoff-check:
	@$(PYTHON) scripts/check_handoff.py

check-run-record:
	@test -n "$(FILE)" || (echo "Usage: make check-run-record FILE=experiments/manifests/<run_id>.json" && exit 2)
	@$(PYTHON) scripts/check_run_record.py "$(FILE)"

arc-bootstrap:
	@$(PYTHON) scripts/arc_bootstrap.py --repo-url "$(ARC_REPO_URL)" --ref "$(ARC_REF)" --arc-dir "$(ARC_DIR)" --venv "$(ARC_VENV)" --sandbox-venv "$(ARC_SANDBOX_VENV)" --optional-packages "$(ARC_OPTIONAL_PACKAGES)" --python "$(ARC_PYTHON)"

arc-doctor:
	@$(PYTHON) scripts/arc_doctor.py --auth "$(ARC_AUTH)" --arc-dir "$(ARC_DIR)" --venv "$(ARC_VENV)" --python "$(ARC_PYTHON)" --config "$(ARC_CONFIG)" --codex-cli "$(CODEX_CLI)" --codex-model "$(CODEX_MODEL)" --codex-reasoning-effort "$(CODEX_REASONING_EFFORT)"

arc-doctor-live:
	@$(PYTHON) scripts/arc_doctor.py --live-probe --auth "$(ARC_AUTH)" --arc-dir "$(ARC_DIR)" --venv "$(ARC_VENV)" --python "$(ARC_PYTHON)" --config "$(ARC_CONFIG)" --codex-cli "$(CODEX_CLI)" --codex-model "$(CODEX_MODEL)" --codex-reasoning-effort "$(CODEX_REASONING_EFFORT)"

arc-check:
	@$(PYTHON) scripts/arc_doctor.py --static-only --auth "$(ARC_AUTH)" --arc-dir "$(ARC_DIR)" --venv "$(ARC_VENV)" --python "$(ARC_PYTHON)" --config "$(ARC_CONFIG)" --codex-cli "$(CODEX_CLI)" --codex-model "$(CODEX_MODEL)" --codex-reasoning-effort "$(CODEX_REASONING_EFFORT)"

arc-run:
	@test -n "$(TOPIC)" || (echo "Usage: make arc-run TOPIC=\"research topic\"" && exit 2)
	@$(MAKE) research-preflight
	@CODEX_MODEL="$(CODEX_MODEL)" CODEX_REASONING_EFFORT="$(CODEX_REASONING_EFFORT)" $(PYTHON) scripts/arc_run.py --topic "$(TOPIC)" --arc-dir "$(ARC_DIR)" --venv "$(ARC_VENV)" --config "$(ARC_CONFIG)" --run-root "$(ARC_RUN_ROOT)"

arc-run-smoke:
	@test -n "$(TOPIC)" || (echo "Usage: make arc-run-smoke TOPIC=\"infrastructure smoke topic\"" && exit 2)
	@CODEX_MODEL="$(CODEX_MODEL)" CODEX_REASONING_EFFORT="$(CODEX_REASONING_EFFORT)" $(PYTHON) scripts/arc_run.py --smoke --topic "$(TOPIC)" --arc-dir "$(ARC_DIR)" --venv "$(ARC_VENV)" --config "$(ARC_CONFIG)" --run-root "$(ARC_RUN_ROOT)"

arc-resume:
	@test -n "$(RUN_DIR)" || (echo "Usage: make arc-resume RUN_DIR=artifacts/arc-runs/<run_id>" && exit 2)
	@CODEX_MODEL="$(CODEX_MODEL)" CODEX_REASONING_EFFORT="$(CODEX_REASONING_EFFORT)" $(PYTHON) scripts/arc_run.py --resume --run-dir "$(RUN_DIR)" --arc-dir "$(ARC_DIR)" --venv "$(ARC_VENV)" --config "$(ARC_CONFIG)" --run-root "$(ARC_RUN_ROOT)"

arc-import:
	@test -n "$(RUN_DIR)" || (echo "Usage: make arc-import RUN_DIR=artifacts/arc-runs/<run_id>" && exit 2)
	@$(PYTHON) scripts/import_arc_run.py "$(RUN_DIR)" --config "$(ARC_CONFIG)"

arc-verify:
	@test -n "$(RUN_DIR)" || (echo "Usage: make arc-verify RUN_DIR=artifacts/arc-runs/<run_id>" && exit 2)
	@$(PYTHON) scripts/verify_arc_run.py "$(RUN_DIR)"

arc-paper-gate:
	@test -n "$(RUN_DIR)" || (echo "Usage: make arc-paper-gate RUN_DIR=artifacts/arc-runs/<run_id>" && exit 2)
	@$(PYTHON) scripts/verify_paper_gate.py "$(RUN_DIR)" --config "$(ARC_CONFIG)"

agent-run:
	@test -n "$(ROLE)" || (echo "Usage: make agent-run ROLE=literature TASK=ARC-LIT-001" && exit 2)
	@test -n "$(TASK)" || (echo "Usage: make agent-run ROLE=literature TASK=ARC-LIT-001" && exit 2)
	@$(PYTHON) scripts/run_agent.py --role "$(ROLE)" --task "$(TASK)" --codex-cli "$(CODEX_CLI)" --codex-model "$(CODEX_MODEL)" --codex-reasoning-effort "$(CODEX_REASONING_EFFORT)"

remote-wsl-doctor:
	@scripts/remote_wsl_doctor.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)"

remote-wsl-sync-auth:
	@scripts/sync_codex_auth_to_wsl.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)"

remote-wsl-arc-doctor:
	@scripts/remote_wsl_exec.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)" --workdir "$(REMOTE_ROOT)" -- make arc-check ARC_PYTHON="$(REMOTE_ARC_PYTHON)"
	@scripts/remote_wsl_exec.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)" --workdir "$(REMOTE_ROOT)" -- make arc-doctor-live ARC_PYTHON="$(REMOTE_ARC_PYTHON)"

remote-wsl-bootstrap:
	@scripts/remote_wsl_exec.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)" --workdir "$(REMOTE_ROOT)" -- make arc-bootstrap ARC_PYTHON="$(REMOTE_ARC_PYTHON)"

remote-wsl-run:
	@test -n "$(TOPIC)" || (echo "Usage: make remote-wsl-run TOPIC=\"research topic\"" && exit 2)
	@scripts/remote_wsl_exec.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)" --workdir "$(REMOTE_ROOT)" -- make arc-run ARC_PYTHON="$(REMOTE_ARC_PYTHON)" TOPIC="$(TOPIC)"

remote-wsl-run-smoke:
	@test -n "$(TOPIC)" || (echo "Usage: make remote-wsl-run-smoke TOPIC=\"infrastructure smoke topic\"" && exit 2)
	@scripts/remote_wsl_exec.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)" --workdir "$(REMOTE_ROOT)" -- make arc-run-smoke ARC_PYTHON="$(REMOTE_ARC_PYTHON)" TOPIC="$(TOPIC)"

remote-wsl-import:
	@test -n "$(RUN_DIR)" || (echo "Usage: make remote-wsl-import RUN_DIR=artifacts/arc-runs/<run_id>" && exit 2)
	@scripts/remote_wsl_exec.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)" --workdir "$(REMOTE_ROOT)" -- make arc-import ARC_PYTHON="$(REMOTE_ARC_PYTHON)" RUN_DIR="$(RUN_DIR)"

remote-wsl-verify:
	@test -n "$(RUN_DIR)" || (echo "Usage: make remote-wsl-verify RUN_DIR=artifacts/arc-runs/<run_id>" && exit 2)
	@scripts/remote_wsl_exec.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)" --workdir "$(REMOTE_ROOT)" -- make arc-verify ARC_PYTHON="$(REMOTE_ARC_PYTHON)" RUN_DIR="$(RUN_DIR)"

remote-wsl-paper-gate:
	@test -n "$(RUN_DIR)" || (echo "Usage: make remote-wsl-paper-gate RUN_DIR=artifacts/arc-runs/<run_id>" && exit 2)
	@scripts/remote_wsl_exec.sh --ssh "$(REMOTE_SSH)" --distro "$(WSL_DISTRO)" --workdir "$(REMOTE_ROOT)" -- make arc-paper-gate ARC_PYTHON="$(REMOTE_ARC_PYTHON)" RUN_DIR="$(RUN_DIR)"

source-status:
	@test -d "$(SRC_DIR)" || (echo "Missing SRC_DIR=$(SRC_DIR). Clone or copy your source repo there." && exit 2)
	@test "$$(find "$(SRC_DIR)" -mindepth 1 -maxdepth 1 ! -name .DS_Store | wc -l | tr -d ' ')" -gt 0 || (echo "SRC_DIR exists but is empty: $(SRC_DIR)" && exit 2)
	@if git -C "$(SRC_DIR)" rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		git -C "$(SRC_DIR)" status --short; \
	else \
		echo "SRC_DIR exists and is non-empty but is not a git repository: $(SRC_DIR)"; \
	fi

source-smoke:
	@test -d "$(SRC_DIR)" || (echo "Missing SRC_DIR=$(SRC_DIR)" && exit 2)
	@echo "source-smoke is not configured. Replace this target with a source-repo-specific smoke command before verifying source tasks." && exit 2

verify-protocol:
	@$(PYTHON) scripts/verify_research_preflight.py protocol

verify-data:
	@$(PYTHON) scripts/verify_research_preflight.py data

verify-metric:
	@$(PYTHON) scripts/verify_research_preflight.py metric

verify-baseline:
	@$(PYTHON) scripts/verify_research_preflight.py baseline

verify-novelty:
	@$(PYTHON) scripts/verify_research_preflight.py novelty

verify-venue:
	@$(PYTHON) scripts/verify_research_preflight.py venue

research-preflight:
	@$(PYTHON) scripts/verify_research_preflight.py all

verify-one-scene:
	@echo "verify-one-scene is not configured. Replace this target with a tiny end-to-end run." && exit 2

verify-figure:
	@echo "verify-figure is not configured. Replace this target with paper artifact regeneration checks." && exit 2

clean-session:
	@bash scripts/clean_session.sh
