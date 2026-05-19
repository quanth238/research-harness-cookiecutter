# Quality Document

Track long-running health of the project.

| Area | Grade | Evidence | Risks | Next Improvement |
|---|---|---|---|---|
| Harness | C | Template generated | Commands are placeholders | Replace `Makefile` TODOs |
| Source repo | Unknown | Not inspected | Upstream setup may be undocumented | Run `make source-status` and source smoke checks |
| Data | Unknown | Not configured | Split or path assumptions may be implicit | Fill `docs/data.md` |
| Metrics | Unknown | Not configured | Claims may use inconsistent aggregation | Fill `docs/metrics.md` and `make verify-metric` |
| Baselines | Unknown | Not configured | Baseline configs may drift | Fill `docs/baselines.md` |
| Evaluation | Unknown | Not configured | Metrics may not be reproducible | Fill `EVAL_PROTOCOL.md` |
| Artifacts | C | Manifest template exists | Large outputs are ignored by default | Commit lightweight run and result manifests |
| Failure learning | C | `docs/failure-log.md` exists | Negative evidence may not be reviewed before retries | Update failure log during `make clean-session` review |
