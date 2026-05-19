#!/usr/bin/env python3
"""Validate a lightweight research run record manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    "run_id",
    "task_id",
    "commit",
    "command",
    "config",
    "dataset",
    "split",
    "seed",
    "status",
    "metrics_path",
    "log_path",
]
PLACEHOLDER_PREFIXES = ("<", "YYYY")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scripts/check_run_record.py experiments/manifests/<run_id>.json", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"[run-record] missing file: {path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[run-record] invalid JSON: {exc}", file=sys.stderr)
        return 1

    missing = [field for field in REQUIRED_FIELDS if field not in data or data[field] in ("", None, [])]
    if missing:
        print(f"[run-record] missing required fields: {', '.join(missing)}", file=sys.stderr)
        return 1

    placeholders = [
        field
        for field in REQUIRED_FIELDS
        if isinstance(data.get(field), str) and data[field].strip().startswith(PLACEHOLDER_PREFIXES)
    ]
    if placeholders:
        print(f"[run-record] unresolved placeholder fields: {', '.join(placeholders)}", file=sys.stderr)
        return 1

    if data["status"] not in {"planned", "running", "passed", "failed", "blocked", "inconclusive", "unstable"}:
        print(f"[run-record] invalid status: {data['status']}", file=sys.stderr)
        return 1

    if data["status"] == "passed":
        for field in ["metrics_path", "log_path"]:
            value = str(data[field]).strip().lower()
            if value in {"none", "n/a", "na"}:
                print(f"[run-record] passed runs must record a concrete {field}", file=sys.stderr)
                return 1

    print(f"[run-record] valid run record: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
