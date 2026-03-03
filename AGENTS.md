# Multi-Agent Workflow

This project uses a 3-agent workflow. Each agent has a specific role defined in `.github/instructions/`.

## Shared State

All agents communicate through `.copilot-workspace/`:
- `plan.md` — current implementation plan (Planner writes, others read)
- `requirements.md` — requirements and feedback loop (Planner writes, Reviewer appends)
- `tasks.md` — task checklist with status (Planner writes, Implementer updates)
- `review.md` — review findings (Reviewer writes)
- `status.json` — current workflow state

## Agents

1. **Planner** — analyses requirements, asks questions, creates plans
2. **Implementer** — writes code based on the plan
3. **Reviewer** — tests, reviews, sends feedback
