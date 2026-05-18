SRC_DIR ?= src/{{ cookiecutter.source_repo_name }}
PYTHON ?= {{ cookiecutter.python_command }}

.PHONY: setup smoke test check verify-feature clean-session source-status source-smoke verify-data verify-metric verify-one-scene verify-figure

setup:
	@mkdir -p work experiments logs results tests docs roles templates scripts configs evals artifacts/figures artifacts/tables paper src
	@echo "Harness directories ready."

smoke:
	@$(PYTHON) scripts/validate_harness.py

test:
	@$(PYTHON) scripts/validate_harness.py

check: smoke test
	@echo "Harness checks passed. Add source-specific checks as the project matures."

verify-feature:
	@test -n "$(ID)" || (echo "Usage: make verify-feature ID=R001" && exit 2)
	@bash scripts/verify_feature.sh "$(ID)"

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
