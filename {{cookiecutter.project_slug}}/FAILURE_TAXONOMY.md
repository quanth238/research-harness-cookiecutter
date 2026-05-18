# Failure Taxonomy

Use these labels when analyzing failed agent runs.

| Label | Meaning | Harness refinement |
|---|---|---|
| task_ambiguity | The task was underspecified | Improve planner template or acceptance criteria |
| missing_context | The needed repo knowledge was absent | Add or update a topic doc |
| environment_failure | Setup, dependency, path, or data access failed | Improve `make setup` or `make smoke` |
| verification_gap | The task looked done but checks were weak | Add an executable test or evaluator rubric item |
| scope_drift | The agent changed unrelated files or goals | Tighten task scope and non-scope |
| handoff_failure | Next session could not recover state | Improve reports and `PROGRESS.md` |
| evaluator_weakness | Evaluator gave vague or wrong feedback | Calibrate rubric with examples |
| tool_failure | Command/tool behavior caused the issue | Improve scripts or tool instructions |

