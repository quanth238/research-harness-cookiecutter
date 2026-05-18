#!/usr/bin/env python3
"""Render the template and run minimal generated-project checks."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    cookiecutter = shutil.which("cookiecutter")
    if cookiecutter is None:
        print("cookiecutter is not installed. Install with: python3 -m pip install cookiecutter", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        subprocess.run(
            [
                cookiecutter,
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
        subprocess.run(["make", "source-status"], cwd=generated, check=True)

    print("Template smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

