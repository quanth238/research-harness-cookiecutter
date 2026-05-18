#!/usr/bin/env python3
"""Validate the generated research harness structure."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "AGENTS.md",
    "PROGRESS.md",
    "DECISIONS.md",
    "EVAL_PROTOCOL.md",
    "feature_list.json",
    "docs/research_question.md",
    "docs/data.md",
    "docs/experiments.md",
    "docs/paper.md",
    "docs/source_repo.md",
]
ACTIVE_STATES = {"active", "in_progress"}
VALID_STATES = {"not_started", "active", "in_progress", "passing", "verified", "blocked"}


def fail(message: str) -> int:
    print(f"[harness-smoke] {message}", file=sys.stderr)
    return 1


def make_targets() -> set[str]:
    makefile = ROOT / "Makefile"
    targets: set[str] = set()
    pattern = re.compile(r"^([A-Za-z0-9_.-]+)\s*:")
    for line in makefile.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            targets.add(match.group(1))
    return targets


def make_target_from(command: str) -> str | None:
    parts = command.split()
    if not parts or parts[0] != "make":
        return None
    for part in parts[1:]:
        if "=" not in part:
            return part
    return None


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        return fail(f"missing required files: {', '.join(missing)}")

    try:
        data = json.loads((ROOT / "feature_list.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"feature_list.json is invalid JSON: {exc}")

    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        return fail("feature_list.json must contain a top-level features list")

    features = data["features"]
    active_limit = int(data.get("active_task_limit", 1))
    targets = make_targets()
    seen_ids: set[str] = set()
    active_count = 0

    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            return fail(f"feature at index {index} must be an object")

        feature_id = feature.get("id")
        if not feature_id:
            return fail(f"feature at index {index} is missing id")
        if feature_id in seen_ids:
            return fail(f"duplicate feature id: {feature_id}")
        seen_ids.add(feature_id)

        state = feature.get("state")
        if state not in VALID_STATES:
            return fail(f"feature {feature_id} has invalid state: {state}")
        if state in ACTIVE_STATES:
            active_count += 1

        if not feature.get("behavior"):
            return fail(f"feature {feature_id} is missing behavior")

        verification = feature.get("verification")
        if not verification:
            return fail(f"feature {feature_id} is missing verification")
        commands = verification if isinstance(verification, list) else [verification]
        if not all(isinstance(command, str) and command.strip() for command in commands):
            return fail(f"feature {feature_id} has an invalid verification command")

        for command in commands:
            target = make_target_from(command)
            if target and target not in targets:
                return fail(f"feature {feature_id} references missing Make target: {target}")

    if active_count > active_limit:
        return fail(f"active task count {active_count} exceeds active_task_limit {active_limit}")

    print("[harness-smoke] harness structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
