#!/bin/bash
# Launch 3 Copilot CLI agent sessions in tmux windows
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

wait_ready() {
  local target=$1
  for i in $(seq 1 60); do
    if tmux capture-pane -t "$target" -p 2>/dev/null | grep -qE '(›|>|copilot)'; then
      sleep 2
      return 0
    fi
    sleep 1
  done
  echo "Warning: timed out waiting for $target"
}

send_prompt() {
  local target=$1
  local msg=$2
  tmux send-keys -t "$target" -l "$msg"
  sleep 0.5
  tmux send-keys -t "$target" C-m
}

# --- Launch ---

tmux kill-session -t $SESSION 2>/dev/null

tmux new-session -d -s $SESSION -n "planner" "cd $DIR && copilot --experimental"
tmux new-window -t $SESSION -n "implementer" "cd $DIR && copilot --experimental"
tmux new-window -t $SESSION -n "reviewer" "cd $DIR && copilot --experimental"

# --- Identity prompts ---

echo "Waiting for Planner to load..."
wait_ready "$SESSION:planner"
send_prompt "$SESSION:planner" \
  "You are the Planner. Follow ONLY planner.instructions.md. Ignore other agent instructions."

echo "Waiting for Implementer to load..."
wait_ready "$SESSION:implementer"
send_prompt "$SESSION:implementer" \
  "You are the Implementer. Follow ONLY implementer.instructions.md. Ignore other agent instructions."

echo "Waiting for Reviewer to load..."
wait_ready "$SESSION:reviewer"

REVIEWER_PROMPT="You are the Reviewer. Follow ONLY reviewer.instructions.md. Ignore other agent instructions."
if [[ "$STRICT" =~ ^[Yy]$ ]]; then
  REVIEWER_PROMPT="$REVIEWER_PROMPT Be extremely strict. Reject anything without full test coverage, error handling, and edge case consideration."
  echo "  → Strict mode ON"
fi
send_prompt "$SESSION:reviewer" "$REVIEWER_PROMPT"

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
