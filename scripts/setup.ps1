# ==============================================================================
# scripts/setup.ps1 - Windows PowerShell Setup Wrapper
# ==============================================================================
# Usage:
#   .\scripts\setup.ps1 [-DryRun] [-Check] [-Finalize]
# ==============================================================================

param (
    [switch]$DryRun,
    [switch]$Check,
    [switch]$Finalize
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " GitHub Repository Template Initialization (Windows PowerShell) " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

$PythonExe = "python"
if (-not (Get-Command $PythonExe -ErrorAction SilentlyContinue)) {
    $PythonExe = "py"
    if (-not (Get-Command $PythonExe -ErrorAction SilentlyContinue)) {
        Write-Error "Python 3 is required but could not be located in PATH."
        exit 1
    }
}

if ($Check) {
    $CheckFailed = $false
    Write-Host "`n[*] Validating file naming conventions..." -ForegroundColor Cyan
    & $PythonExe "$ScriptDir\validate-filenames.py"
    if ($LASTEXITCODE -ne 0) { $CheckFailed = $true }

    Write-Host "`n[*] Checking unresolved template placeholders..." -ForegroundColor Cyan
    & $PythonExe "$ScriptDir\apply-template.py" "--check"
    if ($LASTEXITCODE -ne 0) { $CheckFailed = $true }

    if ($CheckFailed) {
        Write-Error "Repository checks failed."
        exit 1
    }
    Write-Host "`n[+] All repository checks passed." -ForegroundColor Green
    exit 0
}

$ApplyArgs = @("$ScriptDir\apply-template.py")
if ($DryRun) { $ApplyArgs += "--dry-run" }
if ($Finalize) { $ApplyArgs += "--finalize" }

& $PythonExe @ApplyArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "Template substitution failed."
    exit $LASTEXITCODE
}

if (-not $DryRun) {
    Write-Host "`n[*] Configuring Git Hooks..." -ForegroundColor Green
    & $PythonExe "$ScriptDir\install-hooks.py"
}

Write-Host "`n[+] Setup completed successfully!" -ForegroundColor Green
