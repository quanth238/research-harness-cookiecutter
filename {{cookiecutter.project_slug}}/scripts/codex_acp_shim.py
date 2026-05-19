#!/usr/bin/env python3
"""Minimal acpx-compatible shim backed by the logged-in Codex CLI.

This script intentionally never reads ``~/.codex/auth.json``. Codex auth stays
behind the supported ``codex`` CLI boundary.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def fail(message: str) -> int:
    print(f"[codex-acp-shim] {message}", file=sys.stderr)
    return 1


def split_acpx_args(argv: list[str]) -> tuple[dict[str, str | bool], str, list[str]]:
    options: dict[str, str | bool] = {
        "cwd": ".",
        "max_turns": "1",
        "ttl": "0",
        "approve_all": False,
    }
    args = list(argv)
    while args:
        head = args.pop(0)
        if head == "--cwd":
            if not args:
                raise ValueError("--cwd requires a value")
            options["cwd"] = args.pop(0)
        elif head == "--max-turns":
            if not args:
                raise ValueError("--max-turns requires a value")
            options["max_turns"] = args.pop(0)
        elif head == "--ttl":
            if not args:
                raise ValueError("--ttl requires a value")
            options["ttl"] = args.pop(0)
        elif head == "--approve-all":
            options["approve_all"] = True
        elif head.startswith("-"):
            raise ValueError(f"unsupported acpx option: {head}")
        else:
            return options, head, args
    raise ValueError("missing ACP agent command")


def handle_session(rest: list[str]) -> int:
    if len(rest) < 2 or rest[0] != "sessions":
        return 2
    action = rest[1]
    if action not in {"ensure", "new", "close"}:
        return fail(f"unsupported sessions action: {action}")
    print(f"[acpx] session {action} ok")
    return 0


def parse_prompt(rest: list[str]) -> tuple[str, str]:
    session_name = "researchclaw"
    prompt_parts: list[str] = []
    read_stdin = False
    args = list(rest)
    while args:
        item = args.pop(0)
        if item == "-s":
            if not args:
                raise ValueError("-s requires a session name")
            session_name = args.pop(0)
        elif item == "-f":
            if not args:
                raise ValueError("-f requires a path or '-'")
            source = args.pop(0)
            if source != "-":
                prompt_parts.append(Path(source).read_text(encoding="utf-8"))
            else:
                read_stdin = True
        else:
            prompt_parts.append(item)
            if args:
                prompt_parts.extend(args)
                args.clear()
    if read_stdin:
        prompt_parts.append(sys.stdin.read())
    return session_name, "\n".join(part for part in prompt_parts if part)


def codex_login_ok(codex: str) -> bool:
    proc = subprocess.run(
        [codex, "login", "status"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=30,
    )
    return proc.returncode == 0


def codex_exec_flags() -> list[str]:
    flags: list[str] = []
    model = os.environ.get("CODEX_MODEL", "gpt-5.5").strip()
    reasoning_effort = os.environ.get("CODEX_REASONING_EFFORT", "xhigh").strip()
    if model:
        flags.extend(["--model", model])
    if reasoning_effort:
        flags.extend(["-c", f'model_reasoning_effort="{reasoning_effort}"'])
    return flags


def run_codex(codex: str, cwd: str, prompt: str) -> int:
    if not prompt.strip():
        return fail("empty prompt")
    with tempfile.NamedTemporaryFile("r+", encoding="utf-8", delete=False) as handle:
        output_path = Path(handle.name)
    try:
        command = [
            codex,
            "exec",
            *codex_exec_flags(),
            "--sandbox",
            "read-only",
            "-C",
            str(Path(cwd).resolve()),
            "--skip-git-repo-check",
            "--output-last-message",
            str(output_path),
            prompt,
        ]
        proc = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if proc.returncode != 0:
            if proc.stdout:
                print(proc.stdout, file=sys.stderr)
            return proc.returncode
        content = output_path.read_text(encoding="utf-8")
        print(content, end="" if content.endswith("\n") else "\n")
        return 0
    finally:
        output_path.unlink(missing_ok=True)


def main() -> int:
    argv = sys.argv[1:]
    if not argv or argv[0] in {"-h", "--help"}:
        print("Usage: codex_acp_shim.py [acpx-options] codex sessions <ensure|new|close> ...")
        print("   or: codex_acp_shim.py [acpx-options] codex -s <session> <prompt>")
        print("   or: codex_acp_shim.py [acpx-options] codex -s <session> -f -")
        return 0

    try:
        options, agent, rest = split_acpx_args(argv)
    except ValueError as exc:
        return fail(str(exc))

    if rest and rest[0] == "sessions":
        return handle_session(rest)

    codex = shutil.which(agent) or shutil.which("codex")
    if codex is None:
        return fail(f"Codex CLI not found for agent: {agent}")
    if not codex_login_ok(codex):
        return fail("Codex CLI is not logged in; run `codex login` outside the harness")

    try:
        _session_name, prompt = parse_prompt(rest)
    except (OSError, ValueError) as exc:
        return fail(str(exc))
    return run_codex(codex, str(options["cwd"]), prompt)


if __name__ == "__main__":
    raise SystemExit(main())
