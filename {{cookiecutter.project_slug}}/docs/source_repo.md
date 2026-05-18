# Source Repository

Use this file when the harness wraps an existing external repository under `src/`.

## Location
- Path: `src/{{ cookiecutter.source_repo_name }}`
- Upstream URL: `{{ cookiecutter.upstream_repo_url }}`
- Branch or commit:

## Ownership Rule
- Harness files live at the workspace root.
- Source code changes live under `src/{{ cookiecutter.source_repo_name }}/`.
- Do not rewrite upstream history unless the human explicitly asks.
- If using a nested clone, check status in both the harness root and the source repo.

## Source Smoke Commands
Record the cheapest commands that prove the source repo is importable or runnable.

```bash
make source-smoke
```

## Adaptation Notes
- Required dependency changes:
- Data paths:
- Expected entrypoints:
- Known issues:

