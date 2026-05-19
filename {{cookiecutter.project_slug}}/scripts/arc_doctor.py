#!/usr/bin/env python3
"""Check AutoResearchClaw backend readiness."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATIC_FILES = [
    "configs/researchclaw.yaml",
    "configs/researchclaw.codex.yaml",
    "configs/researchclaw.openai.yaml",
    "docs/auto_research.md",
    "docs/remote_wsl.md",
    "agents/agents.yaml",
    "templates/AGENT_BRIEF.md",
    "templates/AGENT_RESULT.md",
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


def check(condition: bool, ok: str, fail: str, *, required: bool = True) -> bool:
    if condition:
        print(f"[ok] {ok}")
        return True
    label = "fail" if required else "warn"
    print(f"[{label}] {fail}")
    return not required


def command_version(command: list[str], *, timeout: int = 20) -> tuple[bool, str]:
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, ""
    return proc.returncode == 0, proc.stdout.strip()


def codex_exec_flags(model: str, reasoning_effort: str) -> list[str]:
    flags: list[str] = []
    if model.strip():
        flags.extend(["--model", model.strip()])
    if reasoning_effort.strip():
        flags.extend(["-c", f'model_reasoning_effort="{reasoning_effort.strip()}"'])
    return flags


def codex_live_probe(codex: str, model: str, reasoning_effort: str) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("r+", encoding="utf-8", delete=False) as handle:
        output_path = Path(handle.name)
    try:
        ok, out = command_version(
            [
                codex,
                "exec",
                *codex_exec_flags(model, reasoning_effort),
                "--sandbox",
                "read-only",
                "-C",
                str(ROOT),
                "--skip-git-repo-check",
                "--output-last-message",
                str(output_path),
                "Reply exactly OK.",
            ],
            timeout=120,
        )
        if not ok:
            return False, out
        content = output_path.read_text(encoding="utf-8").strip()
        return content == "OK", content or out
    finally:
        output_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static-only", action="store_true")
    parser.add_argument("--live-probe", action="store_true")
    parser.add_argument("--auth", choices=("codex", "openai"), default="codex")
    parser.add_argument("--arc-dir", required=True)
    parser.add_argument("--venv", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--codex-cli", required=True)
    parser.add_argument("--codex-model", default="gpt-5.5")
    parser.add_argument("--codex-reasoning-effort", default="xhigh")
    args = parser.parse_args()

    ok = True
    for rel in STATIC_FILES:
        ok = check((ROOT / rel).exists(), f"found {rel}", f"missing {rel}") and ok

    if args.static_only:
        print("[arc-check] static AutoResearchClaw harness files are present")
        return 0 if ok else 1

    py_ok, py_out = command_version([args.python, "--version"])
    py_311 = py_ok and any(token.startswith("3.11") or token.startswith("3.12") or token.startswith("3.13") for token in py_out.split())
    ok = check(py_311, f"{args.python} is usable: {py_out}", f"{args.python} must be Python 3.11 or newer") and ok

    arc_dir = ROOT / args.arc_dir
    arc_ready = (arc_dir / "pyproject.toml").exists()
    check(arc_ready, f"ARC source found at {arc_dir}", f"missing ARC source at {arc_dir}; run make arc-bootstrap before arc-run", required=False)

    venv = ROOT / args.venv
    venv_py = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    venv_ready = venv_py.exists()
    check(venv_ready, f"ARC venv found at {venv}", f"missing ARC venv at {venv}; run make arc-bootstrap before arc-run", required=False)

    rc_ok, rc_out = command_version([str(venv_py), "-m", "researchclaw", "--help"]) if venv_py.exists() else (False, "")
    if venv_ready:
        ok = check(rc_ok, "researchclaw CLI is importable in ARC venv", f"researchclaw CLI failed: {rc_out[:300]}") and ok
    else:
        rc_ok = False

    codex_path = shutil.which(args.codex_cli)
    if args.auth == "codex":
        ok = check(codex_path is not None, f"Codex CLI found: {codex_path}", f"Codex CLI not found: {args.codex_cli}") and ok
        if codex_path is not None:
            login_ok, login_out = command_version([codex_path, "login", "status"])
            ok = check(login_ok, f"Codex auth available: {login_out}", f"Codex login status failed: {login_out}") and ok
            if args.codex_model:
                print(f"[ok] Codex model default: {args.codex_model}")
            if args.codex_reasoning_effort:
                print(f"[ok] Codex reasoning effort default: {args.codex_reasoning_effort}")
            if args.live_probe:
                probe_ok, probe_out = codex_live_probe(codex_path, args.codex_model, args.codex_reasoning_effort)
                ok = check(probe_ok, "Codex live probe returned OK", f"Codex live probe failed: {probe_out[:500]}") and ok
        shim_path = ROOT / "scripts" / "codex_acp_shim.py"
        ok = check(shim_path.exists(), f"Codex ACP shim found: {shim_path.relative_to(ROOT)}", "missing scripts/codex_acp_shim.py") and ok
    else:
        check(codex_path is not None, f"Codex CLI found: {codex_path}", f"Codex CLI not found: {args.codex_cli}", required=False)

    if args.auth == "openai":
        api_env = os.environ.get("OPENAI_API_KEY", "")
        ok = check(bool(api_env), "OPENAI_API_KEY is set", "OPENAI_API_KEY is not set") and ok

    check(shutil.which("acpx") is not None, "acpx found for optional external ACP profile", "acpx not found; using harness Codex shim for Codex auth", required=False)
    check(shutil.which("docker") is not None, "Docker CLI found for optional container sandbox", "Docker not found; docker experiment mode is unavailable", required=False)
    check(shutil.which("latexmk") is not None or shutil.which("tectonic") is not None, "LaTeX compiler found", "latexmk/tectonic not found; TeX export compilation is unavailable", required=False)

    config_path = ROOT / args.config
    ok = check(config_path.exists(), f"ARC config found at {config_path}", f"missing ARC config at {config_path}") and ok
    if rc_ok and config_path.exists():
        validate_ok, validate_out = command_version(
            [
                str(venv_py),
                "-m",
                "researchclaw",
                "validate",
                "--config",
                str(config_path),
                "--no-check-paths",
            ]
        )
        ok = check(validate_ok, "ARC config validates with researchclaw", f"ARC config validation failed: {validate_out[:500]}") and ok

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
