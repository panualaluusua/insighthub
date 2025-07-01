# Create a new git worktree in the 'worktrees' directory.
# Usage: ./scripts/create_worktree.ps1 -BranchName <branch-name> [-WorktreeName <worktree-name>]
[CmdletBinding()]
param (
    [Parameter(Mandatory=$true)]
    [string]$BranchName,

    [Parameter(Mandatory=$false)]
    [string]$WorktreeName = $BranchName
)

$worktreePath = "worktrees/$WorktreeName"
$baseBranch = "master"

Write-Host "Creating worktree for branch '$BranchName' at '$worktreePath'..."

# Add worktree if directory doesn't exist
if (-not (Test-Path $worktreePath)) {
    git worktree add -b "$BranchName" "$worktreePath" "$baseBranch"
    Write-Host "Worktree created successfully."
    Write-Host "To start working, run: cd $worktreePath"
} else {
    Write-Host "Error: Worktree directory '$worktreePath' already exists."
    exit 1
} 