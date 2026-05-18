# Example: 3D Gaussian Splatting

Generate a harness:

```bash
cookiecutter gh:quanth238/research-harness-cookiecutter
```

Suggested answers:

```text
project_name: 3DGS Research Harness
research_goal: Produce reproducible evidence for 3D Gaussian Splatting experiments.
source_repo_name: gaussian-splatting
upstream_repo_url: https://github.com/graphdeco-inria/gaussian-splatting.git
```

Then clone the source repo:

```bash
cd 3dgs-research-harness
git clone https://github.com/graphdeco-inria/gaussian-splatting.git src/gaussian-splatting
```

Good first tasks:

- make the upstream repo install from a clean machine,
- create a tiny data or config smoke test,
- verify one scene can run through the expected render/eval path,
- add metric schema checks before running expensive experiments.
