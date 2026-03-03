#!/bin/bash
# Reset the shared workspace for a new project
# Usage: ./reset-agent-workspace.sh

DIR="/home/krish/copilot-test/.copilot-workspace"

cat > "$DIR/status.json" << 'EOF'
{"phase": "idle", "iteration": 0}
EOF

cat > "$DIR/requirements.md" << 'EOF'
# Requirements

(Describe your requirements here, or let the Planner agent ask you questions)
EOF

cat > "$DIR/plan.md" << 'EOF'
# Plan

(Planner agent will write the implementation plan here)
EOF

cat > "$DIR/tasks.md" << 'EOF'
# Tasks

(Planner agent will write the task checklist here)
EOF

cat > "$DIR/review.md" << 'EOF'
# Review

(Reviewer agent will write review findings here)
EOF

echo "✅ Workspace reset. Ready for a new project."
