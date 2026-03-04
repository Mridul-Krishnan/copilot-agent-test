# 🤖 Copilot CLI Multi-Agent Workflow

A multi-agent development environment using [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) and tmux. Three specialized agents — **Planner**, **Implementer**, and **Reviewer** — collaborate through shared files, each with a defined role and constrained permissions.

## How It Works

```
┌──────────┐    plan.md     ┌──────────────┐   review.md   ┌────────────┐
│          │───────────────▶│              │◀──────────────│            │
│ Planner  │    tasks.md    │ Implementer  │   feedback    │  Reviewer  │
│          │◀───────────────│              │──────────────▶│            │
└──────────┘                └──────────────┘               └────────────┘
     ▲                                                          │
     └──────────────────────────────────────────────────────────┘
                        (revision loop if FAIL)
```

| Agent | Role | Writes To | Reads From |
|-------|------|-----------|------------|
| **Planner** | Analyses requirements, asks questions, creates plans | `plan.md`, `tasks.md`, `requirements.md` | Everything (read-only source) |
| **Implementer** | Writes code strictly following the plan | Source code, `tasks.md` (status only) | `plan.md`, `tasks.md` |
| **Reviewer** | Tests, reviews, sends feedback | `review.md` | Everything (read-only source) |

All shared state lives in `.copilot-workspace/`.

## Prerequisites

- [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) installed (`copilot` command available)
- [tmux](https://github.com/tmux/tmux) installed
- Active Copilot subscription

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url> && cd copilot-test

# 2. Launch all 3 agents in tmux windows
./launch-agents.sh

# 3. Give the Planner your requirements in the first window
#    Then switch agents as prompted
```

### Navigating Between Agents

| Shortcut | Action |
|----------|--------|
| `Ctrl+B n` | Next window |
| `Ctrl+B p` | Previous window |
| `Ctrl+B 0` | Jump to Planner (window 0) |
| `Ctrl+B 1` | Jump to Implementer (window 1) |
| `Ctrl+B 2` | Jump to Reviewer (window 2) |

## The Workflow Loop

1. **Planner window** — describe what you want to build. The Planner asks clarifying questions, then writes `plan.md` and `tasks.md`
2. **Implementer window** — tell it: *"Read the plan and implement"*. It builds the code and checks off tasks
3. **Reviewer window** — tell it: *"Review the implementation against the plan"*. It runs tests and writes `review.md`
4. If the review **fails** → go back to the **Planner** and say: *"Read review.md feedback and revise the plan"*
5. Repeat until `status.json` shows `"phase": "complete"`

## Starting a New Project

```bash
# 1. Kill the current agent session
tmux kill-session -t agents

# 2. Reset the shared workspace files
./reset-agent-workspace.sh

# 3. Relaunch
./launch-agents.sh
```

## Project Structure

```
copilot-test/
├── README.md                              # This file
├── AGENTS.md                              # Agent overview (Copilot reads this)
├── launch-agents.sh                       # Launches 3 agents in tmux
├── reset-agent-workspace.sh               # Clears workspace for a new project
├── .github/agents/
│   ├── planner.agent.md                   # Planner custom agent profile
│   ├── implementer.agent.md               # Implementer custom agent profile
│   └── reviewer.agent.md                  # Reviewer custom agent profile
└── .copilot-workspace/                    # Shared state (agents communicate here)
    ├── status.json                        # Current phase & iteration counter
    ├── requirements.md                    # User requirements
    ├── plan.md                            # Implementation plan
    ├── tasks.md                           # Task checklist with status
    └── review.md                          # Review findings & feedback
```

## How Agent Identity Works

Each agent is launched using the `--agent` CLI flag, which pre-loads its custom agent profile from `.github/agents/`:

```bash
copilot --experimental --agent=planner
```

Each profile (`.agent.md`) contains YAML frontmatter defining the agent's name, description, and allowed tools — so the role is set at the system level before any conversation begins. No identity prompts are needed.

| Agent | Profile | Tools |
|-------|---------|-------|
| **Planner** | `planner.agent.md` | read, search, edit |
| **Implementer** | `implementer.agent.md` | all |
| **Reviewer** | `reviewer.agent.md` | read, search, run_in_terminal |

## Things to Try

- [ ] **Strict reviewer** — tell the Reviewer: *"Be extremely strict. Reject anything without tests."* See how the feedback loop handles multiple revision cycles
- [ ] **Larger projects** — try a multi-file project (REST API, static site generator) to stress-test the planning/task breakdown
- [ ] **Automated handoff** — extend `launch-agents.sh` to watch `status.json` and auto-prompt the next agent when a phase completes
- [ ] **Add a 4th agent** — create a `tester.instructions.md` that only writes and runs tests, separate from the Reviewer
- [ ] **Context management** — use `/compact` in long sessions to compress history and keep agents fast
- [ ] **Custom models per agent** — use `/model` in each window to assign different models (e.g. a fast model for the Planner, a powerful one for the Implementer)
- [ ] **MCP integration** — add a local MCP server via `/mcp` for structured inter-agent communication instead of file-based state
- [ ] **Git branch per iteration** — have the Implementer create a branch per iteration so revisions don't overwrite previous attempts
- [ ] **Parallel fleet mode** — use `/fleet` in the Implementer window to split independent tasks across sub-agents
- [ ] **CI integration** — have the Reviewer trigger actual CI checks and parse the output into `review.md`

## Tips

- If an agent seems confused about its role, send the identity prompt again or use `/clear` and restart
- Use `/instructions` in any agent window to verify which instruction files are loaded
- The `status.json` file tracks the current phase — useful for scripting automation later
- All agents share the same codebase directory, so the Implementer's changes are immediately visible to the Reviewer

## License

MIT
