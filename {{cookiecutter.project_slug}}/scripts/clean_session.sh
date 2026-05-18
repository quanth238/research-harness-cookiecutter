#!/usr/bin/env bash
set -euo pipefail

mkdir -p work experiments logs results tests docs roles templates scripts configs evals artifacts/figures artifacts/tables paper src/{{ cookiecutter.source_repo_name }}
find . -name ".DS_Store" -delete
echo "Session cleanup complete. Review PROGRESS.md before ending."

