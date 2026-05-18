SRC_DIR ?= src/{{ cookiecutter.source_repo_name }}
PYTHON ?= {{ cookiecutter.python_command }}

.PHONY: setup smoke test check verify-feature clean-session source-status source-smoke

setup:
	@echo "TODO: install dependencies and prepare data pointers."

smoke:
	@echo "TODO: run fast import/config/data sanity checks."

test:
	@echo "TODO: run unit and integration tests."

check: smoke test
	@echo "TODO: add full local verification commands."

verify-feature:
	@test -n "$(ID)" || (echo "Usage: make verify-feature ID=R001" && exit 2)
	@bash scripts/verify_feature.sh "$(ID)"

source-status:
	@test -d "$(SRC_DIR)" || (echo "Missing SRC_DIR=$(SRC_DIR). Clone or copy your source repo there." && exit 2)
	@if git -C "$(SRC_DIR)" rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		git -C "$(SRC_DIR)" status --short; \
	else \
		echo "SRC_DIR exists but is not a git repository yet: $(SRC_DIR)"; \
	fi

source-smoke:
	@test -d "$(SRC_DIR)" || (echo "Missing SRC_DIR=$(SRC_DIR)" && exit 2)
	@echo "TODO: add source-repo-specific smoke command for $(SRC_DIR)."

clean-session:
	@bash scripts/clean_session.sh

