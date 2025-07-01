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

# Create worktree
if [ ! -d "$WORKTREE_PATH" ]; then
  git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "$BASE_BRANCH"
  echo "Worktree created successfully."
  echo "To start working, run: cd $WORKTREE_PATH"
else
  echo "Error: Worktree directory '$WORKTREE_PATH' already exists."
  exit 1
fi 