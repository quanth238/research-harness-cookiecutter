#!/usr/bin/env python3
"""Final strict paper gate for imported AutoResearchClaw runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from verify_arc_run import citation_report_passes, load_json, verify_run


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> int:
    print(f"[arc-paper-gate] {message}", file=sys.stderr)
    return 1


def config_experiment_mode(config_path: Path) -> str:
    if not config_path.exists():
        return ""
    in_experiment = False
    for raw in config_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("experiment:"):
            in_experiment = True
            continue
        if in_experiment and line and not raw.startswith((" ", "\t")):
            in_experiment = False
        if in_experiment and line.strip().startswith("mode:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return ""


def has_metric_content(data: dict[str, Any]) -> bool:
    if data.get("metrics"):
        return True
    if data.get("results"):
        return True
    for key in ["primary_metric", "best_metric", "metric", "conditions", "runs"]:
        if key in data:
            return True
    return bool(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--config", default="configs/researchclaw.codex.yaml")
    args = parser.parse_args()

    run_dir = (ROOT / args.run_dir).resolve()
    if not run_dir.exists():
        return fail(f"missing run directory: {run_dir}")

    verified, errors = verify_run(run_dir)
    if not verified:
        for error in errors:
            print(f"[arc-paper-gate] {error}", file=sys.stderr)
        return 1

    config_path = ROOT / args.config
    mode = config_experiment_mode(config_path)
    if mode == "simulated":
        return fail("experiment.mode is simulated; final paper claims require real experiment execution")
    if not mode:
        return fail(f"could not determine experiment.mode from {args.config}")

    experiment_summary = load_json(run_dir / "stage-14" / "experiment_summary.json")
    if experiment_summary is None or not has_metric_content(experiment_summary):
        return fail("experiment summary has no metric content")

    paper = ROOT / "paper" / run_dir.name / "paper_final.md"
    if not paper.exists() or paper.stat().st_size == 0:
        return fail(f"imported paper is missing or empty: {paper.relative_to(ROOT)}")

    citation = load_json(run_dir / "stage-23" / "verification_report.json")
    if citation is None:
        return fail("citation verification report is invalid")
    passes, reason = citation_report_passes(citation)
    if not passes:
        return fail(f"citation verification did not pass: {reason}")

    manifest = ROOT / "experiments" / "manifests" / f"{run_dir.name}.json"
    if not manifest.exists():
        return fail(f"missing run record: {manifest.relative_to(ROOT)}")

    gate_record = ROOT / "results" / "manifests" / run_dir.name / "paper_gate.json"
    gate_record.parent.mkdir(parents=True, exist_ok=True)
    gate_record.write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "status": "passed",
                "experiment_mode": mode,
                "config": args.config,
                "paper": paper.relative_to(ROOT).as_posix(),
                "manifest": manifest.relative_to(ROOT).as_posix(),
                "citation_status": reason,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"[arc-paper-gate] passed: {gate_record.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
