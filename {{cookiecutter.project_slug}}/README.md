# {{ cookiecutter.project_name }}

{{ cookiecutter.research_goal }}

This workspace wraps a source repository under `src/{{ cookiecutter.source_repo_name }}/` and keeps research harness artifacts at the root.

## Start

```bash
./init.sh
make source-status
```

## Add A Source Repository

{% if cookiecutter.upstream_repo_url %}
```bash
git clone {{ cookiecutter.upstream_repo_url }} src/{{ cookiecutter.source_repo_name }}
```
{% else %}
```bash
git clone <upstream-repo-url> src/{{ cookiecutter.source_repo_name }}
```
{% endif %}

## Agent Workflow

1. Read `AGENTS.md`.
2. Read `PROGRESS.md`, `DECISIONS.md`, and `feature_list.json`.
3. Select one task only.
4. Write `work/TASK_SPEC.md`.
5. Implement only the approved scope.
6. Verify with the registered command.
7. Record evidence and update progress.

