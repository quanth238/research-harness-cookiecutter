#!/usr/bin/env bash
set -euo pipefail

feature_id="${1:?feature id required}"

{{ cookiecutter.python_command }} - "$feature_id" <<'PY'
import json
import subprocess
import sys

feature_id = sys.argv[1]
with open("feature_list.json", "r", encoding="utf-8") as f:
    data = json.load(f)

if isinstance(data, dict):
    features = data.get("features", [])
else:
    features = data

matches = [item for item in features if item.get("id") == feature_id]
if not matches:
    raise SystemExit(f"Unknown feature id: {feature_id}")

command = matches[0].get("verification")
if not command:
    raise SystemExit(f"Feature {feature_id} has no verification command")

commands = command if isinstance(command, list) else [command]
for item in commands:
    print(f"Running verification for {feature_id}: {item}")
    exit_code = subprocess.call(item, shell=True)
    if exit_code:
        raise SystemExit(exit_code)
PY

