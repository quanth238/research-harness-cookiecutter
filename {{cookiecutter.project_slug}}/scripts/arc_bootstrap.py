#!/usr/bin/env python3
"""Clone and install AutoResearchClaw as a managed optional backend."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path | None = None) -> None:
    print("$ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd or ROOT, check=True)


def venv_python(venv: Path) -> Path:
    if sys.platform == "win32":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-url", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--arc-dir", required=True)
    parser.add_argument("--venv", required=True)
    parser.add_argument("--python", required=True)
    args = parser.parse_args()

    arc_dir = ROOT / args.arc_dir
    venv_dir = ROOT / args.venv

    if arc_dir.exists():
        if not (arc_dir / ".git").exists():
            print(f"[arc-bootstrap] {arc_dir} exists but is not a git repository", file=sys.stderr)
            return 1
        run(["git", "fetch", "--depth", "1", "origin", args.ref], cwd=arc_dir)
    else:
        arc_dir.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth", "1", args.repo_url, str(arc_dir)])
        run(["git", "fetch", "--depth", "1", "origin", args.ref], cwd=arc_dir)

    run(["git", "checkout", "--detach", args.ref], cwd=arc_dir)
    run([args.python, "-m", "venv", str(venv_dir)])

    py = venv_python(venv_dir)
    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(py), "-m", "pip", "install", "-e", str(arc_dir)])

    print(f"[arc-bootstrap] installed AutoResearchClaw at {arc_dir}")
    print(f"[arc-bootstrap] runtime python: {py}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
