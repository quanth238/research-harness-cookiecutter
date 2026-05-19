#!/usr/bin/env python3
"""Check that persistent handoff artifacts are present and internally plausible."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AGENTS.md",
    "INITIALIZATION_CONTRACT.md",
    "PROGRESS.md",
    "DECISIONS.md",
    "feature_list.json",
    "session-handoff.md",
    "clean-state-checklist.md",
    "docs/failure-log.md",
]


def fail(message: str) -> int:
    print(f"[handoff-check] {message}", file=sys.stderr)
    return 1


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        return fail(f"missing handoff files: {', '.join(missing)}")

    data = json.loads((ROOT / "feature_list.json").read_text(encoding="utf-8"))
    features = data.get("features", [])
    active = [item for item in features if item.get("state") == "active"]
    active_limit = int(data.get("active_task_limit", 1))
    if len(active) > active_limit:
        return fail(f"active task count {len(active)} exceeds active_task_limit {active_limit}")

    for feature in features:
        state = feature.get("state")
        if state == "passing" and not feature.get("evidence"):
            return fail(f"feature {feature.get('id')} is {state} but has no evidence")

    handoff = (ROOT / "session-handoff.md").read_text(encoding="utf-8")
    for heading in ["Current Task", "Verification", "Evidence Artifacts", "Next Best Action"]:
        if heading not in handoff:
            return fail(f"session-handoff.md is missing section: {heading}")

    print("[handoff-check] handoff artifacts are present and consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
