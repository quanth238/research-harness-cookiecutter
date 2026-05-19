#!/usr/bin/env python3
"""Run or resume AutoResearchClaw through the managed backend."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def venv_python(venv: Path) -> Path:
    if sys.platform == "win32":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def slugify(text: str) -> str:
    keep = []
    for char in text.lower():
        if char.isalnum():
            keep.append(char)
        elif keep and keep[-1] != "-":
            keep.append("-")
    slug = "".join(keep).strip("-")
    return slug[:48] or "topic"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--run-dir")
    parser.add_argument("--arc-dir", required=True)
    parser.add_argument("--venv", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-root", required=True)
    args = parser.parse_args()
    if args.resume and args.smoke:
        print("[arc-run] --smoke cannot be combined with --resume", file=sys.stderr)
        return 2

    py = venv_python(ROOT / args.venv)
    if not py.exists():
        print(f"[arc-run] missing ARC venv python: {py}. Run make arc-bootstrap.", file=sys.stderr)
        return 1

    arc_dir = ROOT / args.arc_dir
    if not (arc_dir / "pyproject.toml").exists():
        print(f"[arc-run] missing ARC source: {arc_dir}. Run make arc-bootstrap.", file=sys.stderr)
        return 1

    config = ROOT / args.config
    if not config.exists():
        print(f"[arc-run] missing config: {config}", file=sys.stderr)
        return 1

    if args.resume:
        if not args.run_dir:
            print("[arc-run] --resume requires --run-dir", file=sys.stderr)
            return 2
        run_dir = ROOT / args.run_dir
        command = [
            str(py),
            "-m",
            "researchclaw",
            "run",
            "--config",
            str(config),
            "--output",
            str(run_dir),
            "--resume",
        ]
    else:
        if not args.topic:
            print("[arc-run] --topic is required unless --resume is set", file=sys.stderr)
            return 2
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = ROOT / args.run_root / f"{stamp}-{slugify(args.topic)}"
        run_dir.mkdir(parents=True, exist_ok=True)
        if args.smoke:
            (run_dir / "HARNESS_RUN_TYPE.json").write_text(
                json.dumps(
                    {
                        "run_type": "smoke",
                        "paper_acceptance_allowed": False,
                        "reason": "Infrastructure smoke run bypassed research-preflight and cannot pass paper gate.",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        command = [
            str(py),
            "-m",
            "researchclaw",
            "run",
            "--config",
            str(config),
            "--topic",
            args.topic,
            "--output",
            str(run_dir),
        ]

    print("$ " + " ".join(command), flush=True)
    proc = subprocess.run(command, cwd=ROOT, check=False)
    print(f"[arc-run] run directory: {run_dir}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
