#!/bin/bash
# Launch 3 Copilot CLI custom agent sessions in tmux windows
# Usage: ./launch-agents.sh

SESSION="agents"
DIR="~/copilot-test"

# --- Options ---
echo "🤖 Multi-Agent Launcher"
echo ""

read -p "Enable auto-handoff watcher? (y/n) [n]: " WATCHER
WATCHER=${WATCHER:-n}

read -p "Enable strict reviewer mode? (y/n) [n]: " STRICT
STRICT=${STRICT:-n}

if [[ "$WATCHER" =~ ^[Yy]$ ]]; then
  read -p "Max watcher iterations [5]: " MAX_ITER
  MAX_ITER=${MAX_ITER:-5}
fi

echo ""

# --- Helpers ---

send_prompt() {
  local target=$1
  local msg=$2
  tmux send-keys -t "$target" Escape
  sleep 1
  tmux send-keys -t "$target" -l "$msg"
  sleep 0.5
  tmux send-keys -t "$target" C-m
}

# --- Launch ---

tmux kill-session -t $SESSION 2>/dev/null

REVIEWER_AGENT="reviewer"
if [[ "$STRICT" =~ ^[Yy]$ ]]; then
  echo "  → Strict mode ON (sending extra instruction to reviewer)"
fi

tmux new-session -d -s $SESSION -n "planner"     "cd $DIR && copilot --experimental --agent=planner"
tmux set -t $SESSION focus-events off
tmux new-window  -t $SESSION -n "implementer"    "cd $DIR && copilot --experimental --agent=implementer"
tmux new-window  -t $SESSION -n "reviewer"       "cd $DIR && copilot --experimental --agent=reviewer"

# Strict mode: send extra instruction once reviewer loads
if [[ "$STRICT" =~ ^[Yy]$ ]]; then
  sleep 8
  send_prompt "$SESSION:reviewer" \
    "Be extremely strict. Reject anything without full test coverage, error handling, and edge case consideration."
fi

# --- Watcher ---

if [[ "$WATCHER" =~ ^[Yy]$ ]]; then
  echo "Starting watcher (max $MAX_ITER iterations)..."
  tmux new-window -t $SESSION -n "watcher" \
    "cd $DIR && ./watch-handoff.sh --max-iter $MAX_ITER --session $SESSION --workspace .copilot-workspace"
fi

# --- Attach ---

echo ""
echo "🚀 All agents ready."
if [[ "$WATCHER" =~ ^[Yy]$ ]]; then
  echo "   Ctrl+B 0=Planner  1=Implementer  2=Reviewer  3=Watcher"
else
  echo "   Ctrl+B 0=Planner  1=Implementer  2=Reviewer"
fi
echo ""
tmux select-window -t $SESSION:planner
tmux attach -t $SESSION
