#!/bin/bash
# Create a new git worktree in the 'worktrees' directory.
# Usage: ./scripts/create_worktree.sh <branch-name> [worktree-name]
set -e

# Check for branch name argument
if [ -z "$1" ]; then
  echo "Usage: $0 <branch-name> [worktree-name]"
  exit 1
fi

BRANCH_NAME=$1
WORKTREE_NAME=${2:-$BRANCH_NAME} # Use branch name as worktree name if not provided
WORKTREE_PATH="worktrees/$WORKTREE_NAME"
BASE_BRANCH="master"

echo "Creating worktree for branch '$BRANCH_NAME' at '$WORKTREE_PATH'..."

# SAFETY CHECKS --------------------------------------------------------
# 1) Ensure clean working directory
if [[ -n $(git status --porcelain) ]]; then
  echo "❌ Working tree not clean. Commit or stash your changes before creating a worktree." >&2
  exit 1
fi

# 2) Ensure current branch is master (we branch off from master)
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "master" ]]; then
  echo "❌ You must run this script from the 'master' branch (current: $CURRENT_BRANCH)." >&2
  exit 1
fi

# 3) Ensure target path is under worktrees/
if [[ "$WORKTREE_PATH" != worktrees/* ]]; then
  echo "❌ Worktree path must live under 'worktrees/'." >&2
  exit 1
fi
# ---------------------------------------------------------------------

# Create worktree
if [ ! -d "$WORKTREE_PATH" ]; then
  git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "$BASE_BRANCH"
  echo "Worktree created successfully."
  echo "To start working, run: cd $WORKTREE_PATH"
else
  echo "Error: Worktree directory '$WORKTREE_PATH' already exists."
  exit 1
fi

# Install pre-commit hook to enforce tm-test-guard
HOOK_FILE="$(git rev-parse --git-dir)/hooks/pre-commit"
if ! grep -q "tm-test-guard" "$HOOK_FILE" 2>/dev/null; then
  cat <<'EOF' >> "$HOOK_FILE"
#!/bin/bash
# Auto-generated by create_worktree.sh – enforce TDD guard
scripts/tm-test-guard.sh || exit 1
EOF
  chmod +x "$HOOK_FILE"
  echo "Pre-commit hook installed (tm-test-guard)."
fi 