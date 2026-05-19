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


def markdown_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def has_section_body(lines: list[str]) -> bool:
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("<!--"):
            return True
    return False


def latest_passing_feature(features: list[dict[str, object]]) -> dict[str, object] | None:
    passing = [feature for feature in features if feature.get("state") == "passing"]
    if not passing:
        return None

    def verified_at(feature: dict[str, object]) -> str:
        evidence = feature.get("evidence")
        if isinstance(evidence, dict):
            value = evidence.get("verified_at")
            if isinstance(value, str):
                return value
        return ""

    return max(passing, key=verified_at)


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
    sections = markdown_sections(handoff)
    for heading in ["Current Task", "Verification", "Evidence Artifacts", "Next Best Action"]:
        if heading not in sections:
            return fail(f"session-handoff.md is missing section: {heading}")
        if not has_section_body(sections[heading]):
            return fail(f"session-handoff.md section is empty: {heading}")

    latest = latest_passing_feature(features)
    if latest is not None:
        feature_id = str(latest.get("id"))
        evidence = latest.get("evidence")
        log_path = evidence.get("log_path") if isinstance(evidence, dict) else None
        if not isinstance(log_path, str) or not log_path.strip():
            return fail(f"feature {feature_id} is passing but evidence has no log_path")

        progress = (ROOT / "PROGRESS.md").read_text(encoding="utf-8")
        for path, text in [("session-handoff.md", handoff), ("PROGRESS.md", progress)]:
            if feature_id not in text:
                return fail(f"{path} does not mention latest verified feature {feature_id}")
            if log_path not in text:
                return fail(f"{path} does not mention latest verification evidence {log_path}")

        stale_phrases = [
            ("session-handoff.md", handoff, "Pending initial verification"),
            ("session-handoff.md", handoff, "None yet. Verification logs will be written"),
            ("PROGRESS.md", progress, "Last verified feature: none"),
            ("PROGRESS.md", progress, "pending until commands pass"),
        ]
        for path, text, phrase in stale_phrases:
            if phrase in text:
                return fail(f"{path} still contains stale handoff text: {phrase}")

    print("[handoff-check] handoff artifacts are present and consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
