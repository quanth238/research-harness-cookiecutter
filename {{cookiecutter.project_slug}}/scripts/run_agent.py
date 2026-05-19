#!/usr/bin/env python3
"""Launch a bounded Codex CLI worker from a role brief."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> int:
    print(f"[agent-run] {message}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--codex-cli", default="codex")
    parser.add_argument("--codex-model", default=os.environ.get("CODEX_MODEL", "gpt-5.5"))
    parser.add_argument("--codex-reasoning-effort", default=os.environ.get("CODEX_REASONING_EFFORT", "xhigh"))
    args = parser.parse_args()

    brief_path = ROOT / "agents" / f"{args.role}.md"
    if not brief_path.exists():
        return fail(f"unknown role or missing brief: {brief_path.relative_to(ROOT)}")

    codex = shutil.which(args.codex_cli)
    if codex is None:
        return fail(f"Codex CLI not found: {args.codex_cli}. Run make arc-doctor.")

    task_id = args.task
    run_dir = ROOT / "work" / "agent_runs" / task_id
    outbox = ROOT / "work" / "agent_outbox" / task_id
    run_dir.mkdir(parents=True, exist_ok=True)
    outbox.mkdir(parents=True, exist_ok=True)

    result_path = outbox / "AGENT_RESULT.md"
    prompt = f"""You are the {args.role} role agent for this research harness.

Read:
- AGENTS.md
- INITIALIZATION_CONTRACT.md
- feature_list.json
- {brief_path.relative_to(ROOT).as_posix()}

Task id: {task_id}

Rules:
- Work only on this assigned task.
- Communicate through {result_path.relative_to(ROOT).as_posix()}.
- Do not mark any feature passing.
- Do not claim research results without recorded evidence.
- If you need implementation changes, make them directly and report them.

Write the final result to {result_path.relative_to(ROOT).as_posix()} using templates/AGENT_RESULT.md.
"""
    prompt_path = run_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    codex_flags: list[str] = []
    if args.codex_model.strip():
        codex_flags.extend(["--model", args.codex_model.strip()])
    if args.codex_reasoning_effort.strip():
        codex_flags.extend(["-c", f'model_reasoning_effort="{args.codex_reasoning_effort.strip()}"'])

    command = [
        codex,
        "exec",
        *codex_flags,
        "--sandbox",
        "workspace-write",
        "-C",
        str(ROOT),
        "--skip-git-repo-check",
        prompt,
    ]
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    proc = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (run_dir / "stdout.log").write_text(proc.stdout, encoding="utf-8")
    (run_dir / "metadata.json").write_text(
        (
            "{\n"
            f'  "task": "{task_id}",\n'
            f'  "role": "{args.role}",\n'
            f'  "started_at": "{started}",\n'
            f'  "exit_code": {proc.returncode}\n'
            "}\n"
        ),
        encoding="utf-8",
    )

    if proc.returncode != 0:
        return fail(f"Codex worker exited {proc.returncode}; see {run_dir.relative_to(ROOT) / 'stdout.log'}")
    if not result_path.exists():
        return fail(f"worker completed but did not write {result_path.relative_to(ROOT)}")

    print(f"[agent-run] completed {args.role}/{task_id}: {result_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
