# Session Handoff

## Current Task
No active task. Start with `R001` unless the feature list has been customized.

## What Changed
Generated harness template is in its initial state.

## Verification
Pending initial verification. Run `./init.sh`, then `make verify-feature ID=R001`.

## Evidence Artifacts
None yet. Verification logs will be written under `work/verification_logs/`.

## Commands

- Startup: `./init.sh`
- Verification: `make verify-feature ID=R001`
- Focused debug: none

## Open Risks
Source repository and research-specific checks are not configured yet.

## Next Best Action
Clone or copy the source repository into `src/{{ cookiecutter.source_repo_name }}`, then replace placeholder verification targets with project-specific checks.
