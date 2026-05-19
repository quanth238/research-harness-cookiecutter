# A* Venue Readiness Gate

## Target
- Target venue: <NeurIPS|ICML|ICLR|AAAI|CVPR>

## Criteria
- Problem significance: <why this is a meaningful problem for the venue>
- Baseline standard: <which strong baselines and official protocols are required>
- Ablation plan: <ablations needed to isolate the mechanism>
- Statistical evidence plan: <seeds, confidence intervals, tests, or robustness checks>
- Reproducibility package: <code, data, configs, logs, and manifests to release>
- Citation grounding plan: <how claims and related work will be verified>
- Non-incremental contribution: <why the contribution is more than a small module or tuning change>

## A* Readiness Checklist
- [ ] Problem is important to the target venue community.
- [ ] Baselines include strong current methods, not only easy comparisons.
- [ ] Metrics and splits match accepted benchmark practice.
- [ ] Ablations isolate the proposed mechanism.
- [ ] Statistical evidence plan covers seeds or uncertainty.
- [ ] Reproducibility artifacts are planned before experiments.
- [ ] Citation grounding is required before paper acceptance.
- [ ] Contribution is mechanism/theory driven, not only an empirical improvement.

## Verification Command
- `make verify-venue`
