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
    "INITIALIZATION_CONTRACT.md",
    "PROGRESS.md",
    "DECISIONS.md",
    "EVAL_PROTOCOL.md",
    "clean-state-checklist.md",
    "session-handoff.md",
    "feature_list.json",
    "docs/research_question.md",
    "docs/data.md",
    "docs/metrics.md",
    "docs/baselines.md",
    "docs/novelty.md",
    "docs/venue_readiness.md",
    "docs/experiments.md",
    "docs/testing.md",
    "docs/artifacts.md",
    "docs/paper.md",
    "docs/source_repo.md",
    "docs/failure-log.md",
    "docs/auto_research.md",
    "docs/remote_wsl.md",
    "configs/researchclaw.yaml",
    "configs/researchclaw.codex.yaml",
    "configs/researchclaw.openai.yaml",
    "agents/agents.yaml",
    "templates/RUN_RECORD.json",
    "templates/AGENT_BRIEF.md",
    "templates/AGENT_RESULT.md",
    "templates/ARC_3_AGENT_PROMPT.md",
    "scripts/verify_feature.py",
    "scripts/verify_feature.sh",
    "scripts/clean_session.sh",
    "scripts/check_handoff.py",
    "scripts/check_run_record.py",
    "scripts/verify_research_preflight.py",
    "scripts/arc_bootstrap.py",
    "scripts/arc_doctor.py",
    "scripts/arc_run.py",
    "scripts/codex_acp_shim.py",
    "scripts/import_arc_run.py",
    "scripts/verify_arc_run.py",
    "scripts/verify_paper_gate.py",
    "scripts/run_agent.py",
    "scripts/remote_wsl_exec.sh",
    "scripts/remote_wsl_doctor.sh",
    "scripts/sync_codex_auth_to_wsl.sh",
]
ACTIVE_STATES = {"active"}
VALID_STATES = {"not_started", "active", "blocked", "passing"}


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
    if active_limit != 1:
        return fail("active_task_limit must be 1 for the default harness pattern")

    allowed_states = set(data.get("allowed_states", sorted(VALID_STATES)))
    if allowed_states != VALID_STATES:
        return fail(f"allowed_states must be exactly {sorted(VALID_STATES)}")

    targets = make_targets()
    seen_ids: set[str] = set()
    active_count = 0
    dependency_edges: dict[str, list[str]] = {}
    feature_by_id: dict[str, dict[str, object]] = {}

    for index, feature in enumerate(features):
        if not isinstance(feature, dict):
            return fail(f"feature at index {index} must be an object")

        feature_id = feature.get("id")
        if not feature_id:
            return fail(f"feature at index {index} is missing id")
        if feature_id in seen_ids:
            return fail(f"duplicate feature id: {feature_id}")
        seen_ids.add(feature_id)
        feature_by_id[feature_id] = feature

        state = feature.get("state")
        if state not in VALID_STATES:
            return fail(f"feature {feature_id} has invalid state: {state}")
        if state in ACTIVE_STATES:
            active_count += 1

        if not feature.get("behavior"):
            return fail(f"feature {feature_id} is missing behavior")

        dependency_edges[feature_id] = feature.get("dependencies", [])
        if not isinstance(dependency_edges[feature_id], list):
            return fail(f"feature {feature_id} dependencies must be a list")

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

        if state == "passing" and not feature.get("evidence"):
            return fail(f"feature {feature_id} is {state} but has no evidence")

    for feature_id, dependencies in dependency_edges.items():
        for dependency in dependencies:
            if dependency not in seen_ids:
                return fail(f"feature {feature_id} depends on unknown feature id: {dependency}")
            feature_state = feature_by_id[feature_id].get("state")
            dependency_state = feature_by_id[dependency].get("state")
            if feature_state in {"active", "passing"} and dependency_state != "passing":
                return fail(
                    f"feature {feature_id} is {feature_state} but dependency {dependency} is {dependency_state}"
                )

    if active_count > active_limit:
        return fail(f"active task count {active_count} exceeds active_task_limit {active_limit}")

    try:
        json.loads((ROOT / "templates/RUN_RECORD.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"templates/RUN_RECORD.json is invalid JSON: {exc}")

    print("[harness-smoke] harness structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
