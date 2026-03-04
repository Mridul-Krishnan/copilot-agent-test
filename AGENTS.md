# Multi-Agent Workflow

This project uses a 3-agent workflow. Each agent is a custom Copilot CLI agent defined in `.github/agents/`.

## Shared State

All agents communicate through `.copilot-workspace/`:
- `plan.md` — current implementation plan (Planner writes, others read)
- `requirements.md` — requirements and feedback loop (Planner writes, Reviewer appends)
- `tasks.md` — task checklist with status (Planner writes, Implementer updates)
- `review.md` — review findings (Reviewer writes)
- `status.json` — current workflow state

## Agents

1. **Planner** (`planner.agent.md`) — analyses requirements, asks questions, creates plans. Tools: read, search, edit.
2. **Implementer** (`implementer.agent.md`) — writes code based on the plan. Tools: all.
3. **Reviewer** (`reviewer.agent.md`) — runs tests, reviews, sends feedback. Tools: read, search, run_in_terminal.
