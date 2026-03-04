#!/bin/bash
# Auto-handoff watcher for multi-agent workflow
# Polls status.json and triggers the next agent via tmux send-keys
# Usage: ./watch-handoff.sh [--max-iter N] [--session NAME] [--workspace PATH]

SESSION="agents"
WORKSPACE=".copilot-workspace"
MAX_ITER=5

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --max-iter) MAX_ITER="$2"; shift 2 ;;
    --session) SESSION="$2"; shift 2 ;;
    --workspace) WORKSPACE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

STATUS_FILE="$WORKSPACE/status.json"

send_prompt() {
  local target=$1
  local msg=$2
  # C-u clears any pending input without interrupting a running operation
  tmux send-keys -t "$target" C-u
  sleep 0.5
  tmux send-keys -t "$target" -l "$msg"
  sleep 0.5
  tmux send-keys -t "$target" C-m
}

ITER=0
STALE=0
LAST_PHASE=""
echo "👀 Watcher started"
echo "   Polling: $STATUS_FILE"
echo "   Max iterations: $MAX_ITER"
echo "   tmux session: $SESSION"
echo ""

while [ $ITER -lt $MAX_ITER ]; do
  if [ ! -f "$STATUS_FILE" ]; then
    sleep 5
    continue
  fi

  PHASE=$(jq -r '.phase // "idle"' "$STATUS_FILE" 2>/dev/null)

  # Detect stale phase (agent didn't update status.json)
  if [ "$PHASE" = "$LAST_PHASE" ]; then
    STALE=$((STALE + 1))
    # After 60 seconds of no change, nudge the active agent
    if [ $STALE -ge 12 ]; then
      echo "⏳ Phase '$PHASE' unchanged for 60s, nudging..."
      case $PHASE in
        "implementing")
          send_prompt "$SESSION:implementer" "Remember to update .copilot-workspace/status.json to phase implemented when done."
          ;;
        "reviewing")
          send_prompt "$SESSION:reviewer" "Remember to update .copilot-workspace/status.json when review is complete."
          ;;
        "replanning")
          send_prompt "$SESSION:planner" "Remember to update .copilot-workspace/status.json to phase planned when the revised plan is ready."
          ;;
      esac
      STALE=0
    fi
  else
    STALE=0
  fi
  LAST_PHASE="$PHASE"

  case $PHASE in
    "planned")
      echo "📋 Plan ready → kicking Implementer (iteration $ITER)"
      jq '.phase = "implementing"' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
      send_prompt "$SESSION:implementer" "Read the plan and implement all tasks in plan.md and tasks.md."
      ;;
    "implemented")
      echo "⚙️  Implementation done → kicking Reviewer (iteration $ITER)"
      jq '.phase = "reviewing"' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
      send_prompt "$SESSION:reviewer" "Review the implementation against the plan. Write findings to review.md."
      ;;
    "needs-revision")
      ITER=$((ITER + 1))
      echo "❌ Review failed → kicking Planner (revision $ITER/$MAX_ITER)"
      jq --arg i "$ITER" '.phase = "replanning" | .iteration = ($i | tonumber)' "$STATUS_FILE" > "$STATUS_FILE.tmp" && mv "$STATUS_FILE.tmp" "$STATUS_FILE"
      send_prompt "$SESSION:planner" "Read review.md feedback and revise the plan. This is revision $ITER."
      ;;
    "complete")
      echo ""
      echo "✅ Project complete after $ITER revision(s)!"
      break
      ;;
    *)
      # Transitional phases: implementing, reviewing, replanning, idle
      # Just wait for agent to finish
      ;;
  esac

  sleep 5
done

if [ $ITER -ge $MAX_ITER ]; then
  echo ""
  echo "⚠️  Max iterations ($MAX_ITER) reached. Stopping watcher."
fi

echo ""
echo "Press Enter to close this window."
read
