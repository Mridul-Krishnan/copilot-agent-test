# 🤖 Copilot CLI Multi-Agent Workflow

A multi-agent development environment using [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) and tmux. Three specialized agents — **Planner**, **Implementer**, and **Reviewer** — collaborate through shared files, each with a defined role and constrained toolset. A fourth optional **Watcher** process monitors shared state and automatically hands off between agents, even while you're doing something else.

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

                    ↕ all driven by ↕
              watch-handoff.sh (polls status.json)
```

| Agent | Role | Writes To | Reads From |
|-------|------|-----------|------------|
| **Planner** | Analyses requirements, asks questions, creates plans | `plan.md`, `tasks.md`, `requirements.md` | Everything (read-only source) |
| **Implementer** | Writes code strictly following the plan | Source code, `tasks.md` (status only) | `plan.md`, `tasks.md` |
| **Reviewer** | Tests, reviews, sends feedback | `review.md`, `status.json` | Everything (read-only source) |

All shared state lives in `.copilot-workspace/`.

## Prerequisites

- [GitHub Copilot CLI](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) installed (`copilot` command available)
- [tmux](https://github.com/tmux/tmux) installed
- [jq](https://jqlang.github.io/jq/) installed (`sudo apt install -y jq`) — required for watcher
- Active Copilot subscription

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url> && cd copilot-test

# 2. (Optional) Describe your project tooling in .copilot-workspace/requirements.md
#    e.g. "Use uv for Python. Never use pip or python3 directly."

# 3. Launch all agents in tmux
./launch-agents.sh

# 4. Give the Planner your requirements in the first window
#    If watcher is enabled, handoffs happen automatically
```

### Navigating Between Agents

| Shortcut | Action |
|----------|--------|
| `Ctrl+B n` | Next window |
| `Ctrl+B p` | Previous window |
| `Ctrl+B 0` | Jump to Planner (window 0) |
| `Ctrl+B 1` | Jump to Implementer (window 1) |
| `Ctrl+B 2` | Jump to Reviewer (window 2) |
| `Ctrl+B 3` | Jump to Watcher (window 3, if enabled) |

## The Workflow Loop

1. **Planner window** — describe what you want to build. The Planner asks clarifying questions, then writes `plan.md` and `tasks.md`
2. **Implementer window** — tell it: *"Read the plan and implement"*. It builds the code and checks off tasks
3. **Reviewer window** — tell it: *"Review the implementation against the plan"*. It runs tests and writes `review.md`
4. If the review **fails** → go back to the **Planner** and say: *"Read review.md feedback and revise the plan"*
5. Repeat until `status.json` shows `"phase": "complete"`

With the watcher enabled, steps 2–5 happen automatically.

## Auto-Handoff Watcher

When you enable the watcher at launch, `watch-handoff.sh` runs in a separate tmux window and polls `status.json` every 5 seconds. When an agent completes its phase, the watcher updates the phase to a transitional state and sends the next agent its prompt automatically.

**The watcher works even when the terminal is not in focus** (e.g. you've switched to a browser). This is achieved by:

- Setting `focus-events off` on the tmux session at launch — so Copilot CLI's TUI doesn't receive terminal focus/blur events and always behaves as if it's active
- Using `tmux select-window` before sending keys — ensuring the target agent window is the active pane when input is delivered

The watcher also nudges agents that haven't updated `status.json` in 60 seconds, in case they stalled mid-task.

### Watcher Phase Lifecycle

```
idle → planned → implementing → implemented → reviewing → complete
                                                        ↘ needs-revision → replanning → planned → ...
```

Agents own: `planned`, `implemented`, `needs-revision`, `complete`
Watcher owns: `implementing`, `reviewing`, `replanning` (transitional — prevents double-triggering)

## Starting a New Project

```bash
# 1. Kill the current agent session
tmux kill-session -t agents

# 2. Reset the shared workspace files
./reset-agent-workspace.sh

# 3. (Optional) Add project-specific tooling notes to .copilot-workspace/requirements.md

# 4. Relaunch
./launch-agents.sh
```

## Project Structure

```
copilot-test/
├── README.md                              # This file
├── AGENTS.md                              # Agent overview (Copilot reads this automatically)
├── launch-agents.sh                       # Launches agents in tmux, asks watcher/strict options
├── watch-handoff.sh                       # Auto-handoff watcher (polls status.json)
├── reset-agent-workspace.sh               # Clears workspace for a new project
├── .github/agents/
│   ├── planner.agent.md                   # Planner custom agent profile
│   ├── implementer.agent.md               # Implementer custom agent profile
│   └── reviewer.agent.md                  # Reviewer custom agent profile
└── .copilot-workspace/                    # Shared state (agents communicate here)
    ├── status.json                        # Current phase & iteration counter
    ├── requirements.md                    # User requirements (edit before launch)
    ├── plan.md                            # Implementation plan (Planner writes)
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
| **Reviewer** | `reviewer.agent.md` | read, search, edit, run_in_terminal |

## Specifying Project Tooling

The Implementer auto-detects package managers from lockfiles (`uv.lock`, `poetry.lock`, `package.json`, etc.) and uses the correct tool. For explicit control, add a **Tooling** section to `.copilot-workspace/requirements.md` before launching:

```markdown
## Tooling
- Use `uv` for all Python package management. Never use pip or python3 directly.
- Run scripts with `uv run`, install deps with `uv add`.
```

The Planner reads this file and carries the context into the plan, which the Implementer then follows.

## Things to Try

- [x] **Automated handoff** — `watch-handoff.sh` polls `status.json` and auto-prompts the next agent
- [x] **Background operation** — watcher works even when you switch away from the terminal
- [x] **Strict reviewer** — enable at launch to reject anything without full test coverage and edge case handling
- [x] **Custom agents** — uses `.github/agents/*.agent.md` profiles with native tool restrictions, no identity prompting needed
- [ ] **Add a 4th agent** — create a `tester.agent.md` that only writes and runs tests, separate from the Reviewer
- [ ] **Context management** — use `/compact` in long sessions to compress history and keep agents fast
- [ ] **Custom models per agent** — add `model:` to each `.agent.md` to assign different models (fast model for Planner, powerful for Implementer)
- [ ] **MCP integration** — add a local MCP server via `/mcp` for structured inter-agent communication instead of file-based state
- [ ] **Git branch per iteration** — have the Implementer create a branch per iteration so revisions don't overwrite previous attempts
- [ ] **Parallel fleet mode** — use `/fleet` in the Implementer window to split independent tasks across sub-agents
- [ ] **CI integration** — have the Reviewer trigger actual CI checks and parse the output into `review.md`

## Tips

- Use `/agent` inside any session to see available agents or switch roles
- Use `/context` to check token usage — each agent only loads its own profile, keeping context lean
- The `status.json` file is the source of truth for the watcher — you can manually edit it to re-trigger a phase
- All agents share the same codebase directory, so the Implementer's changes are immediately visible to the Reviewer
- If an agent gets stuck, manually switch to its window and press Enter — or let the watcher's 60s nudge handle it

## License

MIT

