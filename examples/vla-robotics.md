# Example: VLA Robotics

Generate a harness:

```bash
cookiecutter gh:quanth238/research-harness-cookiecutter
```

Suggested answers:

```text
project_name: VLA Robotics Harness
research_goal: Produce reproducible evidence for vision-language-action policy experiments.
source_repo_name: vla-source
```

Good first tasks:

- verify dataset manifests and split integrity,
- run one offline policy evaluation episode,
- check action-space and camera calibration assumptions,
- log policy checkpoint, config, seed, environment version, and evaluation videos.
