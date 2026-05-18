#!/usr/bin/env python3
"""Render the template and run minimal generated-project checks."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def cookiecutter_command() -> list[str] | None:
    module_probe = subprocess.run(
        [sys.executable, "-m", "cookiecutter", "--version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if module_probe.returncode == 0:
        return [sys.executable, "-m", "cookiecutter"]

    executable = shutil.which("cookiecutter")
    if executable is None:
        return None

    executable_probe = subprocess.run(
        [executable, "--version"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if executable_probe.returncode == 0:
        return [executable]

    return None


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    cookiecutter = cookiecutter_command()
    if cookiecutter is None:
        print("cookiecutter is not installed. Install with: python3 -m pip install cookiecutter", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(
            cookiecutter
            + [
                str(root),
                "--no-input",
                "project_name=Smoke Test Harness",
                "source_repo_name=source",
            ],
            cwd=tmp_path,
            check=True,
        )
        generated = tmp_path / "smoke-test-harness"
        subprocess.run(["./init.sh"], cwd=generated, check=True)
        subprocess.run(["make", "verify-feature", "ID=R001"], cwd=generated, check=True)

        missing_source = subprocess.run(
            ["make", "source-status"],
            cwd=generated,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if missing_source.returncode == 0:
            print("source-status unexpectedly passed before a source repo was added", file=sys.stderr)
            return 1

        source_dir = generated / "src" / "source"
        source_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=source_dir, check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["make", "source-status"], cwd=generated, check=True)

        source_smoke = subprocess.run(
            ["make", "source-smoke"],
            cwd=generated,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if source_smoke.returncode == 0:
            print("source-smoke unexpectedly passed before it was configured", file=sys.stderr)
            return 1

    print("Template smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
