#!/usr/bin/env python3
"""Render the template and run minimal generated-project checks."""

from __future__ import annotations

import json
import os
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


def refresh_handoff_files(generated: Path, log_path: str) -> None:
    (generated / "session-handoff.md").write_text(
        f"""# Session Handoff

## Current Task
No active task. R001 is verified.

## What Changed
Generated harness template was initialized and structurally verified.

## Verification
R001 passed with `make verify-feature ID=R001`.

## Evidence Artifacts
- `{log_path}`

## Commands

- Startup: `./init.sh`
- Verification: `make verify-feature ID=R001`
- Focused debug: none

## Open Risks
Source repository and research-specific checks are not configured yet.

## Next Best Action
Clone or copy the source repository into `src/source`, then replace placeholder verification targets with project-specific checks.
""",
        encoding="utf-8",
    )
    (generated / "PROGRESS.md").write_text(
        f"""# Progress

## Current State
- Active task: none
- Last verified feature: R001
- Current blocker: none
- Source path: `src/source`

## Session Log
| Date | Role | Task | Commands run | Result | Next action |
|---|---|---|---|---|---|
| smoke-test | harness | R001 | `./init.sh`, `make verify-feature ID=R001` | passed; evidence `{log_path}` | clone or copy source repo into `src/source` |

## Next Atomic Actions
1. Clone or copy the source repo into `src/source`.
2. Fill `docs/research_question.md`.
3. Replace placeholder commands in `Makefile`.
4. Rewrite `feature_list.json` with real research tasks.
""",
        encoding="utf-8",
    )


