#!/usr/bin/env pwsh
<##
  tm-test-guard.ps1 – Prevent commits if tests fail and remind developer about TDD Red → Green flow.
##>

$ErrorActionPreference = 'Stop'

Write-Host "tm-test-guard: running pytest..." -ForegroundColor Yellow
pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed. Commit aborted." -ForegroundColor Red
    exit 1
}

Write-Host "tm-test-guard: running npm test (if present)..." -ForegroundColor Yellow
npm test --silent --if-present
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed. Commit aborted." -ForegroundColor Red
    exit 1
}

Write-Host "✅ All tests passed." -ForegroundColor Green
$confirm = Read-Host "Did you first see FAILING tests before making them pass? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "Commit aborted by tm-test-guard – ensure TDD Red phase occurred." -ForegroundColor Red
    exit 1
}

exit 0 