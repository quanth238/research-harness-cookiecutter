# Artifact Protocol

## Lightweight Versioned Artifacts
Commit small files that explain or index research evidence:
- `experiments/manifests/<run_id>.json`
- `results/manifests/<artifact_id>.json`
- `artifacts/tables/*.csv`
- `work/verification_logs/<task_id>/*.log` when logs are small enough to review
- selected figures when intentionally versioned
- task reports under `work/`

## Large Or Local Artifacts
Keep large outputs out of git unless the project explicitly decides otherwise:
- checkpoints,
- raw logs,
- rendered videos,
- generated datasets,
- full prediction dumps,
- temporary submissions.

## Run Record Requirements
Every accepted empirical run should have a manifest based on `templates/RUN_RECORD.json`.
Validate it with:

```bash
make check-run-record FILE=experiments/manifests/<run_id>.json
```

## Naming
Use stable run IDs that include date/time, task id, and seed when relevant. Avoid ambiguous names like `latest`, `final`, or `best` unless they are symlinks or generated summaries.

## Failure Evidence

Failed, negative, unstable, and inconclusive runs should still leave evidence. Record the summary in `docs/failure-log.md` and keep the supporting command, log path, metric path, or run manifest if it helps avoid repeating the same failed experiment family.
