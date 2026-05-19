#!/usr/bin/env python3
"""Import selected AutoResearchClaw artifacts into harness-controlled records."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> int:
    print(f"[arc-import] {message}", file=sys.stderr)
    return 1


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def copy_if_exists(src: Path, dst: Path) -> str | None:
    if not src.exists() or not src.is_file():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return relative(dst)


def git_commit() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else "unknown"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scripts/import_arc_run.py artifacts/arc-runs/<run_id>", file=sys.stderr)
        return 2

    run_dir = (ROOT / sys.argv[1]).resolve()
    if not run_dir.exists():
        return fail(f"missing run directory: {run_dir}")

    run_id = run_dir.name
    summary = load_json(run_dir / "pipeline_summary.json")
    config_path = ROOT / "configs" / "researchclaw.yaml"
    imported_dir = ROOT / "results" / "manifests" / run_id
    paper_dir = ROOT / "paper" / run_id
    imported_dir.mkdir(parents=True, exist_ok=True)
    paper_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    for src, dst in [
        (run_dir / "pipeline_summary.json", imported_dir / "pipeline_summary.json"),
        (run_dir / "stage-14" / "experiment_summary.json", imported_dir / "experiment_summary.json"),
        (run_dir / "stage-20" / "quality_report.json", imported_dir / "quality_report.json"),
        (run_dir / "stage-22" / "paper_final.md", paper_dir / "paper_final.md"),
        (run_dir / "stage-22" / "paper.tex", paper_dir / "paper.tex"),
        (run_dir / "stage-22" / "references.bib", paper_dir / "references.bib"),
        (run_dir / "stage-23" / "verification_report.json", imported_dir / "citation_verification.json"),
        (run_dir / "stage-23" / "references_verified.bib", paper_dir / "references_verified.bib"),
    ]:
        copied_path = copy_if_exists(src, dst)
        if copied_path:
            copied.append(copied_path)

    checksums = {
        path: sha256_file(ROOT / path)
        for path in copied
        if (ROOT / path).exists() and (ROOT / path).is_file()
    }
    checksum_path = imported_dir / "checksums.json"
    checksum_path.write_text(json.dumps(checksums, indent=2) + "\n", encoding="utf-8")
    copied.append(relative(checksum_path))

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    metrics_path = f"results/manifests/{run_id}/experiment_summary.json"
    log_path = f"results/manifests/{run_id}/pipeline_summary.json"
    manifest = {
        "run_id": run_id,
        "task_id": "ARC-RUN",
        "commit": git_commit(),
        "command": f"make arc-run/import RUN_DIR={relative(run_dir)}",
        "config": "configs/researchclaw.yaml",
        "config_hash": sha256_file(config_path) if config_path.exists() else "none",
        "dataset": "arc-managed",
        "dataset_version": "none",
        "split": "none",
        "seed": 0,
        "hardware": "see AutoResearchClaw hardware profile if present",
        "started_at": summary.get("generated", now),
        "ended_at": now,
        "status": "passed",
        "metrics_path": metrics_path if (ROOT / metrics_path).exists() else "none",
        "log_path": log_path if (ROOT / log_path).exists() else "none",
        "artifacts": copied,
        "notes": "Imported from AutoResearchClaw managed backend; final acceptance requires arc-paper-gate.",
    }
    manifest_path = ROOT / "experiments" / "manifests" / f"{run_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    index = {
        "run_id": run_id,
        "source_run_dir": relative(run_dir),
        "manifest": relative(manifest_path),
        "artifacts": copied,
        "imported_at": now,
    }
    index_path = imported_dir / "import_index.json"
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"[arc-import] imported {run_id}")
    print(f"[arc-import] run record: {relative(manifest_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
