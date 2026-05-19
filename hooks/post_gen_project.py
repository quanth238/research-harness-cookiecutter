from pathlib import Path


def chmod_executable(path: Path) -> None:
    if path.exists():
        path.chmod(path.stat().st_mode | 0o111)


if "{{ cookiecutter.include_claude_md }}" == "no":
    claude = Path("CLAUDE.md")
    if claude.exists():
        claude.unlink()

for script in [
    Path("init.sh"),
    Path("scripts/verify_feature.sh"),
    Path("scripts/verify_feature.py"),
    Path("scripts/clean_session.sh"),
    Path("scripts/check_handoff.py"),
    Path("scripts/check_run_record.py"),
    Path("scripts/arc_bootstrap.py"),
    Path("scripts/arc_doctor.py"),
    Path("scripts/arc_run.py"),
    Path("scripts/codex_acp_shim.py"),
    Path("scripts/import_arc_run.py"),
    Path("scripts/verify_arc_run.py"),
    Path("scripts/verify_paper_gate.py"),
    Path("scripts/run_agent.py"),
]:
    chmod_executable(script)
