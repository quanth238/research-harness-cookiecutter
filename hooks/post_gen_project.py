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
]:
    chmod_executable(script)