def create_fake_arc_run(
    generated: Path,
    run_id: str,
    *,
    missing_citation: bool = False,
    missing_metrics: bool = False,
) -> Path:
    run_dir = generated / "artifacts" / "arc-runs" / run_id
    (run_dir / "stage-14").mkdir(parents=True, exist_ok=True)
    (run_dir / "stage-22").mkdir(parents=True, exist_ok=True)
    (run_dir / "stage-23").mkdir(parents=True, exist_ok=True)
    (run_dir / "pipeline_summary.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "final_status": "done",
                "final_stage": 23,
                "generated": "2026-05-19T00:00:00+00:00",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if not missing_metrics:
        (run_dir / "stage-14" / "experiment_summary.json").write_text(
            json.dumps(
                {
                    "metrics": {"primary_metric": 0.81},
                    "conditions": [{"name": "baseline"}, {"name": "method"}],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    (run_dir / "stage-22" / "paper_final.md").write_text(
        "# Fake ARC Paper\n\nThis paper is backed by imported fake smoke-test evidence.\n",
        encoding="utf-8",
    )
    (run_dir / "stage-22" / "paper.tex").write_text(
        "\\documentclass{article}\\begin{document}Fake ARC Paper\\end{document}\n",
        encoding="utf-8",
    )
    (run_dir / "stage-22" / "references.bib").write_text(
        "@article{fake2026,title={Fake},author={Smoke Test},year={2026}}\n",
        encoding="utf-8",
    )
    if not missing_citation:
        (run_dir / "stage-23" / "verification_report.json").write_text(
            json.dumps({"summary": {"total": 2, "verified": 2}}, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "stage-23" / "references_verified.bib").write_text(
            "@article{fake2026,title={Fake},author={Smoke Test},year={2026}}\n",
            encoding="utf-8",
        )
    return run_dir


def set_arc_experiment_mode(generated: Path, mode: str) -> None:
    path = generated / "configs" / "researchclaw.codex.yaml"
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    in_experiment = False
    changed = False
    for raw in lines:
        if raw.startswith("experiment:"):
            in_experiment = True
            out.append(raw)
            continue
        if in_experiment and raw and not raw.startswith((" ", "\t")):
            in_experiment = False
        if in_experiment and raw.strip().startswith("mode:") and not changed:
            indent = raw[: len(raw) - len(raw.lstrip())]
            out.append(f'{indent}mode: "{mode}"')
            changed = True
        else:
            out.append(raw)
    if not changed:
        raise RuntimeError("could not update experiment.mode in generated ARC Codex config")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def write_fake_codex_tools(tmp_path: Path) -> Path:
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    (fake_bin / "codex").write_text(
        """#!/usr/bin/env sh
if [ "$1" = "login" ] && [ "$2" = "status" ]; then
  echo "Logged in using ChatGPT"
  exit 0
fi
if [ "$1" = "exec" ]; then
  printf "%s\n" "$*" >> "${0%/*}/fake-codex-args.log"
  out=""
  prompt=""
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --output-last-message)
        shift
        out="$1"
        ;;
      *)
        prompt="$1"
        ;;
    esac
    shift
  done
  case "$prompt" in
    *FAIL*)
      echo "fake codex failure"
      exit 7
      ;;
  esac
  if [ -n "$out" ]; then
    printf "OK: %s\\n" "$prompt" > "$out"
  fi
  echo "fake codex stdout"
  exit 0
fi
echo "unexpected fake codex invocation: $*" >&2
exit 2
""",
        encoding="utf-8",
    )
    (fake_bin / "python3.11").write_text(
        """#!/usr/bin/env sh
if [ "$1" = "--version" ]; then
  echo "Python 3.11.0"
  exit 0
fi
exec python3 "$@"
""",
        encoding="utf-8",
    )
    (fake_bin / "codex").chmod(0o755)
    (fake_bin / "python3.11").chmod(0o755)
    return fake_bin


def check_codex_shim(generated: Path, env: dict[str, str]) -> int:
    shim = generated / "scripts" / "codex_acp_shim.py"
    base = [str(shim), "--ttl", "0", "--cwd", str(generated), "codex"]
    subprocess.run(base + ["sessions", "ensure", "--name", "smoke"], cwd=generated, env=env, check=True)

    cli_prompt = subprocess.run(
        base + ["-s", "smoke", "hello from cli"],
        cwd=generated,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    if "OK: hello from cli" not in cli_prompt.stdout:
        print("codex_acp_shim did not return fake CLI prompt output", file=sys.stderr)
        return 1

    stdin_prompt = subprocess.run(
        base + ["-s", "smoke", "-f", "-"],
        cwd=generated,
        env=env,
        input="hello from stdin",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    if "OK: hello from stdin" not in stdin_prompt.stdout:
        print("codex_acp_shim did not return fake stdin prompt output", file=sys.stderr)
        return 1
    args_log = (generated.parent / "fake-bin" / "fake-codex-args.log").read_text(encoding="utf-8")
    if "--model" not in args_log or "gpt-5.5" not in args_log:
        print("codex_acp_shim did not pass the default Codex model", file=sys.stderr)
        return 1
    if 'model_reasoning_effort="xhigh"' not in args_log:
        print("codex_acp_shim did not pass xhigh reasoning effort", file=sys.stderr)
        return 1

    fail_prompt = subprocess.run(
        base + ["-s", "smoke", "FAIL this call"],
        cwd=generated,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if fail_prompt.returncode == 0:
        print("codex_acp_shim unexpectedly passed a failing Codex call", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    cookiecutter = cookiecutter_command()
    if cookiecutter is None:
        print("cookiecutter is not installed. Install with: python3 -m pip install cookiecutter", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        fake_bin = write_fake_codex_tools(tmp_path)
        fake_env = dict(**os.environ)
        fake_env["PATH"] = f"{fake_bin}:{fake_env.get('PATH', '')}"
        fake_env.pop("OPENAI_API_KEY", None)
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
        subprocess.run(["make", "handoff-check"], cwd=generated, check=True)
        subprocess.run(["make", "verify-feature", "ID=R001"], cwd=generated, check=True)
        subprocess.run(["make", "arc-check"], cwd=generated, check=True)
        subprocess.run(["make", "arc-doctor", "ARC_AUTH=codex"], cwd=generated, env=fake_env, check=True)
        openai_doctor = subprocess.run(
            ["make", "arc-doctor", "ARC_AUTH=openai", "ARC_CONFIG=configs/researchclaw.openai.yaml"],
            cwd=generated,
            env=fake_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if openai_doctor.returncode == 0:
            print("arc-doctor unexpectedly passed OpenAI auth without OPENAI_API_KEY", file=sys.stderr)
            return 1
        shim_status = check_codex_shim(generated, fake_env)
        if shim_status:
            return shim_status

        data = json.loads((generated / "feature_list.json").read_text(encoding="utf-8"))
        r001 = next(item for item in data["features"] if item["id"] == "R001")
        if r001.get("state") != "passing" or not r001.get("evidence"):
            print("verify-feature did not record R001 passing evidence", file=sys.stderr)
            return 1
        log_path = r001["evidence"].get("log_path")
        if log_path not in r001.get("artifacts", []):
            print("verify-feature did not record the verification log as a task artifact", file=sys.stderr)
            return 1

        stale_handoff = subprocess.run(
            ["make", "handoff-check"],
            cwd=generated,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if stale_handoff.returncode == 0:
            print("handoff-check unexpectedly passed after verification with stale handoff files", file=sys.stderr)
            return 1

        refresh_handoff_files(generated, log_path)
        subprocess.run(["make", "handoff-check"], cwd=generated, check=True)
        subprocess.run(["make", "clean-session"], cwd=generated, check=True)

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

        fake_run = create_fake_arc_run(generated, "fake-arc-run")
        rel_fake = fake_run.relative_to(generated).as_posix()
        subprocess.run(["make", "arc-import", f"RUN_DIR={rel_fake}"], cwd=generated, check=True)
        subprocess.run(["make", "arc-verify", f"RUN_DIR={rel_fake}"], cwd=generated, check=True)
        subprocess.run(["make", "arc-paper-gate", f"RUN_DIR={rel_fake}"], cwd=generated, check=True)
        subprocess.run(
            ["make", "check-run-record", "FILE=experiments/manifests/fake-arc-run.json"],
            cwd=generated,
            check=True,
        )
        imported_manifest = json.loads(
            (generated / "experiments" / "manifests" / "fake-arc-run.json").read_text(encoding="utf-8")
        )
        if imported_manifest.get("status") == "passed":
            print("arc-import marked raw ARC output passed before paper gate", file=sys.stderr)
            return 1
        if imported_manifest.get("config") != "configs/researchclaw.codex.yaml":
            print("arc-import did not record the selected Codex ARC config", file=sys.stderr)
            return 1

        missing_citation = create_fake_arc_run(generated, "fake-missing-citation", missing_citation=True)
        rel_missing_citation = missing_citation.relative_to(generated).as_posix()
        subprocess.run(["make", "arc-import", f"RUN_DIR={rel_missing_citation}"], cwd=generated, check=True)
        citation_fail = subprocess.run(
            ["make", "arc-verify", f"RUN_DIR={rel_missing_citation}"],
            cwd=generated,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if citation_fail.returncode == 0:
            print("arc-verify unexpectedly passed with missing citation report", file=sys.stderr)
            return 1

        set_arc_experiment_mode(generated, "simulated")
        simulated_fail = subprocess.run(
            ["make", "arc-paper-gate", f"RUN_DIR={rel_fake}"],
            cwd=generated,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if simulated_fail.returncode == 0:
            print("arc-paper-gate unexpectedly passed with simulated experiment mode", file=sys.stderr)
            return 1
        set_arc_experiment_mode(generated, "sandbox")

        missing_metrics = create_fake_arc_run(generated, "fake-missing-metrics", missing_metrics=True)
        rel_missing_metrics = missing_metrics.relative_to(generated).as_posix()
        subprocess.run(["make", "arc-import", f"RUN_DIR={rel_missing_metrics}"], cwd=generated, check=True)
        metrics_fail = subprocess.run(
            ["make", "arc-paper-gate", f"RUN_DIR={rel_missing_metrics}"],
            cwd=generated,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if metrics_fail.returncode == 0:
            print("arc-paper-gate unexpectedly passed with missing metrics summary", file=sys.stderr)
            return 1

        agent_fail = subprocess.run(
            [
                "make",
                "agent-run",
                "ROLE=literature",
                "TASK=SMOKE-MISSING-CODEX",
                "CODEX_CLI=definitely_missing_codex_cli",
            ],
            cwd=generated,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if agent_fail.returncode == 0:
            print("agent-run unexpectedly passed with missing Codex CLI", file=sys.stderr)
            return 1

    print("Template smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
