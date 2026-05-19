#!/usr/bin/env python3
"""Verify required AutoResearchClaw artifacts and imported run records."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> int:
    print(f"[arc-verify] {message}", file=sys.stderr)
    return 1


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def require_file(path: Path, label: str) -> str | None:
    if not path.exists() or not path.is_file():
        return f"missing {label}: {path}"
    if path.stat().st_size == 0:
        return f"empty {label}: {path}"
    return None


def citation_summary(report: dict[str, Any]) -> tuple[int | None, int | None]:
    summary = report.get("summary", report)
    if not isinstance(summary, dict):
        return None, None
    total = summary.get("total", summary.get("total_citations"))
    verified = summary.get("verified", summary.get("verified_citations"))
    try:
        return int(total), int(verified)
    except (TypeError, ValueError):
        return None, None


def citation_report_passes(report: dict[str, Any], min_ratio: float = 1.0) -> tuple[bool, str]:
    total, verified = citation_summary(report)
    if total is not None and verified is not None:
        if total <= 0:
            return False, "citation report has no citations"
        ratio = verified / total
        if ratio < min_ratio:
            return False, f"verified citation ratio {ratio:.3f} < {min_ratio:.3f}"
        return True, f"verified {verified}/{total}"

    explicit = report.get("passed", report.get("ok"))
    if explicit is True:
        return True, "explicit pass"

    status = str(report.get("status", report.get("overall_status", ""))).lower()
    if status in {"passed", "pass", "ok", "success"}:
        return True, f"status={status}"

    return False, "missing citation summary totals"


def verify_run(run_dir: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    required = [
        (run_dir / "pipeline_summary.json", "pipeline summary"),
        (run_dir / "stage-14" / "experiment_summary.json", "experiment summary"),
        (run_dir / "stage-22" / "paper_final.md", "final paper markdown"),
        (run_dir / "stage-23" / "verification_report.json", "citation verification report"),
    ]
    for path, label in required:
        error = require_file(path, label)
        if error:
            errors.append(error)

    summary = load_json(run_dir / "pipeline_summary.json")
    if summary is not None:
        final_status = str(summary.get("final_status", "")).lower()
        if final_status and final_status not in {"done", "passed", "success"}:
            errors.append(f"pipeline final_status is not done: {final_status}")

    experiment_summary = load_json(run_dir / "stage-14" / "experiment_summary.json")
    if experiment_summary is None:
        errors.append("experiment_summary.json is not valid JSON")

    citation = load_json(run_dir / "stage-23" / "verification_report.json")
    if citation is None:
        errors.append("verification_report.json is not valid JSON")
    else:
        passes, reason = citation_report_passes(citation)
        if not passes:
            errors.append(f"citation verification failed: {reason}")

    manifest_path = ROOT / "experiments" / "manifests" / f"{run_dir.name}.json"
    if not manifest_path.exists():
        errors.append(f"missing imported run record: {manifest_path.relative_to(ROOT)}")
    else:
        manifest = load_json(manifest_path)
        if manifest is None:
            errors.append("imported run record is not valid JSON")
        else:
            for field in ["run_id", "command", "config", "metrics_path", "log_path", "artifacts"]:
                if not manifest.get(field):
                    errors.append(f"imported run record missing {field}")
            if manifest.get("metrics_path") in {"none", "n/a", "na"}:
                errors.append("imported run record has no concrete metrics_path")
            if manifest.get("log_path") in {"none", "n/a", "na"}:
                errors.append("imported run record has no concrete log_path")

    return not errors, errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scripts/verify_arc_run.py artifacts/arc-runs/<run_id>", file=sys.stderr)
        return 2

    run_dir = (ROOT / sys.argv[1]).resolve()
    if not run_dir.exists():
        return fail(f"missing run directory: {run_dir}")

    ok, errors = verify_run(run_dir)
    if not ok:
        for error in errors:
            print(f"[arc-verify] {error}", file=sys.stderr)
        return 1

    print(f"[arc-verify] verified AutoResearchClaw run: {run_dir.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
