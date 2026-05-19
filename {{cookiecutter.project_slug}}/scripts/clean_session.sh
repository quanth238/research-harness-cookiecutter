#!/usr/bin/env bash
set -euo pipefail

mkdir -p work/verification_logs experiments/manifests experiments/runs logs/verification results/manifests tests docs roles templates scripts configs evals artifacts/figures artifacts/tables artifacts/checkpoints paper src
find . -name ".DS_Store" -delete

{{ cookiecutter.python_command }} scripts/validate_harness.py

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[clean-session] harness git status:"
  git status --short
fi

echo "[clean-session] Review before exit:"
echo "  - PROGRESS.md updated with commands, evidence, and next action"
echo "  - DECISIONS.md updated if research assumptions changed"
echo "  - docs/failure-log.md updated for failed, negative, or unstable runs"
echo "  - feature_list.json state matches actual verification evidence"
echo "  - make handoff-check passes or the remaining gap is documented"
echo "Session cleanup complete."
