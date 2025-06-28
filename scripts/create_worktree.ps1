# Create a new UI development worktree at ../ui-dev on branch ui-development
$branch = "ui-development"
$worktree = "../ui-dev"

# Check if branch exists
$branchExists = git branch --list $branch
if (-not $branchExists) {
    git branch $branch
}

# Add worktree if directory doesn't exist
if (-not (Test-Path $worktree)) {
    git worktree add $worktree $branch
    Write-Host "Worktree created at $worktree for branch $branch."
} else {
    Write-Host "Worktree directory $worktree already exists."
} 