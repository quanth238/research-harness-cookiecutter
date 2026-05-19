# Clean State Checklist

Before ending a session:

- [ ] Harness startup path works: `./init.sh` or `make smoke`
- [ ] Relevant verification command passed or failure is documented
- [ ] `feature_list.json` reflects actual task state
- [ ] `PROGRESS.md` records commands, evidence, and next action
- [ ] `DECISIONS.md` records any changed research assumptions
- [ ] `docs/failure-log.md` records failed, negative, or unstable runs
- [ ] No ambiguous temporary files remain
- [ ] Experiment artifacts have stable names or run IDs
- [ ] Accepted empirical runs have manifests under `experiments/manifests/`
- [ ] Source repository status has been checked when applicable
- [ ] `make clean-session` has been run
- [ ] `make handoff-check` passes
