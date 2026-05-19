SRC_DIR ?= src/{{ cookiecutter.source_repo_name }}
PYTHON ?= {{ cookiecutter.python_command }}

.PHONY: setup smoke test check verify-feature clean-session source-status source-smoke \
	verify-protocol verify-data verify-metric verify-one-scene verify-figure handoff-check check-run-record

setup:
	@mkdir -p work/verification_logs experiments/manifests experiments/runs logs/verification results/manifests tests docs roles templates scripts configs evals artifacts/figures artifacts/tables artifacts/checkpoints paper src
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
	@echo "verify-protocol is not configured. Replace this target with checks for research question, data, metric, and baseline protocol completeness." && exit 2

verify-data:
	@echo "verify-data is not configured. Replace this target with dataset manifest, checksum, and split checks." && exit 2

verify-metric:
	@echo "verify-metric is not configured. Replace this target with metric schema and known-answer checks." && exit 2

verify-one-scene:
	@echo "verify-one-scene is not configured. Replace this target with a tiny end-to-end run." && exit 2

verify-figure:
	@echo "verify-figure is not configured. Replace this target with paper artifact regeneration checks." && exit 2

clean-session:
	@bash scripts/clean_session.sh
