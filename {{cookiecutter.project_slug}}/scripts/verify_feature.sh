#!/usr/bin/env bash
set -euo pipefail

feature_id="${1:?feature id required}"
{{ cookiecutter.python_command }} scripts/verify_feature.py "$feature_id"
