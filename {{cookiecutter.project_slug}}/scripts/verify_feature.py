#!/usr/bin/env python3
"""Run, log, and record verification commands registered in feature_list.json."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scripts/verify_feature.py FEATURE_ID", file=sys.stderr)
        return 2

    feature_id = sys.argv[1]
    feature_path = ROOT / "feature_list.json"
    data = json.loads(feature_path.read_text(encoding="utf-8"))
    features = data.get("features", []) if isinstance(data, dict) else data
    matches = [item for item in features if item.get("id") == feature_id]
    if not matches:
        print(f"Unknown feature id: {feature_id}", file=sys.stderr)
        return 2

    feature = matches[0]
    commands = feature.get("verification")
    if not commands:
        print(f"Feature {feature_id} has no verification command", file=sys.stderr)
        return 2
    if isinstance(commands, str):
        commands = [commands]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_dir = ROOT / "work" / "verification_logs" / feature_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{stamp}.log"
    relative_log_path = log_path.relative_to(ROOT).as_posix()
    results: list[dict[str, object]] = []

    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"feature_id: {feature_id}\n")
        log.write(f"started_at: {stamp}\n")
        log.write("commands:\n")
        for command in commands:
            log.write(f"- {command}\n")
        log.write("\n")

        for command in commands:
            print(f"Running verification for {feature_id}: {command}")
            log.write(f"$ {command}\n")
            proc = subprocess.run(
                command,
                cwd=ROOT,
                shell=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            log.write(proc.stdout)
            log.write(f"\nexit_code: {proc.returncode}\n\n")
            print(proc.stdout, end="")
            results.append({"command": command, "exit_code": proc.returncode})
            if proc.returncode:
                feature["state"] = "active"
                feature["evidence"] = {
                    "verified_at": stamp,
                    "status": "failed",
                    "log_path": relative_log_path,
                    "commands": results,
                }
                feature_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                print(f"Verification failed for {feature_id}. Log: {relative_log_path}", file=sys.stderr)
                return proc.returncode

    feature["state"] = "passing"
    feature["claim_status"] = "verified"
    feature["evidence"] = {
        "verified_at": stamp,
        "status": "passed",
        "log_path": relative_log_path,
        "commands": results,
    }
    feature_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Verification passed for {feature_id}. Evidence recorded at {relative_log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
