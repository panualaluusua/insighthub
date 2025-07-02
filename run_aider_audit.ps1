# run_aider_audit.ps1
#
# PowerShell-versio Aider-auditointiskriptistä.
# Suorittaa systemaattisen koodiauditoinnin ilman WSL-riippuvuutta.
#
# Käyttö: ./run_aider_audit.ps1 -AuditType <TYYPPI> -Files <tiedostot>
# Esimerkki: ./run_aider_audit.ps1 -AuditType SECURITY -Files "src/auth.py", "src/config.py"

[CmdletBinding()]
param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("SECURITY", "COST", "PERFORMANCE", "CODE_QUALITY")]
    [string]$AuditType,

    [Parameter(Mandatory=$true)]
    [string[]]$Files
)



# Määritä projektin juurikansio (skripti on projektin juuressa)
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# --- Konfiguraatio ---
$promptFile = Join-Path $projectRoot "AIDER_AUDITOR_PROMPT.md"
$checklistDir = Join-Path $projectRoot "docs/audits"
$reportDir = Join-Path $projectRoot "docs/reports"

# --- Muuttujat ---
$filesToAudit = $Files -join " "
# Tarkista molempia nimeämiskäytäntöjä
$checklistFile1 = Join-Path $checklistDir "${AuditType}_CHECKLIST.md"
$checklistFile2 = Join-Path $checklistDir "${AuditType}_AUDIT_CHECKLIST.md"

if (Test-Path $checklistFile1) {
    $checklistFile = $checklistFile1
} elseif (Test-Path $checklistFile2) {
    $checklistFile = $checklistFile2
} else {
    $checklistFile = $checklistFile1  # Käytä oletuksena ensimmäistä
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = Join-Path $reportDir "${AuditType}_AUDIT_REPORT_${timestamp}.md"
$tempMessageFile = [System.IO.Path]::GetTempFileName()

# --- Tarkistukset ---
Write-Host "Debug: Projektin juuri: $projectRoot"
Write-Host "Debug: Kehotetiedosto: $promptFile"
Write-Host "Debug: Tarkistuslista: $checklistFile"



if (-not (Test-Path $promptFile)) {
    Write-Error "Virhe: Kehotetiedostoa ei löydy polusta $promptFile"
    exit 1
}

if (-not (Test-Path $checklistFile)) {
    Write-Error "Virhe: Tarkistuslistaa ei löydy polusta $checklistFile"
    exit 1
}

# Luo raporttikansio, jos sitä ei ole
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

# --- Suoritus ---
Write-Host "Aloitetaan $AuditType auditointi tiedostoille: $filesToAudit"
Write-Host "Tarkistuslista: $checklistFile"
Write-Host "Raportti tallennetaan tiedostoon: $reportFile"

# Rakenna komento ja kehotteen sisältö väliaikaiseen tiedostoon
$promptContent = Get-Content -Path $promptFile -Raw
Set-Content -Path $tempMessageFile -Value $promptContent

# Suorita Aider --message-file -parametrilla projektin juuressa
try {
    Push-Location $projectRoot
    aider --model anthropic/claude-3-5-sonnet-20241022 --aiderignore NUL --message-file $tempMessageFile "$checklistFile" $filesToAudit | Out-File -FilePath $reportFile -Encoding utf8
}
finally {
    Pop-Location
    # Varmista, että väliaikainen tiedosto poistetaan aina
    Remove-Item $tempMessageFile -ErrorAction SilentlyContinue
}

# --- Valmistuminen ---
Write-Host "✅ Auditointi valmis. Raportti tallennettu tiedostoon $reportFile"
# Tulosta raportti välitöntä tarkastelua varten
Get-Content -Path $reportFile 