#!/usr/bin/env bash
set -euo pipefail

echo "[init] repo: $(pwd)"
echo "[init] python: $({{ cookiecutter.python_command }} --version 2>/dev/null || true)"

make setup
make smoke

echo "[init] harness startup path completed."
echo "[init] next: read PROGRESS.md, DECISIONS.md, and feature_list.json."

