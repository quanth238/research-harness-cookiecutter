# Auto Research Backend

This harness can manage AutoResearchClaw as an optional research backend. AutoResearchClaw may generate literature, hypotheses, experiment code, analyses, drafts, and citation reports, but those outputs are accepted only after this harness imports and verifies them.

By default, the backend uses the existing Codex CLI login. The harness does not read, copy, parse, or export `~/.codex/auth.json`; it calls `codex login status` and `codex exec` through `scripts/codex_acp_shim.py`. ARC Codex calls and `make agent-run` default to `CODEX_MODEL=gpt-5.5` and `CODEX_REASONING_EFFORT=xhigh`.

## Control Model

- The harness is the source of truth for task state, evidence, run records, gates, and handoff.
- AutoResearchClaw is a backend that writes candidate run artifacts under `artifacts/arc-runs/`.
- Final paper claims require imported metrics, run records, and citation verification.
- Codex worker agents communicate through files under `work/agent_*`; they do not mark tasks passing.

## Default Flow

```bash
make arc-check
make arc-bootstrap
make arc-doctor
make arc-run TOPIC="your research topic"
make arc-import RUN_DIR=artifacts/arc-runs/<run_id>
make arc-verify RUN_DIR=artifacts/arc-runs/<run_id>
make arc-paper-gate RUN_DIR=artifacts/arc-runs/<run_id>
```

To override the Codex defaults:

```bash
make arc-doctor CODEX_MODEL=gpt-5.5 CODEX_REASONING_EFFORT=xhigh
make agent-run ROLE=reviewer TASK=ARC-REVIEW-001 CODEX_REASONING_EFFORT=xhigh
```

Use `make arc-resume RUN_DIR=...` when an AutoResearchClaw run has a checkpoint and needs to continue.

To use OpenAI-compatible API-key auth instead of Codex auth:

```bash
make arc-doctor ARC_AUTH=openai ARC_CONFIG=configs/researchclaw.openai.yaml
make arc-run ARC_AUTH=openai ARC_CONFIG=configs/researchclaw.openai.yaml TOPIC="your research topic"
```

## Paper Acceptance

A draft paper is not a final result. `make arc-import RUN_DIR=...` records an imported run as inconclusive; `make arc-paper-gate RUN_DIR=...` must pass before the paper can be treated as an accepted research artifact. The gate rejects simulated experiments, missing metrics, missing citation reports, missing run records, and unverified citation summaries.

The Codex backend used by AutoResearchClaw is text-generation only and runs Codex in a read-only sandbox. Codex role workers launched with `make agent-run` are separate and may edit assigned files under the normal harness task controls.
