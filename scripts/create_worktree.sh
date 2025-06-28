#!/bin/bash
# Create a new UI development worktree at ../ui-dev on branch ui-development
set -e

BRANCH="ui-development"
WORKTREE="../ui-dev"

# Create branch if it doesn't exist
if ! git show-ref --verify --quiet refs/heads/$BRANCH; then
  git branch $BRANCH
fi

# Add worktree
if [ ! -d "$WORKTREE" ]; then
  git worktree add "$WORKTREE" "$BRANCH"
  echo "Worktree created at $WORKTREE for branch $BRANCH."
else
  echo "Worktree directory $WORKTREE already exists."
fi 