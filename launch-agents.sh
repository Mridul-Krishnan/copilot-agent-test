#!/bin/bash
# Launch 3 Copilot CLI agent sessions in tmux windows
# Usage: ./launch-agents.sh

SESSION="agents"
DIR="~/copilot-test"

# Poll tmux pane until copilot prompt appears
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

# Kill existing session if any
tmux kill-session -t $SESSION 2>/dev/null

# Window 0: Planner
tmux new-session -d -s $SESSION -n "planner" "cd $DIR && copilot --experimental"

# Window 1: Implementer
tmux new-window -t $SESSION -n "implementer" "cd $DIR && copilot --experimental"

# Window 2: Reviewer
tmux new-window -t $SESSION -n "reviewer" "cd $DIR && copilot --experimental"

echo "Waiting for Planner to load..."
wait_ready "$SESSION:planner"
tmux send-keys -t $SESSION:planner \
  "You are the Planner. Follow ONLY planner.instructions.md. Ignore other agent instructions." Enter

echo "Waiting for Implementer to load..."
wait_ready "$SESSION:implementer"
tmux send-keys -t $SESSION:implementer \
  "You are the Implementer. Follow ONLY implementer.instructions.md. Ignore other agent instructions." Enter

echo "Waiting for Reviewer to load..."
wait_ready "$SESSION:reviewer"
tmux send-keys -t $SESSION:reviewer \
  "You are the Reviewer. Follow ONLY reviewer.instructions.md. Ignore other agent instructions." Enter

# Attach to planner window
tmux select-window -t $SESSION:planner
tmux attach -t $SESSION
