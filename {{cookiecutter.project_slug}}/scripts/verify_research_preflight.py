#!/usr/bin/env python3
"""Strict pre-run research quality gates for ARC-managed paper runs."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDERS = {
    "",
    "none",
    "n/a",
    "na",
    "tbd",
    "todo",
    "unknown",
    "not configured",
    "not set",
    "fill me",
    "placeholder",
}
ALLOWED_VENUES = {"neurips", "icml", "iclr", "aaai", "cvpr"}
PASSING_BASELINE_STATES = {"passed", "pass", "verified", "reproduced", "accepted"}
WEAK_NOVELTY_PATTERNS = [
    "small module",
    "minor improvement",
    "just improvement",
    "simple improvement",
    "add a module",
    "add the module",
    "incremental improvement",
    "slight improvement",
]


class GateError(Exception):
    """Raised when a preflight gate fails."""


def fail(message: str) -> int:
    print(f"[research-preflight] {message}", file=sys.stderr)
    return 1


def clean(value: str) -> str:
    return value.strip().strip("`").strip()


def unresolved(value: str) -> bool:
    value = clean(value)
    lowered = value.lower()
    return (
        lowered in PLACEHOLDERS
        or lowered.startswith("<")
        or ("{" * 2) in value
        or ("}" * 2) in value
        or lowered.startswith("write ")
        or lowered.startswith("define ")
        or lowered.startswith("what ")
        or lowered.startswith("which ")
        or " / " in lowered
    )


def require_file(path: str, label: str) -> Path:
    value = clean(path)
    if unresolved(value):
        raise GateError(f"{label} is unresolved")
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    if not candidate.exists():
        raise GateError(f"{label} does not exist: {value}")
    return candidate


def read(path: str) -> str:
    full = ROOT / path
    if not full.exists():
        raise GateError(f"missing {path}")
    return full.read_text(encoding="utf-8")


def field(text: str, label: str, *, required: bool = True) -> str:
    pattern = re.compile(rf"^\s*(?:[-*]\s*)?{re.escape(label)}\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        if required:
            raise GateError(f"missing field: {label}")
        return ""
    value = clean(match.group(1))
    if required and unresolved(value):
        raise GateError(f"unresolved field: {label}")
    return value


def split_table_row(raw: str) -> list[str]:
    return [cell.strip() for cell in raw.strip().strip("|").split("|")]


def table_rows(text: str, heading: str) -> list[list[str]]:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip().lower() == heading.lower():
            start = index + 1
            break
    if start is None:
        raise GateError(f"missing table section: {heading}")

    rows: list[list[str]] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## ") and rows:
            break
        if not stripped.startswith("|"):
            continue
        cells = split_table_row(stripped)
        if not cells or all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        raise GateError(f"{heading} has no data rows")
    return rows[1:]


def load_json(path: Path, label: str) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GateError(f"{label} is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise GateError(f"{label} must be a JSON object")
    return data


def check_no_unresolved(values: Iterable[tuple[str, str]]) -> None:
    for label, value in values:
        if unresolved(value):
            raise GateError(f"unresolved field: {label}")


def verify_data() -> None:
    text = read("docs/data.md")
    required = [
        ("Dataset name", field(text, "Dataset name")),
        ("Version", field(text, "Version")),
        ("Location", field(text, "Location")),
        ("Checksum or manifest", field(text, "Checksum or manifest")),
        ("Train", field(text, "Train")),
        ("Validation", field(text, "Validation")),
        ("Test", field(text, "Test")),
        ("Leakage check", field(text, "Leakage check")),
    ]
    check_no_unresolved(required)
    if field(text, "Leakage check").lower() not in {"passed", "pass", "verified", "clean"}:
        raise GateError("Leakage check must be passed, verified, or clean")
    for label in ["Data manifest path", "Split manifest path", "Preprocessing config path", "Last verification log"]:
        require_file(field(text, label), label)


def verify_metric() -> None:
    text = read("docs/metrics.md")
    direction = field(text, "Direction").lower()
    if direction not in {"higher is better", "lower is better", "maximize", "minimize"}:
        raise GateError("Direction must be one of: higher is better, lower is better, maximize, minimize")
    check_no_unresolved(
        [
            ("Name", field(text, "Name")),
            ("Aggregation rule", field(text, "Aggregation rule")),
            ("Required splits", field(text, "Required splits")),
            ("Expected output", field(text, "Expected output")),
        ]
    )
    require_file(field(text, "Script"), "Metric script")
    require_file(field(text, "Fixture"), "Known-answer fixture")
    command = field(text, "Verification command")
    proc = subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.returncode:
        raise GateError(f"metric verification command failed ({proc.returncode}): {command}\n{proc.stdout}")


def verify_baseline() -> None:
    text = read("docs/baselines.md")
    source = field(text, "Source of accepted numbers")
    if source.lower() not in {"own-run", "our-run", "harness-run", "local-run"}:
        raise GateError("Source of accepted numbers must be own-run, our-run, harness-run, or local-run")

    accepted = False
    for row in table_rows(text, "## Accepted Baseline Runs"):
        if len(row) < 7:
            raise GateError("Accepted Baseline Runs rows must have 7 columns")
        baseline, run_record, metrics_path, config_path, dataset_split, seed, status = row[:7]
        check_no_unresolved(
            [
                ("Baseline", baseline),
                ("Run Record", run_record),
                ("Metrics Path", metrics_path),
                ("Config Path", config_path),
                ("Dataset/Split", dataset_split),
                ("Seed", seed),
                ("Status", status),
            ]
        )
        if status.lower() not in PASSING_BASELINE_STATES:
            continue
        record_path = require_file(run_record, "Baseline run record")
        require_file(metrics_path, "Baseline metrics path")
        require_file(config_path, "Baseline config path")
        record = load_json(record_path, "Baseline run record")
        for key in ["command", "config", "config_hash", "dataset", "dataset_version", "split", "seed", "metrics_path", "log_path"]:
            value = str(record.get(key, "")).strip()
            if unresolved(value):
                raise GateError(f"baseline run record has unresolved {key}")
        if str(record.get("status", "")).lower() != "passed":
            raise GateError("baseline run record status must be passed")
        require_file(str(record["metrics_path"]), "Baseline run record metrics_path")
        require_file(str(record["log_path"]), "Baseline run record log_path")
        accepted = True
    if not accepted:
        raise GateError("no accepted reproduced baseline run was found")


def verify_novelty() -> None:
    rq = read("docs/research_question.md")
    novelty = read("docs/novelty.md")
    check_no_unresolved(
        [
            ("Hypothesis", field(rq, "Hypothesis")),
            ("Current Theory", field(rq, "Current Theory")),
            ("Evidence unit", field(rq, "Evidence unit")),
            ("Gap statement", field(novelty, "Gap statement")),
            ("Community importance", field(novelty, "Community importance")),
            ("Theoretical mechanism", field(novelty, "Theoretical mechanism")),
            ("Cross-field source", field(novelty, "Cross-field source")),
            ("Falsifiable prediction", field(novelty, "Falsifiable prediction")),
            ("Rejection condition", field(novelty, "Rejection condition")),
        ]
    )
    contribution = field(novelty, "Contribution type").lower()
    decision = field(novelty, "Incremental-risk decision").lower()
    if not any(token in contribution for token in ["theory", "mechanism", "principle", "framework", "phenomenon"]):
        raise GateError("Contribution type must be theory/mechanism/principle/framework/phenomenon driven")
    if not any(token in decision for token in ["not-incremental", "theory-driven", "mechanism-driven"]):
        raise GateError("Incremental-risk decision must explicitly reject incremental framing")
    for value in [contribution, decision]:
        for pattern in WEAK_NOVELTY_PATTERNS:
            if pattern in value:
                raise GateError(f"novelty framing is too incremental: {pattern}")


def verify_venue() -> None:
    text = read("docs/venue_readiness.md")
    venue = field(text, "Target venue").lower()
    if venue not in ALLOWED_VENUES:
        raise GateError(f"Target venue must be one of: {', '.join(sorted(ALLOWED_VENUES))}")
    for label in [
        "Problem significance",
        "Baseline standard",
        "Ablation plan",
        "Statistical evidence plan",
        "Reproducibility package",
        "Citation grounding plan",
        "Non-incremental contribution",
    ]:
        field(text, label)
    unchecked = [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^- \[[ xX]\]", line.strip()) and not line.strip().lower().startswith("- [x]")
    ]
    if unchecked:
        raise GateError("venue checklist has unchecked items: " + "; ".join(unchecked))


def verify_protocol() -> None:
    verify_data()
    verify_metric()
    verify_baseline()
    verify_novelty()
    verify_venue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "gate",
        choices=["data", "metric", "baseline", "novelty", "venue", "protocol", "all"],
    )
    args = parser.parse_args()

    gates = {
        "data": verify_data,
        "metric": verify_metric,
        "baseline": verify_baseline,
        "novelty": verify_novelty,
        "venue": verify_venue,
        "protocol": verify_protocol,
        "all": verify_protocol,
    }
    try:
        gates[args.gate]()
    except GateError as exc:
        return fail(str(exc))

    print(f"[research-preflight] {args.gate} gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
